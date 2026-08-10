from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from simworld.population.field import PopulationField


AGE_BANDS: tuple[tuple[str, int | None], ...] = (
    ("age_0_4", 5),
    ("age_5_14", 10),
    ("age_15_24", 10),
    ("age_25_44", 20),
    ("age_45_64", 20),
    ("age_65_plus", None),
)
REPRODUCTIVE_CLASSES: tuple[str, str] = ("gestational", "non_gestational")

_BASE_AGE_SHARES = np.array([0.12, 0.18, 0.17, 0.29, 0.17, 0.07], dtype=np.float64)
_BASE_MORTALITY = np.array([0.010, 0.0015, 0.0020, 0.0035, 0.012, 0.055], dtype=np.float64)
_FERTILITY_BY_BAND = np.array([0.0, 0.0, 0.055, 0.050, 0.002, 0.0], dtype=np.float64)


@dataclass(slots=True)
class DemographicCohortField:
    """Age/reproductive composition of unresolved population only.

    Shape is `(age_band, reproductive_class, y, x)`. The reproductive class is a
    minimal biological simulation role and must not be interpreted as gender identity,
    social role or family status.
    """

    counts: NDArray[np.float64]
    water: NDArray[np.bool_]

    @property
    def total_population(self) -> float:
        return float(self.counts.sum())

    def totals_by_cell(self) -> NDArray[np.float64]:
        return self.counts.sum(axis=(0, 1))

    def totals_by_age(self) -> NDArray[np.float64]:
        return self.counts.sum(axis=(1, 2, 3))

    def totals_by_reproductive_class(self) -> NDArray[np.float64]:
        return self.counts.sum(axis=(0, 2, 3))

    def assert_consistent_with(self, population: PopulationField, *, atol: float = 1e-7) -> None:
        assert population.reserved is not None
        expected = np.maximum(0.0, population.population - population.reserved)
        if not np.allclose(self.totals_by_cell(), expected, atol=atol, rtol=0.0):
            raise AssertionError("cohort totals do not equal unresolved population")
        if np.any(self.counts < -atol):
            raise AssertionError("cohort population cannot be negative")

    def _sync_total_population(self, population: PopulationField) -> None:
        assert population.reserved is not None
        population.population = population.reserved + self.totals_by_cell()
        population.population[population.water] = 0.0

    def step(
        self,
        population: PopulationField,
        rng: np.random.Generator,
        *,
        mobility: float = 0.028,
    ) -> dict[str, float]:
        """Advance aging, deaths, births and local unresolved redistribution one year."""

        self.assert_consistent_with(population)
        counts = np.maximum(0.0, self.counts.copy())
        before = float(counts.sum())

        total_by_cell = counts.sum(axis=(0, 1))
        capacity = np.maximum(population.capacity, 1e-9)
        crowding = (total_by_cell + population.reserved) / capacity
        suitability = population.suitability
        mortality_pressure = np.clip(1.05 - 0.30 * suitability + 0.30 * np.maximum(crowding - 0.9, 0.0), 0.72, 1.7)

        deaths = np.zeros_like(counts)
        for band in range(len(AGE_BANDS)):
            rate = _BASE_MORTALITY[band] * mortality_pressure
            deaths[band] = counts[band] * rate[None, :, :]
        counts = np.maximum(0.0, counts - deaths)

        # Age a fraction of every finite-width cohort into the next band each year.
        for band, (_, width) in enumerate(AGE_BANDS[:-1]):
            assert width is not None
            aging_out = counts[band] / float(width)
            counts[band] -= aging_out
            counts[band + 1] += aging_out

        # Aggregate births arise only from unresolved gestational-class fertile cohorts.
        gestational_index = REPRODUCTIVE_CLASSES.index("gestational")
        births_by_cell = np.zeros_like(total_by_cell)
        resource_factor = np.clip(0.65 + 0.50 * suitability - 0.35 * np.maximum(crowding - 0.85, 0.0), 0.25, 1.25)
        for band, rate in enumerate(_FERTILITY_BY_BAND):
            if rate <= 0:
                continue
            births_by_cell += counts[band, gestational_index] * rate * resource_factor

        # Small local stochasticity scales with sqrt(population), never a global cursor.
        noise = rng.normal(0.0, 0.025, size=births_by_cell.shape) * np.sqrt(np.maximum(births_by_cell, 0.2))
        births_by_cell = np.maximum(0.0, births_by_cell + noise)
        births_by_cell[population.water] = 0.0
        counts[0, 0] += 0.5 * births_by_cell
        counts[0, 1] += 0.5 * births_by_cell

        # Move only unresolved population, preserving the cohort composition of movers.
        total_after_demography = counts.sum(axis=(0, 1))
        combined = total_after_demography + population.reserved
        outflow_fraction = mobility * np.clip((combined / capacity) - 0.78, 0.0, 0.50)
        retained = counts * (1.0 - outflow_fraction[None, None, :, :])
        inflow = np.zeros_like(counts)
        height, width = total_after_demography.shape
        for y in range(height):
            for x in range(width):
                fraction = float(outflow_fraction[y, x])
                if fraction <= 1e-12 or population.water[y, x]:
                    continue
                moving = counts[:, :, y, x] * fraction
                neighbours: list[tuple[int, int]] = []
                weights: list[float] = []
                for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    ny, nx = y + dy, x + dx
                    if not (0 <= nx < width and 0 <= ny < height) or population.water[ny, nx]:
                        continue
                    neighbour_total = total_after_demography[ny, nx] + population.reserved[ny, nx]
                    space = max(0.0, 1.0 - neighbour_total / max(population.capacity[ny, nx], 1e-9))
                    weight = 0.12 + 0.62 * population.suitability[ny, nx] + 0.35 * space
                    neighbours.append((ny, nx))
                    weights.append(max(0.001, float(weight)))
                if not neighbours:
                    retained[:, :, y, x] += moving
                    continue
                total_weight = sum(weights)
                for (ny, nx), weight in zip(neighbours, weights, strict=True):
                    inflow[:, :, ny, nx] += moving * (weight / total_weight)

        self.counts = np.maximum(0.0, retained + inflow)
        self.counts[:, :, population.water] = 0.0
        self._sync_total_population(population)
        after = float(self.counts.sum())
        return {
            "unresolved_before": before,
            "unresolved_after": after,
            "births": float(births_by_cell.sum()),
            "deaths": float(deaths.sum()),
        }


