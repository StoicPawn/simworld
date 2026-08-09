from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True, slots=True)
class Hydrology:
    flow_accumulation: NDArray[np.float32]
    river_strength: NDArray[np.float32]
    water_access: NDArray[np.float32]
    ruggedness: NDArray[np.float32]


def derive_hydrology(
    elevation_m: NDArray[np.floating],
    water: NDArray[np.bool_],
    rainfall_mm: NDArray[np.floating],
) -> Hydrology:
    """Derive coarse river corridors from terrain and rainfall.

    This is intentionally a deterministic first hydrology model. It is not a visual
    river painter: downstream accumulation alters agriculture, movement and later
    settlement/conflict incentives.
    """
    height, width = elevation_m.shape
    accumulation = np.maximum(rainfall_mm.astype(np.float64), 1.0).copy()
    downstream = np.full((height, width, 2), -1, dtype=np.int32)
    neighbours = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))

    for y in range(height):
        for x in range(width):
            if water[y, x]:
                continue
            current = float(elevation_m[y, x])
            best: tuple[float, int, int] | None = None
            for dy, dx in neighbours:
                ny, nx = y + dy, x + dx
                if not (0 <= ny < height and 0 <= nx < width):
                    continue
                target = float(elevation_m[ny, nx])
                if water[ny, nx]:
                    target -= 10_000.0
                drop = current - target
                if drop <= 0.0:
                    continue
                if best is None or drop > best[0]:
                    best = (drop, ny, nx)
            if best is not None:
                downstream[y, x] = (best[1], best[2])

    order = np.argsort(elevation_m.ravel())[::-1]
    for flat in order:
        y, x = divmod(int(flat), width)
        ny, nx = downstream[y, x]
        if ny >= 0:
            accumulation[ny, nx] += accumulation[y, x]

    land_acc = accumulation[~water]
    scale = float(np.quantile(land_acc, 0.94)) if land_acc.size else 1.0
    river = np.clip(accumulation / max(scale, 1.0), 0.0, 3.0)
    river = np.where(water, 0.0, river)

    gy, gx = np.gradient(elevation_m.astype(np.float64))
    local_slope = np.hypot(gx, gy)
    ruggedness = np.clip(local_slope / max(1.0, float(np.quantile(local_slope, 0.9))), 0.0, 2.0)
    ruggedness = np.where(water, 0.0, ruggedness)

    water_access = np.clip(river, 0.0, 1.0)
    water_access = np.maximum(water_access, water.astype(np.float64))
    # diffuse local access so valleys near a river benefit without every cell being a river
    for _ in range(3):
        padded = np.pad(water_access, 1, mode="edge")
        water_access = np.maximum(
            water_access,
            0.72
            * np.maximum.reduce(
                [
                    padded[:-2, 1:-1],
                    padded[2:, 1:-1],
                    padded[1:-1, :-2],
                    padded[1:-1, 2:],
                ]
            ),
        )

    return Hydrology(
        flow_accumulation=accumulation.astype(np.float32),
        river_strength=river.astype(np.float32),
        water_access=np.clip(water_access, 0.0, 1.0).astype(np.float32),
        ruggedness=np.clip(ruggedness, 0.0, 1.0).astype(np.float32),
    )
