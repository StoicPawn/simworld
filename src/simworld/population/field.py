from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from simworld.geography.generator import GeneratedWorld
from simworld.spatial import CellCoord


@dataclass(slots=True)
class PopulationField:
    """Aggregate population distributed over physical cells.

    This is background demographic state, not a set of settlements. Cells can gain or
    lose population continuously; materialized people are a refinement layer over it.
    """

    population: NDArray[np.float64]
    capacity: NDArray[np.float64]
    suitability: NDArray[np.float64]
    water: NDArray[np.bool_]

    @property
    def total_population(self) -> float:
        return float(self.population.sum())

    def population_at(self, cell: CellCoord) -> float:
        return float(self.population[cell.y, cell.x])

    def capacity_at(self, cell: CellCoord) -> float:
        return float(self.capacity[cell.y, cell.x])

    def density_ratio_at(self, cell: CellCoord) -> float:
        capacity = self.capacity_at(cell)
        if capacity <= 1e-9:
            return 0.0
        return min(2.0, self.population_at(cell) / capacity)

    def step(self, rng: np.random.Generator, *, growth_rate: float = 0.018, mobility: float = 0.035) -> None:
        """Advance aggregate demography by local growth and neighbour redistribution."""
        pop = self.population
        cap = np.maximum(self.capacity, 1e-9)
        crowding = pop / cap
        local_growth = growth_rate * pop * (1.0 - crowding)
        noise = rng.normal(0.0, 0.0045, size=pop.shape) * np.sqrt(np.maximum(pop, 1.0))
        updated = np.maximum(0.0, pop + local_growth + noise)
        updated[self.water] = 0.0

        # Small local redistribution. Only a fraction of each cell can move in one step.
        outflow = mobility * updated * np.clip((updated / cap) - 0.72, 0.0, 0.55)
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

        self.population = np.maximum(0.0, retained + inflow)
        self.population[self.water] = 0.0

    def sample_cells(self, count: int, rng: np.random.Generator) -> tuple[CellCoord, ...]:
        if count <= 0:
            return ()
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

    # Fine noise prevents equal physical cells from being socially identical while
    # geography remains the dominant driver.
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
