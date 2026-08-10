from __future__ import annotations

from random import Random
from typing import Mapping

from simworld.culture.catalog import AffordanceCatalog
from simworld.culture.effects import apply_effect_specs
from simworld.culture.knowledge import KnowledgeLedger


def actor_effect_channels(
    catalog: AffordanceCatalog,
    knowledge: KnowledgeLedger,
    actor_id: str,
    *,
    base_channels: Mapping[str, float] | None = None,
    context: Mapping[str, float] | None = None,
    rng: Random,
) -> dict[str, float]:
    """Resolve effects from capabilities actually known by one actor.

    Technology is neither global nor binary. Each known capability contributes only
    at the actor's current mastery and only where its effect context applies.
    """

    channels = dict(base_channels or {})
    context = dict(context or {})
    for unit_id in knowledge.known_units(actor_id):
        affordance = catalog.affordances.get(unit_id)
        if affordance is None:
            continue
        mastery = knowledge.mastery(actor_id, unit_id)
        channels = apply_effect_specs(
            affordance.effects,
            mastery=mastery,
            base_channels=channels,
            context=context,
            rng=rng,
        )
    return channels
