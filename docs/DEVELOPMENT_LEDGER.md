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

**New primitives:**
- `Asset` as a real productive/material object;
- temporal, partial, typed `PropertyRight`;
- `PropertyRegistry` preserving historical ownership and transfers;
- `Inventory` for actual stocks, distinct from abstract wealth;
- generic `ProductionProcess` and environmental/labour context;
- bilateral `ExchangeProposal`/`ExchangeResult`;
- integrated household-level field assets, production, consumption, shortage, debt effects and barter.

**Integrated processes:**
- field productivity depends on local map fertility and household productive capacity;
- labour depends on living materialized household members and health/age;
- grain and timber production depend on climate, local resources, tools, debt/security pressure and heterogeneous continuous skills;
- households consume real grain stocks rather than only reading an abstract food score;
- complementary shortage/surplus can create exchange opportunities;
- cross-settlement exchange is constrained by least-cost geography;
- social connections can improve acceptance, but do not guarantee exchange;
- rejected exchanges are preserved as historical events.

**New invariants:**
- resource truth != access != possession != ownership != control != wealth;
- ownership is temporal and historically reconstructible;
- scarcity alters constraints and incentives, never directly triggers a prescribed social/political outcome;
- economic specialization should emerge from continuous heterogeneity, geography, learning and accumulated history rather than static labels;
- wealth must not substitute for inventory, food security, productive capacity or strategic control.

**Validation:** dedicated tests cover temporal partial property transfer, production sensitivity to material context, stock/acceptance-constrained exchange and an integrated material-world run. CI also executes the new material simulation.

**Known limitations / next dependencies:**
- current field assets are household-scale vertical-slice objects rather than full cell/parcel mosaics;
- no transport inventories, spoilage, storage infrastructure, credit contracts, rent/tribute/tax, prices or organization-level production yet;
- personal land inheritance is not yet wired into the property registry;
- encounter formation remains simplified and must later arise from movement, markets, work, kinship and institutions;
- next major bridge is from material networks and property concentration to explicit obligations, organizations, recognition and emergent authority.
