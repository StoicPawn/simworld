from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from random import Random

from simworld.core.event import Event
from simworld.economy.exchange import ExchangeProposal, execute_exchange
from simworld.economy.production import Inventory, ProductionContext, ProductionProcess, produce
from simworld.economy.property import Asset, AssetRelation, PropertyRegistry
from simworld.simulation.first_world import FirstWorldConfig, SimulationResult
from simworld.simulation.generational_world import GenerationalSimulationResult, GenerationalWorldSimulation
from simworld.simulation.social_world import SocialSimulationResult


@dataclass(frozen=True, slots=True)
class MaterialSimulationResult:
    generational: GenerationalSimulationResult
    property_registry: PropertyRegistry
    inventories: dict[str, Inventory]
    exchange_count: int


class MaterialWorldSimulation(GenerationalWorldSimulation):
    """Adds assets, possession/use, production, inventories and spatial exchange.

    The material substrate is deliberately pre-legal. Households can occupy, use and
    effectively control assets without a universal concept of ownership. Formal
    property can later emerge from claims, recognition and enforcement institutions.
    Scarcity changes feasible actions and incentives; it never prescribes a social or
    political response.
    """

    def __init__(self, config: FirstWorldConfig) -> None:
        super().__init__(config)
        self.material_rng = Random(config.seed ^ 0xEC0A011)
        self.property_registry = PropertyRegistry()
        self.inventories: dict[str, Inventory] = {}
        self._household_capacity: dict[str, tuple[float, float]] = {}
        self.exchange_count = 0

    def initialize(self) -> None:
        super().initialize()
        if self.inventories:
            return
        for household in self.households.active_households():
            cell = self._cells[household.settlement_id]
            fertility = float(self.generated.fertility[cell.y, cell.x])
            timber = float(self.generated.timber[cell.y, cell.x])
            farm_skill = self.material_rng.uniform(0.65, 1.25)
            wood_skill = self.material_rng.uniform(0.45, 1.25)
            self._household_capacity[household.id] = (farm_skill, wood_skill)

            field = Asset(
                kind="field_plot",
                location=household.settlement_id,
                productive_capacity=max(0.05, 0.45 + 1.7 * fertility),
                attributes={"fertility": fertility, "x": cell.x, "y": cell.y},
            )
            self.property_registry.add_asset(field)
            # Early-world relation: the household occupies/uses/controls the plot.
            # No universal legal ownership is asserted.
            for relation_kind, strength in (("possess", 1.0), ("use", 1.0), ("control", 0.85)):
                self.property_registry.relate(
                    AssetRelation(
                        asset_id=field.id,
                        actor_id=household.id,
                        strength=strength,
                        kind=relation_kind,
                        started_at=0,
                        provenance="initial_occupation",
                    )
                )

            self.inventories[household.id] = Inventory(
                household.id,
                {
                    "grain": self.material_rng.uniform(0.4, 1.8),
                    "timber": self.material_rng.uniform(0.15, 1.2) * (0.55 + timber),
                    "tools": self.material_rng.uniform(0.25, 0.8),
                },
            )
            self.world.record_event(
                Event(
                    kind="material_household_initialized",
                    time=0,
                    participants=tuple(sorted(household.members)),
                    locations=(household.settlement_id,),
                    impact=0.08,
                    payload={
                        "household_id": household.id,
                        "field_asset_id": field.id,
                        "asset_relation": "occupation_use_control",
                        "farm_skill": round(farm_skill, 4),
                        "wood_skill": round(wood_skill, 4),
                    },
                )
            )

    def _living_members(self, household_id: str) -> list[str]:
        household = self.households.households[household_id]
        return [person_id for person_id in household.members if self._alive(person_id)]

    def _adult_labour(self, household_id: str, year: int) -> float:
        labour = 0.0
        for person_id in self._living_members(household_id):
            entity = self.world.entities[person_id]
            age = year - int(entity.attributes["birth_time"])
            health = float(entity.attributes.get("health", 1.0))
            if 14 <= age <= 70:
                labour += health * (0.55 if age < 18 or age > 60 else 1.0)
        return labour

    def _field_quality(self, household_id: str, year: int) -> float:
        qualities: list[float] = []
        for relation in self.property_registry.relations_of(household_id, year, "use"):
            asset = self.property_registry.assets[relation.asset_id]
            if asset.kind == "field_plot":
                qualities.append(asset.productive_capacity * relation.strength)
        return sum(qualities) if qualities else 0.0

    def _run_material_production(self, year: int, food_ratio: dict[str, float]) -> None:
        grain_process = ProductionProcess("grain", labour_per_unit=1.0, base_productivity=1.12)
        timber_process = ProductionProcess("timber", labour_per_unit=1.0, base_productivity=0.72)

        for household in self.households.active_households():
            inventory = self.inventories.setdefault(household.id, Inventory(household.id))
            labour = self._adult_labour(household.id, year)
            living = self._living_members(household.id)
            if labour <= 0:
                continue
            farm_skill, wood_skill = self._household_capacity.get(household.id, (1.0, 1.0))
            cell = self._cells[household.settlement_id]
            local_timber = float(self.generated.timber[cell.y, cell.x])
            climate = max(0.35, min(1.35, 0.62 + 0.38 * food_ratio.get(household.settlement_id, 1.0)))

            grain_share = max(0.28, min(0.82, 0.52 + self.material_rng.uniform(-0.14, 0.14)))
            grain_result = produce(
                grain_process,
                inventory,
                ProductionContext(
                    labour=labour * grain_share,
                    land_quality=self._field_quality(household.id, year) * farm_skill,
                    climate_factor=climate,
                    tool_factor=0.78 + 0.25 * min(1.5, inventory.amount("tools")),
                    security_factor=max(0.55, 1.0 - 0.18 * household.debt),
                ),
            )
            timber_result = produce(
                timber_process,
                inventory,
                ProductionContext(
                    labour=labour * (1.0 - grain_share),
                    land_quality=(0.35 + local_timber) * wood_skill,
                    climate_factor=1.0,
                    tool_factor=0.75 + 0.28 * min(1.5, inventory.amount("tools")),
                    security_factor=max(0.55, 1.0 - 0.18 * household.debt),
                ),
            )

            consumption = 0.46 * len(living)
            consumed = min(inventory.amount("grain"), consumption)
            inventory.remove("grain", consumed)
            shortage = max(0.0, consumption - consumed)
            household.food_stock = inventory.amount("grain")
            household.wealth = max(
                0.0,
                household.wealth
                + 0.018 * timber_result.quantity
                + 0.008 * grain_result.quantity
                - 0.055 * shortage,
            )
            if shortage > 0:
                household.debt += 0.025 * shortage

            self.world.record_event(
                Event(
                    kind="material_production",
                    time=year,
                    participants=tuple(sorted(living)),
                    locations=(household.settlement_id,),
                    impact=0.08 + 0.08 * shortage,
                    payload={
                        "household_id": household.id,
                        "grain_produced": round(grain_result.quantity, 4),
                        "timber_produced": round(timber_result.quantity, 4),
                        "grain_consumed": round(consumed, 4),
                        "food_shortage": round(shortage, 4),
                        "labour": round(labour, 4),
                    },
                )
            )

    def _household_connection(self, a_id: str, b_id: str, year: int) -> float:
        a_members = self._living_members(a_id)
        b_members = self._living_members(b_id)
        if not a_members or not b_members:
            return 0.0
        strongest = 0.0
        for a in a_members:
            for b in b_members:
                strongest = max(strongest, self.network.connection_strength(a, b, year))
        return strongest

    @lru_cache(maxsize=None)
    def _settlement_exchange_factor(self, a_settlement: str, b_settlement: str) -> float:
        if a_settlement == b_settlement:
            return 1.0
        first, second = sorted((a_settlement, b_settlement))
        path = self.generated.spatial_map.path(
            self._cells[first],
            self._cells[second],
            max_expansions=20_000,
        )
        if path is None:
            return 0.0
        return max(0.0, 1.0 - path.cost / 2_500_000.0)

    def _spatial_exchange_factor(self, a_id: str, b_id: str) -> float:
        a_settlement = self.households.households[a_id].settlement_id
        b_settlement = self.households.households[b_id].settlement_id
        first, second = sorted((a_settlement, b_settlement))
        return self._settlement_exchange_factor(first, second)

    def _run_material_exchange(self, year: int) -> None:
        household_ids = [household.id for household in self.households.active_households()]
        self.material_rng.shuffle(household_ids)
        for index, a_id in enumerate(household_ids):
            a_inv = self.inventories[a_id]
            for b_id in household_ids[index + 1 :]:
                b_inv = self.inventories[b_id]
                complementary = (
                    a_inv.amount("grain") < 0.55
                    and a_inv.amount("timber") > 0.7
                    and b_inv.amount("grain") > 1.0
                ) or (
                    b_inv.amount("grain") < 0.55
                    and b_inv.amount("timber") > 0.7
                    and a_inv.amount("grain") > 1.0
                )
                if not complementary:
                    continue
                spatial = self._spatial_exchange_factor(a_id, b_id)
                if spatial <= 0.08:
                    continue

                if a_inv.amount("grain") < 0.55:
                    buyer_id, seller_id = a_id, b_id
                else:
                    buyer_id, seller_id = b_id, a_id

                buyer = self.inventories[buyer_id]
                seller = self.inventories[seller_id]
                grain_quantity = min(0.45, max(0.1, seller.amount("grain") - 0.8))
                timber_quantity = min(0.35, max(0.08, buyer.amount("timber") - 0.55))
                if grain_quantity <= 0 or timber_quantity <= 0:
                    continue

                social = self._household_connection(buyer_id, seller_id, year)
                acceptance = max(
                    0.0,
                    min(
                        1.0,
                        0.46
                        + 0.27 * spatial
                        + 0.18 * min(1.0, social)
                        + self.material_rng.uniform(-0.12, 0.12),
                    ),
                )
                proposal = ExchangeProposal(
                    proposer_id=buyer_id,
                    receiver_id=seller_id,
                    offered_good="timber",
                    offered_quantity=timber_quantity,
                    requested_good="grain",
                    requested_quantity=grain_quantity,
                )
                result = execute_exchange(proposal, self.inventories, acceptance)
                event_kind = "material_exchange" if result.accepted else "material_exchange_rejected"
                locations = (
                    self.households.households[buyer_id].settlement_id,
                    self.households.households[seller_id].settlement_id,
                )
                self.world.record_event(
                    Event(
                        kind=event_kind,
                        time=year,
                        participants=(buyer_id, seller_id),
                        locations=locations,
                        impact=0.13 if result.accepted else 0.05,
                        payload={
                            "grain": round(grain_quantity, 4),
                            "timber": round(timber_quantity, 4),
                            "spatial_access": round(spatial, 4),
                            "social_connection": round(social, 4),
                            "acceptance_score": round(acceptance, 4),
                            "reason": result.reason,
                        },
                    )
                )
                if result.accepted:
                    self.exchange_count += 1
                    self.households.households[buyer_id].food_stock = buyer.amount("grain")
                    self.households.households[seller_id].food_stock = seller.amount("grain")
                break

    def run(self) -> MaterialSimulationResult:
        self.initialize()
        for year in range(1, self.config.years + 1):
            self.world.advance_to(year)
            self._resolve_pregnancies(year)
            food_ratio = self._run_harvests(year)
            self._run_demography(year, food_ratio)
            self._run_material_production(year, food_ratio)
            self._run_material_exchange(year)
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
        return MaterialSimulationResult(
            generational=generational,
            property_registry=self.property_registry,
            inventories=self.inventories,
            exchange_count=self.exchange_count,
        )
