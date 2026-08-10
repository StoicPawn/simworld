from simworld.simulation.first_world import FirstWorldConfig
from simworld.simulation.spatial_life_world import SpatialLifeWorldSimulation
from simworld.spatial.grid import CellCoord
from simworld.spatial.presence import PresenceLedger


def test_presence_intensity_is_derived_from_activity() -> None:
    ledger = PresenceLedger()
    cell = CellCoord(4, 7)
    ledger.place("A", cell)
    ledger.place("B", cell)
    ledger.record_encounter(cell, 1)
    ledger.record_productive_use(cell, 3)

    assert ledger.site_intensity(cell) > 0
    assert ledger.active_sites()[0][0] == cell


def test_spatial_life_world_generates_movement_encounters_and_active_sites() -> None:
    result = SpatialLifeWorldSimulation(
        FirstWorldConfig(width=40, height=30, settlements=4, years=12, seed=104729)
    ).run()
    world = result.disequilibrium.institutional.material.generational.social.base.world
    kinds = {event.kind for event in world.events}

    assert result.movement_events > 0
    assert result.encounter_events > 0
    assert "local_movement" in kinds
    assert "spatial_encounter" in kinds
    assert result.presence.active_sites(minimum_intensity=3.0)
    assert len(result.presence.positions) >= 24
