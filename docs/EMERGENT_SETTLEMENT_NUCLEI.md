# Emergent residential nuclei

## Intent

This milestone removes another historical category from the causal kernel. A settlement is not created because the simulator needs a village. It is a retrospective interpretation of persistent residence, repeated local activity, construction, exchange and social concentration in connected physical cells.

The previous `settlement` objects remain temporarily as bootstrap coordinates for older vertical slices. They are not treated as proof that a social settlement already exists.

## Minimal substrate

The new layer adds only:

- a persistent residential anchor for each materialized household;
- relocation of that anchor toward more attractive repeatedly used cells;
- sparse residence activity on occupied cells;
- generic construction/improvement activity;
- connected-component clustering of adjacent residential cells into `SettlementNucleusView` projections.

No `Village`, `Town`, `City`, `MarketTown`, `Port` or political centre constructor is introduced.

## Residence is not settlement

A household can reside alone on a cell. Several households can reside near each other without forming a durable community. A residential cluster becomes historically interesting only through persistence and accumulated activity.

The causal direction is:

```text
physical affordances
    -> individual/household use
    -> repeated residence
    -> local improvements
    -> neighbouring residential concentration
    -> derived residential nucleus
```

Later social and institutional processes may interpret a persistent nucleus as a named settlement, market centre, port, administrative centre or something else. Those labels must depend on actual activity and recognition.

## Relocation

Annual individual activity is treated as an excursion from a household residence anchor rather than a random walk. This separates ordinary local movement from migration.

A household can shift its residence when another nearby cell offers persistently better material conditions. The decision is probabilistic and depends on physical affordances and accumulated local use; it is not caused by a `move_to_better_land` script.

## Construction

`local_construction` is deliberately generic. It means labour/material effort has improved a place. The kernel does not yet assert whether the improvement is a house, store, wall, quay, irrigation work or workshop. Later layers may refine important construction into more detailed assets when causal relevance requires it.

## Scalability

Residential history is stored in the existing sparse cell-activity ledger. Unused cells acquire no social objects. `SettlementNucleusView` is computed from active cells and therefore does not require one settlement object per possible location.

## Invariants

- residence != settlement;
- settlement nucleus != named settlement;
- construction != building type;
- local movement != migration;
- clustering is retrospective and must not itself increase causal probability;
- bootstrap settlements are transitional compatibility data, not historical truth;
- place labels and political status must emerge from later recognition and institutions.

## Next dependency

The next major step is to reduce dependence on bootstrap settlements for population placement itself: distribute background population over habitable terrain, materialize individuals/households only where causal resolution requires it, and allow persistent residential nuclei to become the primary anchors for future population aggregation.
