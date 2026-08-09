from __future__ import annotations

from dataclasses import dataclass
from random import Random

from simworld.core.entity import Entity
from simworld.core.event import Event
from simworld.simulation.first_world import FirstWorldConfig
from simworld.simulation.social_world import SocialSimulationResult, SocialWorldSimulation
from simworld.social.kinship import KinshipGraph, PersonRecord, lineage_from_roots
from simworld.social.network import SocialGraph, SocialTie
from simworld.social.reproduction import ReproductiveProfile, conception_occurs, conception_probability


@dataclass(frozen=True, slots=True)
class GenerationalSimulationResult:
    social: SocialSimulationResult
    kinship: KinshipGraph
    network: SocialGraph
    person_ids: tuple[str, ...]
    lineage_candidates: tuple[dict[str, object], ...]


class GenerationalWorldSimulation(SocialWorldSimulation):
    """Adds biological generations and multiplex social networks.

    A family/house is not instantiated as a metaphysical category. Biological descent,
    social ties, memory and later property/recognition can be queried to derive such views.
    """

    def __init__(self, config: FirstWorldConfig) -> None:
        super().__init__(config)
        self.generational_rng = Random(config.seed ^ 0xB10FAMILY)
        self.kinship = KinshipGraph()
        self.network = SocialGraph()
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

            # Initial network is heterogeneous: intimacy is not synonymous with romance.
            pairs = ((0, 1), (2, 3), (4, 5))
            for a_idx, b_idx in pairs:
                a, b = founders[a_idx], founders[b_idx]
                romantic = self.generational_rng.random() < 0.67
                self.network.add(
                    SocialTie(
                        a, b,
                        kind="romantic" if romantic else "intimate",
                        strength=self.generational_rng.uniform(0.55, 0.95),
                        started_at=0,
                        sentiment=self.generational_rng.uniform(0.15, 0.9) if romantic else self.generational_rng.uniform(-0.15, 0.45),
                        trust=self.generational_rng.uniform(0.4, 0.9),
                    )
                )
            for i in range(len(founders) - 1):
                if self.generational_rng.random() < 0.6:
                    self.network.add(
                        SocialTie(
                            founders[i], founders[i + 1], "friendship",
                            strength=self.generational_rng.uniform(0.25, 0.8),
                            started_at=0,
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
            },
            tags={"person", "materialized_individual"},
        )
        self.world.add_entity(child)
        self.person_ids.append(child.id)
        self._settlement_people.setdefault(settlement_id, set()).add(child.id)
        self.kinship.add_person(PersonRecord(child.id, year, "gestational" if child.attributes["gestational"] else "non_gestational", mother_id, father_id))
        self._profiles[child.id] = ReproductiveProfile(
            child.id, year, bool(child.attributes["gestational"]), float(child.attributes["fertility"]), float(child.attributes["health"])
        )
        for parent in (mother_id, father_id):
            self.network.add(SocialTie(parent, child.id, "parent_child", 1.0, year, sentiment=0.65, trust=0.7, dependence=1.0))
        # Prole implies a co-parent relation, not romance or affection.
        self.network.add(SocialTie(mother_id, father_id, "co_parent", 0.72, year, sentiment=0.0, trust=0.5, dependence=0.55))
        for sibling in self.kinship.siblings(child.id):
            self.network.add(SocialTie(child.id, sibling, "sibling", 0.82, year, sentiment=0.25, trust=0.55, dependence=0.3))
        event = Event(
            kind="birth",
            time=year,
            participants=(mother_id, father_id, child.id),
            locations=(settlement_id,),
            impact=0.45,
            payload={"mother_id": mother_id, "father_id": father_id, "child_id": child.id},
        )
        self.world.record_event(event)
        return child.id

    def _run_reproduction(self, year: int) -> None:
        for mother_id, father_id, tie in self._active_reproductive_pairs(year):
            mother = self.world.entities[mother_id]
            settlement_id = str(mother.attributes["settlement_id"])
            house_id = self._house_for_settlement[settlement_id]
            house = self.world.entities[house_id]
            resource_security = max(0.05, min(1.0, float(house.attributes["stability"]) * 0.55 + float(house.attributes["treasury"]) * 0.45))
            intent = max(0.0, min(1.0, 0.45 + 0.25 * tie.sentiment + self.generational_rng.uniform(-0.2, 0.2)))
            probability = conception_probability(
                self._profiles[mother_id], self._profiles[father_id], time=year,
                contact_intensity=tie.strength, resource_security=resource_security, reproductive_intent=intent,
            )
            if conception_occurs(probability, self.generational_rng):
                self._birth(year, mother_id, father_id, settlement_id)

    def _run_mortality(self, year: int) -> None:
        for person_id in tuple(self.person_ids):
            if not self._alive(person_id):
                continue
            entity = self.world.entities[person_id]
            age = year - int(entity.attributes["birth_time"])
            health = float(entity.attributes["health"])
            risk = 0.0008 + max(0, age - 45) ** 2 / 150000.0 + (1.0 - health) * 0.006
            if age < 5:
                risk += 0.006
            if self.generational_rng.random() < min(0.5, risk):
                entity.attributes["alive"] = False
                record = self.kinship.people[person_id]
                self.kinship.people[person_id] = PersonRecord(record.id, record.birth_time, record.sex, record.mother_id, record.father_id, year)
                self.world.record_event(Event(kind="death", time=year, participants=(person_id,), locations=(str(entity.attributes["settlement_id"]),), impact=0.35, payload={"age": age}))

    def _evolve_social_network(self, year: int) -> None:
        for settlement_id, people in self._settlement_people.items():
            alive = [p for p in people if self._alive(p) and year - int(self.world.entities[p].attributes["birth_time"]) >= 12]
            if len(alive) < 2:
                continue
            for _ in range(max(1, len(alive) // 4)):
                a, b = self.generational_rng.sample(alive, 2)
                if self.network.connection_strength(a, b, year) > 0.2:
                    continue
                related = self.kinship.biological_relatedness_hint(a, b)
                kind = "friendship" if self.generational_rng.random() < 0.72 else "rivalry"
                sentiment = self.generational_rng.uniform(0.1, 0.75) if kind == "friendship" else self.generational_rng.uniform(-0.85, -0.15)
                self.network.add(SocialTie(a, b, kind, self.generational_rng.uniform(0.15, 0.65), year, sentiment=sentiment, trust=self.generational_rng.uniform(0.25, 0.75)))
                self.world.record_event(Event(kind="social_tie_formed", time=year, participants=(a, b), locations=(settlement_id,), impact=0.12, payload={"kind": kind, "biological_relatedness_hint": round(related, 5)}))

    def _lineage_candidates(self) -> tuple[dict[str, object], ...]:
        candidates: list[dict[str, object]] = []
        founders = [p for p in self.person_ids if not self.kinship.parents(p)]
        for root in founders:
            view = lineage_from_roots(self.kinship, (root,), generations=6)
            living = [p for p in view.members if self._alive(p)]
            if len(view.members) < 4:
                continue
            cohesion_values: list[float] = []
            members = list(view.members)
            for i, a in enumerate(members):
                for b in members[i + 1:]:
                    strength = self.network.connection_strength(a, b, self.config.years)
                    if strength > 0:
                        cohesion_values.append(strength)
            cohesion = sum(cohesion_values) / len(cohesion_values) if cohesion_values else 0.0
            candidates.append({"root_id": root, "members": len(view.members), "living": len(living), "social_cohesion": round(cohesion, 4)})
        candidates.sort(key=lambda x: (-int(x["members"]), -float(x["social_cohesion"])))
        return tuple(candidates)

    def run(self) -> GenerationalSimulationResult:
        self.initialize()
        for year in range(1, self.config.years + 1):
            food_ratio = self._run_harvests(year)
            self._run_demography(year, food_ratio)
            for settlement_id in self.settlement_ids:
                petition = self._experience_and_request(year, settlement_id, food_ratio[settlement_id])
                self._apply_house_action(year, settlement_id, petition)
                self._verify_reports(year, settlement_id, food_ratio[settlement_id])
            self._run_migration(year, food_ratio)
            self._run_discoveries(year)
            self._run_reproduction(year)
            self._run_mortality(year)
            self._evolve_social_network(year)
            self._transmit_memory(year)
        social = SocialSimulationResult(
            base=super(SocialWorldSimulation, self).run() if False else self._result_without_rerun(),
            house_ids=tuple(self.house_ids), representative_ids=tuple(self.representative_ids), social_memory=self.social_memory,
        )
        return GenerationalSimulationResult(social, self.kinship, self.network, tuple(self.person_ids), self._lineage_candidates())

    def _result_without_rerun(self):
        from simworld.simulation.first_world import SimulationResult
        return SimulationResult(self.config, self.generated, self.world, tuple(self.settlement_ids))
