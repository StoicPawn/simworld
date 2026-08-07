# SimWorld — Project Matrix

This document is the architectural contract for the project. Features can change; these principles should change only deliberately.

## 1. Vision

SimWorld is not primarily a story generator. It is a **world-state simulator from which many histories can be reconstructed**.

The long-term target is a general engine able to move through four increasingly demanding modes:

1. fictional emergent-history simulation;
2. historical-like and counterfactual simulation;
3. calibrated reconstruction of real historical systems;
4. probabilistic geopolitical scenario analysis and inverse inference on the contemporary world.

The project must be useful before reaching the final stage. Each layer should produce a functioning simulator rather than waiting for a hypothetical complete model of humanity.

## 2. Fundamental model of history

### 2.1 History is not one line

A world does not have one privileged timeline. At any moment, many processes occur in parallel.

A person has a history. A family has another. A city, company, army, road, religious institution, river basin, resource deposit, political office, and state each have their own histories. These histories overlap only where their events and dependencies overlap.

Therefore the engine stores **world events and relations**, not a single authored chronology.

### 2.2 Events are numerous and simultaneous

A simulated year must not contain only the event that would appear in a textbook. Thousands or millions of changes may happen across the world:

- births and deaths;
- migrations;
- marriages and inheritance;
- harvest variation;
- local disputes;
- commercial failures;
- discoveries;
- price movements;
- institutional decisions;
- construction and decay of infrastructure;
- changes in beliefs or information;
- diplomacy, conflict, and cooperation.

Several events can happen at exactly the same simulated time in different locations. There is no global narrative lock.

### 2.3 Events may remain isolated

Most real events do not become world-historical events. The engine must allow an event to happen, affect a small neighborhood, and terminate without needing a dramatic continuation.

The simulator must never create consequences merely because an event was generated and a story seems unfinished.

### 2.4 Events may form chains

Some events change state in ways that alter later probabilities. A local chain might be:

```text
landslide
→ trade route interruption
→ local grain price increase
→ merchant bankruptcy
→ creditor acquires warehouses
→ family accumulates commercial power
→ family finances crown decades later
→ political privilege
```

No step needs to have been planned at the beginning.

### 2.5 Chains can diverge and converge

One cause can produce many consequences. One consequence can have many causes. Two histories that were independent for decades may later meet.

The causal representation therefore needs a graph/DAG-like structure rather than a narrative linked list.

### 2.6 Distance does not imply irrelevance forever

A distant event may initially be unrelated to the current focus and later become connected through migration, trade, conquest, technology, disease, finance, diplomacy, or information.

The simulator must preserve enough provenance that a previously quiet chain can later become historically important.

## 3. Dynamic relevance and historical attention

### 3.1 Importance is endogenous and temporary

People, families, objects, resources, institutions, and regions do not receive permanent labels such as "important" or "irrelevant".

An obscure lineage may acquire land, money, offices, allies, or knowledge and become central. A ruling dynasty may lose descendants, wealth, legitimacy, or control and disappear. A peripheral region may become strategic because a route changes or a new resource becomes valuable.

### 3.2 Quiet regions remain alive

A region may remain politically silent for a long time, but it is not frozen. Demography, ecology, production, family structure, beliefs, infrastructure, and local relations can continue to evolve at lower simulation resolution.

Silence means "little current relevance to wider networks", not "nothing happens".

### 3.3 Regions can heat up and cool down

The engine needs a dynamic measure of attention/resolution. A region can move approximately through:

```text
AGGREGATE → DETAILED → FOCUS → DETAILED → AGGREGATE
```

Nothing prevents later re-entry.

### 3.4 Relevance must not become destiny

A critical rule: historical relevance is not itself a physical cause.

The fact that a city has appeared in many important events should not magically cause more wars there. Structural variables — population, wealth, geography, networks, claims, resources, institutions, beliefs, and shocks — cause events. Relevance primarily controls:

- how much simulation detail to allocate;
- which entities are materialized individually;
- what to retain at high fidelity;
- what a historian or UI should surface.

This separation prevents self-reinforcing "main character" regions.

## 4. Multi-resolution simulation

