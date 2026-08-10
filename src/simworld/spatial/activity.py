from __future__ import annotations

from dataclasses import dataclass, field

from simworld.spatial.grid import CellCoord


@dataclass(slots=True)
class CellActivity:
    visits: float = 0.0
    residence: float = 0.0
    gathering: float = 0.0
    cultivation: float = 0.0
    exchange: float = 0.0
    conflict: float = 0.0
    construction: float = 0.0
    first_seen: int | None = None
    last_seen: int | None = None
    actors: set[str] = field(default_factory=set)

    def total(self) -> float:
        return (
            self.visits
            + self.residence
            + self.gathering
            + self.cultivation
            + self.exchange
            + self.conflict
            + self.construction
        )


@dataclass(slots=True)
class CellActivityLedger:
    """Sparse historical use of physical cells.

    Empty/unimportant cells cost nothing beyond the physical raster. A cell only gains
    social state after something actually happens there.
    """

    cells: dict[tuple[int, int], CellActivity] = field(default_factory=dict)

    def record(
        self,
        cell: CellCoord,
        *,
        time: int,
        actor_id: str | None = None,
        kind: str = "visit",
        amount: float = 1.0,
    ) -> None:
        if amount < 0:
            raise ValueError("activity amount must be non-negative")
        key = (cell.x, cell.y)
        state = self.cells.setdefault(key, CellActivity())
        if state.first_seen is None:
            state.first_seen = time
        state.last_seen = time
        if actor_id is not None:
            state.actors.add(actor_id)
        field_name = {
            "visit": "visits",
            "residence": "residence",
            "gather": "gathering",
            "cultivate": "cultivation",
            "exchange": "exchange",
            "conflict": "conflict",
            "construct": "construction",
        }.get(kind)
        if field_name is None:
            raise ValueError(f"unknown activity kind: {kind}")
        setattr(state, field_name, getattr(state, field_name) + amount)

    def at(self, cell: CellCoord) -> CellActivity:
        return self.cells.get((cell.x, cell.y), CellActivity())


@dataclass(frozen=True, slots=True)
class PlaceView:
    cell: CellCoord
    actors: int
    persistence: int
    total_activity: float
    residence_signal: float
    exchange_signal: float
    production_signal: float
    conflict_signal: float
    infrastructure_signal: float


def derive_place_views(ledger: CellActivityLedger, *, min_activity: float = 3.0) -> tuple[PlaceView, ...]:
    """Derive socially meaningful places without declaring place types in the kernel."""
    views: list[PlaceView] = []
    for (x, y), activity in ledger.cells.items():
        total = activity.total()
        if total < min_activity:
            continue
        first = activity.first_seen if activity.first_seen is not None else 0
        last = activity.last_seen if activity.last_seen is not None else first
        views.append(
            PlaceView(
                cell=CellCoord(x, y),
                actors=len(activity.actors),
                persistence=max(1, last - first + 1),
                total_activity=total,
                residence_signal=activity.residence,
                exchange_signal=activity.exchange,
                production_signal=activity.gathering + activity.cultivation,
                conflict_signal=activity.conflict,
                infrastructure_signal=activity.construction,
            )
        )
    views.sort(key=lambda view: (-view.total_activity, -view.actors, view.cell.y, view.cell.x))
    return tuple(views)
