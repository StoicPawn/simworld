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
