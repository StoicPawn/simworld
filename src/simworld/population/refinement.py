from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from simworld.population.field import PopulationField
from simworld.spatial import CellCoord


@dataclass(slots=True)
class MaterializedPopulationRecord:
    person_id: str
    cell: CellCoord
    amount: float = 1.0
    materialized_at: int = 0
    released_at: int | None = None

    @property
    def active(self) -> bool:
        return self.released_at is None


@dataclass(slots=True)
class PopulationRefinementLedger:
    """Accounting bridge between aggregate population and detailed people."""

    records: dict[str, MaterializedPopulationRecord] = field(default_factory=dict)

    def materialize_existing(
        self,
        population: PopulationField,
        person_id: str,
        cell: CellCoord,
        *,
        time: int,
        amount: float = 1.0,
    ) -> MaterializedPopulationRecord:
        existing = self.records.get(person_id)
        if existing is not None and existing.active:
            raise ValueError(f"person already materialized: {person_id}")
        population.reserve(cell, amount)
        record = MaterializedPopulationRecord(person_id, cell, amount, time)
        self.records[person_id] = record
        return record

    def materialized_birth(
        self,
        population: PopulationField,
        person_id: str,
        cell: CellCoord,
        *,
        time: int,
        amount: float = 1.0,
    ) -> MaterializedPopulationRecord:
        if amount <= 0:
            raise ValueError("birth amount must be positive")
        if population.water[cell.y, cell.x]:
            raise ValueError("cannot add land population on water")
        assert population.reserved is not None
        population.population[cell.y, cell.x] += amount
        population.reserved[cell.y, cell.x] += amount
        record = MaterializedPopulationRecord(person_id, cell, amount, time)
        self.records[person_id] = record
        return record

    def materialized_death(self, population: PopulationField, person_id: str, *, time: int) -> None:
        record = self._active(person_id)
        assert population.reserved is not None
        if population.reserved_at(record.cell) + 1e-9 < record.amount:
            raise ValueError("reserved population no longer backs materialized person")
        population.reserved[record.cell.y, record.cell.x] -= record.amount
        population.population[record.cell.y, record.cell.x] -= record.amount
        record.released_at = time

    def move_materialized(
        self,
        population: PopulationField,
        person_id: str,
        destination: CellCoord,
    ) -> None:
        record = self._active(person_id)
        source = record.cell
        if source == destination:
            return
        if population.water[destination.y, destination.x]:
            raise ValueError("cannot move land population onto water")
        assert population.reserved is not None
        if population.reserved_at(source) + 1e-9 < record.amount:
            raise ValueError("source cell no longer backs materialized person")
        population.reserved[source.y, source.x] -= record.amount
        population.population[source.y, source.x] -= record.amount
        population.population[destination.y, destination.x] += record.amount
        population.reserved[destination.y, destination.x] += record.amount
        record.cell = destination

    def dematerialize(self, population: PopulationField, person_id: str, *, time: int) -> None:
        record = self._active(person_id)
        population.release(record.cell, record.amount)
        record.released_at = time

    def active_records(self) -> tuple[MaterializedPopulationRecord, ...]:
        return tuple(record for record in self.records.values() if record.active)

    def active_population(self) -> float:
        return sum(record.amount for record in self.active_records())

    def _active(self, person_id: str) -> MaterializedPopulationRecord:
        record = self.records.get(person_id)
        if record is None or not record.active:
            raise KeyError(f"person is not actively materialized: {person_id}")
        return record


def step_unmaterialized_population(
    population: PopulationField,
    rng: np.random.Generator,
    *,
    growth_rate: float = 0.018,
    mobility: float = 0.035,
) -> None:
    """Advance only people not already represented by detailed life histories."""

    assert population.reserved is not None
    reserved = population.reserved
    total = population.population
    unresolved = np.maximum(0.0, total - reserved)
    cap = np.maximum(population.capacity, 1e-9)
    crowding = total / cap

    local_growth = growth_rate * unresolved * (1.0 - crowding)
    noise = rng.normal(0.0, 0.0045, size=total.shape) * np.sqrt(np.maximum(unresolved, 1.0))
    updated_unresolved = np.maximum(0.0, unresolved + local_growth + noise)
    updated_unresolved[population.water] = 0.0
    updated_total = reserved + updated_unresolved

    outflow = mobility * updated_unresolved * np.clip((updated_total / cap) - 0.72, 0.0, 0.55)
    retained = updated_unresolved - outflow
    inflow = np.zeros_like(total)
    height, width = total.shape
    for y in range(height):
        for x in range(width):
            amount = float(outflow[y, x])
            if amount <= 1e-9 or population.water[y, x]:
                continue
            neighbours: list[tuple[int, int]] = []
            weights: list[float] = []
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                ny, nx = y + dy, x + dx
                if not (0 <= nx < width and 0 <= ny < height) or population.water[ny, nx]:
                    continue
                space = max(0.0, 1.0 - updated_total[ny, nx] / max(population.capacity[ny, nx], 1e-9))
                weight = 0.12 + 0.62 * population.suitability[ny, nx] + 0.35 * space
                neighbours.append((ny, nx))
                weights.append(max(0.001, float(weight)))
            if not neighbours:
                retained[y, x] += amount
                continue
            total_weight = sum(weights)
            for (ny, nx), weight in zip(neighbours, weights, strict=True):
                inflow[ny, nx] += amount * weight / total_weight

    population.population = reserved + np.maximum(0.0, retained + inflow)
    population.population[population.water] = 0.0
