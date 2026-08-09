from __future__ import annotations

from dataclasses import dataclass, field, replace


@dataclass(slots=True)
class SocialTie:
    source_id: str
    target_id: str
    kind: str
    strength: float
    started_at: int
    ended_at: int | None = None
    sentiment: float = 0.0
    trust: float = 0.5
    dependence: float = 0.0
    visibility: float = 1.0

    def active_at(self, time: int) -> bool:
        return self.started_at <= time and (self.ended_at is None or time < self.ended_at)


@dataclass(slots=True)
class SocialGraph:
    ties: list[SocialTie] = field(default_factory=list)

    def add(self, tie: SocialTie) -> None:
        if tie.source_id == tie.target_id:
            raise ValueError("self ties are not supported")
        self.ties.append(tie)

    def end(self, tie: SocialTie, time: int) -> SocialTie:
        if time < tie.started_at:
            raise ValueError("tie cannot end before it starts")
        for index, existing in enumerate(self.ties):
            if existing is tie:
                closed = replace(existing, ended_at=time)
                self.ties[index] = closed
                return closed
        raise ValueError("tie is not part of this graph")

    def active_ties(self, person_id: str, time: int, kind: str | None = None) -> tuple[SocialTie, ...]:
        return tuple(
            tie for tie in self.ties
            if tie.active_at(time)
            and (tie.source_id == person_id or tie.target_id == person_id)
            and (kind is None or tie.kind == kind)
        )

    def neighbours(self, person_id: str, time: int, kind: str | None = None) -> set[str]:
        result: set[str] = set()
        for tie in self.active_ties(person_id, time, kind):
            result.add(tie.target_id if tie.source_id == person_id else tie.source_id)
        return result

    def connection_strength(self, a: str, b: str, time: int) -> float:
        value = 0.0
        for tie in self.ties:
            if not tie.active_at(time):
                continue
            if {tie.source_id, tie.target_id} == {a, b}:
                value += tie.strength * (0.55 + 0.25 * tie.trust + 0.20 * max(0.0, tie.sentiment))
        return value

    def shortest_social_distance(self, source_id: str, target_id: str, time: int, max_depth: int = 8) -> int | None:
        if source_id == target_id:
            return 0
        frontier = {source_id}
        seen = {source_id}
        for depth in range(1, max_depth + 1):
            nxt: set[str] = set()
            for node in frontier:
                nxt.update(self.neighbours(node, time))
            if target_id in nxt:
                return depth
            nxt -= seen
            if not nxt:
                return None
            seen |= nxt
            frontier = nxt
        return None

    def second_order_neighbours(self, person_id: str, time: int) -> set[str]:
        direct = self.neighbours(person_id, time)
        second: set[str] = set()
        for neighbour in direct:
            second.update(self.neighbours(neighbour, time))
        second.discard(person_id)
        second -= direct
        return second
