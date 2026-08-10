import numpy as np

from simworld.geography.hydrology import flow_accumulation
from simworld.simulation.first_world import FirstWorldConfig
from simworld.simulation.microgeography_world import MicrogeographyWorldSimulation
from simworld.spatial import CellCoord
from simworld.spatial.activity import CellActivityLedger, derive_place_views


def test_flow_accumulation_concentrates_downstream() -> None:
    elevation = np.array([[9.0, 8.0, 7.0], [8.0, 6.0, 4.0], [7.0, 4.0, 1.0]], dtype=np.float32)
    water = np.zeros_like(elevation, dtype=np.bool_)
    rainfall = np.ones_like(elevation, dtype=np.float32)
    flow = flow_accumulation(elevation, water, rainfall)
    assert flow[2, 2] > flow[0, 0]
    assert 0.0 <= float(flow.min()) <= float(flow.max()) <= 1.0


def test_place_views_are_derived_from_sparse_activity() -> None:
    ledger = CellActivityLedger()
    cell = CellCoord(3, 4)
    ledger.record(cell, time=1, actor_id="a", kind="visit")
    ledger.record(cell, time=2, actor_id="b", kind="exchange", amount=2.0)
    ledger.record(cell, time=3, actor_id="a", kind="cultivate", amount=1.5)
    views = derive_place_views(ledger, min_activity=2.0)
    assert len(views) == 1
    assert views[0].actors == 2
    assert views[0].exchange_signal == 2.0
    assert views[0].production_signal == 1.5


def test_microgeography_world_creates_cell_history_and_encounters() -> None:
    result = MicrogeographyWorldSimulation(FirstWorldConfig(width=40, height=30, settlements=4, years=8, seed=104729)).run()
    world = result.base.institutional.material.generational.social.base.world
    generated = result.base.institutional.material.generational.social.base.generated
    assert result.activity.cells
    assert result.person_cells
    assert result.place_views
    assert any(event.kind == "micro_encounter" for event in world.events)
    assert generated.river_strength.shape == (30, 40)
    assert generated.coastal_food.shape == (30, 40)
