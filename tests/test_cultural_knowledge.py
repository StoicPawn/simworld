from pathlib import Path
from random import Random

from simworld.culture.catalog import AffordanceCatalog
from simworld.culture.conventions import ConventionState, cluster_conventions, evolve_convention
from simworld.culture.innovation import attempt_innovation
from simworld.culture.knowledge import KnowledgeLedger, KnowledgeState, KnowledgeUnit, decay_knowledge, transmit_knowledge
from simworld.culture.technology import Affordance, InnovationContext, innovation_probability


def test_technology_has_zero_probability_without_required_material() -> None:
    affordance = Affordance(
        id="example_heat_process",
        required_materials=frozenset({"reactive_material"}),
        required_capabilities={"controlled_heat": 0.5},
        complexity=0.6,
    )
    context = InnovationContext(
        materials=frozenset(),
        capabilities={"controlled_heat": 0.9},
        environment={},
        experience=1.0,
        experimentation=1.0,
    )
    assert innovation_probability(affordance, context) == 0.0


def test_possible_technology_is_not_guaranteed_discovery() -> None:
    affordance = Affordance(
        id="example_heat_process",
        required_materials=frozenset({"reactive_material"}),
        required_capabilities={"controlled_heat": 0.5},
        complexity=0.75,
        observability=0.3,
    )
    context = InnovationContext(
        materials=frozenset({"reactive_material"}),
        capabilities={"controlled_heat": 0.7},
        environment={},
        experience=0.3,
        experimentation=0.2,
    )
    probability = innovation_probability(affordance, context)
    assert 0.0 < probability < 0.1


def test_affordance_catalog_is_data_driven_and_every_entry_has_effects() -> None:
    catalog = AffordanceCatalog.from_json(Path("configs/affordances/foundation.json"))
    assert catalog.version == 2
    assert "controlled_heat_processing" in catalog.affordances
    assert catalog.get("metal_ore_reduction").required_materials == frozenset(
        {"metal_bearing_ore", "combustible_fuel"}
    )
    assert all(affordance.effects for affordance in catalog.affordances.values())


def test_innovation_creates_actor_local_not_global_knowledge() -> None:
    affordance = Affordance(
        id="simple_observed_process",
        required_materials=frozenset({"material"}),
        complexity=0.0,
        observability=1.0,
    )
    context = InnovationContext(
        materials=frozenset({"material"}),
        capabilities={},
        environment={},
        experience=1.0,
        experimentation=1.0,
        population_contact=1.0,
        problem_pressure=1.0,
    )
    ledger = KnowledgeLedger()
    discovered = None
    for seed in range(100):
        result = attempt_innovation("actor-a", affordance, context, ledger, time=4, rng=Random(seed))
        if result.discovered:
            discovered = result
            break
    assert discovered is not None
    assert ledger.mastery("actor-a", affordance.id) > 0.0
    assert ledger.mastery("actor-b", affordance.id) == 0.0


def test_knowledge_transmission_can_fail_or_be_partial() -> None:
    unit = KnowledgeUnit("practice-x", "practice", complexity=0.8, demonstrability=0.2)
    source = KnowledgeState("practice-x", mastery=0.9, confidence=0.9, acquired_at=0)
    outcomes = [
        transmit_knowledge(
            unit,
            source,
            receiver_prior=None,
            source_trust=0.2,
            communication_fit=0.2,
            exposure=0.2,
            time=1,
            source_id="a",
            rng=Random(seed),
        )
        for seed in range(30)
    ]
    assert any(outcome is None for outcome in outcomes)
    learned = [outcome for outcome in outcomes if outcome is not None]
    assert learned
    assert any(outcome.mastery < source.mastery for outcome in learned)


def test_unused_knowledge_can_decay_while_practice_preserves_it() -> None:
    unit = KnowledgeUnit("rare-technique", "technique", complexity=0.9)
    state = KnowledgeState("rare-technique", mastery=0.5, confidence=0.6, acquired_at=0)
    unused = decay_knowledge(
        unit,
        state,
        practice=0.0,
        social_reinforcement=0.0,
        record_support=0.0,
        elapsed=4.0,
    )
    practised = decay_knowledge(
        unit,
        state,
        practice=1.0,
        social_reinforcement=0.8,
        record_support=0.0,
        elapsed=4.0,
    )
    assert unused is not None and practised is not None
    assert unused.mastery < practised.mastery


def test_contact_converges_conventions_relative_to_isolated_drift() -> None:
    a = ConventionState((0.1, 0.2, 0.15))
    b = ConventionState((0.9, 0.8, 0.85))
    contact = evolve_convention(
        a,
        interaction_model=b,
        contact_strength=1.0,
        transmission_pressure=1.0,
        drift_rate=0.0,
        identity_resistance=0.0,
        rng=Random(1),
    )
    isolated = evolve_convention(
        a,
        interaction_model=None,
        contact_strength=0.0,
        transmission_pressure=0.0,
        drift_rate=0.05,
        identity_resistance=0.0,
        rng=Random(1),
    )
    assert contact.distance(b) < a.distance(b)
    assert isolated != a


def test_identity_resistance_reduces_but_does_not_define_group() -> None:
    a = ConventionState((0.2, 0.2))
    b = ConventionState((0.8, 0.8))
    low = evolve_convention(
        a,
        interaction_model=b,
        contact_strength=1.0,
        transmission_pressure=1.0,
        drift_rate=0.0,
        identity_resistance=0.0,
        rng=Random(2),
    )
    high = evolve_convention(
        a,
        interaction_model=b,
        contact_strength=1.0,
        transmission_pressure=1.0,
        drift_rate=0.0,
        identity_resistance=0.9,
        rng=Random(2),
    )
    assert low.distance(b) < high.distance(b)


def test_cluster_count_is_derived_not_preassigned() -> None:
    states = {
        "a": ConventionState((0.10, 0.10)),
        "b": ConventionState((0.12, 0.15)),
        "c": ConventionState((0.88, 0.90)),
        "d": ConventionState((0.84, 0.87)),
    }
    strict = cluster_conventions(states, compatibility_threshold=0.85)
    permissive = cluster_conventions(states, compatibility_threshold=0.10)
    assert len(strict) == 2
    assert len(permissive) == 1
