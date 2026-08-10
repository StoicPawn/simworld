from __future__ import annotations

from dataclasses import dataclass

from simworld.core.event import Event
from simworld.core.randomness import SeedStreams
from simworld.simulation.first_world import FirstWorldConfig
from simworld.simulation.microgeography_world import MicrogeographySimulationResult, MicrogeographyWorldSimulation
from simworld.spatial import CellCoord
from simworld.spatial.activity import SettlementNucleusView, derive_settlement_nuclei


@dataclass(frozen=True, slots=True)
class EmergentSettlementSimulationResult:
    base: MicrogeographySimulationResult
    household_home_cells: dict[str, CellCoord]
    nuclei: tuple[SettlementNucleusView, ...]
    residence_shifts: int
    construction_events: int


class EmergentSettlementWorldSimulation(MicrogeographyWorldSimulation):
    """Persistent residence and construction before any primitive settlement category.

    Coarse settlements inherited from the early vertical slice remain only as bootstrap
    coordinates. Households acquire their own residential anchors, which can relocate
    toward repeatedly useful cells. Sparse residence/construction history is then
    clustered retrospectively into inhabited nuclei. No village/town/city object is
    created here.
    """

    def __init__(self, config: FirstWorldConfig) -> None:
        super().__init__(config)
        self.seed_streams = SeedStreams(config.seed)
        self.residence_streams = self.seed_streams.scoped("residence")
        self.household_home_cells: dict[str, CellCoord] = {}
        self.residence_shifts = 0
        self.construction_events = 0

    def initialize(self) -> None:
        super().initialize()
        for household in self.households.active_households():
            if household.id in self.household_home_cells:
                continue
            self.household_home_cells[household.id] = self._cells[household.settlement_id]

    def _home_score(self, household_id: str, cell: CellCoord) -> float:
        gathering, cultivation, general = self._cell_affordances(cell)
        history = self.activity.at(cell)
        household = self.households.households[household_id]
        inventory = self.inventories.get(household_id)
        food = inventory.amount("grain") if inventory is not None else household.food_stock
        security = max(0.0, min(1.0, 0.55 + 0.12 * food - 0.08 * household.debt))
        return (
            0.28 * gathering
            + 0.31 * cultivation
            + 0.25 * general
            + 0.045 * min(8.0, history.residence)
            + 0.035 * min(8.0, history.construction)
            + 0.055 * security
        )

    def _candidate_home_cells(self, household_id: str) -> tuple[CellCoord, ...]:
        household = self.households.households[household_id]
        current = self.household_home_cells[household_id]
        candidates: set[CellCoord] = {current}
        for person_id in household.members:
            cell = self.person_cells.get(person_id)
            if cell is not None:
                candidates.add(cell)
        for cell in tuple(candidates):
            for nearby in self._candidate_cells(cell, radius=1):
                candidates.add(nearby)
        return tuple(sorted(candidates, key=lambda c: (c.y, c.x)))

    def _maybe_relocate_household(self, household_id: str, year: int) -> None:
        current = self.household_home_cells[household_id]
        candidates = self._candidate_home_cells(household_id)
        scored = sorted(
            ((self._home_score(household_id, cell), cell) for cell in candidates),
            key=lambda item: (-item[0], item[1].y, item[1].x),
        )
        best_score, best = scored[0]
        current_score = self._home_score(household_id, current)
        if best == current or best_score < current_score + 0.045:
            return

        household = self.households.households[household_id]
        living = [person_id for person_id in household.members if self._alive(person_id)]
        if not living:
            return
        move_probability = min(0.62, 0.08 + 2.6 * (best_score - current_score))
        move_rng = self.residence_streams.python(household_id, year, "move")
        if move_rng.random() >= move_probability:
            return

        self.household_home_cells[household_id] = best
        self.residence_shifts += 1
        self.world.record_event(
            Event(
                kind="household_residence_shifted",
                time=year,
                participants=tuple(sorted(living)),
                locations=(household.settlement_id,),
                impact=0.12,
                payload={
                    "household_id": household_id,
                    "from_cell": [current.x, current.y],
                    "to_cell": [best.x, best.y],
                    "relative_attraction": round(best_score - current_score, 4),
                },
            )
        )

    def _record_residence_and_construction(self, household_id: str, year: int) -> None:
        household = self.households.households[household_id]
        home = self.household_home_cells[household_id]
        living = [person_id for person_id in household.members if self._alive(person_id)]
        if not living:
            return
        for person_id in living:
            self.activity.record(home, time=year, actor_id=person_id, kind="residence", amount=0.7)

        state = self.activity.at(home)
        inventory = self.inventories.get(household_id)
        food = inventory.amount("grain") if inventory is not None else household.food_stock
        adults = sum(
            1
            for person_id in living
            if year - int(self.world.entities[person_id].attributes["birth_time"]) >= 14
        )
        if adults <= 0:
            return
        persistence = 1
        if state.first_seen is not None and state.last_seen is not None:
            persistence = max(1, state.last_seen - state.first_seen + 1)
        build_probability = min(
            0.36,
            0.015
            + 0.012 * min(12, persistence)
            + 0.012 * min(8.0, state.residence)
            + 0.018 * min(4.0, food),
        )
        build_rng = self.residence_streams.python(household_id, year, "construct")
        if build_rng.random() >= build_probability:
            return

        amount = build_rng.uniform(0.12, 0.42)
        self.activity.record(home, time=year, actor_id=household_id, kind="construct", amount=amount)
        household.shelter_quality = min(1.5, household.shelter_quality + 0.015 * amount)
        self.construction_events += 1
        self.world.record_event(
            Event(
                kind="local_construction",
                time=year,
                participants=tuple(sorted(living)),
                locations=(household.settlement_id,),
                impact=0.07,
                payload={
                    "household_id": household_id,
                    "cell": [home.x, home.y],
                    "construction_amount": round(amount, 4),
                },
            )
        )

    def _run_residence_process(self, year: int) -> None:
        for household in sorted(self.households.active_households(), key=lambda item: item.id):
            if household.id not in self.household_home_cells:
                self.household_home_cells[household.id] = self._cells[household.settlement_id]
            self._maybe_relocate_household(household.id, year)
            self._record_residence_and_construction(household.id, year)

    def _run_microgeography(self, year: int) -> None:
        # Annual activity is treated as excursions from a persistent residence anchor.
        # This prevents random-walk drift from becoming accidental migration.
        for household in sorted(self.households.active_households(), key=lambda item: item.id):
            home = self.household_home_cells.get(household.id)
            if home is None:
                home = self._cells[household.settlement_id]
                self.household_home_cells[household.id] = home
            for person_id in sorted(household.members):
                if self._alive(person_id):
                    self.person_cells[person_id] = home
        super()._run_microgeography(year)
        self._run_residence_process(year)

    def run(self) -> EmergentSettlementSimulationResult:
        base = super().run()
        return EmergentSettlementSimulationResult(
            base=base,
            household_home_cells=dict(self.household_home_cells),
            nuclei=derive_settlement_nuclei(self.activity),
            residence_shifts=self.residence_shifts,
            construction_events=self.construction_events,
        )
