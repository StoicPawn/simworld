from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from simworld.population.field import PopulationField
from simworld.spatial import CellCoord


@dataclass(frozen=True, slots=True)
class PopulationSummaryView:
    """Reporting-only aggregate over a derived set of cells."""

    anchor_id: str
    population: float
    capacity: float
    mean_suitability: float
    cell_count: int

    @property
    def capacity_ratio(self) -> float:
        if self.population <= 1e-9:
            return 1.0
        return self.capacity / self.population


def nearest_anchor_partition(
    *,
    width: int,
    height: int,
    water: NDArray[np.bool_],
    anchors: dict[str, CellCoord],
) -> NDArray[np.int32]:
    """Assign each land cell to the nearest compatibility anchor for reporting only.

    The resulting partition has no causal semantics and must never be interpreted as a
    border, territory or political region.
    """
    if not anchors:
        raise ValueError("anchors must not be empty")
    ordered = sorted(anchors.items(), key=lambda item: item[0])
    ys, xs = np.mgrid[0:height, 0:width]
    best_distance = np.full((height, width), np.inf, dtype=np.float64)
    partition = np.full((height, width), -1, dtype=np.int32)
    for index, (_, cell) in enumerate(ordered):
        distance = (xs - cell.x) ** 2 + (ys - cell.y) ** 2
        better = distance < best_distance
        partition[better] = index
        best_distance[better] = distance[better]
    partition[water] = -1
    return partition


def population_summaries(
    field: PopulationField,
    partition: NDArray[np.int32],
    anchors: dict[str, CellCoord],
) -> dict[str, PopulationSummaryView]:
    ordered = sorted(anchors.items(), key=lambda item: item[0])
    summaries: dict[str, PopulationSummaryView] = {}
    for index, (anchor_id, _) in enumerate(ordered):
        mask = partition == index
        cells = int(np.count_nonzero(mask))
        if cells == 0:
            summaries[anchor_id] = PopulationSummaryView(anchor_id, 0.0, 0.0, 0.0, 0)
            continue
        population = float(field.population[mask].sum())
        capacity = float(field.capacity[mask].sum())
        suitability = float(field.suitability[mask].mean())
        summaries[anchor_id] = PopulationSummaryView(
            anchor_id=anchor_id,
            population=population,
            capacity=capacity,
            mean_suitability=suitability,
            cell_count=cells,
        )
    return summaries
