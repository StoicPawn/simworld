# Keyed RNG substreams

SimWorld uses deterministic semantic replay, but replay alone is not sufficient for adaptive resolution. If all stochastic processes share one mutable random-number stream, adding detail in one place changes which actor receives later draws elsewhere.

`SeedStreams` therefore derives independent pseudo-random streams from a root seed plus semantic keys using BLAKE2. Python's randomized `hash()` is never used.

Examples of intended keys:

- `("population", "demography", year)`
- `("residence", household_id, year, "move")`
- `("microgeography", "movement", person_id, year, x, y)`
- `("microgeography", "encounter", year, x, y, actor_a, actor_b)`

A stream is recreated from its semantic key rather than advanced from a global cursor. Consuming additional random values in an unrelated stream therefore cannot alter the target stream.

## Current integration

The authoritative demographic vertical slice uses keyed substreams for population initialization, initial household-home sampling, annual aggregate demography and compatibility harvest noise. The emergent-residence layer uses household/year-specific streams for relocation and site improvement. Microgeography uses person/year/location-specific streams for movement/activity and cell/year/pair-specific streams for encounter ranking and outcomes.

## Invariants

- Randomness in one unrelated causal scope must not perturb another scope.
- Semantic keys must be stable values, never object memory addresses or Python `hash()` output.
- A key must include enough causal scope to avoid accidental reuse of an identical draw for distinct decisions.
- Adding a new detailed process in one region may change that region through real causal interaction, but must not change distant regions merely by consuming random numbers.
- Keyed RNG isolation does not mean histories are independent: causal state can still propagate between scopes through explicit events, movement, information and material flows.

## Validation

Tests recreate identical streams from identical keys, distinguish key types, consume 10,000 values in an unrelated stream without changing a target draw, and inject 50,000 unrelated adaptive-detail draws into a complete authoritative-demography simulation without changing its population field, household homes, residence shifts or construction count.

## Next dependency

The next population layer can now materialize and dematerialize detail without destabilizing unrelated stochastic history. It must maintain accounting between aggregate population and detailed people so materialization is refinement rather than population creation.