Full individual simulation of every human is unnecessary and often computationally wasteful.

A city of 100,000 people may initially exist as distributions and aggregates. If political or causal activity increases, selected households, organizations, and individuals can be materialized consistently from those aggregates.

When detailed entities become irrelevant, the engine should eventually support safe re-aggregation while retaining historically significant facts.

Target hierarchy:

```text
world
→ macro-regions
→ regions
→ settlements
→ institutions / organizations
→ social groups / households / lineages
→ individuals
→ possessions / objects / information states
```

Resolution is adaptive rather than fixed.

## 5. State → pressure → action → consequence

Avoid rules such as:

```text
every 20 years: generate war
```

Prefer mechanisms where events arise from current state. Conceptually:

```text
world state
→ pressures/opportunities
→ information available to actors
→ actor perception and beliefs
→ intent
→ feasible actions
→ chosen action
→ consequences
→ new world state
```

This creates the possibility of long peaceful periods, clustered crises, accidents, missed opportunities, and unintended consequences.

## 6. Probability and hazards

Event probabilities should be conditional on state:

`P(event | world state, actor state, information)`

A war can become more likely because of claims, succession, resource constraints, geography, alliance structure, perceived weakness, domestic incentives, military capacity, or combinations of these.

The design must support continuous hazards and event-driven scheduling rather than relying only on one coarse annual tick.

## 7. Epistemic simulation

The authoritative state of the world is not the same as what agents know.

Long-term architecture should distinguish:

- actual world state;
- observable evidence;
- information possessed by each actor;
- beliefs inferred from that information;
- misinformation and deception;
- confidence/uncertainty;
- memory and forgotten information.

An actor can rationally act on a false model. That false action can become a real historical cause.

This is essential for diplomacy, markets, intelligence, ideology, panic, deterrence, and geopolitical simulation.

## 8. Entities / ontology

The kernel starts with a generic `Entity` so the ontology can expand without rewriting the engine.

Expected domain concepts include:

```text
Person
Household
Lineage / Dynasty
Organization
  Company
  Army
  Guild
  Religious organization
Institution / Office
Settlement
Territory
State / Polity
Resource
Infrastructure
Technology
Belief / Doctrine
Information object
Physical object
```

Relations will eventually include:

```text
owns
controls
rules
governs
belongs_to
inherits
claims
owes
trades_with
allied_with
rivals
trusts
knows
believes
observes
depends_on
located_in
kinship
```

The goal is composition and extensibility, not a giant hard-coded inheritance tree.

## 9. Event model

Every durable event should eventually carry enough information for reproducibility and causal analysis:

- unique ID;
- simulation time;
- event type;
- participating entities;
- locations;
- direct causes/provenance;
- state delta or structured payload;
- importance/impact estimates;
- visibility/information exposure (later);
- generator/system responsible (later);
- random seed/substream provenance (later).

The event store should be append-only. Derived indexes and materialized state can be rebuilt or checked from it where practical.

## 10. Causal graph

Events are nodes. Causal links are directed edges.

Required operations over time:

- direct parents/children;
- descendants and ancestors;
- merge points between chains;
- chain termination;
- delayed effects;
- attribution scores rather than only binary causation;
- counterfactual removal or modification of nodes.

This graph later becomes central to explanation and inverse inference.

## 11. Event systems / domain modules

The kernel should know almost nothing about concrete history. Domain systems will add processes such as:

1. geography and climate;
2. renewable and finite resources;
3. demography;
4. households and kinship;
5. production and consumption;
6. trade and prices;
7. ownership and wealth;
8. migration;
9. settlements and infrastructure;
10. organizations and institutions;
11. political authority;
12. succession and dynasties;
13. diplomacy and alliances;
14. conflict and military logistics;
15. religion, culture, ideology;
16. knowledge, communication, and technology;
17. disease and ecological shocks;
18. financial systems;
19. intelligence, secrecy, and misinformation.

Modules must interact through shared state/events rather than directly authoring a global story.

## 12. Emergent structures

A family should not be "the banking family" because the generator assigned a trope.

A family can become financially dominant because earlier events created capital, networks, political privileges, expertise, trust, collateral, and opportunities.

