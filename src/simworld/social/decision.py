from __future__ import annotations

from dataclasses import dataclass
from math import exp
from random import Random

from simworld.social.learning import StrategyLearner
from simworld.social.needs import NeedState


@dataclass(frozen=True, slots=True)
class ActionOption:
    name: str
    need_weights: dict[str, float]
    belief_weights: dict[str, float]
    base_bias: float = 0.0
    cost: float = 0.0
    domain: str = "general"


@dataclass(frozen=True, slots=True)
class DecisionContext:
    needs: NeedState
    beliefs: dict[str, float]
    learner: StrategyLearner
    resources: float = 1.0
    temperature: float = 0.35


def action_score(option: ActionOption, context: DecisionContext) -> float:
    need_term = context.needs.pressure(option.need_weights)
    belief_term = sum(context.beliefs.get(name, 0.5) * weight for name, weight in option.belief_weights.items())
    learned = context.learner.estimate(option.name, option.domain)
    affordability_penalty = max(0.0, option.cost - context.resources) * 2.0
    return option.base_bias + need_term + belief_term + learned - affordability_penalty


def choose_action(options: tuple[ActionOption, ...], context: DecisionContext, rng: Random) -> ActionOption:
    """Softmax choice: pressures influence action without deterministic policy mapping."""
    if not options:
        raise ValueError("at least one action option is required")
    temperature = max(0.03, context.temperature)
    scores = [action_score(option, context) for option in options]
    maximum = max(scores)
    weights = [exp((score - maximum) / temperature) for score in scores]
    total = sum(weights)
    draw = rng.random() * total
    cumulative = 0.0
    for option, weight in zip(options, weights, strict=True):
        cumulative += weight
        if draw <= cumulative:
            return option
    return options[-1]
