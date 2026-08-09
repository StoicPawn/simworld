# SimWorld agent constitution

This file contains permanent rules for coding agents working in this repository. Read it together with `docs/PROJECT_MATRIX.md`, `docs/SPATIAL_FOUNDATION.md`, `docs/EPISTEMIC_CULTURAL_FOUNDATION.md`, `docs/KINSHIP_SOCIAL_NETWORK_FOUNDATION.md`, `docs/PRIMITIVE_MATRIX_FOUNDATION.md`, `.agent/project_state.md`, `.agent/roadmap.yaml`, and `.agent/rules.yaml` before changing code.

## Mission

Build SimWorld as a general multi-scale causal world simulator with a **geopolitical, spatial-first and epistemically explicit architecture**. The long-term target is not a story generator: it is a simulation engine from which many overlapping histories can be reconstructed, queried, compared, simulated forward, and eventually used for probabilistic inverse inference and geopolitical scenario analysis.

## Foundational substrate

SimWorld treats **time and space as co-equal simulation substrates**.

```text
TIME + SPACE
    ↓
OBJECTIVE WORLD STATE
    ↓
EVENTS / EXPERIENCES / INFORMATION
    ↓
MEMORY / BELIEFS / NEEDS / SOCIAL TRANSMISSION
    ↓
DECISIONS / ACTIONS
    ↓
CHANGED WORLD STATE
```

The map is causal state, not decoration. Actor knowledge is not world truth. Biological descent is not social identity. Macro historical labels are not primitive causes. Read the foundation documents before domain work.

## Architectural invariants

1. **World state is primary; narrative is derived.** Never generate an event merely because it would make a better story.
2. **Many events may coexist.** Distant, simultaneous, independent events are normal. There is no single global protagonist or canonical storyline.
3. **Events may remain isolated or form causal chains.** Chains may branch, converge, disappear, re-emerge, and intersect other histories.
4. **Historical relevance is not causal force.** Important entities/regions may receive more computational resolution, but must not receive events merely because they are already important.
5. **Importance is dynamic.** Persons, families, institutions, objects, settlements, regions and states may rise, dominate, fade, disappear, or become important again.
6. **Quiet regions still evolve.** Low-relevance areas are simulated at lower resolution, never frozen unless a model explicitly justifies it.
7. **Use variable resolution.** Prefer aggregated representation for background populations/processes and materialize detail only when required by causal relevance or requested observation.
8. **Separate reality from knowledge.** World truth, observation, memory, belief, speech and action are distinct states.
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
21. **Needs are pressures, never direct policies.** A food shortage, threat or legitimacy problem may influence many possible actions or no action; never encode `problem -> prescribed response` as historical logic.
22. **Actors are non-omniscient.** They may fail to observe, misunderstand, forget, misinfer, lie, be lied to, distrust correct information, or act on false beliefs.
23. **Experience, belief, speech and action are distinct.** Do not assume that what an actor says equals what it believes, or that what it believes equals reality.
24. **Trust is relational and contextual.** Prefer actor-to-actor, domain-specific trust with historical updating over a single global reputation scalar.
25. **Perceived learning is not causal truth.** Actors learn from perceived outcomes. Store immediate/perceived reward separately from latent or long-run modeled effects when relevant.
26. **Strategies can become path-dependent.** A policy can be reinforced because it appeared to work even while it creates hidden long-run fragility.
27. **Stories are first-class information objects, not truth.** Narratives may have origin events, competing versions, holders, confidence, emotional valence, mutation and transmission ancestry.
28. **Culture is emergent.** Do not assign unexplained cultural stereotypes. Derive cultural patterns from persistent beliefs, narratives, institutions, norms, incentives and social transmission.
29. **No canonical interpretation of history.** The event store records modeled facts; meanings and causal interpretations can differ by actor or later historian.
30. **Future LLM agents receive only legitimate actor information.** Never leak hidden world truth into an LLM context unless the modeled actor has access to it.
31. **Biological kinship and social relationship are separate layers.** Blood does not imply affection, loyalty, co-residence, political alignment or shared identity.
32. **Reproduction is probabilistic.** Intimacy or partnership changes opportunity; it must never directly call a guaranteed birth.
33. **Birth creates parenthood, not romance.** Offspring establishes biological parent links and a co-parent relation, but not mandatory love, marriage, trust or cooperation.
34. **Social graphs are multiplex and temporal.** Friendship, rivalry, intimacy, care, dependence, trust, employment, debt and political ties may coexist between the same actors and change over time.
35. **Networks contain networks.** Higher-order connections must be queryable; friends-of-friends, in-laws, patrons, creditors and story-carriers may create causal pathways.
36. **Family/house/dynasty are emergent categories.** Never use biological descent alone as a primitive political unit. Derive them from descent plus social cohesion, property, memory, names, institutions and recognition when applicable.
37. **Lineages can branch or dissolve.** Related branches may become separate institutions; unrelated people may be incorporated; kin can become enemies.
38. **Kinship may influence information flow, never guarantee truth.** High family trust can preserve stories and falsehoods alike.
39. **Seek prime causal matrices.** Before introducing a macro concept, decompose it into the smallest reusable lower-level state, constraints, capabilities, perceptions and interactions that can exist independently of the macro outcome.
40. **Macro labels are observational by default.** War, alliance, feud, faction, dynasty, state, class, market, religion and similar labels should be derived views whenever the lower-level mechanics are sufficient.
41. **Conflict is not a primitive war state.** Incompatible claims/interests, distrust, dependence, capabilities and repeated interactions may produce anything from avoidance to negotiation to violence.
42. **Cooperation does not imply alliance.** One-off exchange or coordination must remain possible between rivals, enemies, relatives or strangers without creating a permanent alliance object.
43. **Relations are domain-specific and multiplex.** Two actors can cooperate economically and be violently opposed territorially at the same time.
44. **Macro classifiers must be causally inert.** Removing a `war_like`, `alliance_like` or similar classifier must not alter the simulated trajectory. Use underlying metrics/interactions for causal logic.
45. **No hidden macro state machines.** Never let detecting `war` automatically generate battles, or detecting `alliance` automatically guarantee assistance.
46. **The same primitive matrix must admit multiple outcomes.** Actor information, learning, networks, resources, spatial access and stochastic experience should prevent deterministic historical shortcuts.
47. **Scale does not erase internal structure.** A macro actor such as a state or institution may itself be a network of people, offices, factions and resources; do not assume unitary preferences unless explicitly justified by aggregation.

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
- Epistemic/social foundations must be used rather than bypassed when later political actors, families, institutions and cultures are added.
- Never model houses/dynasties as unexplained containers if their membership can be derived from biological/social/economic/institutional relations.
- Before adding a macro mechanic, apply the prime-matrix test in `docs/PRIMITIVE_MATRIX_FOUNDATION.md` and document why any irreducible macro primitive is necessary.
- Do not branch simulation behavior on an emergent pattern label when its underlying state is available.

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
