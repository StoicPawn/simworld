from __future__ import annotations

from dataclasses import dataclass, field
from random import Random


@dataclass(frozen=True, slots=True)
class NarrativeVersion:
    time: int
    teller_id: str
    claims: tuple[str, ...]
    confidence: float
    emotional_valence: float = 0.0
    parent_index: int | None = None


@dataclass(slots=True)
class Narrative:
    id: str
    origin_event_ids: tuple[str, ...]
    versions: list[NarrativeVersion] = field(default_factory=list)

    def latest(self) -> NarrativeVersion:
        if not self.versions:
            raise ValueError("narrative has no versions")
        return self.versions[-1]


@dataclass(slots=True)
class SocialMemory:
    narratives: dict[str, Narrative] = field(default_factory=dict)
    held_by: dict[str, set[str]] = field(default_factory=dict)

    def add(self, narrative: Narrative, holder_id: str) -> None:
        self.narratives[narrative.id] = narrative
        self.held_by.setdefault(holder_id, set()).add(narrative.id)

    def transmit(
        self,
        narrative_id: str,
        *,
        teller_id: str,
        receiver_id: str,
        trust: float,
        time: int,
        rng: Random,
        mutation_rate: float = 0.08,
    ) -> NarrativeVersion | None:
        """Transmit a story with trust-weighted acceptance and possible drift."""
        narrative = self.narratives[narrative_id]
        if rng.random() > max(0.02, min(0.98, trust)):
            return None
        parent = narrative.latest()
        claims = list(parent.claims)
        if claims and rng.random() < mutation_rate:
            index = rng.randrange(len(claims))
            claim = claims[index]
            if rng.random() < 0.5:
                claims[index] = f"remembered-as-certain: {claim}"
            else:
                claims[index] = f"some-say: {claim}"
        version = NarrativeVersion(
            time=time,
            teller_id=teller_id,
            claims=tuple(claims),
            confidence=max(0.05, min(1.0, parent.confidence * (0.82 + 0.28 * trust))),
            emotional_valence=max(-1.0, min(1.0, parent.emotional_valence + rng.uniform(-0.08, 0.08))),
            parent_index=len(narrative.versions) - 1,
        )
        narrative.versions.append(version)
        self.held_by.setdefault(receiver_id, set()).add(narrative_id)
        return version

    def culture_signal(self, holder_ids: tuple[str, ...], phrase: str) -> float:
        """Derived prevalence of a claim; culture is measured, not assigned."""
        if not holder_ids:
            return 0.0
        matches = 0
        for holder_id in holder_ids:
            ids = self.held_by.get(holder_id, set())
            if any(any(phrase in claim for claim in self.narratives[nid].latest().claims) for nid in ids):
                matches += 1
        return matches / len(holder_ids)