Likewise, kingdoms, empires, monopolies, schools, religious centers, trade hubs, and military elites should ideally emerge from accumulated state transitions.

Historical categories are labels applied after patterns exist.

## 13. LLM role

A local Llama-class model can eventually be useful, but it should not control the simulation directly.

Good uses:

- bounded choice among feasible strategies;
- interpretation of ambiguous social information;
- semantic generation of motives consistent with structured state;
- naming and linguistic content;
- summarization of event chains into chronicles;
- translating structured beliefs into human-readable reasoning.

Bad uses:

- storing canonical state in prose;
- deciding unconstrained that a war "would make the story interesting";
- inventing resources or actors without committing them through world rules;
- replacing probability, accounting, genealogy, logistics, or reproducibility.

LLM outputs should preferably be structured proposals validated by Python.

## 14. Narrative is a query, not the engine

Once enough events exist, the same simulation should support different histories:

- history of one person;
- history of a dynasty;
- history of a city;
- history of a war;
- economic history of a region;
- history of an object or technology;
- global political history;
- history from the information perspective of a particular actor.

A chronicle is produced by selecting and summarizing relevant portions of the event/causal graph. The simulator itself has no protagonist.

## 15. Forward simulation

Forward mode asks:

> Given state S and rules/model M, what distributions of future trajectories arise?

A single seed produces one possible history. Many seeds produce distributions over histories.

This allows questions such as:

- how often does this polity centralize?
- which succession structures are fragile?
- when do trade networks create concentration of political power?
- which shocks tend to remain local and which propagate?

## 16. Counterfactual simulation

Because state and causal provenance are explicit, the engine should eventually support interventions:

- remove an event;
- change a ruler's death date;
- alter a harvest shock;
- prevent a marriage;
- add/remove a resource;
- change a treaty;
- alter information available to an actor.

Then rerun comparable worlds and examine how trajectory distributions change.

This is more informative than producing one alternate-history story.

## 17. Inverse simulation / abduction

The advanced target reverses the problem.

Given an observed event O and known evidence E, infer distributions over latent hypotheses H:

`P(H | O, E) ∝ P(O | H, E) P(H | E)`

Example: if a conflict occurs that the current model considers very unlikely, candidate hidden explanations might include:

- discovery of a strategic resource;
- intelligence unknown to the observer;
- misperception of an opponent's strength;
- hidden alliance commitments;
- domestic political incentives;
- concealed economic constraints;
- combinations of latent causes.

The output must never be "there is secretly oil here". It should be a posterior over hypotheses conditioned on model assumptions.

## 18. Stronger inverse question

A particularly useful form is:

> What would need to be true, but currently unobserved, for this event to become likely under the model?

This is computational abduction / latent-state search. Candidate latent worlds can be generated, forward-simulated, scored against observations, and compared.

Possible methods later:

- Bayesian inference;
- sequential Monte Carlo;
- approximate Bayesian computation;
- MCMC;
- simulation-based inference / neural posterior estimation;
- particle filtering for evolving hidden states.

## 19. Real-world geopolitical helper

The final stage should not be framed as a machine that predicts geopolitics with certainty.

A credible helper would:

1. ingest structured public observations;
2. maintain uncertain state estimates;
3. model actors with partial information;
4. generate scenario distributions;
5. identify variables to which outcomes are sensitive;
6. detect observed events that are surprising under current assumptions;
7. propose latent explanations for those surprises;
8. compare counterfactual interventions;
9. expose assumptions and uncertainty.

The output is scenario analysis and inference under explicit models, not secret knowledge.

## 20. Calibration and validation for the real world

The transition from fantasy to real geopolitics introduces an empirical burden.

Required disciplines will include:

- backtesting on historical periods;
- calibration of event rates/hazards;
- out-of-sample evaluation;
- sensitivity analysis;
- uncertainty decomposition;
- comparison with simple baselines;
- ablation studies;
- causal-identification caution;
- model versioning and provenance;
- prevention of hindsight leakage.

A plausible fantasy history is not evidence that a geopolitical model is calibrated.

## 21. Scalability architecture

