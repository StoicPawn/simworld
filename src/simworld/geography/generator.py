from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from simworld.geography.hydrology import flow_accumulation, freshwater_access
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
    river_strength: NDArray[np.float32]
    freshwater_access: NDArray[np.float32]
    coastal_food: NDArray[np.float32]
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
    """Generate deterministic physical geography that later history must respond to."""
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

    river_strength = flow_accumulation(elevation, water, rainfall)
    fresh_access = freshwater_access(river_strength)

    temp_fit = np.exp(-((temperature - 17.0) / 15.0) ** 2)
    rain_fit = np.clip((rainfall - 250.0) / 1100.0, 0.0, 1.0)
    slope_fit = np.exp(-8.0 * slope)
    local_water_fit = np.clip(0.84 + 0.32 * fresh_access, 0.0, 1.16)
    fertility = temp_fit * rain_fit * slope_fit * local_water_fit * (~water)
    fertility = np.clip(fertility, 0.0, 1.0)

    coast = _coastal_mask(water)
    shore_patchiness = _normalize(_smooth(rng.random(shape), 1))
    coastal_food = coast * np.clip(0.18 + 0.82 * shore_patchiness, 0.0, 1.0)
    coastal_food *= np.clip((temperature + 8.0) / 34.0, 0.15, 1.0)

    timber = np.clip((rainfall - 500.0) / 1300.0, 0.0, 1.0) * np.clip((temperature + 5) / 30, 0, 1)
    timber *= (~water)

    ore_noise = _normalize(_smooth(rng.random(shape), 2))
    ore = np.clip(0.55 * ore_noise + 0.45 * np.clip(slope * 18.0, 0.0, 1.0), 0.0, 1.0)
    ore *= (~water)

    habitability = np.clip(
        0.50 * fertility
        + 0.11 * timber
        + 0.08 * ore
        + 0.08 * coast
        + 0.08 * slope_fit
        + 0.09 * fresh_access
        + 0.06 * coastal_food,
        0,
        1,
    )
    habitability *= (~water)

    spatial_map = SpatialMap.create(spec)
    for name, dtype, fill in (
        ("rainfall_mm", np.float32, 0.0),
        ("temperature_c", np.float32, 0.0),
        ("timber", np.float32, 0.0),
        ("ore", np.float32, 0.0),
        ("river_strength", np.float32, 0.0),
        ("freshwater_access", np.float32, 0.0),
        ("coastal_food", np.float32, 0.0),
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
    spatial_map.layers.require("river_strength").write_array(river_strength.astype(np.float32))
    spatial_map.layers.require("freshwater_access").write_array(fresh_access.astype(np.float32))
    spatial_map.layers.require("coastal_food").write_array(coastal_food.astype(np.float32))
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
        river_strength=river_strength.astype(np.float32),
        freshwater_access=fresh_access.astype(np.float32),
        coastal_food=coastal_food.astype(np.float32),
        habitability=habitability.astype(np.float32),
    )
