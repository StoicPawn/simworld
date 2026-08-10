from __future__ import annotations

from dataclasses import dataclass

from simworld.core.event import Event
from simworld.population.cohorts import DemographicCohortField, build_demographic_cohorts
from simworld.simulation.first_world import FirstWorldConfig
from simworld.simulation.refined_population_world import (
    RefinedPopulationSimulationResult,
    RefinedPopulationWorldSimulation,
)


@dataclass(frozen=True, slots=True)
class CohortPopulationSimulationResult:
    base: RefinedPopulationSimulationResult
    cohorts: DemographicCohortField
    unresolved_children: float
    unresolved_working_age: float
    unresolved_older: float


class CohortPopulationWorldSimulation(RefinedPopulationWorldSimulation):
    """Age/reproductive structure for unresolved population.

    Detailed people remain governed by explicit life histories. Cohorts describe only the
    unresolved share and become its demographic engine, so the same person is never aged,
    born or killed at both resolutions.
    """

    def __init__(self, config: FirstWorldConfig) -> None:
        super().__init__(config)
        self.cohorts: DemographicCohortField | None = None
        self.cohort_streams = self.seed_streams.scoped("demographic-cohorts")

    def initialize(self) -> None:
        super().initialize()
        if self.cohorts is not None:
            return
        assert self.population_field is not None
        self.cohorts = build_demographic_cohorts(
            self.population_field,
            self.cohort_streams.numpy("initialize"),
        )
        self.world.record_event(
            Event(
                kind="demographic_cohorts_initialized",
                time=0,
                impact=0.05,
                payload={
                    "unresolved_population": round(self.cohorts.total_population, 3),
                    "age_bands": 6,
                    "reproductive_classes": 2,
                },
            )
        )

    def _run_demography(self, year: int, food_ratio: dict[str, float]) -> None:
        assert self.population_field is not None
        assert self.cohorts is not None
        before_total = self.population_field.total_population
        stats = self.cohorts.step(
            self.population_field,
            self.cohort_streams.numpy("annual-step", year),
        )
        after_total = self.population_field.total_population
        self.world.record_event(
            Event(
                kind="background_population_change",
                time=year,
                impact=min(0.2, abs(after_total - before_total) / max(1.0, before_total) + 0.02),
                payload={
                    "before": round(before_total, 3),
                    "after": round(after_total, 3),
                    "authoritative": True,
                    "cohort_driven": True,
                    "aggregate_births": round(stats["births"], 3),
                    "aggregate_deaths": round(stats["deaths"], 3),
                    "reserved_population": round(self.population_field.total_reserved_population, 3),
                },
            )
        )
        self._sync_legacy_population_summaries(time=year)

    def run(self) -> CohortPopulationSimulationResult:
        base = super().run()
        assert self.population_field is not None
        assert self.cohorts is not None
        self.cohorts.assert_consistent_with(self.population_field, atol=1e-6)
        by_age = self.cohorts.totals_by_age()
        return CohortPopulationSimulationResult(
            base=base,
            cohorts=self.cohorts,
            unresolved_children=float(by_age[0] + by_age[1]),
            unresolved_working_age=float(by_age[2] + by_age[3] + by_age[4]),
            unresolved_older=float(by_age[5]),
        )
