from __future__ import annotations

from dataclasses import dataclass
from random import Random

from simworld.culture.knowledge import KnowledgeLedger, KnowledgeState
from simworld.culture.technology import Affordance, InnovationContext, innovation_probability


@dataclass(frozen=True, slots=True)
class InnovationResult:
    actor_id: str
    affordance_id: str
    probability: float
    discovered: bool
    prior_mastery: float
    resulting_mastery: float


def attempt_innovation(
    actor_id: str,
    affordance: Affordance,
    context: InnovationContext,
    ledger: KnowledgeLedger,
    *,
    time: int,
    rng: Random,
) -> InnovationResult:
    """Try one actor-local innovation opportunity.

    A successful result adds/improves only that actor's knowledge. It never changes a
    global civilization technology level and never propagates automatically.
    """

    prior = ledger.get(actor_id, affordance.id)
    prior_mastery = 0.0 if prior is None else prior.mastery
    probability = innovation_probability(affordance, context)
    if probability <= 0.0 or rng.random() >= probability:
        return InnovationResult(
            actor_id=actor_id,
            affordance_id=affordance.id,
            probability=probability,
            discovered=False,
            prior_mastery=prior_mastery,
            resulting_mastery=prior_mastery,
        )

    experience = min(1.0, max(0.0, context.experience))
    experimentation = min(1.0, max(0.0, context.experimentation))
    initial_gain = 0.12 + 0.24 * experience + 0.24 * experimentation + rng.uniform(0.0, 0.10)
    mastery = min(1.0, max(prior_mastery, prior_mastery + initial_gain * (1.0 - 0.45 * affordance.complexity)))
    confidence = min(1.0, 0.18 + 0.42 * mastery + 0.18 * affordance.observability)
    ledger.set(
        actor_id,
        KnowledgeState(
            unit_id=affordance.id,
            mastery=mastery,
            confidence=confidence,
            acquired_at=time if prior is None else prior.acquired_at,
            source_id=actor_id,
            generation=0 if prior is None else prior.generation,
        ),
    )
    return InnovationResult(
        actor_id=actor_id,
        affordance_id=affordance.id,
        probability=probability,
        discovered=True,
        prior_mastery=prior_mastery,
        resulting_mastery=mastery,
    )
