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


@dataclass(frozen=True, slots=True)
class SettlementNucleusView:
    """Retrospective residential/activity cluster, never a primitive settlement."""

    cells: tuple[CellCoord, ...]
    centre: CellCoord
    actors: int
    persistence: int
    residence_signal: float
    production_signal: float
    exchange_signal: float
    infrastructure_signal: float
    conflict_signal: float

    @property
    def total_signal(self) -> float:
        return (
            self.residence_signal
            + self.production_signal
            + self.exchange_signal
            + self.infrastructure_signal
            + self.conflict_signal
        )


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


def derive_settlement_nuclei(
    ledger: CellActivityLedger,
    *,
    min_cell_residence: float = 1.0,
    min_cluster_residence: float = 5.0,
) -> tuple[SettlementNucleusView, ...]:
    """Cluster adjacent persistently used cells into retrospective inhabited nuclei.

    The function deliberately does not decide whether a cluster is a village, camp,
    town or city. Those are later social/institutional interpretations.
    """
    eligible = {
        key
        for key, activity in ledger.cells.items()
        if activity.residence >= min_cell_residence
        or (activity.construction > 0 and activity.total() >= min_cell_residence)
    }
    visited: set[tuple[int, int]] = set()
    nuclei: list[SettlementNucleusView] = []

    for start in sorted(eligible, key=lambda item: (item[1], item[0])):
        if start in visited:
            continue
        stack = [start]
        component: list[tuple[int, int]] = []
        visited.add(start)
        while stack:
            x, y = stack.pop()
            component.append((x, y))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    neighbour = (x + dx, y + dy)
                    if neighbour in eligible and neighbour not in visited:
                        visited.add(neighbour)
                        stack.append(neighbour)

        activities = [ledger.cells[key] for key in component]
        residence = sum(activity.residence for activity in activities)
        if residence < min_cluster_residence:
            continue
        actor_ids: set[str] = set()
        first_times: list[int] = []
        last_times: list[int] = []
        for activity in activities:
            actor_ids.update(activity.actors)
            if activity.first_seen is not None:
                first_times.append(activity.first_seen)
            if activity.last_seen is not None:
                last_times.append(activity.last_seen)

        weighted = sorted(
            component,
            key=lambda key: (
                -(
                    ledger.cells[key].residence
                    + 1.5 * ledger.cells[key].construction
                    + 0.5 * ledger.cells[key].exchange
                ),
                key[1],
                key[0],
            ),
        )
        centre = CellCoord(*weighted[0])
        persistence = max(last_times) - min(first_times) + 1 if first_times and last_times else 1
        nuclei.append(
            SettlementNucleusView(
                cells=tuple(CellCoord(x, y) for x, y in sorted(component, key=lambda key: (key[1], key[0]))),
                centre=centre,
                actors=len(actor_ids),
                persistence=persistence,
                residence_signal=residence,
                production_signal=sum(a.gathering + a.cultivation for a in activities),
                exchange_signal=sum(a.exchange for a in activities),
                infrastructure_signal=sum(a.construction for a in activities),
                conflict_signal=sum(a.conflict for a in activities),
            )
        )

    nuclei.sort(key=lambda nucleus: (-nucleus.total_signal, -nucleus.actors, nucleus.centre.y, nucleus.centre.x))
    return tuple(nuclei)
