# SimWorld project state

## Current phase

**First real simulation vertical slice active**

The domain-agnostic kernel, automation layer and first spatial kernel exist on parent branches. This branch connects them into the first end-to-end world simulation.

## Foundational architecture

SimWorld is explicitly a **geopolitical, spatial-first simulator**.

```text
TIME + SPACE
    ↓
ENTITIES + EVENTS + PROCESSES
    ↓
MANY OVERLAPPING HISTORIES
```

Space is causal state, not decoration. Historical relevance controls resolution and presentation, never narrative destiny.

## Implemented substrate

### Core history engine
- generic persistent entities;
- immutable events;
- concurrent timestamps;
- append-only history;
- explicit causal links;
- dynamic relevance;
- seeded event-driven scheduling.

### Spatial engine
- fine regular raster with `GridSpec`;
- cell/chunk coordinates;
- chunked lazy NumPy layers;
- aligned raster layers;
- movement cost and passability;
- slope-sensitive least-cost routing;
- barriers, passes and corridors emerging from geography;
- bulk dense-array import/export for procedural generation and analysis.

### First physical world generation
- deterministic land/water generation from a seed;
- continuous elevation;
- slope-derived movement difficulty;
- temperature baseline;
- rainfall baseline;
- fertility;
- timber resource truth;
- ore resource truth;
- habitability;
- coast-sensitive settlement suitability.

### First human layer
- settlements emerge from high-habitability cells rather than scripted coordinates;
- settlement population is explicit mutable state;
- actual ore can exist before any actor knows it;
- each settlement has its own local event history.

### First historical dynamics
For every simulated year and settlement:
- a local harvest event occurs;
- climate/production shocks vary locally;
- harvest state causally drives demographic change;
- population can grow or contract;
- food pressure can trigger migration;
- migration follows actual least-cost geography;
- a migration event has both source and destination harvests as causes, allowing previously separate histories to converge;
- ore can be discovered probabilistically without changing underlying resource truth.

This is deliberately pre-state, pre-dynasty and pre-war. It is a vertical slice proving that geography can generate many simultaneous local histories and causal intersections without narrative scripting.

## First executable simulation

Run locally:

```bash
python scripts/run_first_world.py --config configs/worlds/first_world.json --output runs/first-world
```

Or use GitHub Actions workflow **Run First Real World** from phone/PC.

Outputs include:
- `map.svg` — generated physical map plus settlements;
- `physical_layers.npz` — elevation, water, rainfall, temperature, fertility, timber, ore truth and habitability;
- `events.jsonl` — append-only event history;
- `settlements.json` — final settlement state;
- `summary.json` and `README.md`.

## Next objective after this vertical slice

1. deterministic RNG substreams by domain/region;
2. persistent chunk serialization and checkpoints;
3. proper hydrology: drainage, rivers and lakes;
4. explicit soils/biomes and renewable resource stocks;
5. background population distributed across cells, not only settlements;
6. settlement founding/abandonment during simulation;
7. local production, inventories and trade flows;
8. roads/infrastructure emerging from repeated routes;
9. groups/families/organizations;
10. political authority and territorial control layered above geography.

## Architectural warnings

- Do not collapse the simulation into one chronological story.
- Do not create events because they would be narratively interesting.
- Do not treat political regions as primitive geography.
- Do not assign permanent strategic importance when it can emerge from spatial state.
- Keep world truth separate from actor knowledge.
- Quiet areas must continue to evolve even when represented at lower resolution.
