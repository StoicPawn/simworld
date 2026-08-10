from __future__ import annotations

import numpy as np
import pytest

from simworld.population.field import PopulationField
from simworld.population.refinement import PopulationRefinementLedger, step_unmaterialized_population
from simworld.simulation.first_world import FirstWorldConfig
from simworld.simulation.refined_population_world import RefinedPopulationWorldSimulation
from simworld.spatial import CellCoord


def _field() -> PopulationField:
    return PopulationField(
        population=np.array([[10.0, 8.0], [4.0, 0.0]], dtype=np.float64),
        capacity=np.array([[20.0, 20.0], [12.0, 0.0]], dtype=np.float64),
        suitability=np.array([[0.8, 0.7], [0.5, 0.0]], dtype=np.float64),
        water=np.array([[False, False], [False, True]], dtype=np.bool_),
    )


def test_materialization_changes_resolution_not_total_population() -> None:
    field = _field()
    ledger = PopulationRefinementLedger()
    before = field.total_population

    ledger.materialize_existing(field, "p1", CellCoord(0, 0), time=0)
    ledger.materialize_existing(field, "p2", CellCoord(0, 0), time=0)

    assert field.total_population == before
    assert field.total_reserved_population == 2.0
    assert field.total_unmaterialized_population == before - 2.0
    assert field.total_population == pytest.approx(
        field.total_reserved_population + field.total_unmaterialized_population
    )

    ledger.dematerialize(field, "p2", time=1)
    assert field.total_population == before
    assert field.total_reserved_population == 1.0


def test_detailed_birth_death_and_move_update_physical_population_once() -> None:
    field = _field()
    ledger = PopulationRefinementLedger()
    ledger.materialize_existing(field, "parent", CellCoord(0, 0), time=0)
    initial = field.total_population

    ledger.materialized_birth(field, "child", CellCoord(0, 0), time=1)
    assert field.total_population == initial + 1.0
    assert field.total_reserved_population == 2.0

    source_before = field.population_at(CellCoord(0, 0))
    destination_before = field.population_at(CellCoord(1, 0))
    ledger.move_materialized(field, "child", CellCoord(1, 0))
    assert field.total_population == initial + 1.0
    assert field.population_at(CellCoord(0, 0)) == source_before - 1.0
    assert field.population_at(CellCoord(1, 0)) == destination_before + 1.0

    ledger.materialized_death(field, "child", time=2)
    assert field.total_population == initial
    assert field.total_reserved_population == 1.0


def test_aggregate_step_does_not_demographically_evolve_reserved_people() -> None:
    field = _field()
    ledger = PopulationRefinementLedger()
    ledger.materialize_existing(field, "p1", CellCoord(0, 0), time=0)
    ledger.materialize_existing(field, "p2", CellCoord(0, 0), time=0)
    reserved_before = field.reserved.copy()

    step_unmaterialized_population(field, np.random.default_rng(1234))

    assert np.array_equal(field.reserved, reserved_before)
    assert np.all(field.population + 1e-9 >= field.reserved)
    assert field.total_population == pytest.approx(
        field.total_reserved_population + field.total_unmaterialized_population
    )


def test_cannot_materialize_more_people_than_existing_aggregate_population() -> None:
    field = _field()
    ledger = PopulationRefinementLedger()
    with pytest.raises(ValueError):
        ledger.materialize_existing(field, "crowd", CellCoord(0, 1), time=0, amount=5.0)


def test_integrated_world_keeps_all_living_detailed_people_backed_by_field() -> None:
    simulation = RefinedPopulationWorldSimulation(
        FirstWorldConfig(width=34, height=26, settlements=4, years=8, seed=104729)
    )
    result = simulation.run()
    field = simulation.population_field
    assert field is not None

    living = sorted(person_id for person_id in simulation.person_ids if simulation._alive(person_id))
    active_records = {record.person_id: record for record in result.refinement.active_records()}

    assert set(living) == set(active_records)
    assert result.living_materialized_people == len(living)
    assert result.materialized_population == pytest.approx(float(len(living)))
    assert result.total_population == pytest.approx(
        result.materialized_population + result.unresolved_population
    )
    for person_id in living:
        record = active_records[person_id]
        assert field.reserved_at(record.cell) >= 1.0


def test_living_household_members_move_with_their_population_reservation() -> None:
    simulation = RefinedPopulationWorldSimulation(
        FirstWorldConfig(width=34, height=26, settlements=4, years=10, seed=314159)
    )
    simulation.run()

    for household in simulation.households.active_households():
        home = simulation.household_home_cells[household.id]
        for person_id in household.members:
            if not simulation._alive(person_id):
                continue
            record = simulation.refinement.records[person_id]
            assert record.active
            assert record.cell == home
