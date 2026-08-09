from __future__ import annotations

from random import Random

from simworld.core.event import Event
from simworld.simulation.disequilibrium_world import DisequilibriumWorldSimulation
from simworld.simulation.first_world import FirstWorldConfig
from simworld.social.encounters import Encounter, EncounterLedger, Visit
from simworld.social.network import SocialTie


class EncounterWorldSimulation(DisequilibriumWorldSimulation):
    """Create new social ties only after shared-space encounters."""

    def __init__(self, config: FirstWorldConfig) -> None:
        super().__init__(config)
        self.encounter_rng = Random(config.seed ^ 0xEAC017)
        self.encounters = EncounterLedger()

    def _eligible(self, settlement_id: str, year: int) -> list[str]:
        return [
            person_id for person_id in self._settlement_people.get(settlement_id, set())
            if self._alive(person_id)
            and year - int(self.world.entities[person_id].attributes["birth_time"]) >= 12
        ]

    def _meet(self, a: str, b: str, location: str, year: int, context: str, intensity: float) -> None:
        encounter = Encounter(a, b, location, year, context, intensity)
        self.encounters.record_encounter(encounter)
        exposure = self.encounters.exposure(a, b)
        self.world.record_event(Event(
            kind="social_encounter",
            time=year,
            participants=(a, b),
            locations=(location,),
            impact=0.04,
            payload={"context": context, "intensity": round(intensity, 4), "exposure": round(exposure, 4)},
        ))
        if self.network.connection_strength(a, b, year) > 0.2 or exposure < 0.22:
            return
        if self.encounter_rng.random() >= min(0.68, 0.08 + 0.32 * exposure):
            return
        kind = "friendship" if self.encounter_rng.random() < 0.72 else "rivalry"
        sentiment = self.encounter_rng.uniform(0.08, 0.78) if kind == "friendship" else self.encounter_rng.uniform(-0.82, -0.12)
        related = self.kinship.biological_relatedness_hint(a, b)
        self.network.add(SocialTie(
            a, b, kind,
            self.encounter_rng.uniform(0.14, 0.58),
            year,
            sentiment=sentiment,
            trust=self.encounter_rng.uniform(0.22, 0.72),
        ))
        self.world.record_event(Event(
            kind="social_tie_formed",
            time=year,
            participants=(a, b),
            locations=(location,),
            impact=0.12,
            payload={"kind": kind, "source": "encounters", "exposure": round(exposure, 4), "biological_relatedness_hint": round(related, 5)},
        ))

    def _destination(self, origin: str) -> tuple[str, float] | None:
        candidates = []
        for destination in self.settlement_ids:
            if destination == origin:
                continue
            access = self._settlement_exchange_factor(*sorted((origin, destination)))
            if access > 0.08:
                candidates.append((destination, access))
        if not candidates:
            return None
        total = sum(access for _, access in candidates)
        draw = self.encounter_rng.random() * total
        running = 0.0
        for candidate in candidates:
            running += candidate[1]
            if draw <= running:
                return candidate
        return candidates[-1]

    def _evolve_social_network(self, year: int) -> None:
        for settlement_id in self.settlement_ids:
            people = self._eligible(settlement_id, year)
            if len(people) >= 2:
                for _ in range(max(1, len(people) // 3)):
                    a, b = self.encounter_rng.sample(people, 2)
                    self._meet(a, b, settlement_id, year, "local", self.encounter_rng.uniform(0.08, 0.42))

            for actor_id in people:
                if self.encounter_rng.random() >= 0.07:
                    continue
                destination = self._destination(settlement_id)
                if destination is None:
                    continue
                destination_id, access = destination
                if self.encounter_rng.random() >= 0.20 * access:
                    continue
                visit = Visit(actor_id, settlement_id, destination_id, year, "travel", access)
                self.encounters.record_visit(visit)
                self.world.record_event(Event(
                    kind="person_visit",
                    time=year,
                    participants=(actor_id,),
                    locations=(settlement_id, destination_id),
                    impact=0.06,
                    payload={"access": round(access, 4)},
                ))
                locals_there = [x for x in self._eligible(destination_id, year) if x != actor_id]
                if locals_there:
                    self._meet(actor_id, self.encounter_rng.choice(locals_there), destination_id, year, "travel", self.encounter_rng.uniform(0.12, 0.5) * access)
