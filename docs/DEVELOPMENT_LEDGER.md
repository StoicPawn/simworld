# SimWorld development ledger

This ledger is the chronological architectural record of material project changes. Every major milestone must update this file together with `.agent/project_state.md` and `.agent/roadmap.yaml`.

For each milestone the purpose is to preserve architectural intent, new primitives/processes, invariants, validation and next dependencies. This is not a marketing changelog.

---

## 2026-08-09 — M0 Core causal kernel
World state, immutable events, causal chains, concurrent timestamps, relevance and seeded scheduling. **Invariant:** narrative importance never causes events.

## 2026-08-09 — M1 Remote/agentic operations
GitHub-centered remote development/simulation, isolated branches, validation and ordered project records.

## 2026-08-09 — M2 Spatial/geopolitical foundation
Fine raster cells, chunked layers, movement/passability and terrain-sensitive routing. **Invariant:** geography is causal state; strategic value is emergent.

## 2026-08-09 — M3 First physical/historical world
Geography connected to resources, early population/settlement compatibility, harvest, migration and discovery; local histories may remain separate or converge.

## 2026-08-09 — M4 Epistemic/cultural foundation
Reality, observation, memory, belief, speech and action separated. Needs, trust, distorted messages, strategy learning and branching narratives introduced. **Invariant:** needs create pressure, never prescribed action.

## 2026-08-09 — M5 Biological generations and multiplex networks
Persons, kinship, probabilistic reproduction, births/deaths, multiplex social ties and derived lineage views. **Invariant:** kinship does not imply romance, loyalty or political identity.

## 2026-08-09 — M6 Household, gestation, relationship evolution and inheritance
Households independent of blood, pregnancy state, relationship change/separation and contested multi-dimensional succession. **Invariant:** co-residence != family != kinship; inheritance != blood-only.

## 2026-08-09 — M7 Material economy
Assets, inventories, production, consumption, exchange and spatial accessibility. The initial modern-style `PropertyRight` approach is superseded by M10.

## 2026-08-09 — M8 Obligations, organizations and derived authority
Generic obligations, cooperation, organizations and domain-specific authority/legitimacy signals. **Invariant:** organization != state; authority != legitimacy; dependency != loyalty.

## 2026-08-09 — M9 Material disequilibrium
Storage, spoilage, heterogeneous demand and local shocks create asynchronous surplus/deficit. **Invariant:** never tune event counts to manufacture history.

## 2026-08-09 — M10 Asset relations before property
`possess`, `use`, `control`, `claim` and actor-specific recognition replace universal legal ownership as the primitive substrate. **Invariant:** document != truth; claim != recognition != control.

## 2026-08-10 — M11 Terrain microgeography and emergent places
Hydrology, freshwater/coastal affordances, sparse cell activity, local movement, gathering/cultivation, encounters and retrospective place views. **Invariant:** place type is derived.

## 2026-08-10 — M12 Persistent residence and emergent nuclei
Household residence anchors, local relocation, generic site improvement and retrospective inhabited-nucleus clustering. **Invariant:** residence != settlement; construction != predefined building type.

## 2026-08-10 — M13 Distributed population field
Terrain-distributed background population, local capacity, density-dependent growth and redistribution. **Invariant:** population exists before settlements and quiet areas continue evolving.

## 2026-08-10 — M14 Authoritative population field
One authoritative raster population truth; legacy settlement totals become reporting compatibility views and old migration is disabled in the authoritative slice.

## 2026-08-10 — M15 Deterministic semantic replay
Stable structural identity/order and same-seed semantic replay regression. **Invariant:** technical identifiers cannot influence causality.

## 2026-08-10 — M16 Keyed RNG substreams
Independent deterministic stochastic scopes derived from semantic keys. **Invariant:** refining one actor/region must not shift unrelated random futures.

## 2026-08-10 — M17 Adaptive population accounting
Detailed persons become reserved high-resolution representations of the same authoritative population. `total = unresolved + materialized`; resolution change is not demographic change.

## 2026-08-10 — M18 Unresolved demographic cohorts
Age/reproductive biological cohorts added to unresolved population with aging, mortality, births and mobility while excluding reserved detailed people.

## 2026-08-10 — M19 Cultural knowledge, conventions and technical affordances

