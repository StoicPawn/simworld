from __future__ import annotations

from dataclasses import dataclass, field
from collections import defaultdict

from simworld.spatial.grid import CellCoord


@dataclass(slots=True)
class PresenceLedger:
    """Tracks where materialized actors actually spend time.

    Cells remain physical substrate. Terms such as market, square, harbour or centre
    are deliberately absent: repeated presence and interaction create measurable site
    intensity from which those higher-level concepts can later be derived.
    """

    positions: dict[str, CellCoord] = field(default_factory=dict)
    visits: dict[CellCoord, int] = field(default_factory=lambda: defaultdict(int))
    unique_visitors: dict[CellCoord, set[str]] = field(default_factory=lambda: defaultdict(set))
    encounters: dict[CellCoord, int] = field(default_factory=lambda: defaultdict(int))
    productive_uses: dict[CellCoord, int] = field(default_factory=lambda: defaultdict(int))

    def place(self, actor_id: str, cell: CellCoord) -> None:
        self.positions[actor_id] = cell
        self.record_visit(actor_id, cell)

    def move(self, actor_id: str, cell: CellCoord) -> None:
        if actor_id not in self.positions:
            raise KeyError(f"actor has no spatial presence: {actor_id}")
        self.positions[actor_id] = cell
        self.record_visit(actor_id, cell)

    def record_visit(self, actor_id: str, cell: CellCoord) -> None:
        self.visits[cell] += 1
        self.unique_visitors[cell].add(actor_id)

    def record_encounter(self, cell: CellCoord, count: int = 1) -> None:
        if count > 0:
            self.encounters[cell] += count

    def record_productive_use(self, cell: CellCoord, count: int = 1) -> None:
        if count > 0:
            self.productive_uses[cell] += count

    def occupants(self) -> dict[CellCoord, tuple[str, ...]]:
        by_cell: dict[CellCoord, list[str]] = defaultdict(list)
        for actor_id, cell in self.positions.items():
            by_cell[cell].append(actor_id)
        return {cell: tuple(sorted(ids)) for cell, ids in by_cell.items()}

    def site_intensity(self, cell: CellCoord) -> float:
        """Derived signal only; it does not create activity by itself."""
        return (
            0.08 * self.visits.get(cell, 0)
            + 0.45 * len(self.unique_visitors.get(cell, set()))
            + 0.7 * self.encounters.get(cell, 0)
            + 0.35 * self.productive_uses.get(cell, 0)
        )

    def active_sites(self, minimum_intensity: float = 1.0) -> tuple[tuple[CellCoord, float], ...]:
        cells = set(self.visits) | set(self.encounters) | set(self.productive_uses)
        ranked = [
            (cell, self.site_intensity(cell))
            for cell in cells
            if self.site_intensity(cell) >= minimum_intensity
        ]
        return tuple(sorted(ranked, key=lambda item: (-item[1], item[0].y, item[0].x)))
