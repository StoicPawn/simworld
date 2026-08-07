from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping
from uuid import uuid4


def new_event_id() -> str:
    return f"evt_{uuid4().hex}"


@dataclass(frozen=True, slots=True)
class Event:
    """Immutable fact recorded by the simulation.

    Several events may share the same `time`. Ordering inside that timestamp is
    represented by append/scheduler order, not by pretending the world has a
    single narrative event at each moment.
    """

    kind: str
    time: int
    participants: tuple[str, ...] = ()
    locations: tuple[str, ...] = ()
    causes: tuple[str, ...] = ()
    impact: float = 1.0
    payload: Mapping[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=new_event_id)

    def __post_init__(self) -> None:
        if self.time < 0:
            raise ValueError("event time cannot be negative")
        if self.impact < 0:
            raise ValueError("event impact cannot be negative")
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))
