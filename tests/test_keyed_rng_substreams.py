from __future__ import annotations

import numpy as np

from simworld.core.randomness import SeedStreams
from simworld.simulation.authoritative_population_world import AuthoritativePopulationWorldSimulation
from simworld.simulation.first_world import FirstWorldConfig


def test_same_semantic_key_recreates_same_stream() -> None:
    streams = SeedStreams(104729)
    first = streams.numpy("demography", 12).normal(size=8)
    second = streams.numpy("demography", 12).normal(size=8)
    assert np.array_equal(first, second)


def test_different_keys_do_not_share_random_state() -> None:
    streams = SeedStreams(104729)
    target_before = streams.python("residence", "household_0001", 7, "move").random()

    unrelated = streams.python("residence", "household_9999", 7, "move")
    for _ in range(10_000):
        unrelated.random()

    target_after = streams.python("residence", "household_0001", 7, "move").random()
    assert target_before == target_after


def test_key_types_are_stable_and_distinct() -> None:
    streams = SeedStreams(17)
    assert streams.seed("1") != streams.seed(1)
    assert streams.seed("actor", 2, "year", 3) == streams.seed("actor", 2, "year", 3)


def test_unrelated_refinement_draws_do_not_perturb_authoritative_world() -> None:
    config = FirstWorldConfig(width=30, height=22, settlements=4, years=5, seed=104729)
    first = AuthoritativePopulationWorldSimulation(config)
    second = AuthoritativePopulationWorldSimulation(config)

    second.initialize()
    extra = second.seed_streams.numpy("adaptive-detail", "unrelated-region", 99)
    extra.random(50_000)

    result_a = first.run()
    result_b = second.run()

    assert np.array_equal(
        np.round(result_a.base.population_field.population, 12),
        np.round(result_b.base.population_field.population, 12),
    )
    assert result_a.field_total == result_b.field_total
    assert result_a.base.base.household_home_cells == result_b.base.base.household_home_cells
    assert result_a.base.base.residence_shifts == result_b.base.base.residence_shifts
    assert result_a.base.base.construction_events == result_b.base.base.construction_events
