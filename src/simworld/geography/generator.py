from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from simworld.spatial import GridSpec, SpatialMap


@dataclass(slots=True)
class GeneratedWorld:
    spatial_map: SpatialMap
    elevation_m: NDArray[np.float32]
    water: NDArray[np.bool_]
    rainfall: NDArray[np.float32]
    temperature_c: NDArray[np.float32]
    fertility: NDArray[np.float32]
    timber: NDArray[np.float32]
    ore: NDArray[np.float32]
    habitability: NDArray[np.float32]


def _smooth(field: NDArray[np.float64], passes: int) -> NDArray[np.float64]:
    result = field.copy()
    for _ in range(passes):
        padded = np.pad(result, 1, mode="reflect")
        result = (
            padded[:-2, :-2]
            + 2 * padded[:-2, 1:-1]
            + padded[:-2, 2:]
            + 2 * padded[1:-1, :-2]
            + 4 * padded[1:-1, 1:-1]
            + 2 * padded[1:-1, 2:]
            + padded[2:, :-2]
            + 2 * padded[2:, 1:-1]
            + padded[2:, 2:]
        ) / 16.0
    return result


def _normalize(field: NDArray[np.float64]) -> NDArray[np.float64]:
    low = float(field.min())
    high = float(field.max())
    if high <= low:
        return np.zeros_like(field)
    return (field - low) / (high - low)


def _coastal_mask(water: NDArray[np.bool_]) -> NDArray[np.bool_]:
    land = ~water
    adjacent_water = np.zeros_like(water)
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        shifted = np.roll(water, shift=(dy, dx), axis=(0, 1))
        if dy == -1:
            shifted[-1, :] = False
        elif dy == 1:
            shifted[0, :] = False
        if dx == -1:
            shifted[:, -1] = False
        elif dx == 1:
            shifted[:, 0] = False
        adjacent_water |= shifted
    return land & adjacent_water


def generate_world(spec: GridSpec, *, seed: int = 0, sea_fraction: float = 0.34) -> GeneratedWorld:
    """Generate a deterministic physical world whose geography constrains later history."""
    if not 0.05 <= sea_fraction <= 0.8:
        raise ValueError("sea_fraction must be between 0.05 and 0.8")

    rng = np.random.default_rng(seed)
    shape = (spec.height, spec.width)
    y, x = np.mgrid[0 : spec.height, 0 : spec.width]
    xn = x / max(1, spec.width - 1)
    yn = y / max(1, spec.height - 1)

    broad = _smooth(rng.normal(size=shape), max(5, min(spec.width, spec.height) // 12))
    medium = _smooth(rng.normal(size=shape), max(2, min(spec.width, spec.height) // 35))
    ridges = np.sin(2 * np.pi * (1.7 * xn + 0.35 * np.sin(2 * np.pi * yn)))
    continental = 0.58 * _normalize(broad) + 0.28 * _normalize(medium) + 0.14 * (ridges + 1) / 2
    continental = _normalize(continental)

    sea_level = float(np.quantile(continental, sea_fraction))
    water = continental <= sea_level
    relative = np.clip((continental - sea_level) / max(1e-6, 1.0 - sea_level), 0.0, 1.0)
    elevation = np.where(water, -120.0 * (sea_level - continental), 30.0 + 3200.0 * relative**1.75)

    gy, gx = np.gradient(elevation, spec.cell_size_m, spec.cell_size_m)
    slope = np.sqrt(gx * gx + gy * gy)

    latitude = np.abs(2.0 * yn - 1.0)
    temperature = 29.0 - 35.0 * latitude - np.maximum(elevation, 0.0) * 0.0062

    moisture_seed = _smooth(rng.random(shape), max(3, min(spec.width, spec.height) // 25))
    moisture_seed = _normalize(moisture_seed)
    rainfall = 350.0 + 1700.0 * moisture_seed
    rainfall *= np.exp(-np.maximum(elevation, 0.0) / 5000.0)
    rainfall = np.where(water, rainfall * 1.25, rainfall)

    temp_fit = np.exp(-((temperature - 17.0) / 15.0) ** 2)
    rain_fit = np.clip((rainfall - 250.0) / 1100.0, 0.0, 1.0)
    slope_fit = np.exp(-8.0 * slope)
    fertility = temp_fit * rain_fit * slope_fit * (~water)

    coast = _coastal_mask(water)
    timber = np.clip((rainfall - 500.0) / 1300.0, 0.0, 1.0) * np.clip((temperature + 5) / 30, 0, 1)
    timber *= (~water)

    ore_noise = _normalize(_smooth(rng.random(shape), 2))
    ore = np.clip(0.55 * ore_noise + 0.45 * np.clip(slope * 18.0, 0.0, 1.0), 0.0, 1.0)
    ore *= (~water)

    habitability = np.clip(0.58 * fertility + 0.13 * timber + 0.09 * ore + 0.10 * coast + 0.10 * slope_fit, 0, 1)
    habitability *= (~water)

    spatial_map = SpatialMap.create(spec)
    for name, dtype, fill in (
        ("rainfall_mm", np.float32, 0.0),
        ("temperature_c", np.float32, 0.0),
        ("timber", np.float32, 0.0),
        ("ore", np.float32, 0.0),
        ("habitability", np.float32, 0.0),
    ):
        spatial_map.layers.add(name, dtype=dtype, fill_value=fill)

    movement_cost = 1.0 + 8.0 * np.clip(slope, 0, 0.5) + 1.5 * (1.0 - fertility)
    movement_cost = np.where(water, 1.0, movement_cost)

    spatial_map.layers.require("elevation_m").write_array(elevation.astype(np.float32))
    spatial_map.layers.require("water").write_array(water.astype(np.bool_))
    spatial_map.layers.require("passable").write_array((~water).astype(np.bool_))
    spatial_map.layers.require("fertility").write_array(fertility.astype(np.float32))
    spatial_map.layers.require("movement_cost").write_array(movement_cost.astype(np.float32))
    spatial_map.layers.require("rainfall_mm").write_array(rainfall.astype(np.float32))
    spatial_map.layers.require("temperature_c").write_array(temperature.astype(np.float32))
    spatial_map.layers.require("timber").write_array(timber.astype(np.float32))
    spatial_map.layers.require("ore").write_array(ore.astype(np.float32))
    spatial_map.layers.require("habitability").write_array(habitability.astype(np.float32))

    return GeneratedWorld(
        spatial_map=spatial_map,
        elevation_m=elevation.astype(np.float32),
        water=water.astype(np.bool_),
        rainfall=rainfall.astype(np.float32),
        temperature_c=temperature.astype(np.float32),
        fertility=fertility.astype(np.float32),
        timber=timber.astype(np.float32),
        ore=ore.astype(np.float32),
        habitability=habitability.astype(np.float32),
    )
