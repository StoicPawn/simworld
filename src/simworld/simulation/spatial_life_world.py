from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from random import Random

from simworld.core.event import Event
from simworld.simulation.disequilibrium_world import DisequilibriumSimulationResult, DisequilibriumWorldSimulation
from simworld.simulation.first_world import FirstWorldConfig
from simworld.social.network import SocialTie
from simworld.spatial.grid import CellCoord
from simworld.spatial.presence import PresenceLedger


@dataclass(frozen=True, slots=True)
class SpatialLifeSimulationResult:
    disequilibrium: DisequilibriumSimulationResult
    presence: PresenceLedger
    movement_events: int
    encounter_events: int
    encounter_ties: int


class SpatialLifeWorldSimulation(DisequilibriumWorldSimulation):
    """Adds individual presence, local movement and co-presence-driven encounters.

    No market, village centre or important place is constructed here. People move
    through actual cells, repeatedly use some cells, meet whoever is present there,
    and leave a measurable spatial history. Higher-level place concepts are derived
    later from that history.
    """

    def __init__(self, config: FirstWorldConfig) -> None:
        super().__init__(config)
        self.spatial_life_rng = Random(config.seed ^ 0x5A17E11)
        self.presence = PresenceLedger()
        self.movement_events = 0
        self.encounter_events = 0
        self.encounter_ties = 0

    def initialize(self) -> None:
        super().initialize()
        if self.presence.positions:
            return
        for person_id in self.person_ids:
            settlement_id = str(self.world.entities[person_id].attributes["settlement_id"])
            self.presence.place(person_id, self._cells[settlement_id])

    def _cell_attractiveness(self, person_id: str, cell: CellCoord) -> float:
        layers = self.generated.spatial_map.layers
        if not bool(layers.get("passable", cell)):
            return -1e9
        fertility = float(self.generated.fertility[cell.y, cell.x])
        timber = float(self.generated.timber[cell.y, cell.x])
        habitability = float(self.generated.habitability[cell.y, cell.x])
        movement_cost = max(0.01, float(layers.get("movement_cost", cell)))
        familiarity = min(1.5, 0.04 * self.presence.visits.get(cell, 0))
        individual_noise = self.spatial_life_rng.uniform(-0.18, 0.18)
        return (
            0.42 * fertility
            + 0.18 * timber
            + 0.36 * habitability
            + familiarity
            - 0.08 * movement_cost
            + individual_noise
        )

    def _choose_local_destination(self, person_id: str) -> CellCoord:
        current = self.presence.positions[person_id]
        candidates = (current,) + self.generated.spatial_map.spec.neighbors(current, diagonals=True)
        scored = [(self._cell_attractiveness(person_id, cell), cell) for cell in candidates]
        scored = [item for item in scored if item[0] > -1e8]
        if not scored:
            return current
        scored.sort(key=lambda item: item[0], reverse=True)
        # Bounded stochastic choice: usually prefer good cells, never perfect optimization.
        shortlist = scored[: min(4, len(scored))]
        weights = [max(0.03, score - shortlist[-1][0] + 0.08) for score, _ in shortlist]
        return self.spatial_life_rng.choices([cell for _, cell in shortlist], weights=weights, k=1)[0]

    def _move_people(self, year: int) -> None:
        for person_id in tuple(self.person_ids):
            if not self._alive(person_id):
                continue
            entity = self.world.entities[person_id]
            age = year - int(entity.attributes["birth_time"])
            if age < 7:
                continue
            # Most people make a local excursion; some remain where they are.
            if self.spatial_life_rng.random() > min(0.92, 0.48 + 0.012 * min(age, 35)):
                self.presence.record_visit(person_id, self.presence.positions[person_id])
                continue
            origin = self.presence.positions[person_id]
            destination = self._choose_local_destination(person_id)
            self.presence.move(person_id, destination)
            if destination == origin:
                continue
            self.movement_events += 1
            self.world.record_event(
                Event(
                    kind="local_movement",
                    time=year,
                    participants=(person_id,),
                    locations=(),
                    impact=0.025,
                    payload={
                        "from_cell": [origin.x, origin.y],
                        "to_cell": [destination.x, destination.y],
                    },
                )
            )

    def _record_productive_presence(self, year: int) -> None:
        for household in self.households.active_households():
            for relation in self.property_registry.relations_of(household.id, year, "use"):
                asset = self.property_registry.assets[relation.asset_id]
                if asset.kind != "field_plot":
                    continue
                x = asset.attributes.get("x")
                y = asset.attributes.get("y")
                if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                    self.presence.record_productive_use(CellCoord(int(x), int(y)))

    def _run_spatial_encounters(self, year: int) -> None:
        for cell, occupants in self.presence.occupants().items():
            alive = tuple(person_id for person_id in occupants if self._alive(person_id))
            if len(alive) < 2:
                continue
            pairs = tuple(combinations(alive, 2))
            self.presence.record_encounter(cell, len(pairs))
            self.encounter_events += 1
            self.world.record_event(
                Event(
                    kind="spatial_encounter",
                    time=year,
                    participants=alive,
                    locations=(),
                    impact=min(0.22, 0.025 + 0.01 * len(pairs)),
                    payload={"cell": [cell.x, cell.y], "pair_count": len(pairs)},
                )
            )
            for a, b in pairs:
                if self.network.connection_strength(a, b, year) > 0.0:
                    continue
                if self.spatial_life_rng.random() < 0.08:
                    positive = self.spatial_life_rng.random() < 0.78
                    self.network.add(
                        SocialTie(
                            a,
                            b,
                            kind="acquaintance" if positive else "rivalry",
                            strength=self.spatial_life_rng.uniform(0.08, 0.32),
                            started_at=year,
                            sentiment=(
                                self.spatial_life_rng.uniform(0.05, 0.42)
                                if positive
                                else self.spatial_life_rng.uniform(-0.55, -0.12)
                            ),
                            trust=self.spatial_life_rng.uniform(0.22, 0.58),
                        )
                    )
                    self.encounter_ties += 1

    def run(self) -> SpatialLifeSimulationResult:
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
            self._move_people(year)
            self._record_productive_presence(year)
            self._run_spatial_encounters(year)
            self._evolve_social_network(year)
            self._transmit_memory(year)

        base_result = super().run if False else None  # keeps composition explicit; no second run
        from simworld.simulation.first_world import SimulationResult
        from simworld.simulation.social_world import SocialSimulationResult
        from simworld.simulation.generational_world import GenerationalSimulationResult
        from simworld.simulation.material_world import MaterialSimulationResult
        from simworld.simulation.institutional_world import InstitutionalSimulationResult
        from simworld.simulation.disequilibrium_world import DisequilibriumSimulationResult

        base = SimulationResult(self.config, self.generated, self.world, tuple(self.settlement_ids))
        social = SocialSimulationResult(base, tuple(self.house_ids), tuple(self.representative_ids), self.social_memory)
        generational = GenerationalSimulationResult(
            social,
            self.kinship,
            self.network,
            self.households,
            self.pregnancies,
            tuple(self.inheritance_transfers),
            tuple(self.person_ids),
            self._lineage_candidates(),
        )
        material = MaterialSimulationResult(generational, self.property_registry, self.inventories, self.exchange_count)
        institutional = InstitutionalSimulationResult(material, self.obligations, self.organizations, self.cooperation, self.authority)
        disequilibrium = DisequilibriumSimulationResult(
            institutional,
            self.storage_profiles,
            self.demand_profiles,
            self.material_shocks,
            self.spoilage_events,
        )
        return SpatialLifeSimulationResult(
            disequilibrium=disequilibrium,
            presence=self.presence,
            movement_events=self.movement_events,
            encounter_events=self.encounter_events,
            encounter_ties=self.encounter_ties,
        )
