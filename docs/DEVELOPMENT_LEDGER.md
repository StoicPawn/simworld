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

## 2026-08-09 — M7 Material economy and spatial exchange

**Intent:** create the material substrate from which durable economic asymmetry and later political power can emerge without assigning economic castes, houses or rulers in advance.

**Historical note:** this milestone initially introduced `PropertyRight`; M10 supersedes that choice with more elementary asset relations.

**Retained processes:** assets, inventories, production, consumption, shortage, barter and geography-constrained exchange.

---

## 2026-08-09 — M8 Obligations, organizations and derived authority

**Intent:** bridge material/social interaction into durable institutional structure without declaring rulers, classes, houses, governments or states as primitive objects.

**Primitives/processes:** general obligations, cooperation ledger, generic organizations and authority signals separated into compliance, dependency, recognition, provision and coercion.

**Invariant:** effective authority != legitimacy; organization != state.

---

## 2026-08-09 — M9 Material disequilibrium, storage and local shocks

**Intent:** create plausible asynchronous surplus/deficit conditions so exchange, credit, dependency and organization can emerge from material history instead of event quotas.

**Processes:** household storage profiles, spoilage, heterogeneous demand, local crop/storage/tool shocks and explicit unmet food need.

**Invariant:** do not tune for target numbers of trades, revolts, organizations, wars or states.

---

## 2026-08-09 — M10 Primitive simplification: asset relations before property

**Intent:** avoid projecting modern legal property backward into worlds without institutions capable of defining or enforcing it.

**Architecture:** `Asset` + temporal `AssetRelation` (`possess`, `use`, `control`, `claim`) + observer-specific `Recognition`. Formal property is a future derived view over claims, recognition, control, norms and enforcement. Documents will be evidence/information objects, not world truth.

**Invariant:** asset != possession != use != control != claim != recognized claim != legal property.

**Reference:** `docs/RESOURCE_CLAIMS_FOUNDATION.md`.

---

## 2026-08-10 — M11 Individual spatial presence, movement and emergent places

**Intent:** make micro-geography causally visible at the individual level so important places can arise from repeated human activity instead of being declared as markets, centres, squares, ports or strategic sites.

**New primitive:** `PresenceLedger`, storing current materialized-person position plus historical visit, unique-visitor, encounter and productive-use counts per cell.

**New processes:**
- materialized individuals begin at actual settlement cells;
- people make bounded stochastic local movements over passable neighbouring cells;
- destination attractiveness depends on physical fertility, timber, habitability, movement cost, accumulated familiarity and individual stochastic variation;
- newborns and later-materialized individuals acquire spatial presence lazily when needed;
- co-presence in the same cell creates explicit `spatial_encounter` events;
- previously unconnected people may form acquaintance or rivalry ties after real co-presence;
- productive asset use contributes to the history of the specific cell where the asset exists;
- `site_intensity` is a derived analytical signal from activity history only.

**New invariants:**
- place importance != permanent map flag;
- co-presence precedes encounter-derived social contact;
- `market`, `centre`, `harbour`, `village`, `sacred place` and similar labels should be derived views unless a later institution explicitly names them;
- site intensity may guide observation/refinement but must not itself cause future visits;
- micro-geographic differences are allowed to compound historically through repeated use and familiarity.

**Validation target:** tests require actual movement, co-presence events and emergence of active cells without creating any market/centre primitive. CI runs a dedicated spatial-life vertical slice and reports the most active cells with their visit/visitor/encounter/use decomposition.

**Next dependencies:** persistent multi-step travel, route learning, temporary vs habitual residence, work/foraging tasks tied to material needs, cell-level resource extraction/depletion, infrastructure built by repeated use, and retrospective settlement/market/route views.
