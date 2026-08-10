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

**New processes/views:**
- each materialized household has a persistent residential anchor distinct from short-range excursions;
- annual local activity starts from that residence, preventing random-walk drift from masquerading as migration;
- households may probabilistically relocate toward nearby cells with persistently better physical/material affordances;
- residence is recorded sparsely in the cell activity ledger;
- generic `local_construction` records persistent site improvement without declaring building type;
- adjacent residentially used cells are clustered retrospectively into `SettlementNucleusView` projections;
- nucleus projections contain centre, cells, actors, persistence, residence, production, exchange, construction and conflict signals.

**New invariants:**
- residence != settlement;
- settlement nucleus != named village/town/city;
- construction != building type;
- local movement != migration;
- derived clustering must not itself create causal advantage;
- bootstrap settlements are compatibility coordinates, not social truth.

**Scalability:** no dense settlement layer is introduced. Residence/construction reuse the sparse cell ledger; only active cells participate in nucleus derivation.

**Validation target:** cluster derivation, persistent residence, relocation/construction events, integrated multi-year run and dedicated CI slice.

**Known limitation / next dependency:** initial aggregate population and founder placement still originate from bootstrap settlements. The next population refactor should distribute unresolved population over habitable terrain and materialize people/households around causally relevant cells/nuclei, so emergent nuclei become the primary anchors rather than compatibility settlements.

**Reference:** `docs/EMERGENT_SETTLEMENT_NUCLEI.md`.
