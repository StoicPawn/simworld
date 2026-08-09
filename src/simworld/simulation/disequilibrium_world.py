from __future__ import annotations

from dataclasses import dataclass
from random import Random

from simworld.core.entity import Entity
from simworld.core.event import Event
from simworld.economy.storage import HouseholdDemandProfile, StorageProfile, age_stock
from simworld.simulation.first_world import FirstWorldConfig, SimulationResult
from simworld.simulation.generational_world import GenerationalSimulationResult
from simworld.simulation.institutional_world import InstitutionalSimulationResult, InstitutionalWorldSimulation
from simworld.simulation.material_world import MaterialSimulationResult
from simworld.simulation.social_world import SocialSimulationResult


@dataclass(frozen=True, slots=True)
class DisequilibriumSimulationResult:
    institutional: InstitutionalSimulationResult
    storage_profiles: dict[str, StorageProfile]
    demand_profiles: dict[str, HouseholdDemandProfile]
    material_shocks: int
    spoilage_events: int


class DisequilibriumWorldSimulation(InstitutionalWorldSimulation):
    """Adds household-level material heterogeneity, storage loss and local shocks.

    The goal is not to manufacture trade or credit. It creates realistic sources of
    asynchronous surplus and shortage so lower-level exchange, obligation and
    institutional processes have causal opportunities to activate.
    """

    def __init__(self, config: FirstWorldConfig) -> None:
        super().__init__(config)
        self.disequilibrium_rng = Random(config.seed ^ 0xD15E0A11)
        self.storage_profiles: dict[str, StorageProfile] = {}
        self.demand_profiles: dict[str, HouseholdDemandProfile] = {}
        self._shock_vulnerability: dict[str, float] = {}
        self.material_shocks = 0
        self.spoilage_events = 0

    def initialize(self) -> None:
        super().initialize()
        if self.storage_profiles:
            return
        for household in self.households.active_households():
            if household.id not in self.world.entities:
                self.world.add_entity(
                    Entity(
                        kind="household",
                        name=f"Household-{household.id[-8:]}",
                        created_at=household.formed_at,
                        id=household.id,
                        attributes={"settlement_id": household.settlement_id},
                        tags={"household", "aggregate_social_unit"},
                    )
                )
            shelter = max(0.05, min(1.5, household.shelter_quality))
            capacity = self.disequilibrium_rng.uniform(0.75, 2.8) * (0.75 + 0.25 * shelter)
            preservation = max(
                0.18,
                min(0.92, self.disequilibrium_rng.uniform(0.32, 0.78) + 0.08 * shelter),
            )
            exposure = self.disequilibrium_rng.uniform(0.15, 0.95)
            self.storage_profiles[household.id] = StorageProfile(
                capacity=capacity,
                preservation=preservation,
                exposure=exposure,
            )
            self.demand_profiles[household.id] = HouseholdDemandProfile(
                adult_food_need=self.disequilibrium_rng.uniform(0.43, 0.59),
                child_food_factor=self.disequilibrium_rng.uniform(0.52, 0.76),
                elder_food_factor=self.disequilibrium_rng.uniform(0.72, 0.94),
                reserve_target_per_person=self.disequilibrium_rng.uniform(0.28, 0.62),
            )
            self._shock_vulnerability[household.id] = self.disequilibrium_rng.uniform(0.45, 1.35)

    def _household_ages(self, household_id: str, year: int) -> tuple[int, ...]:
        ages: list[int] = []
        for person_id in self._living_members(household_id):
            entity = self.world.entities[person_id]
            ages.append(max(0, year - int(entity.attributes["birth_time"])))
        return tuple(ages)

    def _apply_local_material_shock(self, household_id: str, year: int) -> None:
        inventory = self.inventories[household_id]
        vulnerability = self._shock_vulnerability[household_id]
        probability = min(0.22, 0.035 + 0.055 * vulnerability)
        if self.disequilibrium_rng.random() >= probability:
            return

        draw = self.disequilibrium_rng.random()
        household = self.households.households[household_id]
        if draw < 0.48:
            kind = "pest_or_local_crop_loss"
            fraction = self.disequilibrium_rng.uniform(0.18, 0.62) * vulnerability
            loss = min(inventory.amount("grain"), inventory.amount("grain") * fraction)
            if loss > 0:
                inventory.remove("grain", loss)
            payload = {"grain_lost": round(loss, 4)}
        elif draw < 0.76:
            kind = "storage_damage"
            fraction = self.disequilibrium_rng.uniform(0.12, 0.48) * vulnerability
            grain_loss = min(inventory.amount("grain"), inventory.amount("grain") * fraction)
            timber_loss = min(inventory.amount("timber"), inventory.amount("timber") * fraction * 0.5)
            if grain_loss > 0:
                inventory.remove("grain", grain_loss)
            if timber_loss > 0:
                inventory.remove("timber", timber_loss)
            payload = {
                "grain_lost": round(grain_loss, 4),
                "timber_lost": round(timber_loss, 4),
            }
        else:
            kind = "tool_breakage"
            fraction = self.disequilibrium_rng.uniform(0.15, 0.55)
            loss = min(inventory.amount("tools"), inventory.amount("tools") * fraction)
            if loss > 0:
                inventory.remove("tools", loss)
            payload = {"tools_lost": round(loss, 4)}

        household.food_stock = inventory.amount("grain")
        self.material_shocks += 1
        self.world.record_event(
            Event(
                kind="local_material_shock",
                time=year,
                participants=tuple(sorted(self._living_members(household_id))),
                locations=(household.settlement_id,),
                impact=0.16,
                payload={"household_id": household_id, "shock_kind": kind, **payload},
            )
        )

    def _apply_storage_and_demand(self, household_id: str, year: int, food_ratio: dict[str, float]) -> None:
        household = self.households.households[household_id]
        inventory = self.inventories[household_id]
        profile = self.storage_profiles[household_id]
        local_ratio = food_ratio.get(household.settlement_id, 1.0)
        climate_stress = max(0.0, min(1.5, 1.05 - local_ratio))
        storage = age_stock(
            inventory,
            "grain",
            profile,
            climate_stress=climate_stress,
            rng=self.disequilibrium_rng,
        )
        if storage.spoiled > 0.02 or storage.overflow_lost > 0.02:
            self.spoilage_events += 1
            self.world.record_event(
                Event(
                    kind="storage_loss",
                    time=year,
                    participants=tuple(sorted(self._living_members(household_id))),
                    locations=(household.settlement_id,),
                    impact=min(0.35, 0.04 + storage.spoiled + 0.5 * storage.overflow_lost),
                    payload={
                        "household_id": household_id,
                        "spoiled": round(storage.spoiled, 4),
                        "overflow_lost": round(storage.overflow_lost, 4),
                        "remaining": round(storage.remaining, 4),
                    },
                )
            )

        ages = self._household_ages(household_id, year)
        desired = self.demand_profiles[household_id].annual_food_need(ages)
        baseline_already_consumed = 0.46 * len(ages)
        additional_need = max(0.0, desired - baseline_already_consumed)
        consumed = min(inventory.amount("grain"), additional_need)
        if consumed > 0:
            inventory.remove("grain", consumed)
        unmet = max(0.0, additional_need - consumed)
        if unmet > 0:
            household.debt += 0.018 * unmet
            self.world.record_event(
                Event(
                    kind="household_unmet_food_need",
                    time=year,
                    participants=tuple(sorted(self._living_members(household_id))),
                    locations=(household.settlement_id,),
                    impact=min(0.45, 0.08 + 0.12 * unmet),
                    payload={
                        "household_id": household_id,
                        "additional_need": round(additional_need, 4),
                        "unmet": round(unmet, 4),
                    },
                )
            )
        household.food_stock = inventory.amount("grain")

    def _run_material_production(self, year: int, food_ratio: dict[str, float]) -> None:
        super()._run_material_production(year, food_ratio)
        for household in self.households.active_households():
            self._apply_local_material_shock(household.id, year)
            self._apply_storage_and_demand(household.id, year, food_ratio)

    def run(self) -> DisequilibriumSimulationResult:
        self.initialize()
        for year in range(1, self.config.years + 1):
            self.world.advance_to(year)
            self._resolve_pregnancies(year)
            self._run_obligation_resolution(year)
            food_ratio = self._run_harvests(year)
            self._run_demography(year, food_ratio)
            self._run_material_production(year, food_ratio)
            before_exchange = len(self.world.events)
            self._run_material_exchange(year)
            self._learn_from_exchange_events(tuple(self.world.events[before_exchange:]))
            self._run_credit_formation(year)
            self._run_organization_emergence(year)
            self._run_organization_processes(year)
            self._update_households(year, food_ratio)
            for settlement_id in self.settlement_ids:
                petition = self._experience_and_request(year, settlement_id, food_ratio[settlement_id])
                self._apply_house_action(year, settlement_id, petition)
                self._verify_reports(year, settlement_id, food_ratio[settlement_id])
            self._run_migration(year, food_ratio)
            self._run_discoveries(year)
            self._evolve_existing_relations(year)
            self._run_reproduction(year)
            self._run_mortality(year)
            self._evolve_social_network(year)
            self._transmit_memory(year)

        base = SimulationResult(self.config, self.generated, self.world, tuple(self.settlement_ids))
        social = SocialSimulationResult(
            base=base,
            house_ids=tuple(self.house_ids),
            representative_ids=tuple(self.representative_ids),
            social_memory=self.social_memory,
        )
        generational = GenerationalSimulationResult(
            social=social,
            kinship=self.kinship,
            network=self.network,
            households=self.households,
            pregnancies=self.pregnancies,
            inheritance_transfers=tuple(self.inheritance_transfers),
            person_ids=tuple(self.person_ids),
            lineage_candidates=self._lineage_candidates(),
        )
        material = MaterialSimulationResult(
            generational=generational,
            property_registry=self.property_registry,
            inventories=self.inventories,
            exchange_count=self.exchange_count,
        )
        institutional = InstitutionalSimulationResult(
            material=material,
            obligations=self.obligations,
            organizations=self.organizations,
            cooperation=self.cooperation,
            authority=self.authority,
        )
        return DisequilibriumSimulationResult(
            institutional=institutional,
            storage_profiles=self.storage_profiles,
            demand_profiles=self.demand_profiles,
            material_shocks=self.material_shocks,
            spoilage_events=self.spoilage_events,
        )