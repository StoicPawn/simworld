from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True, slots=True)
class CropProfile:
    name: str
    optimal_temperature_c: float
    temperature_tolerance_c: float
    optimal_rainfall_mm: float
    rainfall_tolerance_mm: float
    soil_weight: float = 0.55
    water_weight: float = 0.25
    climate_weight: float = 0.20


GRAINS = CropProfile("grains", 17.0, 13.0, 850.0, 650.0)
PULSES = CropProfile("pulses", 20.0, 14.0, 700.0, 600.0)
TUBERS = CropProfile("tubers", 14.0, 11.0, 1050.0, 750.0)


def crop_suitability(
    fertility: NDArray[np.floating],
    temperature_c: NDArray[np.floating],
    rainfall_mm: NDArray[np.floating],
    water_access: NDArray[np.floating],
    ruggedness: NDArray[np.floating],
    crop: CropProfile,
) -> NDArray[np.float32]:
    temp_fit = np.exp(-((temperature_c - crop.optimal_temperature_c) / crop.temperature_tolerance_c) ** 2)
    rain_fit = np.exp(-((rainfall_mm - crop.optimal_rainfall_mm) / crop.rainfall_tolerance_mm) ** 2)
    climate = temp_fit * rain_fit
    terrain = np.clip(1.0 - 0.8 * ruggedness, 0.05, 1.0)
    score = (
        crop.soil_weight * fertility
        + crop.water_weight * water_access
        + crop.climate_weight * climate
    ) * terrain
    return np.clip(score, 0.0, 1.0).astype(np.float32)


def harvest_yield(
    cultivated_area: float,
    suitability: float,
    labour_factor: float,
    tools_factor: float,
    weather_factor: float,
) -> float:
    """Continuous production primitive; no political response is encoded here."""
    return max(
        0.0,
        cultivated_area
        * max(0.0, suitability)
        * max(0.0, labour_factor)
        * max(0.0, tools_factor)
        * max(0.0, weather_factor),
    )
