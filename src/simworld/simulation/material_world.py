from __future__ import annotations

from dataclasses import dataclass
from random import Random

from simworld.core.event import Event
from simworld.economy.exchange import ExchangeProposal, execute_exchange
from simworld.economy.production import Inventory, ProductionContext, ProductionProcess, produce
from simworld.economy.property import Asset, PropertyRegistry, PropertyRight
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
    """Adds ownership, household production, inventories and spatial exchange.

    The layer intentionally models material constraints rather than prescribing social
    outcomes. Scarcity changes feasible actions and incentives; it does not directly
    create a revolt, migration, trade, or political response.
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
                attributes={
                    "fertility": fertility,
                    "x": cell.x,
                    "y": cell.y,
                },
            )
            self.property_registry.add_asset(field)
            self.property_registry.grant(
                PropertyRight(field.id, household.id, 1.0, started_at=0)
            )

            inventory = Inventory(
                household.id,
                {
                    "grain": self.material_rng.uniform(0.4, 1.8),
                    "timber": self.material_rng.uniform(0.15, 1.2) * (0.55 + timber),
                    "tools": self.material_rng.uniform(0.25, 0.8),
                },
            )
            self.inventories[household.id] = inventory
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
        for right in self.property_registry.holdings(household_id, year):
            asset = self.property_registry.assets[right.asset_id]
            if asset.kind == "field_plot":
                qualities.append(asset.productive_capacity * right.share)
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

    def _spatial_exchange_factor(self, a_id: str, b_id: str) -> float:
        a = self.households.households[a_id]
        b = self.households.households[b_id]
        if a.settlement_id == b.settlement_id:
            return 1.0
        path = self.generated.spatial_map.path(
            self._cells[a.settlement_id],
            self._cells[b.settlement_id],
            max_expansions=20_000,
        )
        if path is None:
            return 0.0
        return max(0.0, 1.0 - path.cost / 2_500_000.0)

    def _run_material_exchange(self, year: int) -> None:
        household_ids = [household.id for household in self.households.active_households()]
        self.material_rng.shuffle(household_ids)
        for index, a_id in enumerate(household_ids):
            a_inv = self.inventories[a_id]
            for b_id in household_ids[index + 1 :]:
                spatial = self._spatial_exchange_factor(a_id, b_id)
                if spatial <= 0.08:
                    continue
                b_inv = self.inventories[b_id]

                if a_inv.amount("grain") < 0.55 and a_inv.amount("timber") > 0.7 and b_inv.amount("grain") > 1.0:
                    buyer_id, seller_id = a_id, b_id
                elif b_inv.amount("grain") < 0.55 and b_inv.amount("timber") > 0.7 and a_inv.amount("grain") > 1.0:
                    buyer_id, seller_id = b_id, a_id
                else:
                    continue

                buyer = self.inventories[buyer_id]
                seller = self.inventories[seller_id]
                grain_quantity = min(0.45, max(0.1, seller.amount("grain") - 0.8))
                timber_quantity = min(0.35, max(0.08, buyer.amount("timber") - 0.55))
                if grain_quantity <= 0 or timber_quantity <= 0:
                    continue

                social = self._household_connection(buyer_id, seller_id, year)
                acceptance = max(
                    0.0,
                    min(1.0, 0.46 + 0.27 * spatial + 0.18 * min(1.0, social) + self.material_rng.uniform(-0.12, 0.12)),
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
