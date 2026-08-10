from __future__ import annotations

from dataclasses import dataclass, field
from random import Random

from simworld.culture.effects import EffectSpec


@dataclass(frozen=True, slots=True)
class Affordance:
    """A data-defined technical possibility, not a historical tech-tree node.

    Requirements describe what must already be physically/cognitively available for
    experimentation to have a meaningful chance. They do not prescribe discovery.

    `effects` exposes generic causal channels.  It never means a capability grants a
    global civilization bonus: only an actor/group that actually knows and applies
    the capability can make those channels available to the relevant process.
    """

    id: str
    required_materials: frozenset[str] = frozenset()
    required_capabilities: dict[str, float] = field(default_factory=dict)
    min_environment: dict[str, float] = field(default_factory=dict)
    complexity: float = 0.5
    observability: float = 0.5
    effects: tuple[EffectSpec, ...] = ()

    def __post_init__(self) -> None:
        if not 0.0 <= self.complexity <= 1.0:
            raise ValueError("complexity must be in [0, 1]")
        if not 0.0 <= self.observability <= 1.0:
            raise ValueError("observability must be in [0, 1]")


@dataclass(frozen=True, slots=True)
class InnovationContext:
    materials: frozenset[str]
    capabilities: dict[str, float]
    environment: dict[str, float]
    experience: float
    experimentation: float
    population_contact: float = 0.0
    problem_pressure: float = 0.0


def requirements_met(affordance: Affordance, context: InnovationContext) -> bool:
    if not affordance.required_materials.issubset(context.materials):
        return False
    for capability, minimum in affordance.required_capabilities.items():
        if context.capabilities.get(capability, 0.0) < minimum:
            return False
    for variable, minimum in affordance.min_environment.items():
        if context.environment.get(variable, 0.0) < minimum:
            return False
    return True


def innovation_probability(affordance: Affordance, context: InnovationContext) -> float:
    """Return a bounded opportunity rate when prerequisites are actually present.

    No positive floor is imposed when requirements fail. Even when they pass, the
    probability can remain tiny; a technically possible world need not discover the
    capability during the simulated horizon.
    """

    if not requirements_met(affordance, context):
        return 0.0
    experience = min(1.0, max(0.0, context.experience))
    experimentation = min(1.0, max(0.0, context.experimentation))
    contact = min(1.0, max(0.0, context.population_contact))
    pressure = min(1.0, max(0.0, context.problem_pressure))

    opportunity = (
        0.004
        + 0.055 * experience
        + 0.090 * experimentation
        + 0.025 * contact
        + 0.020 * pressure
        + 0.025 * affordance.observability
    )
    difficulty = 0.18 + 0.82 * affordance.complexity
    return min(0.35, max(0.0, opportunity * (1.0 - 0.82 * difficulty)))


def innovation_occurs(affordance: Affordance, context: InnovationContext, rng: Random) -> bool:
    return rng.random() < innovation_probability(affordance, context)
