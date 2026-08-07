from __future__ import annotations

from math import isclose

import numpy as np

from simworld.spatial import CellCoord, ChunkCoord, GridSpec, SpatialMap


def test_grid_coordinates_and_neighbors() -> None:
    spec = GridSpec(width=5, height=4, cell_size_m=1_000.0, chunk_size=2)
    cell = CellCoord(2, 1)

    assert spec.cell_center_m(cell) == (2_500.0, 1_500.0)
    assert spec.world_to_cell(2_999.0, 1_001.0) == cell
    assert spec.chunk_for(cell) == ChunkCoord(1, 0)
    assert spec.local_index(cell) == (1, 0)
    assert len(spec.neighbors(cell, diagonals=False)) == 4
    assert len(spec.neighbors(cell, diagonals=True)) == 8


def test_chunked_layers_allocate_only_touched_chunks() -> None:
    world_map = SpatialMap.create(GridSpec(width=10_000, height=10_000, chunk_size=128))
    elevation = world_map.layers.require("elevation_m")

    assert elevation.allocated_chunks == 0
    assert elevation.get(CellCoord(9_999, 9_999)) == 0.0
    assert elevation.allocated_chunks == 0

    elevation.set(CellCoord(3, 4), 950.0)
    elevation.set(CellCoord(4, 5), 1_020.0)
    assert elevation.allocated_chunks == 1
    assert elevation.allocated_cells == 128 * 128

    elevation.set(CellCoord(300, 300), 400.0)
    assert elevation.allocated_chunks == 2


def test_standard_layers_have_physical_defaults() -> None:
    world_map = SpatialMap.create(GridSpec(width=3, height=3))
    cell = CellCoord(1, 1)

    assert world_map.layers.get("passable", cell) is True
    assert world_map.layers.get("water", cell) is False
    assert world_map.layers.get("movement_cost", cell) == 1.0
    assert world_map.layers.names() == (
        "elevation_m",
        "movement_cost",
        "passable",
        "water",
        "fertility",
    )


def test_slope_increases_movement_cost() -> None:
    world_map = SpatialMap.create(GridSpec(width=3, height=1, cell_size_m=1_000.0))
    model = world_map.movement_model(slope_weight=10.0)

    flat = model.step_cost(CellCoord(0, 0), CellCoord(1, 0))
    world_map.layers.set("elevation_m", CellCoord(2, 0), 500.0)
    steep = model.step_cost(CellCoord(1, 0), CellCoord(2, 0))

    assert isclose(flat, 1_000.0)
    assert steep > flat


def test_impassable_cells_break_connectivity() -> None:
    world_map = SpatialMap.create(GridSpec(width=3, height=1))
    world_map.layers.set("passable", CellCoord(1, 0), False)

    assert world_map.path(CellCoord(0, 0), CellCoord(2, 0)) is None


def test_pathfinder_discovers_only_pass_through_barrier() -> None:
    spec = GridSpec(width=9, height=7, cell_size_m=1_000.0, chunk_size=4)
    world_map = SpatialMap.create(spec)

    # A north-south mountain/barrier wall at x=4, with one pass at y=5.
    for y in range(spec.height):
        world_map.layers.set("passable", CellCoord(4, y), False)
        world_map.layers.set("elevation_m", CellCoord(4, y), 3_000.0)
    pass_cell = CellCoord(4, 5)
    world_map.layers.set("passable", pass_cell, True)
    world_map.layers.set("elevation_m", pass_cell, 350.0)

    result = world_map.path(CellCoord(1, 1), CellCoord(7, 1))

    assert result is not None
    assert pass_cell in result.cells
    assert result.cells[0] == CellCoord(1, 1)
    assert result.cells[-1] == CellCoord(7, 1)


def test_higher_terrain_cost_can_redirect_route() -> None:
    world_map = SpatialMap.create(GridSpec(width=5, height=3, cell_size_m=1_000.0))

    # The geometric shortest line is expensive; the engine should route around it.
    for x in (1, 2, 3):
        world_map.layers.set("movement_cost", CellCoord(x, 1), np.float32(20.0))

    result = world_map.path(CellCoord(0, 1), CellCoord(4, 1), slope_weight=0.0)

    assert result is not None
    assert CellCoord(2, 1) not in result.cells
    assert result.cost < 20_000.0
