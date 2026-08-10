# Microgeography and emergent places

## Goal

SimWorld should be able to explain a later market, settlement, noble centre or contested site through the physical and social history of the exact place rather than through a constructor such as `create_market()`.

## Physical substrate

The generated world now exposes continuous signals:
- elevation and slope;
- water/land;
- rainfall and temperature;
- fertility, timber and ore;
- terrain-derived drainage / `river_strength`;
- nearby `freshwater_access`;
- spatially patchy `coastal_food`.

These values are physical opportunities and constraints. They are not historical labels. A high-flow cell is not automatically a city site; a rich coast is not automatically a port or fishing community.

## Sparse social geography

`CellActivityLedger` exists only for cells that are actually used. It can accumulate visits, residence, gathering, cultivation, exchange, conflict and construction.

This is intentionally sparse. Planet-scale physical rasters may contain huge numbers of cells, while only a small fraction need detailed social history at any one time.

## Individuals and co-presence

The microgeography vertical slice gives materialized people local cell positions. Short-range destinations are sampled from physical affordances plus modest familiarity with previously used cells.

Co-presence creates an encounter opportunity, not a guaranteed relationship. Encounters may be neutral, friendly or hostile and can seed social ties.

## Derived places

`PlaceView` is a retrospective view over activity. It contains signals such as persistence, number of actors, production, exchange, conflict and infrastructure. It is not itself a causal entity.

A future observer may interpret different configurations as a market, residence cluster, harbour, shrine, battlefield or political centre. Those names must not be necessary for the underlying history to occur.

## Transitional limitation

Current vertical slices still begin with coarse settlement entities selected from physical habitability. This remains a bootstrap scaffold. The target architecture is for residence clusters and settlements themselves to emerge from repeated location, household movement, construction, resource use and interaction while background population remains aggregated at low resolution.

## Invariants

- terrain role is emergent;
- place type is derived;
- movement != interaction;
- co-presence != relationship;
- familiarity may reinforce use but cannot override physical constraints;
- social geography stays sparse/adaptive;
- a place may rise, decay, be abandoned or later become important again;
- no event exists merely to make a place historically interesting.