def build_demographic_cohorts(
    population: PopulationField,
    rng: np.random.Generator,
) -> DemographicCohortField:
    """Split unresolved population into local age/reproductive cohorts exactly."""

    assert population.reserved is not None
    unresolved = np.maximum(0.0, population.population - population.reserved)
    height, width = unresolved.shape
    weights = np.zeros((len(AGE_BANDS), len(REPRODUCTIVE_CLASSES), height, width), dtype=np.float64)

    age_variation = np.clip(
        rng.lognormal(mean=0.0, sigma=0.10, size=(len(AGE_BANDS), height, width)),
        0.70,
        1.35,
    )
    reproductive_variation = np.clip(rng.normal(0.5, 0.025, size=(height, width)), 0.43, 0.57)

    for band, share in enumerate(_BASE_AGE_SHARES):
        local_age_weight = share * age_variation[band]
        weights[band, 0] = local_age_weight * reproductive_variation
        weights[band, 1] = local_age_weight * (1.0 - reproductive_variation)

    weights[:, :, population.water] = 0.0
    normalizer = weights.sum(axis=(0, 1))
    safe = np.where(normalizer > 0.0, normalizer, 1.0)
    counts = weights / safe[None, None, :, :] * unresolved[None, None, :, :]
    counts[:, :, population.water] = 0.0

    result = DemographicCohortField(counts=counts, water=population.water.copy())
    result.assert_consistent_with(population)
    return result
