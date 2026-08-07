from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from math import exp

from simworld.core.event import Event


class ResolutionLevel(IntEnum):
    """How much detail the simulator should currently spend on an entity."""

    AGGREGATE = 0
    DETAILED = 1
    FOCUS = 2


@dataclass(slots=True)
class AttentionRecord:
    score: float = 0.0
    last_updated: int = 0


class RelevanceIndex:
    """Tracks historical attention without turning attention into causation.

    Relevance helps decide simulation resolution and later narrative extraction.
    It is deliberately decayed: importance is dynamic, so regions and entities
    can rise, fade, and return.
    """

    def __init__(
        self,
        *,
        half_life: float = 50.0,
        detailed_threshold: float = 3.0,
        focus_threshold: float = 10.0,
    ) -> None:
        if half_life <= 0:
            raise ValueError("half_life must be positive")
        self.half_life = half_life
        self.detailed_threshold = detailed_threshold
        self.focus_threshold = focus_threshold
        self._records: dict[str, AttentionRecord] = {}

    def _decay_factor(self, elapsed: int) -> float:
        if elapsed <= 0:
            return 1.0
        return exp(-0.6931471805599453 * elapsed / self.half_life)

    def score(self, entity_id: str, *, at_time: int) -> float:
        record = self._records.get(entity_id)
        if record is None:
            return 0.0
        return record.score * self._decay_factor(at_time - record.last_updated)

    def add_signal(self, entity_id: str, *, amount: float, at_time: int) -> None:
        current = self.score(entity_id, at_time=at_time)
        self._records[entity_id] = AttentionRecord(
            score=current + max(0.0, amount),
            last_updated=at_time,
        )

    def observe(self, event: Event) -> None:
        # Participation matters more than merely being the location of an event.
        for entity_id in event.participants:
            self.add_signal(entity_id, amount=event.impact, at_time=event.time)
        for entity_id in event.locations:
            self.add_signal(entity_id, amount=event.impact * 0.5, at_time=event.time)

    def resolution(self, entity_id: str, *, at_time: int) -> ResolutionLevel:
        value = self.score(entity_id, at_time=at_time)
        if value >= self.focus_threshold:
            return ResolutionLevel.FOCUS
        if value >= self.detailed_threshold:
            return ResolutionLevel.DETAILED
        return ResolutionLevel.AGGREGATE
