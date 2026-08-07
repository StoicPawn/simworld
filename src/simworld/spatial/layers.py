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
