from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from simworld.spatial.grid import CellCoord, GridSpec
from simworld.spatial.layers import SpatialLayers
from simworld.spatial.movement import MovementModel, PathResult, shortest_path


@dataclass(slots=True)
class SpatialMap:
    """Minimal physical map used by the first spatial milestone.

    The standard layers are intentionally mechanical rather than political. Future
    modules may add climate, hydrology, soils, resources, infrastructure, control
    and actor-specific perceived maps on top of the same spatial substrate.
    """

    spec: GridSpec
    layers: SpatialLayers

    @classmethod
    def create(cls, spec: GridSpec) -> SpatialMap:
        layers = SpatialLayers(spec)
        layers.add("elevation_m", dtype=np.float32, fill_value=0.0)
        layers.add("movement_cost", dtype=np.float32, fill_value=1.0)
        layers.add("passable", dtype=np.bool_, fill_value=True)
        layers.add("water", dtype=np.bool_, fill_value=False)
        layers.add("fertility", dtype=np.float32, fill_value=0.0)
        return cls(spec=spec, layers=layers)

    def movement_model(self, *, slope_weight: float = 6.0) -> MovementModel:
        return MovementModel(self.spec, self.layers, slope_weight=slope_weight)

    def path(
        self,
        start: CellCoord,
        goal: CellCoord,
        *,
        slope_weight: float = 6.0,
        max_expansions: int | None = None,
    ) -> PathResult | None:
        return shortest_path(
            self.movement_model(slope_weight=slope_weight),
            start,
            goal,
            max_expansions=max_expansions,
        )
