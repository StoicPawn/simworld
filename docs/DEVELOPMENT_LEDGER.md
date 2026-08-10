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

**Intent:** separate reality, observation, memory, belief, speech and action.

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

**New processes:** household formation independent of blood; shared resources/care burden; relationship evolution; gestation; contested multi-channel succession.

**Invariant:** co-residence != family != kinship; inheritance != biological descent.

---

## 2026-08-09 — M7 Material economy, property and spatial exchange

**Intent:** create a material substrate for durable economic asymmetry and later political power.

**Historical note:** the initial `PropertyRight` primitive is superseded by M10.

**Retained:** assets, inventories, production, consumption, bilateral exchange and spatial accessibility.

---

## 2026-08-09 — M8 Obligations, organizations and derived authority

**Intent:** bridge repeated material/social interaction toward durable organization and authority without primitive rulers/states.

**Primitives:** obligations, cooperation ledger, generic organizations, derived authority/legitimacy observations.

**Invariant:** organization != state; authority != legitimacy; dependency != loyalty.

---

## 2026-08-09 — M9 Material disequilibrium, storage and local shocks

**Intent:** create asynchronous surplus/deficit from storage, demand and local shocks so exchange/credit/cooperation can activate without quotas.

**Invariant:** never tune event counts to obtain a desired historical storyline.

---

## 2026-08-09 — M10 Primitive simplification: asset relations before property

**Intent:** avoid projecting modern property law into worlds without institutions capable of defining/enforcing it.

**Architecture:** `Asset`; temporal `AssetRelation` (`possess`, `use`, `control`, `claim`); actor-specific `Recognition`; formal property becomes derived from claim + recognition + control + norms + enforcement.

**Invariant:** document != truth; asset != property; claim != recognition != control.

**Reference:** `docs/RESOURCE_CLAIMS_FOUNDATION.md`.

---

## 2026-08-10 — M11 Terrain-derived hydrology, individual local activity and emergent places

**Intent:** let terrain create micro-local opportunities, individuals discover/use them, and socially meaningful places emerge from accumulated use.

**Physical additions:** terrain-derived flow accumulation, continuous river strength, freshwater access, patchy coastal food.

**Social-spatial additions:** sparse cell activity, local movement, gathering/cultivation, co-presence encounters, retrospective `PlaceView`.

**Invariant:** place != place type; market/village/port/political centre remain derived interpretations.

**Known limitation:** coarse settlements are still bootstrap entities created before individual history.

---

## 2026-08-10 — M12 Persistent residence and emergent settlement nuclei

**Intent:** remove the next major hard-coded macro category by letting inhabited nuclei arise from household residence and local history rather than a `create_settlement()` decision.

**New processes/views:** persistent household residential anchors; probabilistic local residence shifts; sparse residence history; generic local construction/site improvement; retrospective `SettlementNucleusView` clustering.

**New invariants:** residence != settlement; settlement nucleus != named village/town/city; construction != building type; local movement != migration; derived clustering must not itself create causal advantage.

**Reference:** `docs/EMERGENT_SETTLEMENT_NUCLEI.md`.

---

## 2026-08-10 — M13 Distributed background population field

**Intent:** make population a terrain-distributed state that exists before settlements and can evolve in quiet/unresolved regions without materializing every person.

**New substrate/processes:** `PopulationField` raster; terrain-weighted population distribution; local capacity; density-dependent growth; neighbour redistribution; materialized household homes sampled from the field.

**New invariants:** population != settlement; population hotspot != settlement; aggregate population != materialized people; quiet regions continue demographic evolution at aggregate resolution.

**Scalability rationale:** a raster cell may stand for zero to many thousands of unresolved people. Detailed persons/households remain a selective refinement layer.

**Reference:** `docs/DISTRIBUTED_POPULATION_FIELD.md`.

---

## 2026-08-10 — M14 Authoritative aggregate population field

**Intent:** eliminate the temporary double demographic truth. `PopulationField` becomes the only authoritative aggregate population state; legacy settlement population values become read-only-in-principle derived summaries used only by older layers during migration away from bootstrap settlements.

**New views/processes:**
- `PopulationSummaryView` reports population, capacity, suitability and cell count over a derived compatibility partition;
- a nearest-anchor partition assigns land cells to old bootstrap points only for reporting; it explicitly has no territorial, political or causal semantics;
- legacy `settlement.population` values are overwritten from field summaries rather than advanced independently;
- harvest/food-pressure summaries are derived from field population/capacity and exposed to old social systems as compatibility inputs;
- demographic growth advances the raster exactly once per year;
- inherited background-population stepping is disabled to prevent a second demographic clock;
- old settlement-to-settlement migration is disabled because mutating summary values would create a second population truth; future long-range migration must transfer population directly on the raster/route substrate.

**New invariants:**
- `PopulationField` is authoritative aggregate demography;
- compatibility summaries cannot feed population back into the field;
- reporting partition != region != border != territory;
- legacy settlement population is projection, not state;
- demographic change occurs once per simulation time step;
- future migration must conserve/transfer authoritative field population rather than modify labels or summaries.

**Scalability/complexity rationale:** one demographic truth removes synchronization logic and prevents later state/settlement abstractions from silently becoming alternative population stores.

**Validation:** corrupting a legacy population summary cannot alter the field; field growth occurs once per year; derived summaries cover field total up to rounding; legacy migration no longer mutates demographic state; full lower-layer CI plus dedicated authoritative-demography run passed.

**Reference:** `docs/AUTHORITATIVE_POPULATION_FIELD.md`.

---

## 2026-08-10 — M15 Deterministic semantic replay foundation

**Intent:** ensure adaptive resolution cannot perturb unrelated history merely because technical identifiers or container iteration order change. Same root seed must reproduce the same simulated causal history before large-scale materialization/dematerialization is introduced.

**Changes:**
- deterministic context-local identifiers for structural actors whose identity can affect iteration/order;
- deterministic settlement, household and organization identifiers in the current vertical slice;
- deterministic graph traversal where unordered sets previously could alter processing order;
- replay fingerprint that canonicalizes remaining opaque technical identifiers by first appearance and compares world state, event sequence, demographic raster and emergent nuclei;
- regression test requires equal semantic fingerprints for equal seeds and unequal fingerprints for distinct seeds.

**New invariants:**
- same seed + same configuration + same code must produce the same semantic history;
- UUID/token value must not influence causal decisions;
- unordered container traversal must not choose who consumes a random draw;
- technical identifiers may remain opaque only when they are causally inert;
- byte-for-byte persistence identity is a separate, stricter future target from semantic replay.

**Validation:** complete authoritative-demography world executed twice in one process with the same seed produced identical normalized fingerprints; a different seed diverged; full CI passed.

**Next dependency:** introduce stable keyed RNG substreams by domain/process/actor/spatial key so refining one actor or region consumes randomness only from its own stream and cannot perturb unrelated processes. Only then should adaptive aggregate↔individual materialization become widespread.

**Reference:** `docs/DETERMINISTIC_REPLAY_FOUNDATION.md`.
