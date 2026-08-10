from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Mapping


@dataclass(frozen=True, slots=True)
class EffectSpec:
    """A generic causal effect exposed by a mastered capability.

    Effects are deliberately channel-based rather than technology-specific.  The
    catalog may say that a capability affects `combat_effectiveness`,
    `record_persistence` or `food_output`; simulation domains decide how those
    generic channels enter their own equations.

    `activation_chance` makes effects opportunities rather than unconditional
    bonuses.  `required_context` allows an effect to matter only where the relevant
    material/social circumstance exists (for example, writing only helps a record
    when somebody actually produces and preserves one).
    """

    channel: str
    operation: str = "multiply"
    magnitude: float = 0.0
    activation_chance: float = 1.0
    required_context: Mapping[str, float] | None = None

    def __post_init__(self) -> None:
        if self.operation not in {"multiply", "add"}:
            raise ValueError("effect operation must be 'multiply' or 'add'")
        if not 0.0 <= self.activation_chance <= 1.0:
            raise ValueError("activation_chance must be in [0, 1]")


def effect_is_applicable(spec: EffectSpec, context: Mapping[str, float]) -> bool:
    for key, minimum in (spec.required_context or {}).items():
        if float(context.get(key, 0.0)) < float(minimum):
            return False
    return True


def apply_effect_specs(
    specs: tuple[EffectSpec, ...],
    *,
    mastery: float,
    base_channels: Mapping[str, float],
    context: Mapping[str, float],
    rng: Random,
) -> dict[str, float]:
    """Apply active effects to generic causal channels.

    Mastery scales effect size.  The same technology can therefore be known poorly
    by one actor and expertly by another.  Effects never fire merely because the
    technology exists somewhere in the world.
    """

    mastery = min(1.0, max(0.0, mastery))
    result = {str(key): float(value) for key, value in base_channels.items()}
    for spec in specs:
        if not effect_is_applicable(spec, context):
            continue
        if rng.random() >= spec.activation_chance:
            continue
        current = result.get(spec.channel, 1.0 if spec.operation == "multiply" else 0.0)
        scaled = spec.magnitude * mastery
        if spec.operation == "multiply":
            result[spec.channel] = current * max(0.0, 1.0 + scaled)
        else:
            result[spec.channel] = current + scaled
    return result
