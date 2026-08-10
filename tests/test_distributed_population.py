import numpy as np

from simworld.geography import generate_world
from simworld.population import build_population_field
from simworld.simulation.distributed_population_world import DistributedPopulationWorldSimulation
from simworld.simulation.first_world import FirstWorldConfig
from simworld.spatial import GridSpec


def test_population_field_distributes_without_settlement_objects() -> None:
    generated = generate_world(GridSpec(width=32, height=24, cell_size_m=5000.0, chunk_size=16), seed=104729)
    field = build_population_field(generated, total_population=12000.0, rng=np.random.default_rng(7))
    assert abs(field.total_population - 12000.0) < 1e-6
    assert np.all(field.population[generated.water] == 0.0)
    assert np.count_nonzero(field.population > 1.0) > 10
    assert float(field.population.max()) > float(field.population[field.population > 0].min())


def test_population_field_evolves_locally_without_losing_nonnegativity() -> None:
    generated = generate_world(GridSpec(width=28, height=22, cell_size_m=5000.0, chunk_size=16), seed=104729)
    field = build_population_field(generated, total_population=8000.0, rng=np.random.default_rng(11))
    before = field.population.copy()
    field.step(np.random.default_rng(12))
    assert np.all(field.population >= 0.0)
    assert np.all(field.population[generated.water] == 0.0)
    assert not np.array_equal(before, field.population)


def test_materialized_households_are_decoupled_from_bootstrap_sites() -> None:
    result = DistributedPopulationWorldSimulation(
        FirstWorldConfig(width=42, height=32, settlements=4, years=8, seed=104729)
    ).run()
    households = result.base.base.base.institutional.material.generational.households.active_households()
    assert result.population_field.total_population > 0
    assert result.bootstrap_home_overlap < len(households)
    assert result.base.nuclei
    world = result.base.base.base.institutional.material.generational.social.base.world
    assert any(event.kind == "background_population_distributed" for event in world.events)
    assert any(event.kind == "background_population_change" for event in world.events)
