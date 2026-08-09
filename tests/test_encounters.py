from simworld.simulation.encounter_world import EncounterWorldSimulation
from simworld.simulation.first_world import FirstWorldConfig
from simworld.social.encounters import Encounter, EncounterLedger, Visit


def test_encounter_ledger_accumulates_exposure() -> None:
    ledger = EncounterLedger()
    ledger.record_encounter(Encounter("A", "B", "S", 1, intensity=0.2))
    ledger.record_encounter(Encounter("B", "A", "S", 2, intensity=0.3))
    assert ledger.exposure("A", "B") == 0.5
    assert ledger.exposure("B", "A") == 0.5


def test_visit_does_not_itself_create_social_tie() -> None:
    ledger = EncounterLedger()
    ledger.record_visit(Visit("A", "S1", "S2", 1, access=0.8))
    assert ledger.exposure("A", "B") == 0.0


def test_encounter_world_records_encounters_before_derived_ties() -> None:
    simulation = EncounterWorldSimulation(
        FirstWorldConfig(width=40, height=30, settlements=4, years=8, seed=104729)
    )
    result = simulation.run()
    world = result.institutional.material.generational.social.base.world
    encounter_events = [event for event in world.events if event.kind == "social_encounter"]
    derived_ties = [
        event for event in world.events
        if event.kind == "social_tie_formed" and event.payload.get("source") == "encounters"
    ]
    assert encounter_events
    assert simulation.encounters.encounters
    for event in derived_ties:
        assert simulation.encounters.exposure(event.participants[0], event.participants[1]) >= 0.22
