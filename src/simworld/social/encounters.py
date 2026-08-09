from __future__ import annotations

from dataclasses import dataclass, field
from collections import defaultdict


@dataclass(frozen=True, slots=True)
class Visit:
    actor_id: str
    origin_id: str
    destination_id: str
    time: int
    purpose: str = "unspecified"
    access: float = 1.0


@dataclass(frozen=True, slots=True)
class Encounter:
    actor_a: str
    actor_b: str
    location_id: str
    time: int
    context: str = "local"
    intensity: float = 0.1

    def pair_key(self) -> tuple[str, str]:
        return tuple(sorted((self.actor_a, self.actor_b)))


@dataclass(slots=True)
class EncounterLedger:
    encounters: list[Encounter] = field(default_factory=list)
    visits: list[Visit] = field(default_factory=list)
    _pair_exposure: dict[tuple[str, str], float] = field(default_factory=lambda: defaultdict(float))

    def record_visit(self, visit: Visit) -> None:
        self.visits.append(visit)

    def record_encounter(self, encounter: Encounter) -> None:
        if encounter.actor_a == encounter.actor_b:
            raise ValueError("an actor cannot encounter itself")
        if encounter.intensity <= 0:
            raise ValueError("encounter intensity must be positive")
        self.encounters.append(encounter)
        self._pair_exposure[encounter.pair_key()] += encounter.intensity

    def exposure(self, actor_a: str, actor_b: str) -> float:
        return self._pair_exposure.get(tuple(sorted((actor_a, actor_b))), 0.0)

    def encounters_at(self, location_id: str, time: int | None = None) -> tuple[Encounter, ...]:
        return tuple(
            encounter
            for encounter in self.encounters
            if encounter.location_id == location_id and (time is None or encounter.time == time)
        )

    def visits_by(self, actor_id: str) -> tuple[Visit, ...]:
        return tuple(visit for visit in self.visits if visit.actor_id == actor_id)
