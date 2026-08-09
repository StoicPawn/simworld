from __future__ import annotations

from dataclasses import dataclass
from math import exp
from random import Random
from typing import Mapping

from simworld.relations.matrix import ActorRelationProfile, RelationMatrix


@dataclass(frozen=True, slots=True)
class InteractionOption:
    """Low-level feasible act, not a macro historical category."""

    name: str
    cooperation_weight: float = 0.0
    incompatibility_weight: float = 0.0
    trust_weight: float = 0.0
    dependence_weight: float = 0.0
    capability_domain: str | None = None
    capability_weight: float = 0.0
    uncertainty_weight: float = 0.0
    cost: float = 0.0
    base_bias: float = 0.0


@dataclass(frozen=True, slots=True)
class Interaction:
    time: int
    actor_a: str
    actor_b: str
    action: str
    domain: str
    intensity: float
    perceived_payoff_a: float = 0.0
    perceived_payoff_b: float = 0.0
    physical_harm: float = 0.0
    resource_transfer: float = 0.0
    coordination: float = 0.0
    coercion: float = 0.0


def _mean(values: Mapping[str, float]) -> float:
    return sum(values.values()) / len(values) if values else 0.5


def interaction_score(
    option: InteractionOption,
    matrix: RelationMatrix,
    profile: ActorRelationProfile,
) -> float:
    trust = _mean(matrix.trust)
    dependence = _mean(matrix.dependence)
    capability = (
        profile.capability(option.capability_domain)
        if option.capability_domain is not None
        else 0.0
    )
    return (
        option.base_bias
        + option.cooperation_weight * matrix.aggregate_compatibility
        + option.incompatibility_weight * matrix.aggregate_incompatibility
        + option.trust_weight * trust
        + option.dependence_weight * dependence
        + option.capability_weight * capability
        + option.uncertainty_weight * matrix.uncertainty
        - option.cost
    )


def choose_interaction(
    options: tuple[InteractionOption, ...],
    matrix: RelationMatrix,
    profile: ActorRelationProfile,
    rng: Random,
    *,
    temperature: float = 0.45,
) -> InteractionOption:
    """Bounded stochastic selection among primitive acts.

    This is deliberately not a war/peace decision. The action menu contains elementary
    interactions; persistent macro patterns are inferred later from event history.
    """

    if not options:
        raise ValueError("at least one interaction option is required")
    t = max(0.05, temperature)
    scores = [interaction_score(option, matrix, profile) for option in options]
    high = max(scores)
    weights = [exp((score - high) / t) for score in scores]
    draw = rng.random() * sum(weights)
    cumulative = 0.0
    for option, weight in zip(options, weights, strict=True):
        cumulative += weight
        if draw <= cumulative:
            return option
    return options[-1]


PRIMITIVE_OPTIONS: tuple[InteractionOption, ...] = (
    InteractionOption(
        "communicate",
        cooperation_weight=0.2,
        trust_weight=0.35,
        uncertainty_weight=0.25,
        cost=0.03,
    ),
    InteractionOption(
        "negotiate",
        cooperation_weight=0.35,
        incompatibility_weight=0.2,
        trust_weight=0.35,
        dependence_weight=0.25,
        cost=0.08,
    ),
    InteractionOption(
        "exchange",
        cooperation_weight=0.45,
        trust_weight=0.25,
        dependence_weight=0.45,
        capability_domain="economic",
        capability_weight=0.15,
        cost=0.08,
    ),
    InteractionOption(
        "coordinate",
        cooperation_weight=0.6,
        trust_weight=0.4,
        dependence_weight=0.25,
        capability_domain="organizational",
        capability_weight=0.15,
        cost=0.1,
    ),
    InteractionOption(
        "withhold",
        incompatibility_weight=0.15,
        trust_weight=-0.25,
        uncertainty_weight=0.15,
        cost=0.03,
    ),
    InteractionOption(
        "threaten",
        incompatibility_weight=0.55,
        trust_weight=-0.35,
        capability_domain="coercive",
        capability_weight=0.35,
        cost=0.08,
    ),
    InteractionOption(
        "obstruct",
        incompatibility_weight=0.5,
        trust_weight=-0.25,
        capability_domain="organizational",
        capability_weight=0.2,
        cost=0.12,
    ),
    InteractionOption(
        "seize",
        incompatibility_weight=0.7,
        trust_weight=-0.35,
        capability_domain="coercive",
        capability_weight=0.45,
        cost=0.28,
    ),
    InteractionOption(
        "attack",
        incompatibility_weight=0.85,
        trust_weight=-0.45,
        capability_domain="coercive",
        capability_weight=0.55,
        cost=0.4,
    ),
    InteractionOption("avoid", uncertainty_weight=0.2, cost=0.0, base_bias=0.03),
)
