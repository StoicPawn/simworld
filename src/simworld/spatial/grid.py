from __future__ import annotations

from dataclasses import dataclass
from math import hypot


@dataclass(frozen=True, slots=True, order=True)
class CellCoord:
    x: int
    y: int


@dataclass(frozen=True, slots=True, order=True)
class ChunkCoord:
    x: int
    y: int


@dataclass(frozen=True, slots=True)
class GridSpec:
    """Geometry of a regular raster map.

    Cells are the smallest spatial unit exposed by the simulation. Storage is
    chunked separately so map resolution and memory layout can evolve without
    changing domain logic.
    """

    width: int
    height: int
    cell_size_m: float = 1_000.0
    chunk_size: int = 256
    origin_x_m: float = 0.0
    origin_y_m: float = 0.0

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("grid dimensions must be positive")
        if self.cell_size_m <= 0:
            raise ValueError("cell_size_m must be positive")
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")

    def contains(self, cell: CellCoord) -> bool:
        return 0 <= cell.x < self.width and 0 <= cell.y < self.height

    def require_cell(self, cell: CellCoord) -> None:
        if not self.contains(cell):
            raise IndexError(f"cell outside grid: {cell}")

    def world_to_cell(self, x_m: float, y_m: float) -> CellCoord:
        x = int((x_m - self.origin_x_m) // self.cell_size_m)
        y = int((y_m - self.origin_y_m) // self.cell_size_m)
        cell = CellCoord(x, y)
        self.require_cell(cell)
        return cell

    def cell_center_m(self, cell: CellCoord) -> tuple[float, float]:
        self.require_cell(cell)
        return (
            self.origin_x_m + (cell.x + 0.5) * self.cell_size_m,
            self.origin_y_m + (cell.y + 0.5) * self.cell_size_m,
        )

    def chunk_for(self, cell: CellCoord) -> ChunkCoord:
        self.require_cell(cell)
        return ChunkCoord(cell.x // self.chunk_size, cell.y // self.chunk_size)

    def local_index(self, cell: CellCoord) -> tuple[int, int]:
        self.require_cell(cell)
        return cell.y % self.chunk_size, cell.x % self.chunk_size

    def chunk_shape(self, chunk: ChunkCoord) -> tuple[int, int]:
        x0 = chunk.x * self.chunk_size
        y0 = chunk.y * self.chunk_size
        if x0 < 0 or y0 < 0 or x0 >= self.width or y0 >= self.height:
            raise IndexError(f"chunk outside grid: {chunk}")
        width = min(self.chunk_size, self.width - x0)
        height = min(self.chunk_size, self.height - y0)
        return height, width

    def neighbors(self, cell: CellCoord, *, diagonals: bool = True) -> tuple[CellCoord, ...]:
        self.require_cell(cell)
        offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        if diagonals:
            offsets += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        result = []
        for dx, dy in offsets:
            candidate = CellCoord(cell.x + dx, cell.y + dy)
            if self.contains(candidate):
                result.append(candidate)
        return tuple(result)

    def distance_m(self, a: CellCoord, b: CellCoord) -> float:
        self.require_cell(a)
        self.require_cell(b)
        return hypot(b.x - a.x, b.y - a.y) * self.cell_size_m
