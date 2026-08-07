# SimWorld agent constitution

This file contains permanent rules for coding agents working in this repository. Read it together with `docs/PROJECT_MATRIX.md`, `docs/SPATIAL_FOUNDATION.md`, `.agent/project_state.md`, `.agent/roadmap.yaml`, and `.agent/rules.yaml` before changing code.

## Mission

Build SimWorld as a general multi-scale causal world simulator with a **geopolitical and spatial-first architecture**. The long-term target is not a story generator: it is a simulation engine from which many overlapping histories can be reconstructed, queried, compared, simulated forward, and eventually used for probabilistic inverse inference and geopolitical scenario analysis.

## Foundational substrate

SimWorld treats **time and space as co-equal simulation substrates**.

```text
TIME + SPACE
    ↓
ENTITIES + EVENTS + PROCESSES
    ↓
HISTORIES / POLITICS / ECONOMY / CONFLICT / INFERENCE
```

The map is causal state, not decoration. Read `docs/SPATIAL_FOUNDATION.md` before introducing geography, regions, resources, population, movement, infrastructure, borders, war, trade, climate, or geopolitical inference.

## Architectural invariants

1. **World state is primary; narrative is derived.** Never generate an event merely because it would make a better story.
2. **Many events may coexist.** Distant, simultaneous, independent events are normal. There is no single global protagonist or canonical storyline.
3. **Events may remain isolated or form causal chains.** Chains may branch, converge, disappear, re-emerge, and intersect other histories.
4. **Historical relevance is not causal force.** Important entities/regions may receive more computational resolution, but must not receive events merely because they are already important.
5. **Importance is dynamic.** Persons, families, institutions, objects, settlements, regions and states may rise, dominate, fade, disappear, or become important again.
6. **Quiet regions still evolve.** Low-relevance areas are simulated at lower resolution, never frozen unless a model explicitly justifies it.
7. **Use variable resolution.** Prefer aggregated representation for background populations/processes and materialize detail only when required by causal relevance or requested observation.
8. **Separate reality from knowledge.** Future agent layers must distinguish world truth from what each actor can observe, believe, infer, misperceive or conceal.
9. **Preserve causal traceability.** Important state changes should be attributable to explicit processes/events rather than unexplained mutation.
10. **Keep the kernel domain-agnostic.** Geography, resources, population, economy, institutions, politics, conflict, beliefs and inference belong in modules layered on the core.
11. **LLMs are bounded components, not the simulator.** Deterministic state, constraints, validation and causal mechanics stay outside the language model whenever possible.
12. **Reproducibility matters.** A seed and configuration must be sufficient to reproduce deterministic/stochastic choices within a compatible engine version.
13. **SimWorld is spatial-first.** Physical geography must exist below political, demographic and economic systems rather than being painted onto them later.
14. **The map must be causal.** Terrain, water, slope, climate, resources, accessibility and infrastructure must influence feasible actions, costs and propagation.
15. **Use layered geography.** Keep physical truth, anthropized geography, political control and perceived/known geography distinguishable.
16. **Regions are derived and mutable.** Do not make administrative/political regions the primitive spatial truth; they are views over cells/areas and may overlap, split or merge.
17. **Strategic value is emergent.** Never assign a permanent `strategic = true` role when value can be derived from connectivity, resources, networks, technology, actors and time.
18. **Fine spatial resolution must scale.** Do not instantiate planet-scale raster cells as heavyweight Python objects. Prefer arrays, chunks, tiles, indexes and vectorized operations.
19. **Spatial importance remains dynamic.** A remote cell, pass, harbour, deposit or region may be irrelevant for centuries and later become central, then fade again.
20. **Spatial truth and spatial knowledge are different.** A resource or route can exist without being known, correctly mapped or believed by an actor.

## Development discipline

- Work only on dedicated branches; never push directly to `main`.
- Modify only files required by the task.
- Do not weaken, delete or rewrite tests only to make a change pass.
- Prefer the root cause over patches that merely hide a failure.
- Preserve backward compatibility unless the task explicitly authorizes a breaking change.
- Keep public APIs small and typed.
- Add tests for new invariants and regressions.
- Update project state/roadmap only when a milestone actually changes.
- Do not implement future domains early just because they are interesting. Respect dependency order in `.agent/roadmap.yaml`.
- Spatial foundations must be established before deeply modelling population, economy, states, borders, trade or conflict.

## Mandatory validation

After material changes run:

1. `python -m compileall -q src tests examples scripts`
2. `pytest -q`

When configured, also run formatting/lint/type checks through `scripts/validate.sh`.

## Git and PR rules

- Agent branches use `agent/<run-id>-<slug>`.
- Never force-push `main`.
- No automatic merge to `main` unless repository policy is explicitly changed by a human.
- Before commit/push inspect `git status` and `git diff`.
- PR summaries must state: task, architectural impact, files changed, validation performed, unresolved risks.

## Safety and stop conditions

Stop and report instead of improvising when:

- required credentials are unavailable;
- a task requires modifying secrets, permissions, branch protection or production systems;
- the same root failure repeats three times;
- the requested change conflicts with the project invariants above;
- tests expose an architectural ambiguity that requires a human decision;
- the iteration or time budget is exhausted.

Never print secrets to logs. Never store credentials in the repository.

## Current-phase rule

Before coding, read `.agent/project_state.md`. If a task is outside the current milestone, implement only the prerequisites or stop and explain the dependency unless the task explicitly changes the roadmap.
