# SimWorld development ledger

This ledger is the chronological architectural record of material project changes. Every major milestone must update this file together with `.agent/project_state.md` and `.agent/roadmap.yaml`.

## Rule

For each material change record:
- date / milestone;
- architectural intent;
- new primitives and processes;
- invariants introduced or changed;
- integration points;
- validation performed;
- known limitations / next dependencies.

Do not use this ledger as a marketing changelog. It exists so future humans and coding agents can reconstruct why the simulator works the way it does.

---

## 2026-08-09 — M0 Core causal kernel

**Intent:** establish world state, immutable events, causal chains, concurrent timestamps, dynamic relevance and seeded scheduling.

**Invariant:** narrative importance must never itself cause events.

---

## 2026-08-09 — M1 Remote/agentic operations

**Intent:** make GitHub the command surface for development and simulation from phone or PC, with isolated branches, validation and PR review.

---

## 2026-08-09 — M2 Spatial/geopolitical foundation

**Intent:** make geography causal rather than decorative.

**Primitives:** fine raster cells, chunked layers, movement cost, passability, terrain-sensitive least-cost routing.

**Invariant:** strategic value emerges from geography, resources, networks and technology; it is not assigned as a permanent flag.

---

## 2026-08-09 — M3 First physical/historical world

**Intent:** connect geography to resources, settlements, harvests, population, migration and discovery.

**Result:** multiple local histories can remain separate or converge through spatially constrained processes.

---

## 2026-08-09 — M4 Epistemic/cultural foundation

**Intent:** separate reality, observation, memory, belief, speech, action and perceived learning.

**Primitives:** needs, probabilistic beliefs, contextual trust, messages, distorted reports, strategy learning, narrative objects and branching transmission.

**Invariant:** needs create pressures, never prescribed actions. Actors may learn the wrong causal lesson.

---

## 2026-08-09 — M5 Biological generations and multiplex social networks

**Intent:** separate biological kinship from affection, loyalty, identity and political grouping.

**Primitives:** persons, kinship graph, probabilistic reproduction, births/deaths, multiplex social ties, network-of-networks queries and derived lineage views.

**Invariant:** offspring creates biological parentage and co-parenting but does not imply romance, marriage or loyalty. `House`/`Dynasty` is never biological truth.

---

## 2026-08-09 — M6 Household, relationship evolution, gestation and inheritance processes

**Intent:** move from static relationship snapshots toward persistent life processes capable of generating endogenous families, branches, property continuity, dependency and later institutions.

**New processes:**
- household formation and membership independent of blood;
- shared household resources and care burden;
- relationship strengthening, decay, separation and reconciliation as probabilistic processes;
- conception separated from birth by a pregnancy/gestation state;
- inheritance as competing claims over distinct assets, debts, names, roles and stories rather than a single automatic heir;
- death can open an estate and transfer different things to different people;
- materialized-person detail remains a refinement layer over aggregate population.

**New invariants:**
- co-residence != family != kinship;
- inheritance != biological descent;
- claims, norms, wills/intent, social power and recognition are separate inputs;
- the same death may produce multiple incompatible succession outcomes across property, debt, office, name and narrative custody;
- relationship state must evolve through accumulated interaction rather than static labels.

**Integration target:** generational vertical slice and event store.

**Validation target:** unit tests for household membership, relationship evolution, gestation delay, contested inheritance and integrated multi-year simulation.

**Known limitation:** this remains a vertical slice; production, explicit ownership registries, law, institutions, marriage norms, child development, spatial encounter networks and fully endogenous political organizations are subsequent layers.

---

## 2026-08-09 — M7 Material economy, property and spatial exchange

**Intent:** create the material substrate from which durable economic asymmetry and later political power can emerge without assigning economic castes, houses or rulers in advance.

**Historical note:** this milestone initially introduced `PropertyRight` as if a recognized ownership relation could be a primitive. M10 below supersedes that choice: modern/formal property is now derived from more elementary actor↔asset relations and recognition.

**Other primitives/processes retained:**
- `Asset` as a real productive/material object;
- `Inventory` for actual stocks, distinct from abstract wealth;
- generic `ProductionProcess` and environmental/labour context;
- bilateral `ExchangeProposal`/`ExchangeResult`;
- integrated household-level field assets, production, consumption, shortage, debt effects and barter;
- spatial accessibility for repeated exchange cached by settlement pair.

**Invariant retained:** scarcity alters constraints and incentives, never directly triggers a prescribed social/political outcome.

---

## 2026-08-09 — M8 Obligations, organizations and derived authority

