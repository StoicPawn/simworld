from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

_NEIGHBOURS = (
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1),
)


def flow_accumulation(
    elevation_m: NDArray[np.floating],
    water: NDArray[np.bool_],
    rainfall_mm: NDArray[np.floating] | None = None,
) -> NDArray[np.float32]:
    """Return continuous terrain-derived drainage intensity.

    Each land cell drains toward its lowest strictly lower neighbour. Accumulation is
    propagated from high to low elevation. The result is normalized to [0, 1] after a
    log transform, so it is useful as a scalable physical signal rather than a hard
    river/non-river classification.
    """
    if elevation_m.shape != water.shape:
        raise ValueError("elevation and water shapes must match")
    if rainfall_mm is not None and rainfall_mm.shape != water.shape:
        raise ValueError("rainfall shape must match elevation")

    height, width = elevation_m.shape
    downstream_y = np.full((height, width), -1, dtype=np.int32)
    downstream_x = np.full((height, width), -1, dtype=np.int32)

    for y in range(height):
        for x in range(width):
            if water[y, x]:
                continue
            current = float(elevation_m[y, x])
            best_elevation = current
            best: tuple[int, int] | None = None
            for dy, dx in _NEIGHBOURS:
                ny, nx = y + dy, x + dx
                if not (0 <= ny < height and 0 <= nx < width):
                    continue
                candidate = float(elevation_m[ny, nx])
                if candidate < best_elevation:
                    best_elevation = candidate
                    best = (ny, nx)
            if best is not None:
                downstream_y[y, x], downstream_x[y, x] = best

    if rainfall_mm is None:
        accumulation = np.ones((height, width), dtype=np.float64)
    else:
        rain = np.asarray(rainfall_mm, dtype=np.float64)
        land_rain = rain[~water]
        scale = float(np.mean(land_rain)) if land_rain.size else 1.0
        accumulation = np.clip(rain / max(scale, 1e-9), 0.1, 4.0)
    accumulation[water] = 0.0

    land_indices = np.argwhere(~water)
    order = sorted(
        ((float(elevation_m[y, x]), int(y), int(x)) for y, x in land_indices),
        reverse=True,
    )
    for _, y, x in order:
        ny, nx = int(downstream_y[y, x]), int(downstream_x[y, x])
        if ny >= 0:
            accumulation[ny, nx] += accumulation[y, x]

    logged = np.log1p(accumulation)
    logged[water] = 0.0
    land = logged[~water]
    if not land.size or float(land.max()) <= float(land.min()):
        return np.zeros_like(elevation_m, dtype=np.float32)
    normalized = (logged - float(land.min())) / max(1e-9, float(land.max() - land.min()))
    normalized[water] = 0.0
    return np.clip(normalized, 0.0, 1.0).astype(np.float32)


def freshwater_access(river_strength: NDArray[np.floating]) -> NDArray[np.float32]:
    """Diffuse river intensity one cell outward without creating a legal/place concept."""
    strength = np.asarray(river_strength, dtype=np.float64)
    result = strength.copy()
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        shifted = np.roll(strength, shift=(dy, dx), axis=(0, 1)) * 0.55
        if dy == -1:
            shifted[-1, :] = 0.0
        elif dy == 1:
            shifted[0, :] = 0.0
        if dx == -1:
            shifted[:, -1] = 0.0
        elif dx == 1:
            shifted[:, 0] = 0.0
        result = np.maximum(result, shifted)
    return np.clip(result, 0.0, 1.0).astype(np.float32)
