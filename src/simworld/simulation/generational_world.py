from __future__ import annotations

from dataclasses import dataclass
from random import Random

from simworld.core.entity import Entity
from simworld.core.event import Event
from simworld.simulation.first_world import FirstWorldConfig, SimulationResult
from simworld.simulation.social_world import SocialSimulationResult, SocialWorldSimulation
from simworld.social.household import HouseholdRegistry
from simworld.social.inheritance import Estate, EstateItem, Transfer, build_candidate_claims, resolve_estate
from simworld.social.kinship import KinshipGraph, PersonRecord, lineage_from_roots
from simworld.social.network import SocialGraph, SocialTie
from simworld.social.pregnancy import PregnancyRegistry
from simworld.social.relationship_dynamics import RelationshipContext, evolve_tie
from simworld.social.reproduction import ReproductiveProfile, conception_occurs, conception_probability


@dataclass(frozen=True, slots=True)
class GenerationalSimulationResult:
    social: SocialSimulationResult
    kinship: KinshipGraph
    network: SocialGraph
    households: HouseholdRegistry
    pregnancies: PregnancyRegistry
    inheritance_transfers: tuple[Transfer, ...]
    person_ids: tuple[str, ...]
    lineage_candidates: tuple[dict[str, object], ...]


class GenerationalWorldSimulation(SocialWorldSimulation):
    """Biological generations embedded in social, household and inheritance processes.

    No family, house or dynasty is primitive. Descent, co-residence, resources, memory,
    recognition and social ties remain distinct substrates from which groups may emerge.
    """

    def __init__(self, config: FirstWorldConfig) -> None:
        super().__init__(config)
        self.generational_rng = Random(config.seed ^ 0xB10FA11)
        self.kinship = KinshipGraph()
        self.network = SocialGraph()
        self.households = HouseholdRegistry()
        self.pregnancies = PregnancyRegistry()
        self.inheritance_transfers: list[Transfer] = []
        self.person_ids: list[str] = []
        self._profiles: dict[str, ReproductiveProfile] = {}
        self._settlement_people: dict[str, set[str]] = {}

    def initialize(self) -> None:
        super().initialize()
        if self.person_ids:
            return
        for settlement_index, settlement_id in enumerate(self.settlement_ids, start=1):
            self._settlement_people[settlement_id] = set()
            founders: list[str] = []
            for index in range(6):
                gestational = index % 2 == 0
                age = self.generational_rng.randint(18, 38)
                person = Entity(
                    kind="person",
                    name=f"P-{settlement_index:02d}-{index+1:02d}",
                    created_at=0,
                    attributes={
                        "settlement_id": settlement_id,
                        "birth_time": -age,
                        "alive": True,
                        "gestational": gestational,
                        "health": self.generational_rng.uniform(0.72, 1.0),
                        "fertility": self.generational_rng.uniform(0.65, 1.0),
                        "personal_wealth": self.generational_rng.uniform(0.15, 1.4),
                        "personal_debt": self.generational_rng.uniform(0.0, 0.45),
                        "social_power": self.generational_rng.uniform(0.05, 0.65),
                        "name_claim": f"line-{settlement_index}-{(index // 2) + 1}",
                    },
                    tags={"person", "materialized_individual"},
                )
                self.world.add_entity(person)
                self.person_ids.append(person.id)
                founders.append(person.id)
                self._settlement_people[settlement_id].add(person.id)
                self.kinship.add_person(
                    PersonRecord(
                        id=person.id,
                        birth_time=-age,
                        sex="gestational" if gestational else "non_gestational",
                    )
                )
                self._profiles[person.id] = ReproductiveProfile(
                    person_id=person.id,
                    birth_time=-age,
                    gestational=gestational,
                    fertility=float(person.attributes["fertility"]),
                    health=float(person.attributes["health"]),
                )
                self.world.record_event(
                    Event(
                        kind="person_materialized",
                        time=0,
                        participants=(person.id, settlement_id),
                        locations=(settlement_id,),
                        impact=0.08,
                        payload={"age": age, "gestational": gestational},
                    )
                )

            pairs = ((0, 1), (2, 3), (4, 5))
            for a_idx, b_idx in pairs:
                a, b = founders[a_idx], founders[b_idx]
                household = self.households.create(settlement_id, 0, (a, b))
                household.food_stock = self.generational_rng.uniform(0.5, 1.4)
                household.wealth = self.generational_rng.uniform(0.4, 1.5)
                household.debt = self.generational_rng.uniform(0.0, 0.5)
                household.care_capacity = self.generational_rng.uniform(0.7, 1.2)
                romantic = self.generational_rng.random() < 0.67
                self.network.add(
                    SocialTie(
                        a,
                        b,
                        kind="romantic" if romantic else "intimate",
                        strength=self.generational_rng.uniform(0.55, 0.95),
                        started_at=0,
                        sentiment=(
                            self.generational_rng.uniform(0.15, 0.9)
                            if romantic
                            else self.generational_rng.uniform(-0.15, 0.45)
                        ),
                        trust=self.generational_rng.uniform(0.4, 0.9),
                        dependence=self.generational_rng.uniform(0.15, 0.55),
                    )
                )
                self.world.record_event(
                    Event(
                        kind="household_formed",
                        time=0,
                        participants=(a, b),
                        locations=(settlement_id,),
                        impact=0.1,
                        payload={"household_id": household.id},
                    )
                )
            for i in range(len(founders) - 1):
                if self.generational_rng.random() < 0.6:
                    self.network.add(
                        SocialTie(
                            founders[i],
                            founders[i + 1],
                            "friendship",
                            self.generational_rng.uniform(0.25, 0.8),
                            0,
                            sentiment=self.generational_rng.uniform(0.15, 0.85),
                            trust=self.generational_rng.uniform(0.35, 0.85),
                        )
                    )

    def _alive(self, person_id: str) -> bool:
        return bool(self.world.entities[person_id].attributes.get("alive", True))

    def _active_reproductive_pairs(self, year: int) -> list[tuple[str, str, SocialTie]]:
        pairs: list[tuple[str, str, SocialTie]] = []
        seen: set[frozenset[str]] = set()
        for tie in self.network.ties:
            if tie.kind not in {"romantic", "intimate", "partner"} or not tie.active_at(year):
                continue
            pair_key = frozenset((tie.source_id, tie.target_id))
            if pair_key in seen:
                continue
            seen.add(pair_key)
            a, b = tie.source_id, tie.target_id
            if not self._alive(a) or not self._alive(b):
                continue
            pa, pb = self._profiles.get(a), self._profiles.get(b)
            if pa is None or pb is None or pa.gestational == pb.gestational:
                continue
            gestational, other = (a, b) if pa.gestational else (b, a)
            if self.pregnancies.active_for(gestational):
                continue
            pairs.append((gestational, other, tie))
        return pairs

    def _birth(self, year: int, mother_id: str, father_id: str, settlement_id: str) -> str:
        child = Entity(
            kind="person",
            name=f"P-born-{year}-{len(self.person_ids)+1}",
            created_at=year,
            attributes={
                "settlement_id": settlement_id,
                "birth_time": year,
                "alive": True,
                "gestational": self.generational_rng.random() < 0.5,
                "health": self.generational_rng.uniform(0.68, 1.0),
                "fertility": self.generational_rng.uniform(0.6, 1.0),
                "mother_id": mother_id,
                "father_id": father_id,
                "personal_wealth": 0.0,
                "personal_debt": 0.0,
                "social_power": 0.0,
            },
            tags={"person", "materialized_individual"},
        )
        self.world.add_entity(child)
        self.person_ids.append(child.id)
        self._settlement_people.setdefault(settlement_id, set()).add(child.id)
        maternal_household = self.households.household_of(mother_id)
        if maternal_household is not None:
            self.households.move(child.id, maternal_household.id)
        self.kinship.add_person(
            PersonRecord(
                child.id,
                year,
                "gestational" if child.attributes["gestational"] else "non_gestational",
                mother_id,
                father_id,
            )
        )
        self._profiles[child.id] = ReproductiveProfile(
            child.id,
            year,
            bool(child.attributes["gestational"]),
            float(child.attributes["fertility"]),
            float(child.attributes["health"]),
        )
        for parent in (mother_id, father_id):
            self.network.add(
                SocialTie(
                    parent,
                    child.id,
                    "parent_child",
                    1.0,
                    year,
                    sentiment=0.65,
                    trust=0.7,
                    dependence=1.0,
                )
            )
        self.network.add(
            SocialTie(
                mother_id,
                father_id,
                "co_parent",
                0.72,
                year,
                sentiment=0.0,
                trust=0.5,
                dependence=0.55,
            )
        )
        for sibling in self.kinship.siblings(child.id):
            self.network.add(
                SocialTie(
                    child.id,
                    sibling,
                    "sibling",
                    0.82,
                    year,
                    sentiment=0.25,
                    trust=0.55,
                    dependence=0.3,
                )
            )
        self.world.record_event(
            Event(
                kind="birth",
                time=year,
                participants=(mother_id, father_id, child.id),
                locations=(settlement_id,),
                impact=0.45,
                payload={"mother_id": mother_id, "father_id": father_id, "child_id": child.id},
            )
        )
        return child.id

    def _resource_security_for(self, person_id: str) -> float:
        household = self.households.household_of(person_id)
        if household is None:
            return 0.35
        return max(0.02, min(1.0, 0.35 + 0.25 * household.food_stock + 0.20 * household.wealth - 0.18 * household.debt))

    def _run_reproduction(self, year: int) -> None:
        for mother_id, father_id, tie in self._active_reproductive_pairs(year):
            intent = max(
                0.0,
                min(1.0, 0.45 + 0.25 * tie.sentiment + self.generational_rng.uniform(-0.2, 0.2)),
            )
            probability = conception_probability(
                self._profiles[mother_id],
                self._profiles[father_id],
                time=year,
                contact_intensity=tie.strength,
                resource_security=self._resource_security_for(mother_id),
                reproductive_intent=intent,
            )
            if conception_occurs(probability, self.generational_rng):
                pregnancy = self.pregnancies.start(mother_id, father_id, float(year))
                settlement_id = str(self.world.entities[mother_id].attributes["settlement_id"])
                self.world.record_event(
                    Event(
                        kind="conception",
                        time=year,
                        participants=(mother_id, father_id),
                        locations=(settlement_id,),
                        impact=0.12,
                        payload={"pregnancy_id": pregnancy.id, "due_at": pregnancy.due_at},
                    )
                )

    def _resolve_pregnancies(self, year: int) -> None:
        for pregnancy in self.pregnancies.due_by(float(year)):
            mother = self.world.entities[pregnancy.gestational_parent_id]
            settlement_id = str(mother.attributes["settlement_id"])
            outcome = self.pregnancies.resolve(
                pregnancy.id,
                maternal_health=float(mother.attributes["health"]),
                resource_security=self._resource_security_for(pregnancy.gestational_parent_id),
                rng=self.generational_rng,
            )
            if outcome == "live_birth" and self._alive(pregnancy.gestational_parent_id):
                self._birth(year, pregnancy.gestational_parent_id, pregnancy.other_parent_id, settlement_id)
            else:
                self.world.record_event(
                    Event(
                        kind="pregnancy_loss",
                        time=year,
                        participants=(pregnancy.gestational_parent_id, pregnancy.other_parent_id),
                        locations=(settlement_id,),
                        impact=0.3,
                        payload={"pregnancy_id": pregnancy.id},
                    )
                )

    def _update_households(self, year: int, food_ratio: dict[str, float]) -> None:
        for household in self.households.active_households():
            living_members = [person_id for person_id in household.members if self._alive(person_id)]
            dependants = sum(
                1
                for person_id in living_members
                if year - int(self.world.entities[person_id].attributes["birth_time"]) < 14
                or year - int(self.world.entities[person_id].attributes["birth_time"]) > 65
            )
            carers = max(0, len(living_members) - dependants)
            pressure = household.care_pressure(dependants, carers)
            local_food = food_ratio.get(household.settlement_id, 1.0)
            household.food_stock = max(0.0, household.food_stock + 0.25 * (local_food - 0.9) - 0.035 * len(living_members))
            household.wealth = max(0.0, household.wealth + 0.04 * carers - 0.03 * dependants - 0.025 * household.debt)
            if pressure > 1.2 or household.food_stock < 0.25:
                self.world.record_event(
                    Event(
                        kind="household_stress",
                        time=year,
                        participants=tuple(sorted(living_members)),
                        locations=(household.settlement_id,),
                        impact=min(0.7, 0.15 + 0.2 * pressure),
                        payload={
                            "household_id": household.id,
                            "care_pressure": round(pressure, 4),
                            "food_stock": round(household.food_stock, 4),
                        },
                    )
                )

    def _evolve_existing_relations(self, year: int) -> None:
        for index, tie in enumerate(tuple(self.network.ties)):
            if not tie.active_at(year) or tie.kind not in {"romantic", "intimate", "partner", "friendship"}:
                continue
            same_household = self.households.household_of(tie.source_id) is not None and self.households.household_of(tie.source_id) is self.households.household_of(tie.target_id)
            shared_children = bool(set(self.kinship.children(tie.source_id)) & set(self.kinship.children(tie.target_id)))
            context = RelationshipContext(
                interaction_quality=self.generational_rng.uniform(-0.35, 0.55) + (0.12 if same_household else 0.0),
                shared_stress=self.generational_rng.uniform(0.0, 0.55),
                cooperation=(0.25 if shared_children else 0.0) + self.generational_rng.uniform(0.0, 0.35),
                betrayal_signal=max(0.0, self.generational_rng.gauss(0.05, 0.12)),
                separation_pressure=self.generational_rng.uniform(0.0, 0.45) + (0.08 if not same_household else 0.0),
            )
            outcome = evolve_tie(tie, time=year, context=context, rng=self.generational_rng)
            if outcome.changed:
                self.network.ties[index] = outcome.tie
            if outcome.separated:
                settlement_id = str(self.world.entities[tie.source_id].attributes["settlement_id"])
                self.world.record_event(
                    Event(
                        kind="relationship_separated",
                        time=year,
                        participants=(tie.source_id, tie.target_id),
                        locations=(settlement_id,),
                        impact=0.2,
                        payload={"kind": tie.kind},
                    )
                )

    def _inheritance_candidates(self, person_id: str, year: int) -> tuple[str, ...]:
        candidates: set[str] = set(self.kinship.children(person_id))
        candidates.update(self.kinship.siblings(person_id))
        candidates.update(self.network.neighbours(person_id, year))
        candidates.discard(person_id)
        return tuple(sorted(candidate for candidate in candidates if candidate in self.world.entities and self._alive(candidate)))

    def _resolve_inheritance(self, person_id: str, year: int) -> None:
        entity = self.world.entities[person_id]
        candidates = self._inheritance_candidates(person_id, year)
        if not candidates:
            return
        wealth = float(entity.attributes.get("personal_wealth", 0.0))
        debt = float(entity.attributes.get("personal_debt", 0.0))
        estate = Estate(
            deceased_id=person_id,
            opened_at=year,
            items=[
                EstateItem("wealth", "wealth", wealth, divisible=True),
                EstateItem("debt", "debt", debt, divisible=True),
                EstateItem("name", "name_usage", 0.0, divisible=False),
                EstateItem("memory", "memory_custody", 0.0, divisible=False),
            ],
        )
        preferences: dict[str, dict[str, float]] = {}
        if candidates:
            favoured = max(candidates, key=lambda candidate: self.network.connection_strength(person_id, candidate, year))
            preferences = {
                "wealth": {favoured: 0.8},
                "name_usage": {favoured: 0.65},
                "memory_custody": {favoured: 0.7},
            }
        power = {candidate: float(self.world.entities[candidate].attributes.get("social_power", 0.0)) for candidate in candidates}
        norms = {candidate: min(1.0, self.kinship.biological_relatedness_hint(person_id, candidate) * 1.4) for candidate in candidates}
        estate.claims = build_candidate_claims(
            estate,
            candidate_ids=candidates,
            kinship=self.kinship,
            network=self.network,
            time=year,
            expressed_preferences=preferences,
            norm_bias=norms,
            power=power,
        )
        transfers = resolve_estate(estate, rng=self.generational_rng)
        self.inheritance_transfers.extend(transfers)
        for transfer in transfers:
            recipient = self.world.entities[transfer.to_id]
            if transfer.item_key == "wealth":
                recipient.attributes["personal_wealth"] = float(recipient.attributes.get("personal_wealth", 0.0)) + wealth * transfer.share
            elif transfer.item_key == "debt":
                recipient.attributes["personal_debt"] = float(recipient.attributes.get("personal_debt", 0.0)) + debt * transfer.share
            elif transfer.item_key == "name_usage" and entity.attributes.get("name_claim"):
                recipient.attributes["name_claim"] = entity.attributes["name_claim"]
            self.world.record_event(
                Event(
                    kind="inheritance_transfer",
                    time=year,
                    participants=(person_id, transfer.to_id),
                    locations=(str(entity.attributes["settlement_id"]),),
                    impact=0.22 if transfer.contested else 0.12,
                    payload={
                        "item_key": transfer.item_key,
                        "share": round(transfer.share, 5),
                        "contested": transfer.contested,
                        "score": round(transfer.winning_score, 5),
                    },
                )
            )

    def _run_mortality(self, year: int) -> None:
        for person_id in tuple(self.person_ids):
            if not self._alive(person_id):
                continue
            entity = self.world.entities[person_id]
            age = year - int(entity.attributes["birth_time"])
            health = float(entity.attributes["health"])
            household = self.households.household_of(person_id)
            care_modifier = 0.0
            if household is not None and household.food_stock < 0.2:
                care_modifier = 0.004
            risk = 0.0008 + max(0, age - 45) ** 2 / 150000.0 + (1.0 - health) * 0.006 + care_modifier
            if age < 5:
                risk += 0.006
            if self.generational_rng.random() < min(0.5, risk):
                self._resolve_inheritance(person_id, year)
                entity.attributes["alive"] = False
                record = self.kinship.people[person_id]
                self.kinship.people[person_id] = PersonRecord(
                    record.id,
                    record.birth_time,
                    record.sex,
                    record.mother_id,
                    record.father_id,
                    year,
                )
                self.households.remove_person(person_id)
                self.world.record_event(
                    Event(
                        kind="death",
                        time=year,
                        participants=(person_id,),
                        locations=(str(entity.attributes["settlement_id"]),),
                        impact=0.35,
                        payload={"age": age},
                    )
                )

    def _evolve_social_network(self, year: int) -> None:
        for settlement_id, people in self._settlement_people.items():
            alive = [
                person_id
                for person_id in people
                if self._alive(person_id)
                and year - int(self.world.entities[person_id].attributes["birth_time"]) >= 12
            ]
            if len(alive) < 2:
                continue
            for _ in range(max(1, len(alive) // 4)):
                a, b = self.generational_rng.sample(alive, 2)
                if self.network.connection_strength(a, b, year) > 0.2:
                    continue
                related = self.kinship.biological_relatedness_hint(a, b)
                kind = "friendship" if self.generational_rng.random() < 0.72 else "rivalry"
                sentiment = self.generational_rng.uniform(0.1, 0.75) if kind == "friendship" else self.generational_rng.uniform(-0.85, -0.15)
                self.network.add(
                    SocialTie(
                        a,
                        b,
                        kind,
                        self.generational_rng.uniform(0.15, 0.65),
                        year,
                        sentiment=sentiment,
                        trust=self.generational_rng.uniform(0.25, 0.75),
                    )
                )
                self.world.record_event(
                    Event(
                        kind="social_tie_formed",
                        time=year,
                        participants=(a, b),
                        locations=(settlement_id,),
                        impact=0.12,
                        payload={"kind": kind, "biological_relatedness_hint": round(related, 5)},
                    )
                )

    def _lineage_candidates(self) -> tuple[dict[str, object], ...]:
        candidates: list[dict[str, object]] = []
        founders = [person_id for person_id in self.person_ids if not self.kinship.parents(person_id)]
        for root in founders:
            view = lineage_from_roots(self.kinship, (root,), generations=6)
            living = [person_id for person_id in view.members if self._alive(person_id)]
            if len(view.members) < 4:
                continue
            cohesion_values: list[float] = []
            members = list(view.members)
            for index, a in enumerate(members):
                for b in members[index + 1 :]:
                    strength = self.network.connection_strength(a, b, self.config.years)
                    if strength > 0:
                        cohesion_values.append(strength)
            cohesion = sum(cohesion_values) / len(cohesion_values) if cohesion_values else 0.0
            shared_households = len({self.households.membership.get(member) for member in members if self.households.membership.get(member)})
            candidates.append(
                {
                    "root_id": root,
                    "members": len(view.members),
                    "living": len(living),
                    "social_cohesion": round(cohesion, 4),
                    "household_span": shared_households,
                }
            )
        candidates.sort(key=lambda item: (-int(item["members"]), -float(item["social_cohesion"])))
        return tuple(candidates)

    def run(self) -> GenerationalSimulationResult:
        self.initialize()
        for year in range(1, self.config.years + 1):
            self.world.advance_to(year)
            self._resolve_pregnancies(year)
            food_ratio = self._run_harvests(year)
            self._run_demography(year, food_ratio)
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
        return GenerationalSimulationResult(
            social=social,
            kinship=self.kinship,
            network=self.network,
            households=self.households,
            pregnancies=self.pregnancies,
            inheritance_transfers=tuple(self.inheritance_transfers),
            person_ids=tuple(self.person_ids),
            lineage_candidates=self._lineage_candidates(),
        )
