from __future__ import annotations

from dataclasses import dataclass
from random import Random

from simworld.core.entity import Entity
from simworld.core.event import Event
from simworld.institutions.organization import CooperationLedger, Membership, Organization, OrganizationRegistry
from simworld.politics.authority import AuthorityIndex, AuthorityObservation
from simworld.simulation.first_world import FirstWorldConfig, SimulationResult
from simworld.simulation.generational_world import GenerationalSimulationResult
from simworld.simulation.material_world import MaterialSimulationResult, MaterialWorldSimulation
from simworld.simulation.social_world import SocialSimulationResult
from simworld.social.obligations import Obligation, ObligationRegistry


@dataclass(frozen=True, slots=True)
class InstitutionalSimulationResult:
    material: MaterialSimulationResult
    obligations: ObligationRegistry
    organizations: OrganizationRegistry
    cooperation: CooperationLedger
    authority: AuthorityIndex


class InstitutionalWorldSimulation(MaterialWorldSimulation):
    """Bridge from material/social networks toward emergent institutions and authority.

    No state, ruler, class or house is declared here. Obligations, repeated cooperation,
    dependency, recognition and provision create organization and authority signals that
    later political layers may interpret.
    """

    def __init__(self, config: FirstWorldConfig) -> None:
        super().__init__(config)
        self.institutional_rng = Random(config.seed ^ 0xA0710A17)
        self.obligations = ObligationRegistry()
        self.organizations = OrganizationRegistry()
        self.cooperation = CooperationLedger()
        self.authority = AuthorityIndex()
        self._formed_components: set[frozenset[str]] = set()

    def _learn_from_exchange_events(self, events: tuple[Event, ...]) -> None:
        for event in events:
            if event.kind == "material_exchange" and len(event.participants) >= 2:
                a_id, b_id = event.participants[:2]
                self.cooperation.reinforce(a_id, b_id, 0.45)
            elif event.kind == "material_exchange_rejected" and len(event.participants) >= 2:
                a_id, b_id = event.participants[:2]
                self.cooperation.weaken(a_id, b_id, 0.05)

    def _credit_candidate(self, debtor_id: str, year: int) -> tuple[str, float] | None:
        debtor_inventory = self.inventories[debtor_id]
        best: tuple[str, float] | None = None
        for candidate_id, inventory in self.inventories.items():
            if candidate_id == debtor_id or inventory.amount("grain") <= 1.35:
                continue
            spatial = self._spatial_exchange_factor(debtor_id, candidate_id)
            if spatial <= 0.08:
                continue
            social = self._household_connection(debtor_id, candidate_id, year)
            previous = self.cooperation.score(debtor_id, candidate_id)
            score = 0.48 * spatial + 0.24 * min(1.0, social) + 0.28 * min(1.0, previous)
            if best is None or score > best[1]:
                best = (candidate_id, score)
        return best

    def _run_credit_formation(self, year: int) -> None:
        for household in self.households.active_households():
            debtor_id = household.id
            inventory = self.inventories[debtor_id]
            if inventory.amount("grain") >= 0.26:
                continue
            if any(not obligation.settled for obligation in self.obligations.obligations.values() if obligation.debtor_id == debtor_id):
                continue
            candidate = self._credit_candidate(debtor_id, year)
            if candidate is None:
                continue
            creditor_id, relationship_score = candidate
            acceptance = max(0.0, min(1.0, 0.30 + 0.48 * relationship_score + self.institutional_rng.uniform(-0.16, 0.16)))
            if self.institutional_rng.random() >= acceptance:
                self.world.record_event(
                    Event(
                        kind="credit_request_rejected",
                        time=year,
                        participants=(debtor_id, creditor_id),
                        locations=(
                            self.households.households[debtor_id].settlement_id,
                            self.households.households[creditor_id].settlement_id,
                        ),
                        impact=0.06,
                        payload={"acceptance_probability": round(acceptance, 4)},
                    )
                )
                continue

            creditor_inventory = self.inventories[creditor_id]
            amount = min(0.42, max(0.12, creditor_inventory.amount("grain") - 1.0))
            if amount <= 0:
                continue
            creditor_inventory.remove("grain", amount)
            inventory.add("grain", amount)
            household.food_stock = inventory.amount("grain")
            household.debt += amount
            issue_event = Event(
                kind="grain_credit_issued",
                time=year,
                participants=(debtor_id, creditor_id),
                locations=(
                    self.households.households[debtor_id].settlement_id,
                    self.households.households[creditor_id].settlement_id,
                ),
                impact=0.18,
                payload={"amount": round(amount, 4), "due_at": year + 2},
            )
            self.world.record_event(issue_event)
            obligation = Obligation(
                debtor_id=debtor_id,
                creditor_id=creditor_id,
                kind="credit",
                resource="grain",
                amount=amount * self.institutional_rng.uniform(1.02, 1.16),
                created_at=year,
                due_at=year + 2,
                debtor_acceptance=max(0.25, min(0.95, acceptance)),
                external_recognition=0.15,
                enforceability=0.08,
                origin_event_id=issue_event.id,
            )
            self.obligations.add(obligation)
            self.cooperation.reinforce(debtor_id, creditor_id, 0.24)
            self.authority.observe(
                AuthorityObservation(
                    authority_id=creditor_id,
                    subject_id=debtor_id,
                    domain="material_dependency",
                    time=year,
                    dependency=self.obligations.dependency(debtor_id, creditor_id),
                    recognition=obligation.debtor_acceptance * 0.45,
                    provision=0.72,
                )
            )

    def _run_obligation_resolution(self, year: int) -> None:
        for obligation in self.obligations.due(year):
            if obligation.resource != "grain":
                continue
            debtor_inventory = self.inventories.get(obligation.debtor_id)
            creditor_inventory = self.inventories.get(obligation.creditor_id)
            if debtor_inventory is None or creditor_inventory is None:
                continue
            available = max(0.0, debtor_inventory.amount("grain") - 0.38)
            payment_amount = min(obligation.outstanding, available)
            if payment_amount > 0:
                debtor_inventory.remove("grain", payment_amount)
                creditor_inventory.add("grain", payment_amount)
                payment = self.obligations.pay(obligation.id, payment_amount, year)
                debtor_household = self.households.households[obligation.debtor_id]
                debtor_household.debt = max(0.0, debtor_household.debt - payment_amount)
                debtor_household.food_stock = debtor_inventory.amount("grain")
                self.world.record_event(
                    Event(
                        kind="obligation_payment",
                        time=year,
                        participants=(obligation.debtor_id, obligation.creditor_id),
                        locations=(debtor_household.settlement_id,),
                        impact=0.12,
                        payload={
                            "obligation_id": obligation.id,
                            "amount": round(payment.amount, 4),
                            "completed": payment.completed,
                        },
                    )
                )
                self.cooperation.reinforce(obligation.debtor_id, obligation.creditor_id, 0.36 if payment.completed else 0.14)
                compliance = 1.0 if payment.completed else min(0.8, payment.amount / max(obligation.amount, 1e-9))
            else:
                self.world.record_event(
                    Event(
                        kind="obligation_default",
                        time=year,
                        participants=(obligation.debtor_id, obligation.creditor_id),
                        locations=(self.households.households[obligation.debtor_id].settlement_id,),
                        impact=0.22,
                        payload={"obligation_id": obligation.id, "outstanding": round(obligation.outstanding, 4)},
                    )
                )
                self.cooperation.weaken(obligation.debtor_id, obligation.creditor_id, 0.22)
                compliance = 0.0
            self.authority.observe(
                AuthorityObservation(
                    authority_id=obligation.creditor_id,
                    subject_id=obligation.debtor_id,
                    domain="material_dependency",
                    time=year,
                    compliance=compliance,
                    dependency=self.obligations.dependency(obligation.debtor_id, obligation.creditor_id),
                    recognition=obligation.debtor_acceptance * 0.55,
                    provision=0.32,
                    coercion=obligation.enforceability * 0.25,
                )
            )
            if not obligation.settled:
                obligation.due_at = year + 1

    def _component_strength(self, component: frozenset[str]) -> float:
        members = sorted(component)
        scores: list[float] = []
        for index, a_id in enumerate(members):
            for b_id in members[index + 1 :]:
                score = self.cooperation.score(a_id, b_id)
                if score > 0:
                    scores.append(score)
        return sum(scores) / len(scores) if scores else 0.0

    def _run_organization_emergence(self, year: int) -> None:
        for component in self.cooperation.components(min_edge_score=0.75, min_members=3):
            if component in self._formed_components:
                continue
            strength = self._component_strength(component)
            formation_probability = max(0.0, min(0.72, 0.08 + 0.22 * strength))
            if self.institutional_rng.random() >= formation_probability:
                continue
            organization = Organization(
                formed_at=year,
                purpose={"exchange": min(1.0, strength), "mutual_provision": min(1.0, 0.5 + 0.3 * strength)},
                internal_recognition=max(0.35, min(0.9, 0.45 + 0.16 * strength)),
            )
            for member_id in sorted(component):
                organization.add_member(
                    Membership(
                        member_id=member_id,
                        joined_at=year,
                        stake=max(0.1, min(1.0, self.cooperation.score(member_id, next(iter(component - {member_id}), member_id)))),
                        recognition=organization.internal_recognition,
                    )
                )
            self.organizations.add(organization)
            self._formed_components.add(component)
            entity = Entity(
                kind="organization",
                name=f"Association-{len(self.organizations.organizations):03d}",
                created_at=year,
                id=organization.id,
                attributes={
                    "member_count": len(component),
                    "internal_recognition": organization.internal_recognition,
                },
                tags={"organization", "emergent_group"},
            )
            self.world.add_entity(entity)
            self.world.record_event(
                Event(
                    kind="organization_formed",
                    time=year,
                    participants=tuple(sorted(component)) + (organization.id,),
                    locations=tuple(sorted({self.households.households[member].settlement_id for member in component})),
                    impact=0.25 + 0.08 * len(component),
                    payload={
                        "organization_id": organization.id,
                        "cooperation_strength": round(strength, 4),
                        "formation_probability": round(formation_probability, 4),
                    },
                )
            )

    def _run_organization_processes(self, year: int) -> None:
        for organization in self.organizations.active(year):
            members = organization.members(year)
            if not members:
                continue
            for member_id in sorted(members):
                inventory = self.inventories.get(member_id)
                if inventory is None:
                    continue
                contribution_probability = max(0.08, min(0.88, 0.18 + 0.55 * organization.internal_recognition))
                contributed = 0.0
                if inventory.amount("grain") > 0.85 and self.institutional_rng.random() < contribution_probability:
                    contributed = min(0.12, inventory.amount("grain") - 0.72)
                    inventory.remove("grain", contributed)
                    organization.shared_resources["grain"] = organization.shared_resources.get("grain", 0.0) + contributed
                    self.world.record_event(
                        Event(
                            kind="organization_contribution",
                            time=year,
                            participants=(member_id, organization.id),
                            locations=(self.households.households[member_id].settlement_id,),
                            impact=0.08,
                            payload={"resource": "grain", "amount": round(contributed, 4)},
                        )
                    )
                self.authority.observe(
                    AuthorityObservation(
                        authority_id=organization.id,
                        subject_id=member_id,
                        domain="resource_coordination",
                        time=year,
                        compliance=1.0 if contributed > 0 else 0.25,
                        dependency=self.obligations.dependency(member_id, organization.id),
                        recognition=organization.internal_recognition,
                        provision=0.1,
                    )
                )

            grain_pool = organization.shared_resources.get("grain", 0.0)
            if grain_pool <= 0.05:
                continue
            needy = sorted(
                (
                    member_id
                    for member_id in members
                    if member_id in self.inventories and self.inventories[member_id].amount("grain") < 0.25
                ),
                key=lambda member_id: self.inventories[member_id].amount("grain"),
            )
            for member_id in needy:
                if organization.shared_resources.get("grain", 0.0) <= 0.05:
                    break
                amount = min(0.14, organization.shared_resources["grain"])
                organization.shared_resources["grain"] -= amount
                self.inventories[member_id].add("grain", amount)
                self.households.households[member_id].food_stock = self.inventories[member_id].amount("grain")
                self.world.record_event(
                    Event(
                        kind="organization_aid",
                        time=year,
                        participants=(organization.id, member_id),
                        locations=(self.households.households[member_id].settlement_id,),
                        impact=0.14,
                        payload={"resource": "grain", "amount": round(amount, 4)},
                    )
                )
                self.authority.observe(
                    AuthorityObservation(
                        authority_id=organization.id,
                        subject_id=member_id,
                        domain="resource_coordination",
                        time=year,
                        dependency=0.45,
                        recognition=organization.internal_recognition,
                        provision=1.0,
                    )
                )

    def run(self) -> InstitutionalSimulationResult:
        self.initialize()
        for year in range(1, self.config.years + 1):
            self.world.advance_to(year)
            self._resolve_pregnancies(year)
            self._run_obligation_resolution(year)
            food_ratio = self._run_harvests(year)
            self._run_demography(year, food_ratio)
            self._run_material_production(year, food_ratio)
            before_exchange = len(self.world.events)
            self._run_material_exchange(year)
            self._learn_from_exchange_events(tuple(self.world.events[before_exchange:]))
            self._run_credit_formation(year)
            self._run_organization_emergence(year)
            self._run_organization_processes(year)
            self._update_households(year, food_ratio)
            for settlement_id in self.settlement_ids:
                petition = self._experience_and_request(year, settlement_id, food_ratio[settlement_id])
                self._apply_house_action(year, settlement_id, petition)
                self._verify_reports(year, settlement_id, food_ratio[settlement_id])
            self._run_migration(year, food_ratio)
            self._run_discoveries(year)
            self._evolve_existing_relations(year)
            self._run_reproduction(year)
            self._run_mortality(year)
            self._evolve_social_network(year)
            self._transmit_memory(year)

        base = SimulationResult(self.config, self.generated, self.world, tuple(self.settlement_ids))
        social = SocialSimulationResult(
            base=base,
            house_ids=tuple(self.house_ids),
            representative_ids=tuple(self.representative_ids),
            social_memory=self.social_memory,
        )
        generational = GenerationalSimulationResult(
            social=social,
            kinship=self.kinship,
            network=self.network,
            households=self.households,
            pregnancies=self.pregnancies,
            inheritance_transfers=tuple(self.inheritance_transfers),
            person_ids=tuple(self.person_ids),
            lineage_candidates=self._lineage_candidates(),
        )
        material = MaterialSimulationResult(
            generational=generational,
            property_registry=self.property_registry,
            inventories=self.inventories,
            exchange_count=self.exchange_count,
        )
        return InstitutionalSimulationResult(
            material=material,
            obligations=self.obligations,
            organizations=self.organizations,
            cooperation=self.cooperation,
            authority=self.authority,
        )
