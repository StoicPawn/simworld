from __future__ import annotations

from random import Random

from simworld.simulation.first_world import FirstWorldConfig
from simworld.simulation.social_world import SocialWorldSimulation
from simworld.social.communication import Message, communicate, evaluate_message_accuracy
from simworld.social.decision import ActionOption, DecisionContext, choose_action
from simworld.social.epistemics import EpistemicState
from simworld.social.learning import Experience, StrategyLearner
from simworld.social.narrative import Narrative, NarrativeVersion, SocialMemory
from simworld.social.needs import NeedState


def test_message_updates_belief_from_trust_not_hidden_truth() -> None:
    receiver = EpistemicState()
    receiver.trust.set("speaker", 0.9, "food")
    message = Message(
        sender_id="speaker",
        receiver_id="ruler",
        proposition="food_shortage",
        asserted_probability=0.9,
        truthful_probability=0.1,
        domain="food",
    )
    communicate(message, receiver, time=3)
    assert receiver.belief("food_shortage").probability > 0.5
    accuracy = evaluate_message_accuracy(message, 0.1)
    assert accuracy < 0.3
    trust_after = receiver.trust.reinforce("speaker", accuracy, "food", rate=0.5)
    assert trust_after < 0.9


def test_contextual_trust_is_not_one_global_scalar() -> None:
    state = EpistemicState()
    state.trust.set("advisor", 0.92, "military")
    state.trust.set("advisor", 0.21, "food")
    assert state.trust.get("advisor", "military") == 0.92
    assert state.trust.get("advisor", "food") == 0.21


def test_same_need_does_not_force_one_action() -> None:
    needs = NeedState({"food": 1.0})
    learner = StrategyLearner()
    options = (
        ActionOption("farm", {"food": 0.5}, {}, domain="policy"),
        ActionOption("trade", {"food": 0.5}, {}, domain="policy"),
    )
    context = DecisionContext(needs=needs, beliefs={}, learner=learner, temperature=1.0)
    outcomes = {choose_action(options, context, Random(seed)).name for seed in range(20)}
    assert outcomes == {"farm", "trade"}


def test_actor_can_learn_from_perceived_reward_not_latent_effect() -> None:
    learner = StrategyLearner()
    learner.record(
        Experience(
            time=1,
            strategy="coerce",
            domain="governance",
            perceived_reward=0.8,
            latent_effect=-0.7,
        )
    )
    assert learner.estimate("coerce", "governance") > 0.0
    assert learner.experiences[-1].latent_effect < 0.0


def test_narrative_transmission_can_mutate() -> None:
    memory = SocialMemory()
    narrative = Narrative(
        id="winter",
        origin_event_ids=("event-1",),
        versions=[NarrativeVersion(1, "parent", ("the granary was opened",), 0.9)],
    )
    memory.add(narrative, "parent")
    version = memory.transmit(
        "winter",
        teller_id="parent",
        receiver_id="child",
        trust=1.0,
        time=20,
        rng=Random(3),
        mutation_rate=1.0,
    )
    assert version is not None
    assert "child" in memory.held_by
    assert version.claims != ("the granary was opened",)


def test_integrated_social_world_produces_requests_choices_learning_and_memory() -> None:
    config = FirstWorldConfig(width=42, height=32, settlements=5, years=12, seed=4813)
    result = SocialWorldSimulation(config).run()
    kinds = [event.kind for event in result.base.world.events]

    assert kinds.count("petition_or_report") == config.settlements * config.years
    assert kinds.count("house_action") == config.settlements * config.years
    assert "report_evaluated" in kinds
    assert len(result.house_ids) == config.settlements
    actions = {
        str(event.payload["action"])
        for event in result.base.world.events
        if event.kind == "house_action"
    }
    assert len(actions) >= 2
    assert any(result.social_memory.held_by.values())


def test_social_world_contains_perceived_vs_latent_policy_effects() -> None:
    config = FirstWorldConfig(width=40, height=30, settlements=4, years=15, seed=90125)
    result = SocialWorldSimulation(config).run()
    policy_events = [event for event in result.base.world.events if event.kind == "house_action"]
    assert policy_events
    assert all("perceived_reward" in event.payload for event in policy_events)
    assert all("latent_effect" in event.payload for event in policy_events)
    assert any(
        float(event.payload["perceived_reward"]) > float(event.payload["latent_effect"])
        for event in policy_events
    )
