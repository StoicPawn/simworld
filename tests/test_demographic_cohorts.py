from __future__ import annotations

import numpy as np
import pytest

from simworld.population.cohorts import build_demographic_cohorts
from simworld.population.field import PopulationField
from simworld.simulation.cohort_population_world import CohortPopulationWorldSimulation
from simworld.simulation.first_world import FirstWorldConfig
from simworld.spatial import CellCoord


def _field() -> PopulationField:
    return PopulationField(
        population=np.array([[100.0, 80.0], [40.0, 0.0]], dtype=np.float64),
        capacity=np.array([[180.0, 140.0], [90.0, 0.0]], dtype=np.float64),
        suitability=np.array([[0.8, 0.7], [0.5, 0.0]], dtype=np.float64),
        water=np.array([[False, False], [False, True]], dtype=np.bool_),
    )


def test_cohorts_exactly_partition_unresolved_population() -> None:
    field = _field()
    field.reserve(CellCoord(0, 0), 7.0)
    cohorts = build_demographic_cohorts(field, np.random.default_rng(1))

    cohorts.assert_consistent_with(field)
    assert cohorts.total_population == pytest.approx(field.total_unmaterialized_population)
    assert cohorts.totals_by_age().sum() == pytest.approx(cohorts.total_population)
    assert cohorts.totals_by_reproductive_class().sum() == pytest.approx(cohorts.total_population)


def test_cohort_step_rebuilds_authoritative_total_from_unresolved_plus_reserved() -> None:
    field = _field()
    field.reserve(CellCoord(0, 0), 5.0)
    cohorts = build_demographic_cohorts(field, np.random.default_rng(2))
    reserved_before = field.total_reserved_population

    stats = cohorts.step(field, np.random.default_rng(3))

    assert field.total_reserved_population == reserved_before
    cohorts.assert_consistent_with(field)
    assert field.total_population == pytest.approx(
        cohorts.total_population + field.total_reserved_population
    )
    assert stats["births"] >= 0.0
    assert stats["deaths"] >= 0.0
    assert np.all(cohorts.counts >= 0.0)


def test_cohort_composition_changes_through_aging_birth_and_mortality() -> None:
    field = _field()
    cohorts = build_demographic_cohorts(field, np.random.default_rng(4))
    before = cohorts.totals_by_age().copy()

    for year in range(1, 6):
        cohorts.step(field, np.random.default_rng(100 + year))

    after = cohorts.totals_by_age()
    assert not np.allclose(before / before.sum(), after / after.sum())
    cohorts.assert_consistent_with(field)


def test_integrated_world_keeps_cohorts_equal_to_unresolved_population() -> None:
    simulation = CohortPopulationWorldSimulation(
        FirstWorldConfig(width=34, height=26, settlements=4, years=10, seed=104729)
    )
    result = simulation.run()
    field = simulation.population_field
    assert field is not None

    result.cohorts.assert_consistent_with(field, atol=1e-6)
    assert result.cohorts.total_population == pytest.approx(result.base.unresolved_population)
    assert result.base.materialized_population == pytest.approx(float(result.base.living_materialized_people))
    assert result.unresolved_children > 0.0
    assert result.unresolved_working_age > 0.0
    assert result.unresolved_older > 0.0
