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

## Current objective

Finish the automation foundation, then move to the first simulation-domain milestone:

1. typed relations;
2. state-delta/reducer semantics;
3. deterministic random substreams;
4. geography;
5. resources;
6. low-resolution background processes for quiet regions.

## Not yet implemented

The following are long-term roadmap items, not current assumptions:

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

## Architectural warning

Do not collapse the simulation into one chronological story. SimWorld models a world with many concurrent local processes. Histories are views over the event/causal graph and may remain independent, intersect, diverge or converge.
