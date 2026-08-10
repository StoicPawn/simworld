# Deterministic semantic replay foundation

## Intent

A world simulator cannot support counterfactuals, causal comparison, debugging or adaptive resolution if the same seed silently produces a different history because of UUID ordering or hash/set traversal.

M15 establishes **semantic replay** as an invariant:

> same code + same configuration + same seed -> same simulated causal history.

This is deliberately distinguished from byte-for-byte persistence. Opaque identifiers that do not affect behaviour may still be normalized by analysis tools until all persistence formats are stabilized.

## Changes

- core `Entity` and `Event` identifiers use a context-local deterministic creation-order scope;
- the scope resets at the start of a simulation initialization;
- bootstrap settlement IDs are explicit and deterministic;
- household IDs are allocated locally by `HouseholdRegistry` in creation order;
- organization IDs use the deterministic scope;
- cooperation graph traversal sorts unordered edges/nodes before traversal;
- semantic replay tests run two complete authoritative-demography worlds sequentially in one Python process.

## Why UUIDs caused historical divergence

A random UUID is harmless if it is only a label. It becomes causal accidentally when code sorts actors by ID, iterates unordered structures containing those IDs, or couples a shared RNG sequence to that order. Then identical random streams are assigned to different actors.

The rule is therefore stronger than “seed every RNG”:

```text
seeded randomness
+ stable actor/process ordering
+ stable substream assignment
= reproducible history
```

## Replay regression

The test compares:

- entity semantic state;
- ordered event history (with irrelevant legacy opaque UUIDs canonicalized by first occurrence);
- household residence cells;
- derived residential nuclei;
- authoritative population raster.

A different seed must produce a different fingerprint.

## Invariants

- technical identifiers must never be sources of randomness or historical significance;
- unordered container traversal must not choose who consumes the next random draw;
- same seed must reproduce semantic history;
- different seeds must remain capable of divergent histories;
- deterministic replay must survive sequential runs in one process;
- future adaptive materialization must use deterministic actor/process substreams so changing resolution does not perturb unrelated regions.

## Next step

Before large-scale adaptive materialization, introduce stable PRNG substreams derived from root seed + process + stable actor/spatial key. This will prevent adding/removing detail in one region from shifting the random sequence of unrelated regions. Then materialization can reserve/release aggregate population while preserving replay.
