from __future__ import annotations

from dataclasses import dataclass, field
from math import exp


@dataclass(slots=True)
class Belief:
    proposition: str
    probability: float = 0.5
    confidence: float = 0.0
    last_updated: int = 0
    source_ids: tuple[str, ...] = ()

    def update(self, evidence: float, reliability: float, *, time: int, source_id: str | None = None) -> None:
        """Bounded evidence update without pretending to perform exact Bayes."""
        reliability = max(0.0, min(1.0, reliability))
        evidence = max(0.0, min(1.0, evidence))
        weight = reliability * (0.15 + 0.85 * (1.0 - self.confidence))
        self.probability = max(0.0, min(1.0, self.probability * (1.0 - weight) + evidence * weight))
        self.confidence = max(0.0, min(1.0, self.confidence + reliability * 0.18))
        self.last_updated = time
        if source_id is not None and source_id not in self.source_ids:
            self.source_ids = (*self.source_ids, source_id)


@dataclass(frozen=True, slots=True)
class MemoryTrace:
    time: int
    kind: str
    content: str
    salience: float
    confidence: float
    source_id: str | None = None

    def strength(self, *, at_time: int, half_life: float = 25.0) -> float:
        elapsed = max(0, at_time - self.time)
        return self.salience * self.confidence * exp(-0.6931471805599453 * elapsed / half_life)


@dataclass(slots=True)
class TrustProfile:
    """Trust is actor-to-actor and domain-specific rather than one scalar reputation."""

    values: dict[tuple[str, str], float] = field(default_factory=dict)

    def get(self, other_id: str, domain: str = "general") -> float:
        if (other_id, domain) in self.values:
            return self.values[(other_id, domain)]
        return self.values.get((other_id, "general"), 0.5)

    def set(self, other_id: str, value: float, domain: str = "general") -> None:
        self.values[(other_id, domain)] = max(0.0, min(1.0, float(value)))

    def reinforce(self, other_id: str, accuracy: float, domain: str = "general", rate: float = 0.18) -> float:
        current = self.get(other_id, domain)
        target = max(0.0, min(1.0, accuracy))
        updated = current + rate * (target - current)
        self.set(other_id, updated, domain)
        return updated


@dataclass(slots=True)
class EpistemicState:
    beliefs: dict[str, Belief] = field(default_factory=dict)
    memories: list[MemoryTrace] = field(default_factory=list)
    trust: TrustProfile = field(default_factory=TrustProfile)

    def belief(self, proposition: str) -> Belief:
        return self.beliefs.setdefault(proposition, Belief(proposition=proposition))

    def observe(
        self,
        proposition: str,
        evidence: float,
        *,
        reliability: float,
        time: int,
        source_id: str | None = None,
        salience: float = 0.5,
    ) -> Belief:
        belief = self.belief(proposition)
        belief.update(evidence, reliability, time=time, source_id=source_id)
        self.memories.append(
            MemoryTrace(
                time=time,
                kind="observation",
                content=proposition,
                salience=max(0.0, min(1.0, salience)),
                confidence=max(0.0, min(1.0, reliability)),
                source_id=source_id,
            )
        )
        return belief
