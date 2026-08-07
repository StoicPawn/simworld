"""Spatial foundation for SimWorld.

Space is a causal substrate of the simulation. The public API intentionally exposes
coordinates, chunked raster layers, movement costs and path finding without
requiring higher-level political or narrative concepts.
"""

from simworld.spatial.grid import CellCoord, ChunkCoord, GridSpec
from simworld.spatial.layers import ChunkedRaster, SpatialLayers
from simworld.spatial.movement import MovementModel, PathResult, shortest_path

__all__ = [
    "CellCoord",
    "ChunkCoord",
    "GridSpec",
    "ChunkedRaster",
    "SpatialLayers",
    "MovementModel",
    "PathResult",
    "shortest_path",
]
