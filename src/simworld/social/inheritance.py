from __future__ import annotations

from dataclasses import dataclass, field
from random import Random

from simworld.social.kinship import KinshipGraph
from simworld.social.network import SocialGraph


@dataclass(frozen=True, slots=True)
class EstateItem:
    kind: str
    key: str
    value: float = 0.0
    divisible: bool = True


@dataclass(frozen=True, slots=True)
class SuccessionClaim:
    claimant_id: str
    item_key: str
    biological_weight: float = 0.0
    dependence_weight: float = 0.0
    social_weight: float = 0.0
    expressed_intent_weight: float = 0.0
    norm_weight: float = 0.0
    power_weight: float = 0.0

    @property
    def score(self) -> float:
        return (
            0.23 * self.biological_weight
            + 0.17 * self.dependence_weight
            + 0.16 * self.social_weight
            + 0.18 * self.expressed_intent_weight
            + 0.14 * self.norm_weight
            + 0.12 * self.power_weight
        )


@dataclass(slots=True)
class Estate:
    deceased_id: str
    opened_at: int
    items: list[EstateItem] = field(default_factory=list)
    claims: list[SuccessionClaim] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class Transfer:
    item_key: str
    from_id: str
    to_id: str
    share: float
    contested: bool
    winning_score: float


def build_candidate_claims(
    estate: Estate,
    *,
    candidate_ids: tuple[str, ...],
    kinship: KinshipGraph,
    network: SocialGraph,
    time: int,
    expressed_preferences: dict[str, dict[str, float]] | None = None,
    norm_bias: dict[str, float] | None = None,
    power: dict[str, float] | None = None,
) -> list[SuccessionClaim]:
    preferences = expressed_preferences or {}
    norms = norm_bias or {}
    power_map = power or {}
    claims: list[SuccessionClaim] = []
    for item in estate.items:
        for candidate_id in candidate_ids:
            biological = kinship.biological_relatedness_hint(estate.deceased_id, candidate_id)
            social = min(1.0, network.connection_strength(estate.deceased_id, candidate_id, time))
            dependence = 0.0
            for tie in network.active_ties(candidate_id, time):
                if {tie.source_id, tie.target_id} == {estate.deceased_id, candidate_id}:
                    dependence = max(dependence, tie.dependence)
            claims.append(
                SuccessionClaim(
                    claimant_id=candidate_id,
                    item_key=item.key,
                    biological_weight=min(1.0, biological),
                    dependence_weight=dependence,
                    social_weight=social,
                    expressed_intent_weight=max(0.0, min(1.0, preferences.get(item.key, {}).get(candidate_id, 0.0))),
                    norm_weight=max(0.0, min(1.0, norms.get(candidate_id, 0.0))),
                    power_weight=max(0.0, min(1.0, power_map.get(candidate_id, 0.0))),
                )
            )
    return claims


def resolve_estate(estate: Estate, *, rng: Random) -> tuple[Transfer, ...]:
    transfers: list[Transfer] = []
    for item in estate.items:
        claims = [claim for claim in estate.claims if claim.item_key == item.key]
        if not claims:
            continue
        scored = sorted(
            ((claim.score + rng.uniform(-0.06, 0.06), claim) for claim in claims),
            key=lambda pair: pair[0],
            reverse=True,
        )
        contested = len(scored) > 1 and scored[0][0] - scored[1][0] < 0.16
        if item.divisible and contested and len(scored) >= 2:
            positive = [(max(0.01, score), claim) for score, claim in scored[:2]]
            total = sum(score for score, _ in positive)
            for score, claim in positive:
                transfers.append(
                    Transfer(
                        item_key=item.key,
                        from_id=estate.deceased_id,
                        to_id=claim.claimant_id,
                        share=score / total,
                        contested=True,
                        winning_score=score,
                    )
                )
        else:
            score, claim = scored[0]
            transfers.append(
                Transfer(
                    item_key=item.key,
                    from_id=estate.deceased_id,
                    to_id=claim.claimant_id,
                    share=1.0,
                    contested=contested,
                    winning_score=score,
                )
            )
    return tuple(transfers)
