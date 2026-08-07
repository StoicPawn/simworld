from simworld import Entity, Event, SimulationEngine, WorldState


world = WorldState()
west = Entity(kind="region", name="Western Valley")
east = Entity(kind="region", name="Eastern Coast")
house = Entity(kind="lineage", name="House Aster", created_at=0)
for entity in (west, east, house):
    world.add_entity(entity)

engine = SimulationEngine(world, seed=42)


def western_harvest(world: WorldState, rng):
    return Event(
        kind="harvest_variation",
        time=5,
        locations=(west.id,),
        impact=1.5,
        payload={"yield_delta": rng.uniform(-0.25, 0.25)},
    )


def eastern_marriage(world: WorldState, rng):
    del rng
    return Event(
        kind="dynastic_marriage",
        time=5,
        participants=(house.id,),
        locations=(east.id,),
        impact=2.0,
    )


engine.schedule(5, western_harvest)
engine.schedule(5, eastern_marriage)
engine.run_until(5)

for event in world.events:
    print(event.time, event.kind, event.id)
print(engine.snapshot())
