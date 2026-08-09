# SimWorld project state

## Current phase

**Material disequilibrium + asset-claim simplification + encounter-driven social foundation active**

The repository now has eleven connected foundations:

1. causal/event kernel;
2. remote automation;
3. spatial/geopolitical substrate;
4. epistemic-social/cultural layer;
5. biological generations + multiplex social networks;
6. household, gestation, relationship evolution and inheritance;
7. assets, inventories, production/consumption and spatial exchange;
8. obligations, cooperation, generic organizations and derived authority/legitimacy;
9. household-level storage, spoilage, heterogeneous demand and local material shocks;
10. pre-legal asset relations: possession, use, control, claim and observer-specific recognition;
11. encounter/mobility substrate: visits, shared-space encounters, cumulative exposure and encounter-driven relationship formation.

Every material milestone must be recorded in `docs/DEVELOPMENT_LEDGER.md`.

## Current architecture

```text
TIME + SPACE
    ↓
PHYSICAL WORLD / ASSETS
    ↓
POSSESSION / USE / CONTROL / CLAIMS
    ↓
PRODUCTION / STORAGE / CONSUMPTION / SHOCKS
    ↓
MOVEMENT / PRESENCE / ENCOUNTERS
    ↓
SOCIAL EXPOSURE / RELATIONSHIPS / INFORMATION FLOW
    ↓
SURPLUS / DEFICIT / EXCHANGE / OBLIGATIONS
    ↓
EXPERIENCE / INFORMATION / BELIEF / DECISION
    ↓
HOUSEHOLDS / GENERATIONS / SUCCESSION
    ↓
COOPERATION / ORGANIZATIONS
    ↓
DERIVED AUTHORITY + LEGITIMACY
    ↓
FUTURE NORMS / OFFICES / CONTROL FIELDS / POLITICAL FORMATIONS
```

## Simplification rule

SimWorld prefers **small generic primitives plus derived historical structures** over bespoke systems for each era.

Before introducing a primitive, ask whether the concept can instead be represented as:
- state;
- relation;
- process;
- observation/information;
- derived view.

Examples already applied:
- property is derived from asset relations + recognition + institutions;
- family/house/dynasty is derived from biological/social/material/mnemonic relations;
- authority is derived from historical interaction, not assigned as a title;
- a new social relation now requires encounter opportunity rather than spontaneous pairing.

## Encounter foundation

`Visit` records temporary movement between settlements. `Encounter` records shared-space contact between actors. `EncounterLedger` accumulates exposure for each pair.

A visit does **not** imply a relationship. An encounter does **not** imply friendship, rivalry, exchange or romance. Accumulated exposure only creates an opportunity for a social tie to form probabilistically.

Local encounters and travel contacts use the same substrate. Future work, markets, religious gatherings, military service, schools, offices and organizations should add encounter contexts rather than invent separate relationship-generation systems.

Travel is constrained by the existing spatial accessibility layer. This begins replacing abstract random social pairing with causal contact opportunities.

## Current diagnostic principle

Do not make the model complicated merely to produce visible history. If a high-level process stays dormant, inspect whether lower-level opportunities, heterogeneity or contact processes are missing. Do not add event quotas or narrative triggers.

## Critical invariants

- world truth != actor knowledge;
- asset != property;
- possession != use != control != claim;
- claim != recognition;
- document != truth;
- need/shock != prescribed action;
- visit != relationship;
- encounter != relationship;
- social tie formation requires a causal opportunity/contact path in detailed simulation;
- kinship != household != loyalty != political identity;
- request != obligation;
- compliance != consent;
- dependency != loyalty;
- coercion != legitimacy;
- organization != state;
- authority is historical, relational and domain-specific;
- never tune event quotas to obtain a desired storyline;
- prefer derived concepts over hard-coded historical categories.

## Next work toward the ultimate objective

1. validate material disequilibrium and encounter-driven networks across multiple seeds;
2. deterministic RNG substreams by actor/process/domain;
3. enrich movement with recurring destinations/activities while keeping encounter as the primitive contact mechanism;
4. connect encounters to exchange, information transmission and relationship evolution more directly;
5. storage/transport infrastructure and transport loss;
6. spatial possession/use/control/claims on cells/parcels using the same generic asset-relation model;
7. claim disputes, evidence objects and institution-specific recognition;
8. richer obligations: rent, tribute, labour, protection and military duties;
9. norms/sanctions, roles/offices and institutional memory;
10. protection/extraction and coercive capacity;
11. organization competition/fission/merger and emergent family/house recognition;
12. spatial authority/control fields, territorial claims and borders as derived states;
13. coalitions, diplomacy and conflict under imperfect beliefs;
14. state detection as a retrospective configuration, not a primitive constructor;
15. counterfactuals and inverse inference;
16. real-world geospatial ingestion/calibration for uncertainty-aware geopolitical analysis.

## Complexity budget

Before adding a new primitive, ask:
1. Can this be represented as a state, relation, process, observation or derived view over existing primitives?
2. Does the concept exist independently of the institution/era being simulated?
3. Will adding it reduce or increase the number of special-case rules later?

Prefer not to add it when the answers point toward a derived view.

## Temporary naming warning

The early social vertical slice still contains `house` / `House-XX` placeholder entities for local authority. They are **not genealogical houses** and must be removed/refactored before emergent houses are exposed as a first-class derived concept.
