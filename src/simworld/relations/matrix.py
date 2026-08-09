from __future__ import annotations

from dataclasses import dataclass, field
from math import fsum
from typing import Mapping


def _clip(value: float, low: float = -1.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


@dataclass(frozen=True, slots=True)
class Interest:
    """An actor's directional preference in one domain.

    `target` is intentionally generic: land, status, safety, food, access, office,
    information, doctrine, affection, prestige, debt relief, etc.
    Direction is in [-1, 1], importance in [0, 1].
    """

    domain: str
    target: str
    direction: float
    importance: float
    confidence: float = 1.0

    def __post_init__(self) -> None:
        if not -1.0 <= self.direction <= 1.0:
            raise ValueError("interest direction must be in [-1, 1]")
        if not 0.0 <= self.importance <= 1.0:
            raise ValueError("interest importance must be in [0, 1]")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("interest confidence must be in [0, 1]")


@dataclass(frozen=True, slots=True)
class Claim:
    """A perceived entitlement or asserted control over a target.

    Claims are actor-side social facts, not necessarily objective truth. Two actors can
    hold overlapping claims with different confidence, salience and willingness to act.
    """

    domain: str
    target: str
    strength: float
    salience: float
    confidence: float = 1.0

    def __post_init__(self) -> None:
        for value, label in (
            (self.strength, "strength"),
            (self.salience, "salience"),
            (self.confidence, "confidence"),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"claim {label} must be in [0, 1]")


@dataclass(slots=True)
class ActorRelationProfile:
    actor_id: str
    interests: list[Interest] = field(default_factory=list)
    claims: list[Claim] = field(default_factory=list)
    capabilities: dict[str, float] = field(default_factory=dict)
    constraints: dict[str, float] = field(default_factory=dict)

    def capability(self, domain: str) -> float:
        return max(0.0, min(1.0, self.capabilities.get(domain, 0.0)))


@dataclass(frozen=True, slots=True)
class RelationPressure:
    domain: str
    target: str
    incompatibility: float
    compatibility: float
    salience: float


@dataclass(frozen=True, slots=True)
class RelationMatrix:
    actor_a: str
    actor_b: str
    pressures: tuple[RelationPressure, ...]
    trust: Mapping[str, float]
    dependence: Mapping[str, float]
    contact: float
    uncertainty: float

    @property
    def aggregate_incompatibility(self) -> float:
        weighted = [p.incompatibility * p.salience for p in self.pressures]
        weights = [p.salience for p in self.pressures]
        return fsum(weighted) / fsum(weights) if weights and fsum(weights) > 0 else 0.0

    @property
    def aggregate_compatibility(self) -> float:
        weighted = [p.compatibility * p.salience for p in self.pressures]
        weights = [p.salience for p in self.pressures]
        return fsum(weighted) / fsum(weights) if weights and fsum(weights) > 0 else 0.0


def build_relation_matrix(
    a: ActorRelationProfile,
    b: ActorRelationProfile,
    *,
    trust: Mapping[str, float] | None = None,
    dependence: Mapping[str, float] | None = None,
    contact: float = 0.0,
    uncertainty: float = 0.5,
) -> RelationMatrix:
    """Derive relational pressures from primitive preferences and overlapping claims.

    The result is descriptive state. It never prescribes negotiation, violence, alliance
    or any other response.
    """

    pressures: list[RelationPressure] = []
    interests_a = {(i.domain, i.target): i for i in a.interests}
    interests_b = {(i.domain, i.target): i for i in b.interests}
    keys = interests_a.keys() | interests_b.keys()
    for key in sorted(keys):
        ia, ib = interests_a.get(key), interests_b.get(key)
        da = ia.direction if ia else 0.0
        db = ib.direction if ib else 0.0
        wa = (ia.importance * ia.confidence) if ia else 0.0
        wb = (ib.importance * ib.confidence) if ib else 0.0
        salience = max(wa, wb)
        same = max(0.0, da * db)
        opposed = max(0.0, -(da * db))
        pressures.append(
            RelationPressure(
                domain=key[0],
                target=key[1],
                incompatibility=_clip(opposed * (wa + wb) / 2.0, 0.0, 1.0),
                compatibility=_clip(same * (wa + wb) / 2.0, 0.0, 1.0),
                salience=salience,
            )
        )

    claims_a = {(c.domain, c.target): c for c in a.claims}
    claims_b = {(c.domain, c.target): c for c in b.claims}
    for key in sorted(claims_a.keys() & claims_b.keys()):
        ca, cb = claims_a[key], claims_b[key]
        collision = min(ca.strength * ca.confidence, cb.strength * cb.confidence)
        salience = max(ca.salience, cb.salience)
        pressures.append(
            RelationPressure(
                domain=key[0],
                target=key[1],
                incompatibility=_clip(collision * salience, 0.0, 1.0),
                compatibility=0.0,
                salience=salience,
            )
        )

    return RelationMatrix(
        actor_a=a.actor_id,
        actor_b=b.actor_id,
        pressures=tuple(pressures),
        trust=dict(trust or {}),
        dependence=dict(dependence or {}),
        contact=max(0.0, min(1.0, contact)),
        uncertainty=max(0.0, min(1.0, uncertainty)),
    )
