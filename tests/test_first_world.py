from __future__ import annotations

import numpy as np

from simworld.geography import generate_world
from simworld.simulation import FirstWorldConfig, FirstWorldSimulation
from simworld.spatial import GridSpec


def test_geography_is_deterministic_and_spatially_varied() -> None:
    spec = GridSpec(width=40, height=30, cell_size_m=5_000.0, chunk_size=16)
    a = generate_world(spec, seed=77)
    b = generate_world(spec, seed=77)

    assert np.array_equal(a.elevation_m, b.elevation_m)
    assert np.array_equal(a.water, b.water)
    assert np.array_equal(a.ore, b.ore)
    assert 0.15 < float(np.mean(a.water)) < 0.6
    assert float(np.std(a.elevation_m)) > 100.0
    assert float(np.max(a.habitability)) > float(np.mean(a.habitability))


def test_physical_truth_can_exist_before_discovery() -> None:
    sim = FirstWorldSimulation(
        FirstWorldConfig(width=42, height=30, settlements=6, years=0, seed=13, chunk_size=16)
    )
    result = sim.run()

    assert float(np.max(result.generated.ore)) > 0.0
    assert all(
        result.world.entities[entity_id].attributes["known_ore"] is False
        for entity_id in result.settlement_ids
    )


def test_first_world_produces_parallel_local_histories() -> None:
    config = FirstWorldConfig(width=48, height=36, settlements=6, years=8, seed=9, chunk_size=16)
    result = FirstWorldSimulation(config).run()

    harvests = [event for event in result.world.events if event.kind == "harvest"]
    demographic = [event for event in result.world.events if event.kind == "population_change"]

    assert len(harvests) == len(result.settlement_ids) * config.years
    assert len(demographic) == len(result.settlement_ids) * config.years
    assert len({event.time for event in harvests if event.time == 1}) == 1
    assert sum(event.time == 1 for event in harvests) == len(result.settlement_ids)
    assert all(event.causes for event in demographic)


def test_settlements_emerge_only_on_land_and_habitable_cells() -> None:
    result = FirstWorldSimulation(
        FirstWorldConfig(width=52, height=40, settlements=7, years=1, seed=202, chunk_size=16)
    ).run()

    for entity_id in result.settlement_ids:
        entity = result.world.entities[entity_id]
        x = int(entity.attributes["x"])
        y = int(entity.attributes["y"])
        assert not bool(result.generated.water[y, x])
        assert float(result.generated.habitability[y, x]) > 0.18


def test_longer_run_can_create_cross_settlement_events() -> None:
    result = FirstWorldSimulation(
        FirstWorldConfig(width=56, height=42, settlements=8, years=55, seed=104729, chunk_size=16)
    ).run()

    cross = [event for event in result.world.events if len(event.participants) > 1]
    assert cross, "expected at least one migration/intersection between local histories"
    assert any(event.kind == "migration" and len(event.causes) == 2 for event in cross)
