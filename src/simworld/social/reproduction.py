from __future__ import annotations

from dataclasses import dataclass
from math import exp
from random import Random


@dataclass(frozen=True, slots=True)
class ReproductiveProfile:
    person_id: str
    birth_time: int
    gestational: bool
    fertility: float = 1.0
    health: float = 1.0

    def age(self, time: int) -> int:
        return max(0, time - self.birth_time)


def age_fertility_factor(age: int, gestational: bool) -> float:
    """Broad demographic prior, deliberately smooth rather than a hard reproductive switch."""
    if age < 14 or age > 60:
        return 0.0
    if gestational:
        if age <= 24:
            return max(0.0, (age - 13) / 11)
        if age <= 32:
            return 1.0
        if age <= 45:
            return max(0.02, 1.0 - (age - 32) / 14)
        return max(0.0, 0.08 - (age - 45) * 0.01)
    if age <= 25:
        return max(0.0, (age - 13) / 12)
    if age <= 45:
        return 1.0
    return max(0.1, exp(-(age - 45) / 22.0))


def conception_probability(
    gestational: ReproductiveProfile,
    other: ReproductiveProfile,
    *,
    time: int,
    contact_intensity: float,
    resource_security: float = 0.5,
    reproductive_intent: float = 0.5,
    contraception_effect: float = 0.0,
) -> float:
    """Return a bounded annualized opportunity probability, not a guaranteed consequence."""
    if not gestational.gestational or other.gestational:
        return 0.0
    gf = age_fertility_factor(gestational.age(time), True)
    of = age_fertility_factor(other.age(time), False)
    biological = gf * of * gestational.fertility * other.fertility * gestational.health * other.health
    behavioural = max(0.0, min(1.0, contact_intensity))
    intent_factor = 0.45 + 0.75 * max(0.0, min(1.0, reproductive_intent))
    resource_factor = 0.75 + 0.35 * max(0.0, min(1.0, resource_security))
    prevention = 1.0 - max(0.0, min(0.995, contraception_effect))
    return max(0.0, min(0.95, 0.32 * biological * behavioural * intent_factor * resource_factor * prevention))


def conception_occurs(probability: float, rng: Random) -> bool:
    return rng.random() < max(0.0, min(1.0, probability))
