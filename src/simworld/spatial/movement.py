from __future__ import annotations

import heapq
from dataclasses import dataclass
from math import inf

from simworld.spatial.grid import CellCoord, GridSpec
from simworld.spatial.layers import SpatialLayers


@dataclass(frozen=True, slots=True)
class PathResult:
    cells: tuple[CellCoord, ...]
    cost: float


class MovementModel:
    """Converts physical raster properties into traversal cost.

    The model intentionally reads generic spatial layers rather than terrain labels.
    Higher-level domains can later construct these layers from roads, rivers,
    vegetation, political control, weather, technology or military conditions.
    """

    def __init__(
        self,
        spec: GridSpec,
        layers: SpatialLayers,
        *,
        movement_cost_layer: str = "movement_cost",
        passable_layer: str = "passable",
        elevation_layer: str = "elevation_m",
        slope_weight: float = 6.0,
        heuristic_cost_floor: float = 0.0,
        allow_corner_cutting: bool = False,
    ) -> None:
        if slope_weight < 0:
            raise ValueError("slope_weight cannot be negative")
        if heuristic_cost_floor < 0:
            raise ValueError("heuristic_cost_floor cannot be negative")
        self.spec = spec
        self.layers = layers
        self.movement_cost_layer = movement_cost_layer
        self.passable_layer = passable_layer
        self.elevation_layer = elevation_layer
        self.slope_weight = slope_weight
        self.heuristic_cost_floor = heuristic_cost_floor
        self.allow_corner_cutting = allow_corner_cutting

    def is_passable(self, cell: CellCoord) -> bool:
        return bool(self.layers.get(self.passable_layer, cell))

    def _diagonal_crosses_blocked_corner(
        self, origin: CellCoord, destination: CellCoord
    ) -> bool:
        dx = destination.x - origin.x
        dy = destination.y - origin.y
        if abs(dx) != 1 or abs(dy) != 1 or self.allow_corner_cutting:
            return False
        side_a = CellCoord(origin.x + dx, origin.y)
        side_b = CellCoord(origin.x, origin.y + dy)
        return not self.is_passable(side_a) or not self.is_passable(side_b)

    def step_cost(self, origin: CellCoord, destination: CellCoord) -> float:
        if destination not in self.spec.neighbors(origin, diagonals=True):
            raise ValueError("movement is only defined between adjacent cells")
        if not self.is_passable(origin) or not self.is_passable(destination):
            return inf
        if self._diagonal_crosses_blocked_corner(origin, destination):
            return inf

        horizontal_m = self.spec.distance_m(origin, destination)
        base_a = float(self.layers.get(self.movement_cost_layer, origin))
        base_b = float(self.layers.get(self.movement_cost_layer, destination))
        if base_a <= 0 or base_b <= 0:
            return inf

        elevation_a = float(self.layers.get(self.elevation_layer, origin))
        elevation_b = float(self.layers.get(self.elevation_layer, destination))
        grade = abs(elevation_b - elevation_a) / horizontal_m
        terrain_factor = (base_a + base_b) / 2.0
        return horizontal_m * terrain_factor * (1.0 + self.slope_weight * grade)

    def heuristic(self, cell: CellCoord, goal: CellCoord) -> float:
        # A floor of zero degrades safely to Dijkstra. A positive value may be used
        # only when the caller knows it is a lower bound for all traversable costs.
        return self.spec.distance_m(cell, goal) * self.heuristic_cost_floor


def shortest_path(
    model: MovementModel,
    start: CellCoord,
    goal: CellCoord,
    *,
    max_expansions: int | None = None,
) -> PathResult | None:
    """Find a minimum-cost traversable path with A*/Dijkstra semantics.

    ``None`` means no traversable connection exists under the current map state.
    The path reacts automatically when geography or infrastructure layers change;
    no strategic corridor is hard-coded.
    """

    model.spec.require_cell(start)
    model.spec.require_cell(goal)
    if not model.is_passable(start) or not model.is_passable(goal):
        return None
    if start == goal:
        return PathResult((start,), 0.0)

    frontier: list[tuple[float, int, CellCoord]] = [(model.heuristic(start, goal), 0, start)]
    came_from: dict[CellCoord, CellCoord] = {}
    cost_so_far: dict[CellCoord, float] = {start: 0.0}
    sequence = 1
    expansions = 0

    while frontier:
        _, _, current = heapq.heappop(frontier)
        if current == goal:
            path = [goal]
            while path[-1] != start:
                path.append(came_from[path[-1]])
            path.reverse()
            return PathResult(tuple(path), cost_so_far[goal])

        expansions += 1
        if max_expansions is not None and expansions > max_expansions:
            return None

        for neighbor in model.spec.neighbors(current, diagonals=True):
            step = model.step_cost(current, neighbor)
            if step == inf:
                continue
            candidate_cost = cost_so_far[current] + step
            if candidate_cost >= cost_so_far.get(neighbor, inf):
                continue
            cost_so_far[neighbor] = candidate_cost
            came_from[neighbor] = current
            priority = candidate_cost + model.heuristic(neighbor, goal)
            heapq.heappush(frontier, (priority, sequence, neighbor))
            sequence += 1

    return None
