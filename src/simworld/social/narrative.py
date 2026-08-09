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

    def version(self, index: int) -> NarrativeVersion:
        return self.versions[index]


@dataclass(slots=True)
class SocialMemory:
    """Branching social memory: different holders may carry different story versions."""

    narratives: dict[str, Narrative] = field(default_factory=dict)
    held_versions: dict[str, dict[str, int]] = field(default_factory=dict)

    @property
    def held_by(self) -> dict[str, set[str]]:
        return {holder: set(versions) for holder, versions in self.held_versions.items()}

    def add(self, narrative: Narrative, holder_id: str, *, version_index: int = 0) -> None:
        if not narrative.versions:
            raise ValueError("narrative must contain at least one version")
        if not 0 <= version_index < len(narrative.versions):
            raise IndexError("invalid narrative version index")
        self.narratives[narrative.id] = narrative
        self.held_versions.setdefault(holder_id, {})[narrative.id] = version_index

    def hold_version(self, holder_id: str, narrative_id: str, version_index: int) -> None:
        narrative = self.narratives[narrative_id]
        if not 0 <= version_index < len(narrative.versions):
            raise IndexError("invalid narrative version index")
        self.held_versions.setdefault(holder_id, {})[narrative_id] = version_index

    def version_for(self, holder_id: str, narrative_id: str) -> NarrativeVersion:
        index = self.held_versions[holder_id][narrative_id]
        return self.narratives[narrative_id].versions[index]

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
        """Transmit the teller's branch with trust-weighted acceptance and drift."""
        narrative = self.narratives[narrative_id]
        parent_index = self.held_versions[teller_id][narrative_id]
        parent = narrative.versions[parent_index]
        if rng.random() > max(0.02, min(0.98, trust)):
            return None
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
            parent_index=parent_index,
        )
        narrative.versions.append(version)
        self.held_versions.setdefault(receiver_id, {})[narrative_id] = len(narrative.versions) - 1
        return version

    def culture_signal(self, holder_ids: tuple[str, ...], phrase: str) -> float:
        """Derived prevalence of a claim over holder-specific narrative branches."""
        if not holder_ids:
            return 0.0
        matches = 0
        for holder_id in holder_ids:
            versions = self.held_versions.get(holder_id, {})
            if any(
                any(phrase in claim for claim in self.narratives[nid].versions[index].claims)
                for nid, index in versions.items()
            ):
                matches += 1
        return matches / len(holder_ids)
