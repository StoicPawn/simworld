from random import Random

from simworld.social.household import HouseholdRegistry
from simworld.social.inheritance import Estate, EstateItem, build_candidate_claims, resolve_estate
from simworld.social.kinship import KinshipGraph, PersonRecord
from simworld.social.network import SocialGraph, SocialTie
from simworld.social.pregnancy import PregnancyRegistry
from simworld.social.relationship_dynamics import RelationshipContext, evolve_tie


def test_household_membership_is_not_kinship_and_can_change() -> None:
    registry = HouseholdRegistry()
    a = registry.create("s1", 0, ("a", "b"))
    c = registry.create("s1", 0, ("c",))
    assert registry.household_of("a") is a
    registry.move("a", c.id)
    assert "a" not in a.members
    assert registry.household_of("a") is c
    assert registry.household_of("b") is a


def test_conception_and_birth_are_separated_by_gestation_state() -> None:
    pregnancies = PregnancyRegistry()
    pregnancy = pregnancies.start("m", "f", 3.0, gestation_years=0.75)
    assert pregnancies.due_by(3.0) == ()
    assert pregnancies.due_by(3.74) == ()
    assert pregnancies.due_by(3.75) == (pregnancy,)
    outcome = pregnancies.resolve(
        pregnancy.id,
        maternal_health=1.0,
        resource_security=1.0,
        rng=Random(1),
    )
    assert outcome in {"live_birth", "pregnancy_loss"}
    assert not pregnancy.active


def test_relationships_evolve_without_prescribed_outcome() -> None:
    tie = SocialTie("a", "b", "romantic", 0.7, 0, sentiment=0.4, trust=0.7)
    positive = evolve_tie(
        tie,
        time=2,
        context=RelationshipContext(interaction_quality=0.8, cooperation=0.8),
        rng=Random(2),
    )
    negative = evolve_tie(
        tie,
        time=2,
        context=RelationshipContext(
            interaction_quality=-0.8,
            shared_stress=0.9,
            betrayal_signal=0.8,
            separation_pressure=0.9,
        ),
        rng=Random(2),
    )
    assert positive.tie.sentiment > negative.tie.sentiment
    assert positive.tie.trust > negative.tie.trust
    assert positive.tie != negative.tie


def test_inheritance_uses_competing_claims_and_can_split_divisible_assets() -> None:
    kinship = KinshipGraph()
    kinship.add_person(PersonRecord("p", -50, "gestational"))
    kinship.add_person(PersonRecord("c1", -20, "non_gestational", "p", None))
    kinship.add_person(PersonRecord("c2", -18, "gestational", "p", None))
    network = SocialGraph()
    network.add(SocialTie("p", "c1", "parent_child", 1.0, 0, trust=0.8, dependence=0.4))
    network.add(SocialTie("p", "c2", "parent_child", 1.0, 0, trust=0.7, dependence=0.4))
    estate = Estate(
        deceased_id="p",
        opened_at=10,
        items=[EstateItem("wealth", "wealth", 10.0, divisible=True)],
    )
    estate.claims = build_candidate_claims(
        estate,
        candidate_ids=("c1", "c2"),
        kinship=kinship,
        network=network,
        time=10,
        expressed_preferences={"wealth": {"c1": 0.6, "c2": 0.6}},
        norm_bias={"c1": 0.8, "c2": 0.8},
        power={"c1": 0.4, "c2": 0.4},
    )
    transfers = resolve_estate(estate, rng=Random(9))
    assert transfers
    assert all(transfer.item_key == "wealth" for transfer in transfers)
    assert abs(sum(transfer.share for transfer in transfers) - 1.0) < 1e-9
    assert {transfer.to_id for transfer in transfers}.issubset({"c1", "c2"})
