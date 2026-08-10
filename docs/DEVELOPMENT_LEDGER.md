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

**Integrated processes:** credit can move real grain and create explicit obligations; repayment/default affect cooperation; repeated cooperation can create generic organizations; authority is derived from compliance, dependency, recognition, provision and coercion.

**New invariants:** request != obligation; compliance != consent; dependency != loyalty; coercion != legitimacy; organization != state; authority != legitimacy.

**Observed baseline:** with seed `104729`, 20 years and 5 settlements, the first institutional run produced zero obligations, organizations and authority relations. This was treated as a model diagnostic rather than a reason to force events.

---

## 2026-08-09 — M9 Material disequilibrium, storage and local shocks

**Intent:** create plausible asynchronous surplus/deficit conditions so exchange, credit, dependency and organization can emerge from material history instead of being forced by event quotas or lowered thresholds.

**New primitives/processes:** per-household storage/preservation/exposure, spoilage and overflow, age-sensitive demand, household-specific local material shocks and explicit unmet food need.

**New invariants:** heterogeneous outcomes must arise from heterogeneous state/processes; never tune target counts of wars/trades/revolts/organizations/states; shocks create conditions, not prescribed responses.

---

## 2026-08-09 — M10 Primitive simplification: asset relations before property

**Intent:** reduce conceptual complexity and avoid projecting modern legal property backward into worlds that may not yet contain institutions capable of defining, recording or enforcing it.

**Architectural change:** `Asset` remains physical truth; `AssetRelation` represents `possess`, `use`, `control`, `claim`; `Recognition` is observer-specific; formal property becomes a future derived view; documents are future evidence objects, not truth.

**Integrated change:** farming households occupy/use/control plots. Production depends on use, not universal legal ownership.

**New invariants:** asset != property; possession != use != control != claim; claim != recognition; recognition != control; document != truth; formal property requires institutional context.

**Reference:** `docs/RESOURCE_CLAIMS_FOUNDATION.md`.

---

## 2026-08-10 — M11 Sparse micro-place activity and geography-driven encounters

**Intent:** make terrain causally protagonist at individual scale without materializing the entire planet as heavyweight objects. Individuals should create history because they repeatedly use concrete places, and social contact should increasingly arise from physical co-presence rather than arbitrary within-settlement pairing.

**New primitives/processes:**
- sparse `PlaceActivityLedger`, keyed only by cells that are actually used;
- `Presence(actor, cell, time, activity)` for materialized individual activity;
- per-site accumulated visits, distinct visitors, gathering, cultivation, cooperation, conflict and exchange signals;
- `PlaceView` as a derived retrospective view over persistent activity, without primitive labels such as market/village/neighbourhood;
- geography-weighted local cell choice using fertility, timber, coast, habitability, distance and accumulated familiarity;
- people can repeatedly return to useful places;
- exact same-cell co-presence creates opportunities for cooperative or competitive encounters;
- new weak friendship/rivalry ties in this layer can arise from real co-presence;
- legacy random within-settlement weak-tie formation is disabled in this higher-resolution slice.

**New invariants:**
- same settlement != physical encounter;
- place significance is accumulated history, not a permanent map label;
- market/village/centre are future derived views, not constructors;
- inactive cells must remain cheap: activity storage scales with used places rather than total world area;
- geography changes probabilities/opportunities but never prescribes a historical outcome;
- exact cell detail may live in event payloads while settlement entities remain coarse kernel locations until spatial references become first-class.

**Validation target:** sparse-ledger unit tests; used cells must be real land; integrated runs must generate exact-cell encounter events; CI must retain every previous vertical slice.

**Known limitations / next dependencies:** current local movement is a bounded-radius choice around settlement anchors rather than continuous routes; rivers/drainage are not yet generated; material exchange is still household-level and is not yet assigned to the exact cells where participants met; violent conflict has not yet been connected to injury/death. Next work should deepen physical geography (especially drainage/rivers), persistent movement paths and co-located material exchange before introducing any `Market` or `Settlement` primitive.
