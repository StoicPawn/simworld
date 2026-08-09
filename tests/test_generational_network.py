from __future__ import annotations

from random import Random

from simworld.simulation.first_world import FirstWorldConfig
from simworld.simulation.generational_world import GenerationalWorldSimulation
from simworld.social.kinship import KinshipGraph, PersonRecord, lineage_from_roots
from simworld.social.network import SocialGraph, SocialTie
from simworld.social.reproduction import ReproductiveProfile, conception_probability


def test_kinship_graph_derives_family_relations() -> None:
    graph = KinshipGraph()
    graph.add_person(PersonRecord("m", -30, "gestational"))
    graph.add_person(PersonRecord("f", -31, "non_gestational"))
    graph.add_person(PersonRecord("c1", 0, "gestational", "m", "f"))
    graph.add_person(PersonRecord("c2", 2, "non_gestational", "m", "f"))
    graph.add_person(PersonRecord("g", 22, "gestational", "c1", None))

    assert graph.parents("c1") == ("m", "f")
    assert graph.siblings("c1") == ("c2",)
    assert graph.ancestors("g")["m"] == 2
    assert "g" in graph.descendants("m")
    assert graph.biological_relatedness_hint("c1", "c2") > 0.0


def test_lineage_is_a_derived_view_not_an_entity_type() -> None:
    graph = KinshipGraph()
    graph.add_person(PersonRecord("root", -50, "gestational"))
    graph.add_person(PersonRecord("child", -20, "non_gestational", "root", None))
    graph.add_person(PersonRecord("grandchild", 5, "gestational", "child", None))
    view = lineage_from_roots(graph, ("root",), generations=4)
    assert view.members == frozenset({"root", "child", "grandchild"})


def test_social_graph_is_multiplex_and_connections_have_connections() -> None:
    graph = SocialGraph()
    graph.add(SocialTie("a", "b", "friendship", 0.8, 0, sentiment=0.7, trust=0.8))
    graph.add(SocialTie("b", "c", "rivalry", 0.5, 0, sentiment=-0.5, trust=0.2))
    graph.add(SocialTie("a", "b", "co_parent", 0.7, 1, sentiment=0.0, trust=0.5))

    assert graph.neighbours("a", 2) == {"b"}
    assert graph.second_order_neighbours("a", 2) == {"c"}
    assert graph.shortest_social_distance("a", "c", 2) == 2
    assert graph.connection_strength("a", "b", 2) > 0.8


def test_reproduction_is_probabilistic_not_a_direct_consequence_of_relation() -> None:
    gestational = ReproductiveProfile("a", -25, True, fertility=0.9, health=0.95)
    other = ReproductiveProfile("b", -27, False, fertility=0.9, health=0.95)
    low = conception_probability(
        gestational,
        other,
        time=0,
        contact_intensity=0.1,
        resource_security=0.5,
        reproductive_intent=0.3,
    )
    high = conception_probability(
        gestational,
        other,
        time=0,
        contact_intensity=0.9,
        resource_security=0.8,
        reproductive_intent=0.8,
    )
    assert 0.0 < low < high < 1.0
    outcomes = {Random(seed).random() < high for seed in range(30)}
    assert outcomes == {False, True}


def test_birth_creates_biological_and_co_parent_relations_without_forcing_romance() -> None:
    sim = GenerationalWorldSimulation(
        FirstWorldConfig(width=36, height=28, settlements=3, years=1, seed=3317)
    )
    sim.initialize()
    settlement = sim.settlement_ids[0]
    mother, father, _ = sim._active_reproductive_pairs(0)[0]
    sim.world.advance_to(1)
    child = sim._birth(1, mother, father, settlement)

    assert set(sim.kinship.parents(child)) == {mother, father}
    assert any(
        tie.kind == "co_parent" and {tie.source_id, tie.target_id} == {mother, father}
        for tie in sim.network.ties
    )
    co_parent = next(
        tie
        for tie in sim.network.ties
        if tie.kind == "co_parent" and {tie.source_id, tie.target_id} == {mother, father}
    )
    assert co_parent.sentiment == 0.0


def test_integrated_generational_world_produces_births_networks_and_lineages() -> None:
    config = FirstWorldConfig(width=44, height=34, settlements=4, years=28, seed=8128)
    result = GenerationalWorldSimulation(config).run()
    kinds = [event.kind for event in result.social.base.world.events]

    founders = config.settlements * 6
    assert len(result.person_ids) >= founders
    assert "social_tie_formed" in kinds
    assert any(tie.kind == "friendship" for tie in result.network.ties)
    assert any(tie.kind in {"romantic", "intimate"} for tie in result.network.ties)
    assert all(person_id in result.kinship.people for person_id in result.person_ids)
    if "birth" in kinds:
        assert any(tie.kind == "parent_child" for tie in result.network.ties)
        assert any(tie.kind == "co_parent" for tie in result.network.ties)
    assert isinstance(result.lineage_candidates, tuple)
