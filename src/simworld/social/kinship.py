from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque


@dataclass(frozen=True, slots=True)
class PersonRecord:
    id: str
    birth_time: int
    sex: str
    mother_id: str | None = None
    father_id: str | None = None
    death_time: int | None = None

    def alive_at(self, time: int) -> bool:
        return self.birth_time <= time and (self.death_time is None or time < self.death_time)


@dataclass(slots=True)
class KinshipGraph:
    people: dict[str, PersonRecord] = field(default_factory=dict)
    children_by_parent: dict[str, set[str]] = field(default_factory=dict)

    def add_person(self, person: PersonRecord) -> None:
        if person.id in self.people:
            raise ValueError(f"duplicate person: {person.id}")
        for parent_id in (person.mother_id, person.father_id):
            if parent_id is not None and parent_id not in self.people:
                raise ValueError(f"unknown parent: {parent_id}")
        self.people[person.id] = person
        for parent_id in (person.mother_id, person.father_id):
            if parent_id is not None:
                self.children_by_parent.setdefault(parent_id, set()).add(person.id)

    def parents(self, person_id: str) -> tuple[str, ...]:
        p = self.people[person_id]
        return tuple(x for x in (p.mother_id, p.father_id) if x is not None)

    def children(self, person_id: str) -> tuple[str, ...]:
        return tuple(sorted(self.children_by_parent.get(person_id, set())))

    def siblings(self, person_id: str) -> tuple[str, ...]:
        siblings: set[str] = set()
        for parent in self.parents(person_id):
            siblings.update(self.children_by_parent.get(parent, set()))
        siblings.discard(person_id)
        return tuple(sorted(siblings))

    def ancestors(self, person_id: str, max_generations: int | None = None) -> dict[str, int]:
        distances: dict[str, int] = {}
        queue = deque((p, 1) for p in self.parents(person_id))
        while queue:
            current, generation = queue.popleft()
            if current in distances and distances[current] <= generation:
                continue
            distances[current] = generation
            if max_generations is None or generation < max_generations:
                queue.extend((p, generation + 1) for p in self.parents(current))
        return distances

    def descendants(self, person_id: str, max_generations: int | None = None) -> dict[str, int]:
        distances: dict[str, int] = {}
        queue = deque((c, 1) for c in self.children(person_id))
        while queue:
            current, generation = queue.popleft()
            if current in distances and distances[current] <= generation:
                continue
            distances[current] = generation
            if max_generations is None or generation < max_generations:
                queue.extend((c, generation + 1) for c in self.children(current))
        return distances

    def shared_ancestors(self, a: str, b: str, max_generations: int = 8) -> set[str]:
        return set(self.ancestors(a, max_generations)) & set(self.ancestors(b, max_generations))

    def biological_relatedness_hint(self, a: str, b: str, max_generations: int = 8) -> float:
        if a == b:
            return 1.0
        aa = self.ancestors(a, max_generations)
        bb = self.ancestors(b, max_generations)
        score = 0.0
        for ancestor in set(aa) & set(bb):
            score += 0.5 ** (aa[ancestor] + bb[ancestor])
        if a in bb:
            score += 0.5 ** bb[a]
        if b in aa:
            score += 0.5 ** aa[b]
        return min(1.0, score)


@dataclass(frozen=True, slots=True)
class LineageView:
    roots: tuple[str, ...]
    members: frozenset[str]
    depth: int


def lineage_from_roots(graph: KinshipGraph, roots: tuple[str, ...], generations: int = 8) -> LineageView:
    members = set(roots)
    for root in roots:
        members.update(graph.descendants(root, generations))
    return LineageView(roots=roots, members=frozenset(members), depth=generations)
