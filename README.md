# SimWorld

SimWorld is a **spatial-first, geopolitical, multi-scale causal world simulator**.

It is not primarily a story generator. The simulator maintains a world state in which many local processes and events can occur simultaneously, remain isolated, form causal chains, diverge, converge, and later be reconstructed as many different histories.

## Foundational model

```text
TIME + SPACE
    ↓
ENTITIES + EVENTS + PROCESSES
    ↓
HISTORIES / POLITICS / ECONOMY / CONFLICT / INFERENCE
```

The map is part of the causal state of the world, not decoration. SimWorld is designed around fine-grained spatial cells/layers, scalable storage, terrain-dependent movement and accessibility, dynamic regions, mutable political control, emergent strategic value, and a strict separation between physical truth and what actors know or believe about geography.

See:

- `docs/PROJECT_MATRIX.md` — complete architectural vision;
- `docs/SPATIAL_FOUNDATION.md` — spatial/geopolitical foundation;
- `AGENTS.md` — permanent coding-agent invariants;
- `.agent/roadmap.yaml` — machine-readable development roadmap.

## Current kernel

The first kernel provides:

- generic persistent entities;
- immutable events;
- many events at the same simulated time;
- append-only event history;
- explicit causal links;
- dynamic historical relevance with decay;
- adaptive simulation resolution;
- deterministic seeded event-driven scheduling.

Historical relevance controls attention/resolution, **not causality**. A region does not receive events because it has become a protagonist.

## Development direction

The immediate sequence is:

```text
core foundations
→ spatial foundation
→ physical geography
→ resources
→ population
→ economy/social structures
→ political + epistemic layers
→ conflict/history
→ counterfactual experiments
→ inverse inference
→ real-world geopolitical scenario helper
```

Population, trade, borders, states and conflict will be built over a stable spatial substrate rather than added first and mapped later.

## Development automation

The repository includes GitHub-based automation intended to allow development and simulation runs from phone or PC.

Two separate workflows are planned/implemented on the agentic infrastructure branch:

- **SimWorld Development Agent** — bounded coding-agent loop, validation, branch isolation and draft PR creation;
- **Run SimWorld** — simulation-only execution that produces downloadable run artifacts.

A self-hosted PC runner can later provide local compute and local LLM capabilities, with GitHub-hosted execution as fallback where supported.

## Development

Python 3.11+.

```bash
python -m pip install -e '.[dev]'
pytest
```

The architecture is deliberately modular. Domain systems should interact through explicit state, events and causal mechanics rather than authoring a global storyline.
