from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray

from simworld.spatial.grid import CellCoord, ChunkCoord, GridSpec


@dataclass(slots=True)
class ChunkedRaster:
    """Lazy chunked raster layer.

    The conceptual map may contain millions of cells while memory is allocated only
    for chunks that are touched. Untouched cells read as ``fill_value``.
    """

    spec: GridSpec
    dtype: np.dtype[Any] = field(default_factory=lambda: np.dtype(np.float64))
    fill_value: float | int | bool = 0.0
    _chunks: dict[ChunkCoord, NDArray[Any]] = field(default_factory=dict, repr=False)

    def _allocate(self, chunk: ChunkCoord) -> NDArray[Any]:
        array = self._chunks.get(chunk)
        if array is None:
            array = np.full(self.spec.chunk_shape(chunk), self.fill_value, dtype=self.dtype)
            self._chunks[chunk] = array
        return array

    def get(self, cell: CellCoord) -> Any:
        chunk = self.spec.chunk_for(cell)
        array = self._chunks.get(chunk)
        if array is None:
            return self.dtype.type(self.fill_value).item()
        row, column = self.spec.local_index(cell)
        return array[row, column].item()

    def set(self, cell: CellCoord, value: float | int | bool) -> None:
        chunk = self.spec.chunk_for(cell)
        row, column = self.spec.local_index(cell)
        self._allocate(chunk)[row, column] = value

    def chunk(self, chunk: ChunkCoord, *, writable: bool = False) -> NDArray[Any]:
        if writable:
            return self._allocate(chunk)
        array = self._chunks.get(chunk)
        if array is None:
            return np.full(self.spec.chunk_shape(chunk), self.fill_value, dtype=self.dtype)
        return array.copy()

    def write_array(self, values: NDArray[Any]) -> None:
        """Write a full raster efficiently while preserving chunked storage."""
        expected = (self.spec.height, self.spec.width)
        if values.shape != expected:
            raise ValueError(f"expected raster shape {expected}, got {values.shape}")
        for chunk_y in range((self.spec.height + self.spec.chunk_size - 1) // self.spec.chunk_size):
            for chunk_x in range((self.spec.width + self.spec.chunk_size - 1) // self.spec.chunk_size):
                chunk = ChunkCoord(chunk_x, chunk_y)
                row0 = chunk_y * self.spec.chunk_size
                col0 = chunk_x * self.spec.chunk_size
                shape = self.spec.chunk_shape(chunk)
                block = np.asarray(
                    values[row0 : row0 + shape[0], col0 : col0 + shape[1]], dtype=self.dtype
                )
                if np.all(block == self.fill_value):
                    self._chunks.pop(chunk, None)
                else:
                    self._chunks[chunk] = block.copy()

    def to_array(self) -> NDArray[Any]:
        """Materialize the raster into a dense array for analysis/export."""
        result = np.full((self.spec.height, self.spec.width), self.fill_value, dtype=self.dtype)
        for chunk, block in self._chunks.items():
            row0 = chunk.y * self.spec.chunk_size
            col0 = chunk.x * self.spec.chunk_size
            result[row0 : row0 + block.shape[0], col0 : col0 + block.shape[1]] = block
        return result

    @property
    def allocated_chunks(self) -> int:
        return len(self._chunks)

    @property
    def allocated_cells(self) -> int:
        return sum(int(array.size) for array in self._chunks.values())


class SpatialLayers:
    """Named spatial layers sharing one grid geometry."""

    def __init__(self, spec: GridSpec) -> None:
        self.spec = spec
        self._layers: dict[str, ChunkedRaster] = {}

    def add(
        self,
        name: str,
        *,
        dtype: np.dtype[Any] | type[Any] = np.float64,
        fill_value: float | int | bool = 0.0,
    ) -> ChunkedRaster:
        if not name or name in self._layers:
            raise ValueError(f"invalid or duplicate layer name: {name!r}")
        layer = ChunkedRaster(self.spec, dtype=np.dtype(dtype), fill_value=fill_value)
        self._layers[name] = layer
        return layer

    def require(self, name: str) -> ChunkedRaster:
        try:
            return self._layers[name]
        except KeyError as exc:
            raise KeyError(f"unknown spatial layer: {name}") from exc

    def get(self, name: str, cell: CellCoord) -> Any:
        return self.require(name).get(cell)

    def set(self, name: str, cell: CellCoord, value: float | int | bool) -> None:
        self.require(name).set(cell, value)

    def names(self) -> tuple[str, ...]:
        return tuple(self._layers)
