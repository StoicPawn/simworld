from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from simworld.geography.generator import GeneratedWorld
from simworld.spatial import CellCoord


@dataclass(slots=True)
class PopulationField:
    """Authoritative aggregate population with explicit high-resolution reservations.

    `population` is total underlying population. `reserved` is the portion currently
    represented by detailed agents. Unmaterialized population is therefore
    `population - reserved`, not a second population universe.
    """

    population: NDArray[np.float64]
    capacity: NDArray[np.float64]
    suitability: NDArray[np.float64]
    water: NDArray[np.bool_]
    reserved: NDArray[np.float64] | None = None

    def __post_init__(self) -> None:
        if self.reserved is None:
            self.reserved = np.zeros_like(self.population, dtype=np.float64)
        else:
            self.reserved = self.reserved.astype(np.float64, copy=True)
        if self.reserved.shape != self.population.shape:
            raise ValueError("reserved population shape must match population field")
        if np.any(self.reserved < -1e-9):
            raise ValueError("reserved population cannot be negative")
        if np.any(self.reserved - self.population > 1e-9):
            raise ValueError("reserved population cannot exceed total population")
        self.reserved[self.water] = 0.0

    @property
    def total_population(self) -> float:
        return float(self.population.sum())

    @property
    def total_reserved_population(self) -> float:
        assert self.reserved is not None
        return float(self.reserved.sum())

    @property
    def total_unmaterialized_population(self) -> float:
        return self.total_population - self.total_reserved_population

    def population_at(self, cell: CellCoord) -> float:
        return float(self.population[cell.y, cell.x])

    def reserved_at(self, cell: CellCoord) -> float:
        assert self.reserved is not None
        return float(self.reserved[cell.y, cell.x])

    def available_at(self, cell: CellCoord) -> float:
        return max(0.0, self.population_at(cell) - self.reserved_at(cell))

    def capacity_at(self, cell: CellCoord) -> float:
        return float(self.capacity[cell.y, cell.x])

    def density_ratio_at(self, cell: CellCoord) -> float:
        capacity = self.capacity_at(cell)
        if capacity <= 1e-9:
            return 0.0
        return min(2.0, self.population_at(cell) / capacity)

    def reserve(self, cell: CellCoord, amount: float) -> None:
        if amount <= 0:
            raise ValueError("reservation amount must be positive")
        if self.water[cell.y, cell.x]:
            raise ValueError("cannot reserve land population on water")
        available = self.available_at(cell)
        if amount > available + 1e-9:
            raise ValueError(
                f"insufficient unmaterialized population at {cell}: requested {amount}, available {available}"
            )
        assert self.reserved is not None
        self.reserved[cell.y, cell.x] += amount

    def release(self, cell: CellCoord, amount: float) -> None:
        if amount <= 0:
            raise ValueError("release amount must be positive")
        current = self.reserved_at(cell)
        if amount > current + 1e-9:
            raise ValueError(
                f"cannot release more population than reserved at {cell}: requested {amount}, reserved {current}"
            )
        assert self.reserved is not None
        self.reserved[cell.y, cell.x] = max(0.0, current - amount)

    def move_reservation(self, source: CellCoord, destination: CellCoord, amount: float) -> None:
        if source == destination:
            return
        if amount <= 0:
            raise ValueError("reservation transfer amount must be positive")
        if self.reserved_at(source) + 1e-9 < amount:
            raise ValueError("source cell does not contain enough reserved population")
        if self.available_at(destination) + 1e-9 < amount:
            raise ValueError("destination cell does not contain enough unmaterialized population")
        self.release(source, amount)
        try:
            self.reserve(destination, amount)
        except Exception:
            self.reserve(source, amount)
            raise

    def step(self, rng: np.random.Generator, *, growth_rate: float = 0.018, mobility: float = 0.035) -> None:
        """Advance total demography while keeping detailed reservations locally backed."""
        pop = self.population
        assert self.reserved is not None
        cap = np.maximum(self.capacity, 1e-9)
        crowding = pop / cap
        local_growth = growth_rate * pop * (1.0 - crowding)
        noise = rng.normal(0.0, 0.0045, size=pop.shape) * np.sqrt(np.maximum(pop, 1.0))
        updated = np.maximum(self.reserved, pop + local_growth + noise)
        updated[self.water] = 0.0

        # Only the unresolved share may be redistributed by the aggregate process.
        # Materialized people move through explicit detailed movement/migration processes.
        unresolved = np.maximum(0.0, updated - self.reserved)
        outflow = mobility * unresolved * np.clip((updated / cap) - 0.72, 0.0, 0.55)
        retained = updated - outflow
        inflow = np.zeros_like(updated)
        height, width = updated.shape
        for y in range(height):
            for x in range(width):
                amount = float(outflow[y, x])
                if amount <= 1e-9 or self.water[y, x]:
                    continue
                neighbours: list[tuple[int, int]] = []
                weights: list[float] = []
                for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    ny, nx = y + dy, x + dx
                    if not (0 <= nx < width and 0 <= ny < height) or self.water[ny, nx]:
                        continue
                    space = max(0.0, 1.0 - updated[ny, nx] / max(self.capacity[ny, nx], 1e-9))
                    weight = 0.12 + 0.62 * self.suitability[ny, nx] + 0.35 * space
                    neighbours.append((ny, nx))
                    weights.append(max(0.001, float(weight)))
                if not neighbours:
                    retained[y, x] += amount
                    continue
                total_weight = sum(weights)
                for (ny, nx), weight in zip(neighbours, weights, strict=True):
                    inflow[ny, nx] += amount * weight / total_weight

        self.population = np.maximum(self.reserved, retained + inflow)
        self.population[self.water] = 0.0

    def sample_cells(self, count: int, rng: np.random.Generator, *, use_available: bool = False) -> tuple[CellCoord, ...]:
        if count <= 0:
            return ()
        if use_available:
            assert self.reserved is not None
            weights = np.maximum(0.0, self.population - self.reserved)
        else:
            weights = self.population.copy()
        weights[self.water] = 0.0
        flat = weights.ravel()
        if float(flat.sum()) <= 0:
            flat = self.suitability.ravel().copy()
        probabilities = flat / flat.sum()
        indexes = rng.choice(len(flat), size=count, replace=True, p=probabilities)
        width = self.population.shape[1]
        return tuple(CellCoord(int(index % width), int(index // width)) for index in indexes)

    def high_density_cells(self, *, minimum_population: float = 1.0) -> tuple[CellCoord, ...]:
        coords: list[CellCoord] = []
        height, width = self.population.shape
        for y in range(height):
            for x in range(width):
                if self.population[y, x] >= minimum_population:
                    coords.append(CellCoord(x, y))
        coords.sort(key=lambda cell: (-self.population[cell.y, cell.x], cell.y, cell.x))
        return tuple(coords)


def build_population_field(
    generated: GeneratedWorld,
    *,
    total_population: float,
    rng: np.random.Generator,
) -> PopulationField:
    """Distribute aggregate population over terrain without creating settlements."""
    if total_population <= 0:
        raise ValueError("total_population must be positive")

    suitability = (
        0.46 * generated.habitability.astype(np.float64)
        + 0.20 * generated.fertility.astype(np.float64)
        + 0.16 * generated.freshwater_access.astype(np.float64)
        + 0.10 * generated.coastal_food.astype(np.float64)
        + 0.08 * generated.timber.astype(np.float64)
    )
    suitability = np.clip(suitability, 0.0, 1.0)
    suitability[generated.water] = 0.0

    micro_variation = np.clip(rng.lognormal(mean=0.0, sigma=0.22, size=suitability.shape), 0.55, 1.8)
    weights = np.power(suitability, 1.65) * micro_variation
    weights[generated.water] = 0.0
    if float(weights.sum()) <= 0:
        raise RuntimeError("generated world has no habitable population cells")
    population = total_population * weights / weights.sum()

    mean_land = float(np.mean(suitability[~generated.water])) if np.any(~generated.water) else 0.1
    scale = total_population / max(1.0, float((~generated.water).sum()))
    capacity = scale * (0.28 + 3.4 * suitability / max(mean_land, 0.05))
    capacity *= np.clip(rng.lognormal(mean=0.0, sigma=0.12, size=capacity.shape), 0.7, 1.45)
    capacity[generated.water] = 0.0
    capacity = np.maximum(capacity, population * 0.72)

    return PopulationField(
        population=population.astype(np.float64),
        capacity=capacity.astype(np.float64),
        suitability=suitability.astype(np.float64),
        water=generated.water.copy(),
    )
