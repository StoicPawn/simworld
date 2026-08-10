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

---

## 2026-08-10 — M12 Persistent residence and emergent settlement nuclei

**Intent:** let inhabited nuclei arise from persistent household residence and local history rather than a primitive settlement-founding decision.

**New processes/views:** residential anchors; probabilistic residence shifts; sparse residence history; generic site improvement; retrospective `SettlementNucleusView` clustering.

**Invariants:** residence != settlement; settlement nucleus != named village/town/city; construction != building type; local movement != migration; derived clustering cannot create causal advantage.

**Reference:** `docs/EMERGENT_SETTLEMENT_NUCLEI.md`.

---

## 2026-08-10 — M13 Distributed background population field

**Intent:** make population terrain-distributed state that exists before settlements and evolves in quiet/unresolved regions without one object per person.

**New substrate/processes:** `PopulationField`; terrain-weighted distribution; local capacity; density-dependent growth; neighbour redistribution; household-home sampling from the field.

**Invariants:** population != settlement; population hotspot != settlement; aggregate population != materialized people; quiet regions continue demographic evolution at aggregate resolution.

**Reference:** `docs/DISTRIBUTED_POPULATION_FIELD.md`.

---

## 2026-08-10 — M14 Authoritative aggregate population field

**Intent:** eliminate double demographic truth. `PopulationField` becomes the only authoritative aggregate state; legacy settlement populations become compatibility projections.

**Changes:** reporting-only nearest-anchor summaries; one demographic clock; compatibility harvest signals from raster population/capacity; legacy settlement migration disabled in the authoritative slice.

**Invariants:** compatibility summaries cannot feed population back into the field; reporting partition != region/border/territory; legacy settlement population is projection, not state.

**Reference:** `docs/AUTHORITATIVE_POPULATION_FIELD.md`.

---

## 2026-08-10 — M15 Deterministic semantic replay foundation

**Intent:** same seed/config/code must reproduce the same semantic history before adaptive resolution becomes widespread.

**Changes:** deterministic structural identifiers where ordering matters; deterministic graph traversal; normalized semantic replay fingerprint over state/events/raster/nuclei.

**Invariants:** technical IDs cannot influence causal outcomes; unordered traversal cannot decide who consumes a draw.

**Reference:** `docs/DETERMINISTIC_REPLAY_FOUNDATION.md`.

---

## 2026-08-10 — M16 Stable keyed RNG substreams

**Intent:** local refinement must not perturb unrelated stochastic history through a shared random cursor.

**New primitive:** `SeedStreams` derives independent Python/NumPy streams from root seed + canonical semantic keys with stable BLAKE2 hashing.

**Integration:** population initialization/demography, harvests, household relocation/construction, individual movement/activity and pair encounters use keyed scopes.

**Validation:** unrelated streams can consume tens of thousands of draws without changing the target stream or the reference authoritative world.

**Reference:** `docs/KEYED_RNG_SUBSTREAMS.md`.

---

## 2026-08-10 — M17 Adaptive population accounting

**Intent:** make detailed people a true high-resolution representation of the same authoritative physical population rather than a second population universe.

**New substrate/processes:** `PopulationField.reserved`; `PopulationRefinementLedger`; reserve/release without demographic change; detailed birth/death accounting; detailed residence population transfer; unresolved-only aggregate demography.

**Core identity:** `total population = unresolved population + materialized population`.

**Invariants:** resolution change != demographic event; birth/death are demographic events exactly once; every living detailed person must have exactly one active backing record; aggregate dynamics exclude reserved people.

**Reference:** `docs/ADAPTIVE_POPULATION_ACCOUNTING.md`.

---

## 2026-08-10 — M18 Unresolved demographic cohorts

**Intent:** give unresolved/background population enough biological-demographic structure to evolve realistically while preserving adaptive resolution and one authoritative population truth.

**New substrate/processes:** unresolved population split into age bands and minimal reproductive biological classes per cell; cohort aging; age-specific mortality; aggregate births; local mobility preserving cohort composition; authoritative population reconstructed from reserved detailed population + unresolved cohort totals.

**Invariants:** detailed people and unresolved cohorts are alternative resolution representations of the same population; cohort processes never re-simulate reserved people; biological reproductive class is not gender identity or social role.

**Validation:** dedicated M18 tests require non-negative cohort evolution, exact unresolved partitioning and consistency with authoritative population.

**Next dependency:** cohort-aware materialization/dematerialization.

---

## 2026-08-10 — M19 Cultural knowledge, convention dynamics and technical affordances

