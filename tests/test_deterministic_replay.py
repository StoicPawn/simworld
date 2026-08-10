from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

import numpy as np

from simworld.simulation.authoritative_population_world import AuthoritativePopulationWorldSimulation
from simworld.simulation.first_world import FirstWorldConfig


OPAQUE_ID = re.compile(r"^([a-zA-Z]+)_[0-9a-f]{24,40}$")


class Canonicalizer:
    def __init__(self) -> None:
        self._ids: dict[str, str] = {}
        self._counts: dict[str, int] = {}

    def value(self, value: Any) -> Any:
        if isinstance(value, str):
            match = OPAQUE_ID.match(value)
            if not match:
                return value
            if value not in self._ids:
                prefix = match.group(1)
                number = self._counts.get(prefix, 0) + 1
                self._counts[prefix] = number
                self._ids[value] = f"{prefix}_opaque_{number:06d}"
            return self._ids[value]
        if isinstance(value, Mapping):
            return tuple(sorted((str(key), self.value(item)) for key, item in value.items()))
        if isinstance(value, (tuple, list)):
            return tuple(self.value(item) for item in value)
        if isinstance(value, set):
            return tuple(sorted(self.value(item) for item in value))
        if isinstance(value, float):
            return round(value, 10)
        return value


def semantic_fingerprint(simulation: AuthoritativePopulationWorldSimulation) -> tuple[object, ...]:
    result = simulation.run()
    canonical = Canonicalizer()
    world = result.base.base.base.base.institutional.material.generational.social.base.world

    entities = tuple(
        (
            canonical.value(entity.id),
            entity.kind,
            entity.name,
            entity.created_at,
            entity.active,
            canonical.value(entity.attributes),
            tuple(sorted(entity.tags)),
        )
        for entity in world.entities.values()
    )
    events = tuple(
        (
            event.kind,
            event.time,
            canonical.value(event.participants),
            canonical.value(event.locations),
            canonical.value(event.causes),
            round(event.impact, 10),
            canonical.value(event.payload),
        )
        for event in world.events
    )
    homes = tuple(
        sorted(
            (canonical.value(household_id), cell.x, cell.y)
            for household_id, cell in result.base.base.household_home_cells.items()
        )
    )
    nuclei = tuple(
        (
            nucleus.centre.x,
            nucleus.centre.y,
            tuple((cell.x, cell.y) for cell in nucleus.cells),
            nucleus.actors,
            nucleus.persistence,
            round(nucleus.residence_signal, 8),
            round(nucleus.production_signal, 8),
            round(nucleus.exchange_signal, 8),
            round(nucleus.infrastructure_signal, 8),
            round(nucleus.conflict_signal, 8),
        )
        for nucleus in result.base.base.nuclei
    )
    field = result.base.population_field
    population_bytes = np.round(field.population, 10).tobytes()
    return entities, events, homes, nuclei, population_bytes


def test_same_seed_replays_same_semantic_history_in_one_process() -> None:
    config = FirstWorldConfig(width=34, height=26, settlements=4, years=8, seed=104729)
    first = semantic_fingerprint(AuthoritativePopulationWorldSimulation(config))
    second = semantic_fingerprint(AuthoritativePopulationWorldSimulation(config))
    assert first == second


def test_different_seed_changes_semantic_history() -> None:
    first = semantic_fingerprint(
        AuthoritativePopulationWorldSimulation(FirstWorldConfig(width=32, height=24, settlements=4, years=5, seed=104729))
    )
    second = semantic_fingerprint(
        AuthoritativePopulationWorldSimulation(FirstWorldConfig(width=32, height=24, settlements=4, years=5, seed=104730))
    )
    assert first != second
