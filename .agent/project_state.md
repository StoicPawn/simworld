# SimWorld project state

## Current phase

**Spatial foundation active — kernel and development automation already established on parent branches**

The domain-agnostic kernel provides:

- persistent generic entities;
- immutable events;
- multiple events at the same simulated time;
- append-only world history;
- explicit causal links;
- dynamic relevance with decay;
- adaptive resolution levels;
- deterministic seeded event-driven scheduling.

The automation layer provides remote development/run infrastructure through GitHub Actions, with bounded agent execution and local/cloud routing.

## Foundational correction: spatial-first geopolitics

SimWorld is explicitly a **geopolitical, spatial-first simulator**. Space is not a later presentation layer and the map is not a decorative background.

The two primary simulation substrates are:

```text
TIME + SPACE
    ↓
ENTITIES + EVENTS + PROCESSES
```

The spatial contract is defined in `docs/SPATIAL_FOUNDATION.md` and is mandatory context for future development.

## Spatial code now implemented

The first executable spatial kernel now includes:

- `GridSpec` for a fine regular raster;
- `CellCoord` and `ChunkCoord`;
- coordinate-to-cell and cell-center transforms;
- 4/8-neighbour spatial queries;
- metric cell distance;
- lazy chunked NumPy raster layers;
- aligned named layers over one spatial grid;
- canonical physical layers for elevation, movement cost, passability, water and fertility;
- terrain/slope-sensitive movement costs;
- impassable barriers;
- A* least-cost routing;
- tests proving that a unique mountain pass or cheaper corridor emerges from map state rather than a hard-coded strategic flag.

The implementation deliberately avoids one heavyweight Python object per planetary cell. Untouched raster chunks consume no layer memory.

## Current objective

Continue the spatial substrate while the generic core-foundations track can progress in parallel:

1. real coordinate reference/georeferencing policy;
2. persistent chunk serialization;
3. multi-resolution tiles/chunks;
4. region views derived from cells;
5. deterministic spatial generation substreams;
6. elevation/land-water generation or ingestion;
7. slope, coastline and hydrology;
8. resource layers;
9. low-resolution background processes for quiet regions.

Population, economy and political systems should be built deeply only after this spatial foundation is stable.

## Not yet implemented

The following remain future work:

- real-world CRS/projection support;
- persistent/memory-mapped planet-scale rasters;
- physical geography generation;
- resources and hydrology;
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