**Intent:** bridge material/social interaction into durable institutional structure without declaring rulers, classes, houses, governments or states as primitive objects.

**New primitives:**
- general `Obligation` and `ObligationRegistry` for resource/labour/service duties with provenance, due time, fulfilment, debtor acceptance, external recognition and enforceability;
- `CooperationLedger` accumulating repeated successful/failed interaction;
- generic `Organization`, `Membership` and `OrganizationRegistry`;
- `AuthorityObservation`, `AuthoritySignal` and `AuthorityIndex` separating effective authority from legitimacy.

**Integrated processes:**
- severe household grain shortage may generate a credit request rather than an automatic policy response;
- possible creditors are constrained by actual surplus, spatial access, social connection and previous cooperation;
- accepted credit moves real grain and creates an explicit obligation;
- repayment, partial repayment and default become historical events;
- repeated successful interaction can reinforce cooperation while failed interaction can weaken it;
- connected cooperation networks may probabilistically form a generic organization;
- organizations can pool voluntary grain contributions and redistribute aid;
- authority signals emerge from observed compliance, dependency, recognition, provision and coercion;
- organization-level authority can grow in the resource-coordination domain through repeated contribution/provision without making the organization a government.

**New invariants:**
- request != obligation;
- obligation != financial debt only;
- compliance != consent;
- dependency != loyalty;
- coercion != legitimacy;
- organization != institution != government != state;
- effective authority and legitimacy are separate signals;
- authority is domain-specific and historically derived;
- economic dependency may become political power later, but never automatically.

**Validation:** unit tests cover partial/full obligation fulfilment, cooperation-derived group candidates, authority/legitimacy separation and an integrated no-primitive-state run. CI runs the institutional vertical slice after all previous layers.

**Observed baseline:** with seed `104729`, 20 years and 5 settlements, the first institutional run produced zero obligations, organizations and authority relations. This was treated as a model diagnostic rather than a failure: the material layer was too homogeneous to create the disequilibria required for those processes to activate naturally.

---

## 2026-08-09 — M9 Material disequilibrium, storage and local shocks

**Intent:** create plausible asynchronous surplus/deficit conditions so exchange, credit, dependency and organization can emerge from material history instead of being forced by event quotas or lowered thresholds.

**New primitives/processes:**
- per-household `StorageProfile` with capacity, preservation and exposure;
- grain spoilage and overflow loss;
- heterogeneous `HouseholdDemandProfile` with age-sensitive food needs and reserve targets;
- household-specific vulnerability to local material shocks;
- local pest/crop loss, storage damage and tool breakage events that affect actual inventories;
- explicit unmet household food need events after real stock consumption;
- integrated disequilibrium run layered on top of obligations, organizations and authority.

**New invariants:**
- heterogeneous outcomes must arise from heterogeneous state/processes, not from a target count of historical events;
- do not tune the simulator to produce a desired number of wars, trades, revolts, organizations or states;
- storage and spoilage are material processes independent of later social interpretation;
- two households in the same settlement may experience the same macro year differently;
- shocks create opportunities/constraints, never prescribed behavioural responses.

---

## 2026-08-09 — M10 Primitive simplification: asset relations before property

**Intent:** reduce conceptual complexity and avoid projecting modern legal property backward into worlds that may not yet contain institutions capable of defining, recording or enforcing it.

**Architectural change:**
- `Asset` remains physical/material truth;
- primitive `PropertyRight` is superseded by temporal `AssetRelation`;
- minimal relation kinds are `possess`, `use`, `control`, and `claim`;
- `Recognition` records that one actor accepts another actor's claim, independently of physical control;
- formal/legal property becomes a future **derived view** over claims, recognition, control, norms and enforcement;
- deeds, titles, cadastral records and contracts will later be information/evidence objects whose force depends on issuer recognition and institutional enforcement;
- compatibility wrappers remain temporarily so prior vertical slices do not require a destructive rewrite.

**Integrated change:** initial farming households now occupy, use and effectively control their field plots. The simulation no longer asserts that they own those plots under a universal legal regime. Production depends on `use`, not legal ownership.

**New invariants:**
- asset != property;
- possession != use != control != claim;
- claim != recognized claim;
- recognized claim != effective control;
- document != truth;
- legal/formal property requires institutional context;
- no universal property law is built into the kernel.

**Scalability rationale:** the simulator keeps a small set of generic relations and lets historical institutions add meaning later. This is preferred to creating separate hard-coded systems for prehistoric possession, feudal tenure, customary property and modern title.

**Reference:** `docs/RESOURCE_CLAIMS_FOUNDATION.md`.
