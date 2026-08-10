# Authoritative aggregate population field

## Intent

SimWorld must not have two independent answers to “how many people exist here?”. M13 introduced a terrain-distributed population raster but older settlement objects still maintained their own population totals. M14 removes that conceptual duplication.

`PopulationField` is now the sole authoritative aggregate demographic state in this vertical slice.

## Compatibility summaries

Older social systems still expect settlement-keyed population and food-pressure values. During the transition, each legacy bootstrap point receives a reporting-only cell partition based on nearest-anchor distance. Population/capacity are summed from the field and copied into the old entity attributes.

The partition is not a region model. It has no political, territorial, cultural or causal meaning.

```text
PopulationField
    -> reporting partition
    -> PopulationSummaryView
    -> legacy settlement attributes
```

There is no reverse arrow.

## Demographic clock

The raster advances once per simulation year. The inherited background-population hook is disabled in this layer to prevent double growth.

Legacy settlement-to-settlement migration is also disabled because moving their summary numbers would create a second demographic state. Future long-range migration must operate by transferring population directly between raster cells along feasible routes.

## Food pressure

Older social layers still need local food-pressure signals. These are derived from aggregate population/capacity within reporting partitions, with environmental variation, and are passed downward strictly as compatibility observations. They do not own population.

## Invariants

- one authoritative aggregate demographic state;
- settlement population attributes are projections;
- compatibility partition != region/border/territory;
- summaries cannot mutate population truth;
- demographic state advances exactly once per time step;
- future migration acts on the authoritative field;
- future materialization/dematerialization must conserve population between aggregate and detailed representations.

## Next step

Introduce an explicit resolution ledger for materialized population. Creating a detailed person/household must reserve population mass from a cell/cohort; dematerializing quiet detail must return compatible state to the aggregate representation without erasing persistent genealogy, claims, memories or causal provenance that remain relevant.
