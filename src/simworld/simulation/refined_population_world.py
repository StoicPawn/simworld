from __future__ import annotations

from dataclasses import dataclass

from simworld.core.event import Event
from simworld.population.refinement import PopulationRefinementLedger, step_unmaterialized_population
from simworld.simulation.authoritative_population_world import (
    AuthoritativePopulationSimulationResult,
    AuthoritativePopulationWorldSimulation,
)
from simworld.simulation.first_world import FirstWorldConfig
from simworld.spatial import CellCoord


@dataclass(frozen=True, slots=True)
class RefinedPopulationSimulationResult:
    base: AuthoritativePopulationSimulationResult
    refinement: PopulationRefinementLedger
    total_population: float
    materialized_population: float
    unresolved_population: float
    living_materialized_people: int


class RefinedPopulationWorldSimulation(AuthoritativePopulationWorldSimulation):
    """First true aggregate↔individual demographic resolution bridge.

    The population field remains total physical headcount. Living detailed people reserve
    one unit each from that field. Aggregate demographic dynamics apply only to the
    unresolved remainder; detailed births, deaths and residence moves update the total
    field explicitly.
    """

    def __init__(self, config: FirstWorldConfig) -> None:
        super().__init__(config)
        self.refinement = PopulationRefinementLedger()
        self._refinement_initialized = False

    def _backing_cell(self, preferred: CellCoord, people: int) -> CellCoord:
        assert self.population_field is not None
        if self.population_field.available_at(preferred) + 1e-9 >= people:
            return preferred

        candidates = [
            cell
            for cell in self.population_field.high_density_cells(minimum_population=float(people))
            if self.population_field.available_at(cell) + 1e-9 >= people
        ]
        if not candidates:
            raise RuntimeError("population field cannot back current materialized household")
        candidates.sort(
            key=lambda cell: (
                (cell.x - preferred.x) ** 2 + (cell.y - preferred.y) ** 2,
                -self.population_field.available_at(cell),
                cell.y,
                cell.x,
            )
        )
        return candidates[0]

    def initialize(self) -> None:
        super().initialize()
        if self._refinement_initialized:
            return
        assert self.population_field is not None

        for household in sorted(self.households.active_households(), key=lambda item: item.id):
            living = sorted(person_id for person_id in household.members if self._alive(person_id))
            if not living:
                continue
            preferred = self.household_home_cells[household.id]
            backing = self._backing_cell(preferred, len(living))
            self.household_home_cells[household.id] = backing
            for person_id in living:
                self.person_cells[person_id] = backing
                self.refinement.materialize_existing(
                    self.population_field,
                    person_id,
                    backing,
                    time=0,
                )

        # Handle any detailed person not currently assigned to an active household.
        for person_id in sorted(self.person_ids):
            if not self._alive(person_id) or person_id in self.refinement.records:
                continue
            preferred = self.person_cells.get(person_id)
            if preferred is None:
                settlement_id = str(self.world.entities[person_id].attributes["settlement_id"])
                preferred = self._cells[settlement_id]
            backing = self._backing_cell(preferred, 1)
            self.person_cells[person_id] = backing
            self.refinement.materialize_existing(self.population_field, person_id, backing, time=0)

        self._refinement_initialized = True
        self.world.record_event(
            Event(
                kind="population_refinement_initialized",
                time=0,
                impact=0.08,
                payload={
                    "materialized_people": len(self.refinement.active_records()),
                    "reserved_population": round(self.population_field.total_reserved_population, 3),
                    "unresolved_population": round(self.population_field.total_unmaterialized_population, 3),
                    "total_population": round(self.population_field.total_population, 3),
                },
            )
        )
        self._sync_legacy_population_summaries(time=0, emit_events=False)

    def _run_demography(self, year: int, food_ratio: dict[str, float]) -> None:
        assert self.population_field is not None
        before = self.population_field.total_population
        step_unmaterialized_population(
            self.population_field,
            self.population_streams.numpy("demography", year),
        )
        after = self.population_field.total_population
        self.world.record_event(
            Event(
                kind="background_population_change",
                time=year,
                impact=min(0.2, abs(after - before) / max(1.0, before) + 0.02),
                payload={
                    "before": round(before, 3),
                    "after": round(after, 3),
                    "authoritative": True,
                    "unresolved_only": True,
                    "reserved_population": round(self.population_field.total_reserved_population, 3),
                },
            )
        )
        self._sync_legacy_population_summaries(time=year)

    def _birth(self, year: int, mother_id: str, father_id: str, settlement_id: str) -> str:
        child_id = super()._birth(year, mother_id, father_id, settlement_id)
        if not self._refinement_initialized:
            return child_id
        assert self.population_field is not None
        household = self.households.household_of(child_id)
        if household is not None:
            cell = self.household_home_cells[household.id]
        else:
            cell = self.person_cells.get(mother_id, self._cells[settlement_id])
        self.person_cells[child_id] = cell
        self.refinement.materialized_birth(
            self.population_field,
            child_id,
            cell,
            time=year,
        )
        return child_id

    def _run_mortality(self, year: int) -> None:
        previously_alive = {
            record.person_id
            for record in self.refinement.active_records()
            if record.person_id in self.world.entities and self._alive(record.person_id)
        }
        super()._run_mortality(year)
        assert self.population_field is not None
        for person_id in sorted(previously_alive):
            if not self._alive(person_id):
                self.refinement.materialized_death(self.population_field, person_id, time=year)

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
        living = sorted(person_id for person_id in household.members if self._alive(person_id))
        if not living:
            return
        move_probability = min(0.62, 0.08 + 2.6 * (best_score - current_score))
        if self.residence_streams.python(household_id, year, "move").random() >= move_probability:
            return

        assert self.population_field is not None
        for person_id in living:
            record = self.refinement.records.get(person_id)
            if record is not None and record.active:
                self.refinement.move_materialized(self.population_field, person_id, best)
            self.person_cells[person_id] = best
        self.household_home_cells[household_id] = best
        self.residence_shifts += 1
        self.world.record_event(
            Event(
                kind="household_residence_shifted",
                time=year,
                participants=tuple(living),
                locations=(household.settlement_id,),
                impact=0.12,
                payload={
                    "household_id": household_id,
                    "from_cell": [current.x, current.y],
                    "to_cell": [best.x, best.y],
                    "relative_attraction": round(best_score - current_score, 4),
                    "population_accounted": True,
                },
            )
        )

    def run(self) -> RefinedPopulationSimulationResult:
        base = super().run()
        assert self.population_field is not None
        living_materialized = sum(
            1
            for record in self.refinement.active_records()
            if record.person_id in self.world.entities and self._alive(record.person_id)
        )
        return RefinedPopulationSimulationResult(
            base=base,
            refinement=self.refinement,
            total_population=self.population_field.total_population,
            materialized_population=self.population_field.total_reserved_population,
            unresolved_population=self.population_field.total_unmaterialized_population,
            living_materialized_people=living_materialized,
        )
