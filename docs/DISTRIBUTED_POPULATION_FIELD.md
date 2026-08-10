# Distributed background population field

## Intent

Population should exist before settlements. A valley, coast or river basin can carry people even when no village, town or state has been recognized there.

This milestone introduces a settlement-independent demographic raster. It is deliberately aggregate: materialized people and households remain a refinement layer used only where causal detail matters.

## Substrate

`PopulationField` stores per-cell:

- aggregate population;
- local demographic capacity;
- physical suitability;
- water mask.

Initial population is distributed from continuous physical affordances: habitability, fertility, freshwater access, coastal food and timber, plus bounded micro-variation. No settlement object is consulted when deciding the raster distribution.

## Evolution

Each step applies:

- local density-dependent growth;
- small demographic noise;
- limited neighbour redistribution when cells become crowded;
- destination weighting by local suitability and available capacity.

This is intentionally a minimal demographic process, not a complete migration model.

## Materialization

Existing materialized households are sampled from the background field rather than being forced to live on the legacy bootstrap settlement coordinates. The bootstrap settlement entities remain temporarily because older simulation layers still use them for aggregate harvest/demography and event location references.

The intended long-term direction is:

```text
physical terrain
    -> distributed population field
    -> local demographic concentration
    -> selective household/person materialization
    -> residence/activity history
    -> derived inhabited nuclei
    -> named/institutional settlements only if socially recognized
```

## Scalability

A raster cell can represent zero, one or many thousands of unresolved people without creating Python entities for each person. Fine individual simulation is reserved for causally relevant areas, lineages and interactions.

This is the bridge between a planet-scale world and individual-scale history.

## Invariants

- population != settlement;
- density hotspot != settlement;
- aggregate population != materialized people;
- materialization must not create population from nothing;
- a settlement label must not determine where population is allowed to exist;
- background demographic evolution continues in unresolved/quiet cells;
- demographic hotspots can emerge, decline and move.

## Transitional limitation

Legacy bootstrap settlement populations still evolve separately in older layers, so the current field is not yet the single authoritative demographic source. The next refactor should make the raster population the authoritative aggregate state and convert old settlement population totals into derived regional summaries.
