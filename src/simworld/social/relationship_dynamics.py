from __future__ import annotations

from dataclasses import dataclass
from random import Random

from simworld.social.network import SocialTie


@dataclass(frozen=True, slots=True)
class RelationshipContext:
    interaction_quality: float = 0.0
    shared_stress: float = 0.0
    cooperation: float = 0.0
    betrayal_signal: float = 0.0
    separation_pressure: float = 0.0


@dataclass(frozen=True, slots=True)
class RelationshipOutcome:
    tie: SocialTie
    changed: bool
    separated: bool = False
    reconciled: bool = False


def evolve_tie(tie: SocialTie, *, time: int, context: RelationshipContext, rng: Random) -> RelationshipOutcome:
    if not tie.active_at(time):
        return RelationshipOutcome(tie=tie, changed=False)

    noise = rng.uniform(-0.08, 0.08)
    sentiment_delta = (
        0.18 * context.interaction_quality
        + 0.12 * context.cooperation
        - 0.16 * context.shared_stress
        - 0.30 * context.betrayal_signal
        + noise
    )
    trust_delta = 0.10 * context.cooperation - 0.34 * context.betrayal_signal + rng.uniform(-0.04, 0.04)
    strength_delta = 0.10 * abs(context.interaction_quality) + 0.06 * context.cooperation - 0.12 * context.separation_pressure + rng.uniform(-0.04, 0.04)

    sentiment = max(-1.0, min(1.0, tie.sentiment + sentiment_delta))
    trust = max(0.0, min(1.0, tie.trust + trust_delta))
    strength = max(0.0, min(1.0, tie.strength + strength_delta))

    separation_score = (
        context.separation_pressure
        + max(0.0, -sentiment) * 0.45
        + max(0.0, 0.25 - trust) * 0.7
        + max(0.0, 0.2 - strength) * 0.5
    )
    separable = tie.kind in {"romantic", "intimate", "partner", "friendship"}
    if separable and rng.random() < min(0.9, max(0.0, separation_score * 0.22)):
        ended = SocialTie(
            tie.source_id,
            tie.target_id,
            tie.kind,
            strength,
            tie.started_at,
            ended_at=time,
            sentiment=sentiment,
            trust=trust,
            dependence=tie.dependence,
            visibility=tie.visibility,
        )
        return RelationshipOutcome(tie=ended, changed=True, separated=True)

    updated = SocialTie(
        tie.source_id,
        tie.target_id,
        tie.kind,
        strength,
        tie.started_at,
        ended_at=tie.ended_at,
        sentiment=sentiment,
        trust=trust,
        dependence=max(0.0, min(1.0, tie.dependence + 0.05 * context.cooperation - 0.05 * context.separation_pressure)),
        visibility=tie.visibility,
    )
    changed = updated != tie
    return RelationshipOutcome(tie=updated, changed=changed)


def reconciliation_probability(previous: SocialTie, *, shared_dependants: bool, renewed_contact: float) -> float:
    if previous.ended_at is None:
        return 0.0
    base = 0.04 + 0.16 * max(0.0, previous.sentiment) + 0.12 * previous.trust
    if shared_dependants:
        base += 0.08
    base += 0.20 * max(0.0, min(1.0, renewed_contact))
    return max(0.0, min(0.55, base))