**Intent:** establish a generic substrate from which technological traditions, languages, religions and identities can later emerge without primitive historical labels.

**Architecture:** actor-specific partial knowledge/mastery/confidence; imperfect transmission; decay/loss; convention convergence/divergence; retrospective non-causal clustering; data-defined `AffordanceCatalog`; actor-local innovation; no global civilization tech level.

**Technology rule:** hard-code constraints and possibility spaces, not chronological unlock sequences. Full first-principles chemistry/biology/physics is out of scope initially, so technical possibilities are supplied as versioned data affordances with material/capability/environment requirements. `possible != discovered != widespread != retained`.

**Cultural rule:** language/religion/ethnicity remain future derived configurations. Biological ancestry, phenotype and social identity are distinct. No target counts and no automatic progress.

**Reference:** `docs/CULTURE_TECHNOLOGY_FOUNDATION.md`.

---

## 2026-08-10 — M20 Control Tower and causal technology effects

**Intent:** ensure that technology changes the simulated world rather than existing only as a discovery label, and establish one powerful declarative surface for constructing/parameterizing future worlds without editing simulation code.

### Technology effect architecture

Every technical affordance loaded from a configured catalog must now expose at least one causal `EffectSpec`. Effects use generic channels instead of technology-specific historical functions. Current channels demonstrate production/storage/construction/combat/information effects.

`actor_effect_channels()` resolves effects only from capabilities actually known by the actor, scaled by mastery and gated by local context/material state. There is no global civilization-wide bonus.

The foundation catalog now demonstrates:
- managed water channels affecting cultivation/drought channels only with usable water;
- worked iron affecting cultivation, construction and combat only when iron equipment is actually available;
- durable symbolic recording exposing record creation, persistence, transmission-fidelity and sometimes credibility effects;
- fired clay and heat processing influencing their relevant material channels.

**Invariant:** every configured technology must have a modeled world consequence, but possession of knowledge alone does not guarantee that consequence; required equipment/context may be absent.

### Writing and narrative integration

`SocialMemory` now supports `NarrativeRecord`, a materialized record of a specific narrative version. Recording requires externally supplied record capability; subsequent use can reduce transmission mutation and affect perceived confidence/acceptance.

**Critical invariant:** a record never certifies truth. Written falsehoods can become durable and credible; true oral accounts can remain more trusted than documents. `record persistence/credibility != truth`.

### Control Tower foundation

`WorldBlueprint` provides the first portable JSON control surface. It can configure:
- root simulation seed and horizon;
- map source, dimensions, cell size and map seed;
- initial population quantities/locations;
- resource overrides;
- technical catalog files and enabled/disabled possibilities;
- actor knowledge present at time zero;
- generic model parameters and metadata.

`load_effective_affordance_catalog()` merges configured catalogs and validates the technical possibility space for that universe. Enabling a technology means **the possibility exists**, not that anyone knows it.

An example blueprint is stored at `configs/worlds/control_tower_example.json`.

**Control Tower invariant:** configuration defines initial conditions and possibility spaces, never desired outcomes or story beats. Long term the UI must compile to this same versioned configuration source of truth.

### Validation

Tests cover:
- blueprint loading and initial-condition parsing;
- world-specific technology enable/disable filtering;
- requirement that catalog technologies expose causal effects;
- writing effects gated by actual record context and probabilistic credibility;
- iron knowledge producing no combat benefit without equipment;
- actor-local technology effect resolution;
- creation/use of durable narrative records without truth leakage.

### Next dependencies

1. wire the blueprint into the actual world factory and snapshot effective config/catalog versions in run artifacts;
2. bind technology requirement/effect contexts to real world material state rather than manually supplied context maps;
3. integrate actor knowledge with actual work/encounters/socialization and generate experience from real activities;
4. feed technology effect channels into all relevant domain equations (production, storage, construction, combat, transport, information);
5. add schema versioning, parameter registry and eventually a visual Control Tower UI;
6. support batch blueprints, counterfactual overlays and inverse-inference experiment definitions.

**References:** `docs/CONTROL_TOWER_FOUNDATION.md`, `docs/CULTURE_TECHNOLOGY_FOUNDATION.md`.
