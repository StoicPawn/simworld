from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


def new_entity_id() -> str:
    return f"ent_{uuid4().hex}"


@dataclass(slots=True)
class Entity:
    """A generic thing that can persist and participate in world history.

    Domain modules will later specialize entities through composition and typed
    components rather than by forcing the kernel to know what a king, river,
    company, religion, or oil field is.
    """

    kind: str
    name: str
    created_at: int = 0
    id: str = field(default_factory=new_entity_id)
    active: bool = True
    attributes: dict[str, Any] = field(default_factory=dict)
    tags: set[str] = field(default_factory=set)

    def deactivate(self) -> None:
        self.active = False
