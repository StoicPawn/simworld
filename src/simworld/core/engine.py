from __future__ import annotations

import heapq
import random
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Any

from simworld.core.event import Event
from simworld.core.world import WorldState

EventFactory = Callable[[WorldState, random.Random], Event | Iterable[Event] | None]


@dataclass(order=True, slots=True)
class ScheduledAction:
    time: int
    sequence: int
    factory: EventFactory = field(compare=False)
    label: str | None = field(default=None, compare=False)


class SimulationEngine:
    """Deterministic event-driven scheduler.

    Multiple actions can be scheduled for the same time. The sequence number only
    guarantees reproducibility; it does not imply that history contains one main
    event at a time.
    """

    def __init__(self, world: WorldState | None = None, *, seed: int = 0) -> None:
        self.world = world or WorldState()
        self.seed = seed
        self.rng = random.Random(seed)
        self._queue: list[ScheduledAction] = []
        self._sequence = 0

    def schedule(self, time: int, factory: EventFactory, *, label: str | None = None) -> None:
        if time < self.world.current_time:
            raise ValueError("cannot schedule an action in the simulated past")
        heapq.heappush(
            self._queue,
            ScheduledAction(time=time, sequence=self._sequence, factory=factory, label=label),
        )
        self._sequence += 1

    def pending(self) -> int:
        return len(self._queue)

    def run_until(self, end_time: int) -> tuple[Event, ...]:
        if end_time < self.world.current_time:
            raise ValueError("end_time cannot be earlier than current world time")

        emitted: list[Event] = []
        while self._queue and self._queue[0].time <= end_time:
            action = heapq.heappop(self._queue)
            self.world.current_time = max(self.world.current_time, action.time)
            produced = action.factory(self.world, self.rng)
            if produced is None:
                continue
            events = (produced,) if isinstance(produced, Event) else tuple(produced)
            for event in events:
                if event.time != action.time:
                    raise ValueError("scheduled factories must emit events at their scheduled time")
                self.world.record_event(event)
                emitted.append(event)

        self.world.current_time = max(self.world.current_time, end_time)
        return tuple(emitted)

    def snapshot(self) -> dict[str, Any]:
        return {
            "seed": self.seed,
            "time": self.world.current_time,
            "entities": len(self.world.entities),
            "events": len(self.world.events),
            "pending_actions": len(self._queue),
        }