The system must scale in objects, events, domains, and resolution.

Likely technical evolution:

### Early
- in-memory Python objects;
- append-only event list;
- deterministic priority queue;
- unit tests.

### Medium
- persistent event store;
- graph indexes;
- spatial indexing;
- component/entity system;
- vectorized aggregate processes;
- parallel regional simulation;
- checkpoints/snapshots;
- reproducible random substreams.

### Large
- partition world by spatial/network dependency;
- asynchronous/event-driven workers;
- hierarchical aggregation;
- hot-region refinement;
- cold-region compression;
- distributed event bus;
- columnar analytics store;
- graph database or specialized causal index where justified.

Never distribute the system before deterministic single-process semantics are stable.

## 22. Phase roadmap

### Phase 0 — Kernel
Current target.

Deliver:
- entity registry;
- event type;
- event store;
- causal edges;
- deterministic scheduler;
- concurrent timestamps;
- relevance decay;
- resolution levels;
- tests.

### Phase 1 — Geography and resources
- map cells/regions;
- terrain;
- climate baselines;
- resource stocks/flows;
- distance and movement cost;
- adjacency and transport graph.

### Phase 2 — Population
- aggregate populations;
- households;
- birth/death/migration;
- cohort statistics;
- adaptive materialization of individuals.

### Phase 3 — Production and exchange
- basic needs;
- production;
- inventories;
- ownership;
- trade routes;
- prices/scarcity;
- shocks and propagation.

### Phase 4 — Social and political structures
- groups and organizations;
- family/kinship;
- status and legitimacy;
- institutions/offices;
- authority/control;
- taxation and public capacity.

### Phase 5 — Dynasties and state formation
- inheritance;
- succession;
- claims;
- marriage networks;
- factions;
- emergence/splitting/merging of polities.

### Phase 6 — Diplomacy and conflict
- interests;
- alliances;
- deterrence;
- military capacity/logistics;
- wars as choices/outcomes rather than timers;
- peace and settlement mechanisms.

### Phase 7 — Information and beliefs
- local knowledge;
- communication networks;
- secrecy;
- propaganda;
- misinformation;
- actor belief states and uncertainty.

### Phase 8 — LLM bounded agents
- structured context;
- constrained action menus;
- validation of model outputs;
- semantic motives and negotiation;
- narrative generation separated from state.

### Phase 9 — Multi-scale optimization
- dynamic refinement/re-aggregation;
- regional parallelism;
- persistent event/graph storage;
- large-population performance.

### Phase 10 — Counterfactual lab
- interventions;
- repeated seeded ensembles;
- trajectory comparison;
- sensitivity and causal attribution tools.

### Phase 11 — Historical calibration
- load historical geography/data;
- fit hazards/process parameters;
- reproduce distributions and known macro-patterns;
- test on held-out periods.

### Phase 12 — Geopolitical scenario helper
- uncertain contemporary state;
- scenario ensembles;
- surprise detection;
- latent-hypothesis inference;
- explicit uncertainty and model diagnostics.

## 23. Immediate engineering rules

1. Keep `core` domain-agnostic.
2. Events are immutable facts once recorded.
3. Randomness is seeded and must become traceable.
4. No domain module writes prose as canonical state.
5. Same-time events are legal and expected.
6. Causal parents are explicit when known.
7. Unrelated events are allowed to remain unrelated.
8. Relevance decays; nothing is permanently central.
9. Quiet entities continue to evolve through aggregate systems later.
10. Resolution and causation remain separate concerns.
11. Prefer components and relations over deep class inheritance.
12. Add a test whenever a new architectural invariant is introduced.

## 24. First concrete coding milestones

The next issues after this initialization should be:

1. define typed relation storage;
2. define event state-delta / reducer semantics;
3. add deterministic random substreams per system/region;
4. introduce `Region` and spatial graph as the first domain module;
5. define aggregate resource stocks and flows;
6. schedule autonomous background processes so quiet regions actually evolve;
7. add event-query filters by time/entity/location/kind/causal ancestry;
8. add snapshots and replay tests.

That sequence turns the kernel into the first genuine world rather than prematurely adding dynasties or LLM agents.
