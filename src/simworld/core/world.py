from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

from simworld.core.entity import Entity
from simworld.core.event import Event
from simworld.core.relevance import RelevanceIndex, ResolutionLevel


@dataclass(slots=True)
class WorldState:
    """Authoritative current state plus append-only historical memory."""

    current_time: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    relevance: RelevanceIndex = field(default_factory=RelevanceIndex)
    entities: dict[str, Entity] = field(default_factory=dict)
    _events: list[Event] = field(default_factory=list, repr=False)
    _events_by_id: dict[str, Event] = field(default_factory=dict, repr=False)
    _events_by_entity: dict[str, list[str]] = field(
        default_factory=lambda: defaultdict(list), repr=False
    )
    _causal_children: dict[str, list[str]] = field(
        default_factory=lambda: defaultdict(list), repr=False
    )

    @property
    def events(self) -> tuple[Event, ...]:
        return tuple(self._events)

    def advance_to(self, time: int) -> None:
        """Advance simulated time monotonically without inventing an event."""
        if time < self.current_time:
            raise ValueError("cannot move world time backwards")
        self.current_time = time

    def add_entity(self, entity: Entity) -> None:
        if entity.id in self.entities:
            raise ValueError(f"duplicate entity id: {entity.id}")
        if entity.created_at > self.current_time:
            raise ValueError("entity cannot be created in the future")
        self.entities[entity.id] = entity

    def record_event(self, event: Event) -> None:
        if event.id in self._events_by_id:
            raise ValueError(f"duplicate event id: {event.id}")
        if event.time < self.current_time:
            raise ValueError("cannot append an event in the simulated past")

        referenced_entities = set(event.participants) | set(event.locations)
        unknown_entities = referenced_entities.difference(self.entities)
        if unknown_entities:
            raise KeyError(f"event references unknown entities: {sorted(unknown_entities)}")

        for cause_id in event.causes:
            cause = self._events_by_id.get(cause_id)
            if cause is None:
                raise KeyError(f"unknown causal event: {cause_id}")
            if cause.time > event.time:
                raise ValueError("an event cannot be caused by a future event")

        self.current_time = max(self.current_time, event.time)
        self._events.append(event)
        self._events_by_id[event.id] = event

        for entity_id in referenced_entities:
            self._events_by_entity[entity_id].append(event.id)
        for cause_id in event.causes:
            self._causal_children[cause_id].append(event.id)

        self.relevance.observe(event)

    def get_event(self, event_id: str) -> Event:
        return self._events_by_id[event_id]

    def history_of(self, entity_id: str) -> tuple[Event, ...]:
        return tuple(self._events_by_id[event_id] for event_id in self._events_by_entity[entity_id])

    def causal_children(self, event_id: str) -> tuple[Event, ...]:
        return tuple(self._events_by_id[event_id] for event_id in self._causal_children[event_id])

    def causal_descendants(self, event_id: str) -> tuple[Event, ...]:
        """Return all downstream events, breadth-first, without duplicates."""

        seen: set[str] = set()
        queue: deque[str] = deque(self._causal_children[event_id])
        result: list[Event] = []

        while queue:
            child_id = queue.popleft()
            if child_id in seen:
                continue
            seen.add(child_id)
            result.append(self._events_by_id[child_id])
            queue.extend(self._causal_children[child_id])
        return tuple(result)

    def histories_of(self, entity_ids: Iterable[str]) -> dict[str, tuple[Event, ...]]:
        return {entity_id: self.history_of(entity_id) for entity_id in entity_ids}

    def resolution_of(self, entity_id: str) -> ResolutionLevel:
        return self.relevance.resolution(entity_id, at_time=self.current_time)
