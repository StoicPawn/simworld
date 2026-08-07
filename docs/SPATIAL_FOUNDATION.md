# SimWorld — Spatial Foundation

This document defines a non-negotiable architectural principle of SimWorld: **the project is geopolitical and spatial-first**.

SimWorld is not a narrative engine with a map attached. The physical world is one of the two fundamental substrates of the simulation:

```text
TIME + SPACE
    ↓
ENTITIES + EVENTS + PROCESSES
    ↓
HISTORIES / POLITICS / ECONOMY / CONFLICT / INFERENCE
```

The map must therefore be causal, queryable, high-resolution, multi-layered, and capable of changing the historical importance of places without assigning fixed narrative roles.

## 1. The map is part of the simulation state

The map is not decorative. Terrain must influence what can happen, where it can happen, how costly it is, who can observe it, and how effects propagate.

Examples:

- mountains alter movement, settlement, climate, communication and military access;
- rivers may be barriers, transport corridors, agricultural inputs, borders or flood hazards;
- coastlines and natural harbours affect navigation and trade;
- narrow passes and straits create bottlenecks only when surrounding networks make them valuable;
- soil, water and climate affect agricultural potential;
- mineral and energy deposits can remain irrelevant for centuries until technology, knowledge or demand changes;
- infrastructure can transform previously peripheral cells into major corridors.

Geography constrains history, but geographical importance is not fixed.

## 2. Fine-grained spatial cells

Conceptually, the world is represented by very small pixels/cells. In code these should be treated as spatial cells or raster cells rather than millions of heavyweight Python objects.

A logical cell may expose properties such as:

```text
coordinate
cell_size
land / water
altitude
slope
terrain / biome
soil
surface water
climate variables
vegetation
agricultural potential
natural hazards
movement cost
resource deposits
population density
built infrastructure
political control
claims
observability / mapped knowledge
```

Not every property belongs in one object. The preferred design is a set of aligned spatial layers.

## 3. Layered GIS-like model

The same geographic coordinate can be queried across independent but aligned layers.

### Physical geography

```text
elevation
slope
coastline
hydrology
rivers
lakes
soil
biome
climate
natural hazards
```

### Resources

```text
fresh water
arable potential
forests
fish
iron
copper
coal
oil
gas
strategic minerals
other finite / renewable stocks
```

### Human geography

```text
population
settlement density
land use
language
religion
culture
migration pressure
```

### Infrastructure

```text
paths
roads
bridges
ports
canals
railways
energy networks
communications
fortifications
```

### Political geography

```text
control
sovereignty
claims
administrative units
borders
military occupation
jurisdiction
```

### Epistemic geography

```text
what is actually present
what has been surveyed
what each actor knows
what each actor believes
confidence in that belief
hidden / secret spatial information
```

These layers must remain distinguishable. A political border must not overwrite the physical terrain; an actor's belief about a mineral deposit must not overwrite world truth.

## 4. Physical truth, human modification and perceived map

The spatial model should explicitly support at least three conceptual levels.

### 4.1 Physical world truth

Features that exist independently of political interpretation:

- topography;
- rivers and watersheds;
- geology;
- climate state;
- underlying resource deposits.

### 4.2 Anthropized world

Features created or altered by agents:

- settlements;
- farms;
- roads;
- ports;
- canals;
- mines;
- dams;
- railways;
- fortifications.

### 4.3 Perceived world

Each actor may have incomplete or false spatial knowledge.

A deposit may exist in world truth while being unknown to most actors. A state may believe a pass is usable when recent weather has made it impassable. A military map may be outdated. A government may know about a strategic discovery before the public or neighbouring states.

This distinction becomes essential for later geopolitical inference.

## 5. Space must be causal

Spatial variables must affect process probabilities and constraints rather than merely annotate events.

A generic causal pattern is:

```text
physical state
→ local opportunity / constraint
→ movement / production / settlement / information effects
→ actor incentives and feasible actions
→ events
→ changed spatial and social state
```

Example:

```text
low rainfall in a watershed
→ reduced local agricultural yield
→ regional food deficit
→ price increases along connected markets
→ household migration
→ higher density in neighbouring cells
→ political pressure / local conflict / institutional response
```

At the same time, thousands of unrelated processes may continue elsewhere.

## 6. Routes, passes and movement cost

A geopolitical simulator needs more than Euclidean distance.

Movement and interaction should eventually depend on effective cost surfaces and transport networks. Important concepts include:

- local traversal cost;
- slope penalties;
- rivers and crossing points;
- seasonal accessibility;
- roads and infrastructure quality;
- maritime movement;
- ports;
- border restrictions;
- security / conflict risk;
- transport technology;
- travel time;
- freight capacity;
- information propagation time.

The engine should be able to derive least-cost routes and identify bottlenecks from these properties.

A cell or corridor must not be labelled `strategic = true` by fiat. Strategic importance should emerge from the interaction between geography, technology, networks, resources, population and political state.

## 7. Dynamic strategic value

A place can be peripheral in one century and central in another.

Conceptually:

```text
StrategicValue(location, time, state)
```

may depend on:

- connectivity;
- alternative routes;
- nearby population and production;
- technology;
- military reach;
- resource demand;
- infrastructure;
- political borders;
- trade networks;
- actor knowledge;
- competing claims.

Examples:

- coal-bearing land is not necessarily strategically important before coal-using technology;
- a natural harbour becomes more important after maritime trade expands;
- a mountain pass becomes less important after a tunnel or alternative route is built;
- a desert corridor can become central after discovery of an energy resource or construction of infrastructure.

Importance can rise, decay and return. This follows the same SimWorld rule used for people, institutions and regions: **relevance is dynamic, never destiny**.

