from __future__ import annotations

from random import Random

from simworld.relations.interaction import (
    PRIMITIVE_OPTIONS,
    Interaction,
    InteractionOption,
    choose_interaction,
)
from simworld.relations.matrix import (
    ActorRelationProfile,
    Claim,
    Interest,
    build_relation_matrix,
)
from simworld.relations.patterns import infer_patterns


def test_overlapping_claims_create_pressure_but_not_a_prescribed_action() -> None:
    a = ActorRelationProfile(
        "a",
        claims=[Claim("land", "valley", 0.9, 0.9)],
        capabilities={"coercive": 0.7, "organizational": 0.5},
    )
    b = ActorRelationProfile(
        "b",
        claims=[Claim("land", "valley", 0.8, 0.8)],
        capabilities={"coercive": 0.6},
    )
    matrix = build_relation_matrix(a, b, trust={"general": 0.35}, contact=0.8)
    assert matrix.aggregate_incompatibility > 0.4

    outcomes = {
        choose_interaction(PRIMITIVE_OPTIONS, matrix, a, Random(seed), temperature=1.0).name
        for seed in range(80)
    }
    assert len(outcomes) >= 3
    assert "attack" not in outcomes or len(outcomes) > 1


def test_compatible_interests_can_coexist_with_conflicting_claims() -> None:
    a = ActorRelationProfile(
        "a",
        interests=[Interest("trade", "river_access", 1.0, 0.9)],
        claims=[Claim("status", "office", 0.8, 0.8)],
    )
    b = ActorRelationProfile(
        "b",
        interests=[Interest("trade", "river_access", 1.0, 0.8)],
        claims=[Claim("status", "office", 0.9, 0.9)],
    )
    matrix = build_relation_matrix(a, b)
    assert matrix.aggregate_compatibility > 0.0
    assert matrix.aggregate_incompatibility > 0.0


def test_conflict_substrate_is_actor_type_agnostic() -> None:
    person = ActorRelationProfile(
        "person:1",
        interests=[Interest("status", "inheritance", 1.0, 0.8)],
    )
    sibling = ActorRelationProfile(
        "person:2",
        interests=[Interest("status", "inheritance", -1.0, 0.8)],
    )
    state = ActorRelationProfile(
        "state:1",
        interests=[Interest("territory", "pass", 1.0, 0.9)],
    )
    neighbour = ActorRelationProfile(
        "state:2",
        interests=[Interest("territory", "pass", -1.0, 0.9)],
    )
    assert build_relation_matrix(person, sibling).aggregate_incompatibility > 0
    assert build_relation_matrix(state, neighbour).aggregate_incompatibility > 0


def test_macro_classifier_is_observational_only() -> None:
    history = tuple(
        Interaction(
            time=t,
            actor_a="a",
            actor_b="b",
            action="attack",
            domain="land",
            intensity=0.9,
            physical_harm=0.9,
            coercion=0.8,
        )
        for t in range(1, 8)
    )
    before = tuple((x.time, x.action, x.physical_harm) for x in history)
    patterns = infer_patterns(history)
    after = tuple((x.time, x.action, x.physical_harm) for x in history)
    assert before == after
    assert any(pattern.label == "war_like" for pattern in patterns)


def test_one_off_cooperation_does_not_create_alliance_like_pattern() -> None:
    history = (
        Interaction(1, "a", "b", "coordinate", "route", 0.8, coordination=0.9),
    )
    assert infer_patterns(history) == ()


def test_repeated_coordination_can_be_recognized_retrospectively() -> None:
    history = tuple(
        Interaction(
            time=t,
            actor_a="a",
            actor_b="b",
            action="coordinate",
            domain="security",
            intensity=0.9,
            coordination=0.95,
        )
        for t in range(1, 9)
    )
    labels = {pattern.label for pattern in infer_patterns(history)}
    assert "sustained_cooperation" in labels
    assert "alliance_like" in labels


def test_relational_choice_can_mix_cooperation_and_hostility() -> None:
    a = ActorRelationProfile(
        "a",
        interests=[
            Interest("trade", "market", 1.0, 1.0),
            Interest("territory", "border", 1.0, 1.0),
        ],
        claims=[Claim("territory", "border", 0.9, 1.0)],
        capabilities={"economic": 0.8, "coercive": 0.8, "organizational": 0.7},
    )
    b = ActorRelationProfile(
        "b",
        interests=[
            Interest("trade", "market", 1.0, 1.0),
            Interest("territory", "border", -1.0, 1.0),
        ],
        claims=[Claim("territory", "border", 0.9, 1.0)],
    )
    matrix = build_relation_matrix(
        a,
        b,
        trust={"trade": 0.7, "territory": 0.2},
        dependence={"trade": 0.8},
        contact=0.9,
    )
    options = (
        InteractionOption("exchange", cooperation_weight=0.7, dependence_weight=0.5),
        InteractionOption("threaten", incompatibility_weight=0.7, trust_weight=-0.4),
    )
    outcomes = {
        choose_interaction(options, matrix, a, Random(seed), temperature=1.2).name
        for seed in range(50)
    }
    assert outcomes == {"exchange", "threaten"}
