from __future__ import annotations

from dataclasses import dataclass

from simworld.core.event import Event
from simworld.population import PopulationField, build_population_field
from simworld.simulation.emergent_settlement_world import (
    EmergentSettlementSimulationResult,
    EmergentSettlementWorldSimulation,
)
from simworld.simulation.first_world import FirstWorldConfig
from simworld.spatial import CellCoord


@dataclass(frozen=True, slots=True)
class DistributedPopulationSimulationResult:
    base: EmergentSettlementSimulationResult
    population_field: PopulationField
    initial_background_population: float
    final_background_population: float
    bootstrap_home_overlap: int


class DistributedPopulationWorldSimulation(EmergentSettlementWorldSimulation):
    """Background population distributed over terrain, with people as refinements."""

    def __init__(self, config: FirstWorldConfig) -> None:
        super().__init__(config)
        self.population_streams = self.seed_streams.scoped("population")
        self.population_field: PopulationField | None = None
        self.initial_background_population = 0.0
        self.bootstrap_home_overlap = 0

    def initialize(self) -> None:
        super().initialize()
        if self.population_field is not None:
            return

        total = float(
            sum(int(self.world.entities[settlement_id].attributes["population"]) for settlement_id in self.settlement_ids)
        )
        self.population_field = build_population_field(
            self.generated,
            total_population=max(1.0, total),
            rng=self.population_streams.numpy("initialize", "field"),
        )
        self.initial_background_population = self.population_field.total_population

        households = sorted(self.households.active_households(), key=lambda household: household.id)
        sampled = self.population_field.sample_cells(
            len(households),
            self.population_streams.numpy("initialize", "household_homes"),
        )
        bootstrap_cells = {(cell.x, cell.y) for cell in self._cells.values()}
        overlap = 0
        for household, cell in zip(households, sampled, strict=True):
            self.household_home_cells[household.id] = cell
            if (cell.x, cell.y) in bootstrap_cells:
                overlap += 1
            for person_id in sorted(household.members):
                self.person_cells[person_id] = cell
        self.bootstrap_home_overlap = overlap

        self.world.record_event(
            Event(
                kind="background_population_distributed",
                time=0,
                impact=0.15,
                payload={
                    "total_population": round(self.initial_background_population, 3),
                    "occupied_cells": len(self.population_field.high_density_cells(minimum_population=0.1)),
                    "materialized_households": len(households),
                    "bootstrap_home_overlap": overlap,
                },
            )
        )

    def _home_score(self, household_id: str, cell: CellCoord) -> float:
        score = super()._home_score(household_id, cell)
        if self.population_field is None:
            return score
        background = self.population_field.population_at(cell)
        capacity = self.population_field.capacity_at(cell)
        suitability = float(self.population_field.suitability[cell.y, cell.x])
        density = background / max(capacity, 1e-9)
        agglomeration = min(1.0, background / max(1.0, self.initial_background_population * 0.003))
        crowding_penalty = max(0.0, density - 0.82)
        return score + 0.055 * suitability + 0.035 * agglomeration - 0.05 * crowding_penalty

    def _advance_background_population(self, year: int) -> None:
        if self.population_field is None:
            return
        before = self.population_field.total_population
        self.population_field.step(self.population_streams.numpy("demography", year))
        after = self.population_field.total_population
        self.world.record_event(
            Event(
                kind="background_population_change",
                time=year,
                impact=min(0.2, abs(after - before) / max(1.0, before) + 0.02),
                payload={"before": round(before, 3), "after": round(after, 3)},
            )
        )

    def _run_microgeography(self, year: int) -> None:
        self._advance_background_population(year)
        super()._run_microgeography(year)

    def run(self) -> DistributedPopulationSimulationResult:
        base = super().run()
        assert self.population_field is not None
        return DistributedPopulationSimulationResult(
            base=base,
            population_field=self.population_field,
            initial_background_population=self.initial_background_population,
            final_background_population=self.population_field.total_population,
            bootstrap_home_overlap=self.bootstrap_home_overlap,
        )
