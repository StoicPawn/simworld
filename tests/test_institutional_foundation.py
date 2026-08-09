from simworld.institutions.organization import CooperationLedger, Membership, Organization, OrganizationRegistry
from simworld.politics.authority import AuthorityIndex, AuthorityObservation
from simworld.simulation.first_world import FirstWorldConfig
from simworld.simulation.institutional_world import InstitutionalWorldSimulation
from simworld.social.obligations import Obligation, ObligationRegistry


def test_obligation_can_be_partially_then_fully_paid() -> None:
    registry = ObligationRegistry()
    obligation = Obligation("debtor", "creditor", "credit", "grain", 1.0, 0, 2)
    registry.add(obligation)
    first = registry.pay(obligation.id, 0.4, 2)
    assert not first.completed
    assert round(obligation.outstanding, 6) == 0.6
    second = registry.pay(obligation.id, 0.8, 3)
    assert second.completed
    assert obligation.outstanding == 0.0


def test_cooperation_network_derives_group_candidate_without_declaring_state() -> None:
    ledger = CooperationLedger()
    ledger.reinforce("A", "B", 1.0)
    ledger.reinforce("B", "C", 0.9)
    ledger.reinforce("A", "C", 0.8)
    components = ledger.components(min_edge_score=0.75, min_members=3)
    assert components == (frozenset({"A", "B", "C"}),)

    registry = OrganizationRegistry()
    organization = Organization(formed_at=4, purpose={"mutual_provision": 0.8})
    for member in components[0]:
        organization.add_member(Membership(member, 4))
    registry.add(organization)
    assert organization.members(4) == {"A", "B", "C"}


def test_authority_is_derived_and_legitimacy_differs_from_effective_power() -> None:
    index = AuthorityIndex()
    signal = index.observe(
        AuthorityObservation(
            "org",
            "member",
            "resource_coordination",
            5,
            compliance=0.9,
            dependency=0.8,
            recognition=0.2,
            provision=0.1,
            coercion=0.9,
        )
    )
    assert signal.effective_authority > 0.4
    assert signal.legitimacy_signal < signal.effective_authority


def test_institutional_world_runs_without_primitive_state() -> None:
    result = InstitutionalWorldSimulation(
        FirstWorldConfig(width=42, height=32, settlements=4, years=7, seed=104729)
    ).run()
    world = result.material.generational.social.base.world
    assert any(event.kind == "material_production" for event in world.events)
    assert all(entity.kind != "state" for entity in world.entities.values())
    assert isinstance(result.obligations, ObligationRegistry)
    assert isinstance(result.organizations, OrganizationRegistry)
