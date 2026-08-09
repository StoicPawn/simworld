from __future__ import annotations

from dataclasses import dataclass

from simworld.relations.interaction import Interaction


@dataclass(frozen=True, slots=True)
class EmergentPattern:
    """Retrospective classifier over interaction history.

    Labels are analytical views, not causal states. Removing this classifier must not
    change the underlying simulation trajectory.
    """

    label: str
    actor_ids: frozenset[str]
    start_time: int
    end_time: int
    confidence: float
    evidence_count: int
    metrics: dict[str, float]


def infer_patterns(
    interactions: tuple[Interaction, ...],
    *,
    min_events: int = 3,
) -> tuple[EmergentPattern, ...]:
    if not interactions:
        return ()

    grouped: dict[frozenset[str], list[Interaction]] = {}
    for interaction in interactions:
        key = frozenset((interaction.actor_a, interaction.actor_b))
        grouped.setdefault(key, []).append(interaction)

    patterns: list[EmergentPattern] = []
    for actors, history in grouped.items():
        if len(history) < min_events:
            continue
        history.sort(key=lambda item: item.time)
        n = len(history)
        violence = sum(item.physical_harm * item.intensity for item in history) / n
        coercion = sum(item.coercion * item.intensity for item in history) / n
        coordination = sum(item.coordination * item.intensity for item in history) / n
        transfer = sum(abs(item.resource_transfer) * item.intensity for item in history) / n
        hostile = sum(item.action in {"threaten", "obstruct", "seize", "attack"} for item in history) / n
        cooperative = sum(item.action in {"exchange", "coordinate", "negotiate"} for item in history) / n
        persistence = min(1.0, (history[-1].time - history[0].time + 1) / max(3, n))

        metrics = {
            "violence": violence,
            "coercion": coercion,
            "coordination": coordination,
            "resource_transfer": transfer,
            "hostile_fraction": hostile,
            "cooperative_fraction": cooperative,
            "persistence": persistence,
        }

        candidates: list[tuple[str, float]] = []
        # These are descriptive classifiers only. No downstream simulation may branch
        # on the label when the underlying metrics/interactions are available.
        candidates.append(("sustained_cooperation", cooperative * 0.55 + coordination * 0.3 + persistence * 0.15))
        candidates.append(("competitive_rivalry", hostile * 0.5 + coercion * 0.25 + persistence * 0.25))
        candidates.append(("violent_feud", hostile * 0.35 + violence * 0.45 + persistence * 0.2))
        candidates.append(("alliance_like", coordination * 0.45 + cooperative * 0.3 + persistence * 0.25))
        candidates.append(("war_like", violence * 0.4 + hostile * 0.3 + coercion * 0.15 + persistence * 0.15))

        for label, score in candidates:
            if score >= 0.52:
                patterns.append(
                    EmergentPattern(
                        label=label,
                        actor_ids=actors,
                        start_time=history[0].time,
                        end_time=history[-1].time,
                        confidence=min(1.0, score),
                        evidence_count=n,
                        metrics=metrics,
                    )
                )

    return tuple(sorted(patterns, key=lambda p: (p.start_time, p.label, sorted(p.actor_ids))))
