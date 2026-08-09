from __future__ import annotations

from dataclasses import dataclass
from random import Random


@dataclass(frozen=True, slots=True)
class ConflictContext:
    actor_a: str
    actor_b: str
    resource_overlap: float
    territorial_friction: float
    rivalry: float
    fear: float
    grievance: float
    opportunity: float
    interdependence: float
    kinship_inhibition: float
    geographic_access: float


@dataclass(frozen=True, slots=True)
class ConflictDecision:
    action: str
    pressure: float
    probability: float


def conflict_pressure(context: ConflictContext) -> float:
    """Return pressure toward coercive interaction, never a scripted war trigger."""
    positive = (
        0.18 * context.resource_overlap
        + 0.20 * context.territorial_friction
        + 0.18 * context.rivalry
        + 0.16 * context.fear
        + 0.14 * context.grievance
        + 0.14 * context.opportunity
    )
    inhibition = 0.22 * context.interdependence + 0.12 * context.kinship_inhibition
    access = 0.15 + 0.85 * context.geographic_access
    return max(0.0, min(1.5, (positive - inhibition) * access))


def choose_conflict_action(context: ConflictContext, rng: Random) -> ConflictDecision:
    """Bounded stochastic escalation.

    Even high pressure may yield bargaining or restraint; low pressure may occasionally
    yield a raid or threat because actors are fallible. There is deliberately no
    `pressure > threshold -> war` rule.
    """
    pressure = conflict_pressure(context)
    weights = {
        "avoid": max(0.05, 1.15 - pressure),
        "negotiate": 0.35 + 0.55 * context.interdependence + 0.2 * context.kinship_inhibition,
        "threaten": 0.10 + 0.75 * pressure,
        "raid": 0.02 + 0.38 * pressure * context.opportunity,
        "attack": 0.005 + 0.23 * pressure * context.opportunity * context.geographic_access,
    }
    total = sum(weights.values())
    draw = rng.random() * total
    cumulative = 0.0
    for action, weight in weights.items():
        cumulative += weight
        if draw <= cumulative:
            return ConflictDecision(action, pressure, weight / total)
    return ConflictDecision("avoid", pressure, weights["avoid"] / total)
