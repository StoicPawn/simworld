from __future__ import annotations

from dataclasses import dataclass, field
from random import Random
from uuid import uuid4


def new_pregnancy_id() -> str:
    return f"preg_{uuid4().hex}"


@dataclass(slots=True)
class Pregnancy:
    gestational_parent_id: str
    other_parent_id: str
    conceived_at: float
    due_at: float
    id: str = field(default_factory=new_pregnancy_id)
    active: bool = True
    outcome: str | None = None


@dataclass(slots=True)
class PregnancyRegistry:
    pregnancies: dict[str, Pregnancy] = field(default_factory=dict)

    def start(
        self,
        gestational_parent_id: str,
        other_parent_id: str,
        conceived_at: float,
        *,
        gestation_years: float = 0.75,
    ) -> Pregnancy:
        if self.active_for(gestational_parent_id):
            raise ValueError("gestational parent already has an active pregnancy")
        pregnancy = Pregnancy(
            gestational_parent_id=gestational_parent_id,
            other_parent_id=other_parent_id,
            conceived_at=conceived_at,
            due_at=conceived_at + gestation_years,
        )
        self.pregnancies[pregnancy.id] = pregnancy
        return pregnancy

    def active_for(self, person_id: str) -> tuple[Pregnancy, ...]:
        return tuple(
            p
            for p in self.pregnancies.values()
            if p.active and p.gestational_parent_id == person_id
        )

    def due_by(self, time: float) -> tuple[Pregnancy, ...]:
        return tuple(p for p in self.pregnancies.values() if p.active and p.due_at <= time)

    def resolve(
        self,
        pregnancy_id: str,
        *,
        maternal_health: float,
        resource_security: float,
        rng: Random,
    ) -> str:
        pregnancy = self.pregnancies[pregnancy_id]
        if not pregnancy.active:
            if pregnancy.outcome is None:
                raise ValueError("resolved pregnancy has no outcome")
            return pregnancy.outcome
        viability = 0.72 + 0.18 * max(0.0, min(1.0, maternal_health)) + 0.08 * max(
            0.0, min(1.0, resource_security)
        )
        outcome = "live_birth" if rng.random() < min(0.985, viability) else "pregnancy_loss"
        pregnancy.active = False
        pregnancy.outcome = outcome
        return outcome
