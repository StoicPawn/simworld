from __future__ import annotations

from dataclasses import dataclass, field
from random import Random


@dataclass(slots=True)
class Household:
    id: str
    settlement_id: str
    members: set[str] = field(default_factory=set)
    co_resident_since: dict[str, int] = field(default_factory=dict)
    food_stock: float = 0.0
    wealth: float = 0.0
    debt: float = 0.0
    land: float = 0.0
    tools: float = 0.0

    def add_member(self, person_id: str, time: int) -> None:
        self.members.add(person_id)
        self.co_resident_since.setdefault(person_id, time)

    def remove_member(self, person_id: str) -> None:
        self.members.discard(person_id)

    @property
    def net_wealth(self) -> float:
        return self.wealth + self.tools + self.land - self.debt


@dataclass(frozen=True, slots=True)
class Pregnancy:
    gestational_parent_id: str
    other_parent_id: str
    conceived_at: int
    due_at: int
    viability: float

    def due(self, time: int) -> bool:
        return time >= self.due_at


def pregnancy_survives(pregnancy: Pregnancy, health: float, food_security: float, rng: Random) -> bool:
    probability = pregnancy.viability * (0.72 + 0.18 * health + 0.10 * food_security)
    return rng.random() < max(0.05, min(0.995, probability))


def allocate_inheritance(
    estate: float,
    heirs: tuple[str, ...],
    *,
    custom_weights: dict[str, float] | None = None,
) -> dict[str, float]:
    """Allocate an estate without assuming one universal inheritance rule.

    The caller may later supply culturally/institutionally learned weights. Equal division
    is merely the neutral fallback, not a historical law.
    """
    if estate <= 0.0 or not heirs:
        return {}
    if custom_weights is None:
        share = estate / len(heirs)
        return {heir: share for heir in heirs}
    weights = {heir: max(0.0, custom_weights.get(heir, 0.0)) for heir in heirs}
    total = sum(weights.values())
    if total <= 0.0:
        share = estate / len(heirs)
        return {heir: share for heir in heirs}
    return {heir: estate * weight / total for heir, weight in weights.items()}
