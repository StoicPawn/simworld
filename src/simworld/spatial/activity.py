from __future__ import annotations

from dataclasses import dataclass, field


CellKey = tuple[int, int]


@dataclass(frozen=True, slots=True)
class Presence:
    actor_id: str
    cell: CellKey
    time: int
    activity: str
    intensity: float = 1.0


@dataclass(slots=True)
class SiteActivity:
    visits: float = 0.0
    gathering: float = 0.0
    cultivation: float = 0.0
    exchange: float = 0.0
    cooperation: float = 0.0
    conflict: float = 0.0
    visitors: set[str] = field(default_factory=set)
    first_seen: int | None = None
    last_seen: int | None = None

    def observe(self, presence: Presence) -> None:
        self.visits += presence.intensity
        self.visitors.add(presence.actor_id)
        self.first_seen = presence.time if self.first_seen is None else min(self.first_seen, presence.time)
        self.last_seen = presence.time if self.last_seen is None else max(self.last_seen, presence.time)
        if presence.activity == "gather":
            self.gathering += presence.intensity
        elif presence.activity == "cultivate":
            self.cultivation += presence.intensity


@dataclass(frozen=True, slots=True)
class PlaceView:
    cell: CellKey
    visits: float
    unique_visitors: int
    persistence: int
    gathering: float
    cultivation: float
    exchange: float
    cooperation: float
    conflict: float

    @property
    def interaction_density(self) -> float:
        return self.exchange + self.cooperation + self.conflict


@dataclass(slots=True)
class PlaceActivityLedger:
    """Sparse history of actual human use of physical cells.

    Cells with no activity consume no ledger entry. Labels such as market, village or
    sacred place are intentionally absent: higher layers may derive such views from
    persistent patterns of use and interaction.
    """

    sites: dict[CellKey, SiteActivity] = field(default_factory=dict)
    current_presence: dict[int, dict[CellKey, list[str]]] = field(default_factory=dict)

    def visit(self, presence: Presence) -> None:
        if presence.intensity <= 0:
            return
        self.sites.setdefault(presence.cell, SiteActivity()).observe(presence)
        by_cell = self.current_presence.setdefault(presence.time, {})
        by_cell.setdefault(presence.cell, []).append(presence.actor_id)

    def actors_at(self, cell: CellKey, time: int) -> tuple[str, ...]:
        return tuple(self.current_presence.get(time, {}).get(cell, ()))

    def record_interaction(self, cell: CellKey, *, exchange: float = 0.0, cooperation: float = 0.0, conflict: float = 0.0) -> None:
        site = self.sites.setdefault(cell, SiteActivity())
        site.exchange += max(0.0, exchange)
        site.cooperation += max(0.0, cooperation)
        site.conflict += max(0.0, conflict)

    def views(self, *, min_visits: float = 1.0) -> tuple[PlaceView, ...]:
        result: list[PlaceView] = []
        for cell, site in self.sites.items():
            if site.visits < min_visits:
                continue
            persistence = 0
            if site.first_seen is not None and site.last_seen is not None:
                persistence = site.last_seen - site.first_seen + 1
            result.append(
                PlaceView(
                    cell=cell,
                    visits=site.visits,
                    unique_visitors=len(site.visitors),
                    persistence=persistence,
                    gathering=site.gathering,
                    cultivation=site.cultivation,
                    exchange=site.exchange,
                    cooperation=site.cooperation,
                    conflict=site.conflict,
                )
            )
        result.sort(key=lambda view: (-view.visits, -view.unique_visitors, view.cell[1], view.cell[0]))
        return tuple(result)

    def forget_presence_before(self, time: int) -> None:
        for old_time in tuple(self.current_presence):
            if old_time < time:
                del self.current_presence[old_time]
