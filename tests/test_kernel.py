import random

import pytest

from simworld import Entity, Event, SimulationEngine, WorldState
from simworld.core.relevance import ResolutionLevel


def test_multiple_events_can_exist_at_same_time() -> None:
    world = WorldState()
    north = Entity(kind="region", name="North")
    south = Entity(kind="region", name="South")
    world.add_entity(north)
    world.add_entity(south)

    engine = SimulationEngine(world, seed=1)
    engine.schedule(10, lambda world, rng: Event(kind="storm", time=10, locations=(north.id,)))
    engine.schedule(10, lambda world, rng: Event(kind="festival", time=10, locations=(south.id,)))

    emitted = engine.run_until(10)

    assert [event.kind for event in emitted] == ["storm", "festival"]
    assert all(event.time == 10 for event in emitted)


def test_causal_chains_can_merge() -> None:
    world = WorldState()
    region = Entity(kind="region", name="Delta")
    world.add_entity(region)

    drought = Event(kind="drought", time=1, locations=(region.id,))
    dispute = Event(kind="trade_dispute", time=1, locations=(region.id,))
    world.record_event(drought)
    world.record_event(dispute)
    unrest = Event(
        kind="unrest",
        time=4,
        locations=(region.id,),
        causes=(drought.id, dispute.id),
    )
    world.record_event(unrest)

    assert world.causal_children(drought.id) == (unrest,)
    assert world.causal_children(dispute.id) == (unrest,)


def test_unrelated_event_remains_outside_causal_chain() -> None:
    world = WorldState()
    a = Entity(kind="region", name="A")
    b = Entity(kind="region", name="B")
    world.add_entity(a)
    world.add_entity(b)

    root = Event(kind="discovery", time=2, locations=(a.id,))
    unrelated = Event(kind="birth", time=2, locations=(b.id,))
    consequence = Event(kind="migration", time=3, locations=(a.id,), causes=(root.id,))
    for event in (root, unrelated, consequence):
        world.record_event(event)

    assert world.causal_descendants(root.id) == (consequence,)
    assert unrelated not in world.causal_descendants(root.id)


def test_relevance_can_rise_and_decay() -> None:
    world = WorldState()
    city = Entity(kind="settlement", name="Harbor")
    world.add_entity(city)

    for time in range(4):
        world.record_event(Event(kind="market_event", time=time, locations=(city.id,), impact=3.0))

    assert world.resolution_of(city.id) >= ResolutionLevel.DETAILED
    score_then = world.relevance.score(city.id, at_time=world.current_time)
    score_later = world.relevance.score(city.id, at_time=500)
    assert score_later < score_then


def test_seeded_engine_is_reproducible() -> None:
    def run(seed: int) -> float:
        world = WorldState()
        region = Entity(kind="region", name="R")
        world.add_entity(region)
        engine = SimulationEngine(world, seed=seed)

        def factory(world: WorldState, rng: random.Random) -> Event:
            return Event(kind="sample", time=1, locations=(region.id,), payload={"x": rng.random()})

        engine.schedule(1, factory)
        (event,) = engine.run_until(1)
        return float(event.payload["x"])

    assert run(99) == run(99)
    assert run(99) != run(100)


def test_unknown_entities_and_future_causes_are_rejected() -> None:
    world = WorldState()
    with pytest.raises(KeyError):
        world.record_event(Event(kind="ghost", time=1, participants=("missing",)))

    region = Entity(kind="region", name="R")
    world.add_entity(region)
    future = Event(kind="future", time=10, locations=(region.id,))
    world.record_event(future)

    with pytest.raises(ValueError):
        world.record_event(Event(kind="past", time=9, locations=(region.id,), causes=(future.id,)))
