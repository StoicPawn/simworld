from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from simworld.core.event import Event
from simworld.population import PopulationSummaryView, nearest_anchor_partition, population_summaries
from simworld.simulation.distributed_population_world import (
    DistributedPopulationSimulationResult,
    DistributedPopulationWorldSimulation,
)
from simworld.simulation.first_world import FirstWorldConfig


@dataclass(frozen=True, slots=True)
class AuthoritativePopulationSimulationResult:
    base: DistributedPopulationSimulationResult
    summaries: dict[str, PopulationSummaryView]
    legacy_summary_total: float
    field_total: float


class AuthoritativePopulationWorldSimulation(DistributedPopulationWorldSimulation):
    """Use the distributed raster as the sole aggregate demographic truth."""

    def __init__(self, config: FirstWorldConfig) -> None:
        super().__init__(config)
        self._population_partition: NDArray[np.int32] | None = None
        self._population_summaries: dict[str, PopulationSummaryView] = {}
        self.harvest_streams = self.seed_streams.scoped("harvest")

    def initialize(self) -> None:
        super().initialize()
        assert self.population_field is not None
        if self._population_partition is None:
            self._population_partition = nearest_anchor_partition(
                width=self.config.width,
                height=self.config.height,
                water=self.generated.water,
                anchors=self._cells,
            )
        self._sync_legacy_population_summaries(time=0, emit_events=False)

    def _summaries(self) -> dict[str, PopulationSummaryView]:
        assert self.population_field is not None
        assert self._population_partition is not None
        return population_summaries(self.population_field, self._population_partition, self._cells)

    def _sync_legacy_population_summaries(self, *, time: int, emit_events: bool = True) -> None:
        summaries = self._summaries()
        self._population_summaries = summaries
        for settlement_id in self.settlement_ids:
            summary = summaries[settlement_id]
            entity = self.world.entities[settlement_id]
            before = int(entity.attributes.get("population", 0))
            after = max(0, int(round(summary.population)))
            entity.attributes["population"] = after
            entity.attributes["peak_population"] = max(int(entity.attributes.get("peak_population", 0)), after)
            entity.attributes["population_source"] = "derived_from_population_field"
            if emit_events:
                self.world.record_event(
                    Event(
                        kind="population_summary_updated",
                        time=time,
                        participants=(settlement_id,),
                        locations=(settlement_id,),
                        impact=abs(after - before) / max(1, before) + 0.02,
                        payload={
                            "before": before,
                            "after": after,
                            "field_population": round(summary.population, 3),
                            "reporting_cells": summary.cell_count,
                            "source": "population_field",
                            "causal_authority": False,
                        },
                    )
                )

    def _run_harvests(self, year: int) -> dict[str, float]:
        """Expose local food pressure to legacy social code without shared RNG coupling."""
        summaries = self._summaries()
        food_ratio: dict[str, float] = {}
        for settlement_id in self.settlement_ids:
            summary = summaries[settlement_id]
            rng = self.harvest_streams.numpy(settlement_id, year)
            climate_noise = float(rng.normal(0.0, 0.11))
            rare_shock = float(rng.normal(-0.30, 0.06)) if rng.random() < 0.045 else 0.0
            production_factor = max(0.35, 1.0 + climate_noise + rare_shock)
            effective_capacity = summary.capacity * production_factor
            ratio = effective_capacity / max(1.0, summary.population)
            ratio = float(np.clip(ratio, 0.25, 2.5))
            food_ratio[settlement_id] = ratio
            event = Event(
                kind="harvest",
                time=year,
                participants=(settlement_id,),
                locations=(settlement_id,),
                impact=abs(1.0 - ratio) + 0.15,
                payload={
                    "population_source": "population_field_summary",
                    "population": round(summary.population, 3),
                    "food_capacity": round(effective_capacity, 3),
                    "food_ratio": round(ratio, 5),
                    "mean_suitability": round(summary.mean_suitability, 5),
                    "shock": round(climate_noise + rare_shock, 5),
                },
            )
            self.world.record_event(event)
            self._last_harvest[settlement_id] = event.id
        return food_ratio

    def _run_demography(self, year: int, food_ratio: dict[str, float]) -> None:
        """Advance only the raster with a year-keyed demographic stream."""
        assert self.population_field is not None
        before = self.population_field.total_population
        self.population_field.step(self.population_streams.numpy("demography", year))
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
                },
            )
        )
        self._sync_legacy_population_summaries(time=year)

    def _advance_background_population(self, year: int) -> None:
        return

    def _run_migration(self, year: int, food_ratio: dict[str, float]) -> None:
        return

    def run(self) -> AuthoritativePopulationSimulationResult:
        base = super().run()
        summaries = self._summaries()
        legacy_total = float(sum(int(self.world.entities[sid].attributes["population"]) for sid in self.settlement_ids))
        assert self.population_field is not None
        return AuthoritativePopulationSimulationResult(
            base=base,
            summaries=summaries,
            legacy_summary_total=legacy_total,
            field_total=self.population_field.total_population,
        )
