# Deterministic randomness foundation

SimWorld is stochastic, but modular stochasticity must remain reproducible and locally stable as the engine grows.

## Problem

A single global pseudo-random stream makes unrelated systems accidentally coupled. If a new feature consumes one extra draw, every later draw shifts and births, harvests, encounters or political choices may all change even though the new feature has no causal relation to them.

That is implementation coupling, not simulated causality.

## Rule

Randomness is addressed by semantic coordinates derived from the root world seed.

Examples:

```text
(root seed, social, encounters)
(root seed, demography, settlement A)
(root seed, actor, person X, decision, year 42)
```

`RandomStreams` derives stable independent seeds using BLAKE2b. Python's process-randomized `hash()` must not be used for persistent simulation seeds.

## Stateful vs ephemeral streams

Use `stream(...)` when a process has a meaningful sequential stochastic history.

Use `ephemeral(...)` when a decision should depend only on explicit semantic coordinates and not on how many random draws happened elsewhere. Actor/time/process scoped choices are good candidates.

## Invariant

Adding or running an unrelated stochastic process must not change an existing process merely because it consumed random numbers.

This does **not** mean histories must remain unchanged when a new feature is causally connected. If a new institution changes food distribution, downstream demography may correctly change. The invariant only removes accidental RNG call-order coupling.

## Migration policy

Do not rewrite every existing subsystem at once. Older vertical slices keep their existing domain-specific RNGs until touched for substantive work. New processes should use semantic streams, and existing processes should migrate incrementally with regression tests.
