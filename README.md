# SimWorld

SimWorld is a procedural, multi-scale world simulation engine designed to generate **emergent histories rather than scripted stories**.

The world is not treated as one linear plot. It contains many entities and many processes, so many events can happen independently or simultaneously in distant places. Some events remain local and disappear from wider history; others form causal chains, intersect with other chains, or gradually increase the historical importance of people, families, institutions, resources, objects, settlements, and entire regions.

The project starts as a fictional-world simulator and is deliberately architected to scale toward historical reconstruction, counterfactual simulation, and eventually probabilistic geopolitical scenario analysis and inverse inference.

## Core principles

- **Many histories, not one timeline.** Every person, family, institution, territory, resource, and object can have its own history.
- **Concurrent events.** The world does not wait for a main plot; distant events can occur at the same simulated time.
- **Causal chains can remain separate or reconnect.** A local crop failure, a marriage, a trade dispute, and a discovery may stay unrelated, or their consequences may meet decades later.
- **Emergence over scripting.** Wars, dynasties, commercial powers, institutions, and crises must arise from state and interaction rather than narrative schedules.
- **Dynamic historical relevance.** Entities and regions can become central, fade into the background, remain quiet for centuries, and later return. Nothing is permanently important or permanently silent.
- **Variable resolution.** Quiet parts of the world can be simulated statistically; active or consequential parts can be expanded into detailed agents and event chains.
- **Reality and narrative are separate.** Relevance controls what deserves resolution and what a historian would notice; it must not become a magical force that makes events happen merely because something is already famous.
- **Causal memory.** The engine records provenance so later events can be traced to direct and indirect antecedents.
- **Imperfect knowledge.** Later, agents act on local beliefs, misinformation, incentives, and partial observations rather than omniscient state.
- **Forward and inverse simulation.** Long term, SimWorld should simulate consequences from causes and infer distributions over plausible latent causes from observed consequences.
- **LLMs are bounded semantic components.** Python owns state, constraints, probability, reproducibility, and causal bookkeeping. LLMs may later support bounded decisions, interpretation, or narration.

## Phase 0 — simulation kernel

The repository currently establishes the abstractions that future systems must share:

1. generic entities;
2. immutable events in an append-only store;
3. explicit causal links between events;
4. a world-state registry;
5. event-driven scheduling with simultaneous timestamps;
6. dynamic relevance and simulation resolution;
7. deterministic seeded runs;
8. tests protecting those invariants.

## Repository layout

```text
src/simworld/core/
  entity.py       # generic things that can exist in the world
  event.py        # immutable event records
  world.py        # world state + event/causal indexes
  relevance.py    # dynamic attention and resolution
  engine.py       # deterministic event-driven scheduler

tests/            # kernel invariants
examples/         # small executable simulations
docs/             # project matrix and long-term architecture
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
python examples/minimal_world.py
```

See [`docs/PROJECT_MATRIX.md`](docs/PROJECT_MATRIX.md) for the complete architecture and scaling roadmap.
