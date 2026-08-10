"""Spatial foundation for SimWorld.

Space is a causal substrate of the simulation. The public API intentionally exposes
coordinates, chunked raster layers, movement costs, path finding and sparse activity
history without requiring higher-level political or narrative concepts.
"""

from simworld.spatial.activity import CellActivity, CellActivityLedger, PlaceView, derive_place_views
from simworld.spatial.grid import CellCoord, ChunkCoord, GridSpec
from simworld.spatial.layers import ChunkedRaster, SpatialLayers
from simworld.spatial.map import SpatialMap
from simworld.spatial.movement import MovementModel, PathResult, shortest_path

__all__ = [
    "CellCoord",
    "ChunkCoord",
    "GridSpec",
    "ChunkedRaster",
    "SpatialLayers",
    "SpatialMap",
    "MovementModel",
    "PathResult",
    "shortest_path",
    "CellActivity",
    "CellActivityLedger",
    "PlaceView",
    "derive_place_views",
]