## 8. Spatial events

Events should support spatial geometry richer than a single region label.

Depending on event type, later representations may include:

```text
point
set of cells
polygon / affected area
origin + destination
route
front line
radius / diffusion field
watershed
network edge / corridor
```

Examples:

- a birth occurs at a location;
- a landslide affects a small area and a road segment;
- a drought affects a spatial field across political borders;
- migration is a flow from origin through routes to destinations;
- a trade route is a path/network relation;
- a battle occupies a local area;
- a war may generate changing fronts and occupied areas;
- a disease or information process propagates across networks and space.

Spatial provenance should be retained so local events can later become part of larger causal histories.

## 9. Simultaneous geography-driven histories

The spatial foundation reinforces the core SimWorld model of history.

At one simulated moment:

- a river may flood in one basin;
- a mine may be discovered hundreds of kilometres away;
- a family may inherit land in another region;
- a road may deteriorate elsewhere;
- a port may expand;
- a remote population may migrate because of climate pressure.

These events may remain independent forever, or decades later their causal chains may intersect through trade, migration, conflict, institutions, technology or information.

There is no privileged centre of the map and no globally authored storyline.

## 10. Spatial multi-resolution

The logical map should support very fine cells, but the implementation must remain scalable.

Do not instantiate one Python object for every square kilometre of a planet-sized world.

Preferred long-term techniques include:

- dense or sparse raster arrays;
- chunked storage;
- tiled loading;
- vectorized calculations;
- spatial indexes;
- hierarchical grids / pyramids;
- cache of active regions;
- refinement around high-activity areas;
- aggregation for low-activity areas;
- parallel regional processing when semantics are stable.

The base geographic truth may have a fixed fine resolution, while expensive social simulation can operate adaptively.

A quiet region is not deleted. It evolves through aggregate processes and can later be refined if its causal or geopolitical relevance increases.

## 11. Resolution and scale

No permanent cell size is mandated yet. The architecture must allow a practical base resolution and future refinement.

A possible conceptual hierarchy is:

```text
planet
→ large tiles
→ regional tiles
→ fine raster cells
→ optional local refinement
```

For an Earth-scale simulation, kilometre-scale cells already imply on the order of hundreds of millions of surface cells globally, so storage must be array/chunk based rather than object based.

The project must benchmark memory, routing and update cost before choosing final resolutions.

## 12. Regions are derived and mutable

Regions should not be the primitive spatial truth.

A `Region` is a useful grouping/view over cells and may represent:

- a watershed;
- ecological zone;
- administrative area;
- cultural area;
- market basin;
- military theatre;
- political territory;
- arbitrary simulation partition.

Different region systems can overlap. Political regions can split and merge without changing the underlying cell grid.

## 13. Borders and control

Political control is a time-varying layer over physical space.

The engine must eventually distinguish concepts such as:

- claimed territory;
- legally recognized territory;
- administratively controlled territory;
- military occupation;
- contested cells;
- de facto access;
- local autonomy.

This prevents a simplistic one-colour-per-country map from becoming the canonical political model.

## 14. Spatial resources and discovery

Resources have at least three separate states:

1. **physical existence** — the deposit or renewable potential exists;
2. **knowledge** — actors may or may not know it exists and with what confidence;
3. **exploitation** — technology, capital, access and institutions determine whether it can be used.

This enables historical transitions in which previously unimportant land becomes strategically valuable without rewriting the world's geology after the fact.

## 15. Connection to inverse geopolitical inference

Spatial uncertainty is central to the long-term inverse engine.

Given an observed action that appears unlikely under the known state, SimWorld may later ask:

> What unobserved spatial facts would make this action substantially more probable?

Candidate latent variables could include:

- an undisclosed resource discovery;
- a newly mapped passage;
- hidden infrastructure;
- unknown military accessibility;
- an unobserved environmental constraint;
- private intelligence about another region.

The result must be a probability distribution over hypotheses, not a claim that a hidden resource actually exists.

World truth, observer evidence and actor knowledge must therefore remain separate from the first spatial implementation onward.

## 16. Architectural requirements for the first implementation

The first spatial milestone should establish abstractions before complex terrain generation.

Minimum target:

1. coordinate/reference system;
2. world extent;
3. raster/grid abstraction;
4. chunk/tile abstraction;
5. aligned scalar/categorical layers;
6. cell and neighbourhood queries;
7. adjacency;
8. distance utilities;
9. movement-cost layer;
10. region views over cell sets;
11. deterministic serialization;
12. tests for boundaries, neighbours and reproducibility.

Then add physical layers:

1. elevation;
2. slope derived from elevation;
3. land/water;
4. hydrology basics;
5. terrain/biome;
6. climate baseline;
7. resource layers;
8. accessibility / least-cost routing.

Only after this foundation should population, economy and political control be deeply modelled.

## 17. Permanent invariants

All future code and agents must respect these rules:

1. **SimWorld is spatial-first and geopolitical by construction.**
2. **The map is causal state, not decoration.**
3. **Space and time are co-equal simulation substrates.**
4. **Fine geographic resolution must remain computationally scalable.**
5. **Physical geography, anthropized geography, political geography and perceived geography are separate layers.**
6. **Regions are views/groupings over spatial primitives, not immutable world truth.**
7. **Strategic importance must emerge from state and networks rather than fixed labels.**
8. **Quiet territory continues to evolve.**
9. **Spatial events may remain local or join larger causal chains later.**
10. **Actor knowledge about space must remain distinct from true spatial state.**
11. **Political borders and control may change without altering underlying physical geography.**
12. **A future real-world map must be representable using the same abstractions used by fictional worlds.**

These are architectural constraints, not optional worldbuilding preferences.
