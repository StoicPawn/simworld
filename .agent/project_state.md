# SimWorld project state

## Current phase

**Phase 0 — kernel + development automation**

The domain-agnostic kernel exists on the parent branch and establishes:

- persistent generic entities;
- immutable events;
- multiple events at the same simulated time;
- append-only world history;
- explicit causal links;
- dynamic relevance with decay;
- adaptive resolution levels;
- deterministic seeded event-driven scheduling.

This branch adds the remote development/run infrastructure so the repository can be developed and simulations can eventually be launched from phone or PC through GitHub Actions.

## Foundational correction: spatial-first geopolitics

SimWorld is explicitly a **geopolitical, spatial-first simulator**. Space is not a later presentation layer and the map is not a decorative background.

The two primary simulation substrates are:

```text
TIME + SPACE
    ↓
ENTITIES + EVENTS + PROCESSES
```

The spatial contract is defined in `docs/SPATIAL_FOUNDATION.md` and is mandatory context for future development.

Core consequences:

- the world must support a fine-grained raster/cell representation;
- planet-scale cells must use scalable array/chunk/tile structures rather than one heavyweight Python object per cell;
- terrain, hydrology, resources, accessibility and infrastructure must causally affect events and feasible actions;
- physical geography, anthropized geography, political control and perceived/known geography remain distinct layers;
- political regions and borders are mutable views/layers over underlying spatial primitives;
- strategic importance must emerge dynamically from geography, networks, technology, resources, population, knowledge and political state;
- quiet areas continue evolving at lower resolution and may later become central;
- actor knowledge of spatial facts must remain separate from world truth, enabling future geopolitical and inverse inference.

## Current objective

Finish the automation foundation, then build prerequisites and move directly into the spatial substrate:

1. typed relations;
2. state-delta/reducer semantics;
3. deterministic random substreams;
4. serialization and experiment metadata;
5. coordinate/reference system;
6. raster/grid and chunk/tile abstractions;
7. aligned spatial layers;
8. neighbourhood, adjacency and distance queries;
9. movement-cost surfaces and region views;
10. physical geography and resources;
11. low-resolution background processes for quiet regions.

Population, economy and political systems should be built deeply only after this spatial foundation is stable.

## Not yet implemented

The following are long-term roadmap items, not current assumptions:

- fine-grained spatial grid implementation;
- physical geography layers;
- population/demography;
- families, houses and dynasties;
- economy/trade;
- institutions/states;
- actor knowledge and beliefs;
- LLM-governed decisions;
- war/conflict systems;
- narrative/history extraction;
- counterfactual experiment engine;
- inverse causal inference;
- real-world geopolitical helper.

## Architectural warnings

Do not collapse the simulation into one chronological story. SimWorld models a world with many concurrent local processes. Histories are views over the event/causal graph and may remain independent, intersect, diverge or converge.

Do not collapse the world into political regions as primitive spatial objects. The underlying geography must remain independent of changing borders, administrations, claims and control.

Do not assign strategic importance as a permanent narrative attribute when it can be derived from spatial and social state.
