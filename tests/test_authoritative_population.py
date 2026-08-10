from simworld.simulation.authoritative_population_world import AuthoritativePopulationWorldSimulation
from simworld.simulation.first_world import FirstWorldConfig


def test_legacy_population_is_only_a_derived_summary() -> None:
    simulation = AuthoritativePopulationWorldSimulation(
        FirstWorldConfig(width=36, height=28, settlements=4, years=2, seed=104729)
    )
    simulation.initialize()
    assert simulation.population_field is not None
    field_before = simulation.population_field.total_population
    settlement_id = simulation.settlement_ids[0]
    simulation.world.entities[settlement_id].attributes["population"] = 9_999_999

    assert simulation.population_field.total_population == field_before
    simulation._sync_legacy_population_summaries(time=0, emit_events=False)
    assert simulation.world.entities[settlement_id].attributes["population"] != 9_999_999
    assert simulation.world.entities[settlement_id].attributes["population_source"] == "derived_from_population_field"


def test_authoritative_field_advances_once_and_summaries_cover_population() -> None:
    result = AuthoritativePopulationWorldSimulation(
        FirstWorldConfig(width=38, height=30, settlements=4, years=5, seed=104729)
    ).run()
    world = result.base.base.base.base.institutional.material.generational.social.base.world
    background_events = [event for event in world.events if event.kind == "background_population_change"]
    assert len(background_events) == 5
    assert all(event.payload.get("authoritative") is True for event in background_events)
    assert abs(result.legacy_summary_total - result.field_total) <= max(4.0, 0.002 * result.field_total)
    assert all(view.cell_count > 0 for view in result.summaries.values())


def test_old_settlement_migration_no_longer_mutates_population_summaries() -> None:
    simulation = AuthoritativePopulationWorldSimulation(
        FirstWorldConfig(width=36, height=28, settlements=4, years=2, seed=104729)
    )
    simulation.initialize()
    assert simulation.population_field is not None
    before_field = simulation.population_field.population.copy()
    before = {sid: simulation.world.entities[sid].attributes["population"] for sid in simulation.settlement_ids}
    simulation._run_migration(1, {sid: 0.2 for sid in simulation.settlement_ids})
    after = {sid: simulation.world.entities[sid].attributes["population"] for sid in simulation.settlement_ids}
    assert before == after
    assert (simulation.population_field.population == before_field).all()
