from __future__ import annotations

from dataclasses import dataclass, field
from random import Random


@dataclass(frozen=True, slots=True)
class KnowledgeUnit:
    """A transmissible unit of know-how, convention, claim or practice.

    It deliberately does not say whether the unit is 'technology', 'language',
    'religion' or 'culture'. Higher-level interpretations are derived later.
    """

    id: str
    domain: str
    complexity: float = 0.5
    demonstrability: float = 0.5
    mutation_rate: float = 0.02

    def __post_init__(self) -> None:
        for name, value in (
            ("complexity", self.complexity),
            ("demonstrability", self.demonstrability),
            ("mutation_rate", self.mutation_rate),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0, 1]")


@dataclass(slots=True)
class KnowledgeState:
    unit_id: str
    mastery: float
    confidence: float
    acquired_at: int
    source_id: str | None = None
    generation: int = 0

    def clamp(self) -> None:
        self.mastery = min(1.0, max(0.0, self.mastery))
        self.confidence = min(1.0, max(0.0, self.confidence))


@dataclass(slots=True)
class KnowledgeLedger:
    """Sparse actor-specific knowledge state."""

    by_actor: dict[str, dict[str, KnowledgeState]] = field(default_factory=dict)

    def get(self, actor_id: str, unit_id: str) -> KnowledgeState | None:
        return self.by_actor.get(actor_id, {}).get(unit_id)

    def set(self, actor_id: str, state: KnowledgeState) -> None:
        state.clamp()
        self.by_actor.setdefault(actor_id, {})[state.unit_id] = state

    def forget(self, actor_id: str, unit_id: str) -> None:
        units = self.by_actor.get(actor_id)
        if units is None:
            return
        units.pop(unit_id, None)
        if not units:
            self.by_actor.pop(actor_id, None)

    def mastery(self, actor_id: str, unit_id: str) -> float:
        state = self.get(actor_id, unit_id)
        return 0.0 if state is None else state.mastery

    def known_units(self, actor_id: str, threshold: float = 0.05) -> tuple[str, ...]:
        return tuple(
            sorted(
                unit_id
                for unit_id, state in self.by_actor.get(actor_id, {}).items()
                if state.mastery >= threshold
            )
        )


def transmit_knowledge(
    unit: KnowledgeUnit,
    source: KnowledgeState,
    *,
    receiver_prior: KnowledgeState | None,
    source_trust: float,
    communication_fit: float,
    exposure: float,
    time: int,
    source_id: str,
    rng: Random,
) -> KnowledgeState | None:
    """Attempt imperfect cultural transmission.

    Transmission is neither guaranteed nor exact. Complexity resists transfer;
    demonstrability, trust, communication compatibility and repeated exposure help.
    A receiver can partially learn, misunderstand, or fail to acquire the unit.
    """

    source_trust = min(1.0, max(0.0, source_trust))
    communication_fit = min(1.0, max(0.0, communication_fit))
    exposure = min(1.0, max(0.0, exposure))

    success = (
        0.12
        + 0.28 * source.mastery
        + 0.20 * unit.demonstrability
        + 0.18 * source_trust
        + 0.17 * communication_fit
        + 0.15 * exposure
        - 0.30 * unit.complexity
    )
    success = min(0.98, max(0.01, success))
    if rng.random() >= success:
        return None

    prior_mastery = 0.0 if receiver_prior is None else receiver_prior.mastery
    prior_confidence = 0.0 if receiver_prior is None else receiver_prior.confidence
    learning_gain = (
        (0.10 + 0.42 * source.mastery)
        * (0.35 + 0.65 * exposure)
        * (0.45 + 0.55 * communication_fit)
        * (1.0 - 0.55 * unit.complexity)
    )
    noise = rng.uniform(-0.08, 0.08) * (0.4 + unit.complexity)
    mastery = min(1.0, max(0.01, prior_mastery + learning_gain + noise))
    confidence = min(
        1.0,
        max(
            0.02,
            0.45 * prior_confidence
            + 0.25 * source.confidence
            + 0.18 * source_trust
            + 0.12 * exposure
            + rng.uniform(-0.05, 0.05),
        ),
    )
    generation = 0 if receiver_prior is None else receiver_prior.generation
    return KnowledgeState(
        unit_id=unit.id,
        mastery=mastery,
        confidence=confidence,
        acquired_at=time,
        source_id=source_id,
        generation=generation + 1,
    )


def decay_knowledge(
    unit: KnowledgeUnit,
    state: KnowledgeState,
    *,
    practice: float,
    social_reinforcement: float,
    record_support: float,
    elapsed: float = 1.0,
) -> KnowledgeState | None:
    """Decay unused knowledge without imposing inevitable loss.

    Practice, repeated social reinforcement and external records preserve knowledge.
    If mastery falls below a tiny threshold the detailed actor no longer carries the
    unit. This allows locally discovered techniques to disappear historically.
    """

    practice = min(1.0, max(0.0, practice))
    social_reinforcement = min(1.0, max(0.0, social_reinforcement))
    record_support = min(1.0, max(0.0, record_support))
    elapsed = max(0.0, elapsed)
    retention = 0.50 * practice + 0.30 * social_reinforcement + 0.20 * record_support
    base_decay = 0.035 + 0.055 * unit.complexity
    decay = base_decay * (1.0 - 0.86 * retention) * elapsed
    mastery = max(0.0, state.mastery - decay)
    confidence = max(0.0, state.confidence - 0.65 * decay)
    if mastery < 0.015:
        return None
    return KnowledgeState(
        unit_id=state.unit_id,
        mastery=mastery,
        confidence=confidence,
        acquired_at=state.acquired_at,
        source_id=state.source_id,
        generation=state.generation,
    )
