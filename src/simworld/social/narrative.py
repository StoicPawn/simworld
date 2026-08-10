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


@dataclass(frozen=True, slots=True)
class NarrativeRecord:
    """A materialized record of one narrative version.

    A record preserves information; it does not certify truth.  Credibility is only
    a social signal and may increase belief in a false claim.
    """

    id: str
    narrative_id: str
    version_index: int
    author_id: str
    created_at: int
    durability: float
    credibility_signal: float


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
    held_by: dict[str, set[str]] = field(default_factory=dict)
    held_versions: dict[str, dict[str, int]] = field(default_factory=dict)
    records: dict[str, NarrativeRecord] = field(default_factory=dict)

    def add(self, narrative: Narrative, holder_id: str, *, version_index: int = 0) -> None:
        if not narrative.versions:
            raise ValueError("narrative must contain at least one version")
        if not 0 <= version_index < len(narrative.versions):
            raise IndexError("invalid narrative version index")
        self.narratives[narrative.id] = narrative
        self.held_by.setdefault(holder_id, set()).add(narrative.id)
        self.held_versions.setdefault(holder_id, {})[narrative.id] = version_index

    def hold_version(self, holder_id: str, narrative_id: str, version_index: int) -> None:
        narrative = self.narratives[narrative_id]
        if not 0 <= version_index < len(narrative.versions):
            raise IndexError("invalid narrative version index")
        self.held_by.setdefault(holder_id, set()).add(narrative_id)
        self.held_versions.setdefault(holder_id, {})[narrative_id] = version_index

    def version_for(self, holder_id: str, narrative_id: str) -> NarrativeVersion:
        narrative = self.narratives[narrative_id]
        index = self.held_versions.get(holder_id, {}).get(narrative_id, len(narrative.versions) - 1)
        return narrative.versions[index]

    def create_record(
        self,
        narrative_id: str,
        *,
        holder_id: str,
        record_id: str,
        time: int,
        record_creation: float,
        durability: float,
        credibility_signal: float,
    ) -> NarrativeRecord | None:
        """Create a record only if some external capability makes recording possible."""

        if record_creation <= 0.0:
            return None
        narrative = self.narratives[narrative_id]
        version_index = self.held_versions.get(holder_id, {}).get(
            narrative_id, len(narrative.versions) - 1
        )
        record = NarrativeRecord(
            id=record_id,
            narrative_id=narrative_id,
            version_index=version_index,
            author_id=holder_id,
            created_at=time,
            durability=max(0.0, durability),
            credibility_signal=max(0.0, credibility_signal),
        )
        self.records[record_id] = record
        return record

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
        record_id: str | None = None,
        transmission_fidelity: float = 1.0,
        credibility_multiplier: float = 1.0,
    ) -> NarrativeVersion | None:
        """Transmit a branch orally or through a durable record.

        Records can reduce mutation and raise perceived confidence, but they never
        change the event truth or guarantee acceptance.
        """

        narrative = self.narratives[narrative_id]
        record = None if record_id is None else self.records.get(record_id)
        if record is not None and record.narrative_id != narrative_id:
            raise ValueError("record belongs to a different narrative")

        if record is None:
            parent_index = self.held_versions.get(teller_id, {}).get(
                narrative_id, len(narrative.versions) - 1
            )
        else:
            parent_index = record.version_index
        parent = narrative.versions[parent_index]

        acceptance = max(0.02, min(0.98, trust))
        if record is not None:
            acceptance = min(
                0.98,
                max(
                    0.02,
                    acceptance
                    * max(0.1, credibility_multiplier)
                    * max(0.25, record.credibility_signal),
                ),
            )
        if rng.random() > acceptance:
            return None

        claims = list(parent.claims)
        effective_mutation = mutation_rate / max(0.25, transmission_fidelity)
        if record is not None:
            effective_mutation /= max(1.0, 1.0 + record.durability)
        if claims and rng.random() < effective_mutation:
            index = rng.randrange(len(claims))
            claim = claims[index]
            if rng.random() < 0.5:
                claims[index] = f"remembered-as-certain: {claim}"
            else:
                claims[index] = f"some-say: {claim}"

        confidence_factor = 0.82 + 0.28 * trust
        if record is not None:
            confidence_factor *= max(0.5, credibility_multiplier)
        version = NarrativeVersion(
            time=time,
            teller_id=teller_id,
            claims=tuple(claims),
            confidence=max(0.05, min(1.0, parent.confidence * confidence_factor)),
            emotional_valence=max(
                -1.0, min(1.0, parent.emotional_valence + rng.uniform(-0.08, 0.08))
            ),
            parent_index=parent_index,
        )
        narrative.versions.append(version)
        self.held_by.setdefault(receiver_id, set()).add(narrative_id)
        self.held_versions.setdefault(receiver_id, {})[narrative_id] = len(narrative.versions) - 1
        return version

    def culture_signal(self, holder_ids: tuple[str, ...], phrase: str) -> float:
        """Derived prevalence of a claim over holder-specific narrative branches."""
        if not holder_ids:
            return 0.0
        matches = 0
        for holder_id in holder_ids:
            ids = self.held_by.get(holder_id, set())
            if any(
                any(phrase in claim for claim in self.version_for(holder_id, nid).claims)
                for nid in ids
            ):
                matches += 1
        return matches / len(holder_ids)
