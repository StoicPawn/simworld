from simworld.simulation.first_world import FirstWorldConfig
from simworld.simulation.micro_place_world import MicroPlaceWorldSimulation
from simworld.spatial.activity import PlaceActivityLedger, Presence


def test_place_activity_is_sparse_and_derived() -> None:
    ledger = PlaceActivityLedger()
    ledger.visit(Presence("a", (3, 4), 1, "gather"))
    ledger.visit(Presence("b", (3, 4), 1, "cultivate"))
    ledger.record_interaction((3, 4), cooperation=1.0)

    assert len(ledger.sites) == 1
    view = ledger.views()[0]
    assert view.cell == (3, 4)
    assert view.unique_visitors == 2
    assert view.gathering == 1.0
    assert view.cultivation == 1.0
    assert view.cooperation == 1.0


def test_micro_place_world_puts_people_on_real_land_cells() -> None:
    result = MicroPlaceWorldSimulation(
        FirstWorldConfig(width=40, height=30, settlements=4, years=8, seed=104729)
    ).run()
    world = result.disequilibrium.institutional.material.generational.social.base

    assert result.place_ledger.sites
    assert result.place_views
    for x, y in result.place_ledger.sites:
        assert not world.generated.water[y, x]


def test_micro_place_encounters_reference_exact_cells() -> None:
    result = MicroPlaceWorldSimulation(
        FirstWorldConfig(width=36, height=28, settlements=3, years=12, seed=41)
    ).run()
    events = result.disequilibrium.institutional.material.generational.social.base.world.events
    encounter_events = [
        event for event in events if event.kind in {"cooperative_encounter", "competitive_encounter"}
    ]

    assert result.encounters == len(encounter_events)
    assert encounter_events
    assert all("cell" in event.payload for event in encounter_events)