**Intent:** establish one generic substrate from which technological traditions, languages, religions and identities can later emerge without assigning those historical categories as primitive labels.

**Architecture decision:** SimWorld hard-codes constraints and **possibility spaces**, not historical outcomes. Full first-principles chemistry/biology/physics discovery is intentionally out of scope for the initial engine; technology therefore uses data-defined technical affordances rather than a chronological tech tree.

**New primitives/processes:**
- `KnowledgeUnit`: generic transmissible know-how/convention/practice unit with complexity, demonstrability and mutation parameters;
- actor-specific `KnowledgeState` with partial mastery, confidence, source and transmission generation;
- sparse `KnowledgeLedger`;
- imperfect `transmit_knowledge()` driven by source mastery, trust, communication compatibility, exposure, demonstrability and complexity;
- transmission can fail or create only partial mastery;
- `decay_knowledge()` allows unused/unreinforced knowledge to weaken and disappear while practice/social reinforcement/records improve retention;
- generic continuous `ConventionState` for learned conventions without declaring them linguistic/religious/etc.;
- contact-driven convention convergence and isolation-driven stochastic drift;
- retrospective `ConventionClusterView` / `cluster_conventions()` detect compatibility clusters but have no causal force;
- `Affordance`: data-defined technical possibility with material, prior-capability and environmental requirements;
- `InnovationContext` and bounded innovation probability from actual opportunity, experience, experimentation, contact and problem pressure;
- `AffordanceCatalog` loads technical possibility definitions from JSON, separating simulation mechanics from catalog growth;
- initial low-level catalog in `configs/affordances/foundation.json` demonstrates controlled heat processing, fired clay, managed water channels and ore reduction as independent possibilities rather than historical eras;
- `attempt_innovation()` creates/improves knowledge **only for the discovering actor**; it never changes a global civilization technology level;
- hard prerequisites failing implies zero discovery probability;
- prerequisites passing still does not guarantee discovery.

**Language design:** future languages/dialects will be derived from bundles of communicative conventions and mutual intelligibility. Contact, mobility, trade, family transmission, prestige, administration and education can promote convergence; isolation, drift, local networks and identity resistance can promote divergence. Valid runs may have one broad language network or many; no language-count target exists.

**Religion design:** future religions/cults will be derived from lower-level beliefs, narratives, rituals, prescriptions, norms, symbols, trusted transmitters and institutions. Private belief, ritual participation and social membership remain distinct.

**Identity/ancestry design:** biological ancestry, inherited phenotype and actor-created social identity are separate. Human ethnicity/race-like categories are social classifications, never automatic biological labels. Truly different fantasy species may be biological primitives only if physically present in the world definition.

**Technology design:** high-level historical labels such as agriculture, metallurgy, navigation or industrialization should be derived capability bundles. Individual techniques may be independently discovered, remain local, spread, mutate, combine, disappear or be rediscovered. `possible != discovered != widespread != retained`.

**Equilibrium/path-dependence rule:** there is no target equilibrium such as one language or inevitable technological progress. Convergence, divergence, persistence and loss compete locally. Temporary attractors may form and later dissolve.

**New invariants:**
- hard-code laws/constraints/opportunity spaces, not historical outcomes;
- knowledge possessed by one actor is not society-wide knowledge;
- knowledge may be incomplete, wrong, lost or rediscovered;
- language != primitive population label;
- religion != primitive population label;
- biological ancestry != phenotype != social identity;
- technological affordance != discovery;
- discovery != diffusion;
- discovery modifies actor knowledge, not a universal tech level;
- no chronological tech tree in the causal kernel;
- no automatic technological progress;
- no target number of languages/religions/cultures/technologies;
- derived cultural clusters cannot create causal advantage merely because they were detected.

**Validation added:** tests cover data catalog loading, zero innovation opportunity without required materials, low/non-guaranteed discovery with prerequisites, actor-local innovation, imperfect/partial knowledge transmission, practice-sensitive knowledge decay, contact convergence versus isolated drift, identity resistance, and derived cluster counts changing with actual convention similarity rather than preassignment.

**Known limitation:** M19 is still a generic substrate rather than a fully integrated cultural world loop. Knowledge must next connect to detailed people, actual activity experience, encounters, parent-child socialization, death, records and aggregate cultural state for unresolved population. Affordance requirements must progressively bind to actual material/environmental properties instead of placeholder capability names.

**Reference:** `docs/CULTURE_TECHNOLOGY_FOUNDATION.md`.
