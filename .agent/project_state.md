# SimWorld project state

## Current phase

**Material disequilibrium + institutional-emergence foundation active, with primitive property simplified into asset relations**

The repository now has ten connected foundations:

1. causal/event kernel;
2. remote automation;
3. spatial/geopolitical substrate;
4. epistemic-social/cultural layer;
5. biological generations + multiplex social networks;
6. household, gestation, relationship evolution and inheritance;
7. assets, inventories, production/consumption and spatial exchange;
8. obligations, cooperation, generic organizations and derived authority/legitimacy;
9. household-level storage, spoilage, heterogeneous demand and local material shocks;
10. pre-legal asset relations: possession, use, control, claim and observer-specific recognition.

Every material milestone must be recorded in `docs/DEVELOPMENT_LEDGER.md`.

## Current architecture

```text
TIME + SPACE
    ↓
PHYSICAL WORLD / ASSETS
    ↓
POSSESSION / USE / CONTROL / CLAIMS
    ↓
RECOGNITION (actor-specific)
    ↓
PRODUCTION / STORAGE / CONSUMPTION / SHOCKS
    ↓
SURPLUS / DEFICIT / EXCHANGE / OBLIGATIONS
    ↓
EXPERIENCE / INFORMATION / BELIEF / DECISION
    ↓
HOUSEHOLDS / RELATIONSHIPS / GENERATIONS
    ↓
COOPERATION / ORGANIZATIONS
    ↓
DERIVED AUTHORITY + LEGITIMACY
    ↓
FUTURE INSTITUTIONS MAY DEFINE/ENFORCE FORMAL PROPERTY
    ↓
FUTURE TERRITORIAL POLITICS / STATES / CONFLICT
```

## Simplification rule

SimWorld should prefer **small generic primitives plus derived historical structures** over separate bespoke systems for each era.

The world does not contain a universal legal fact called `property`. It contains assets and actor↔asset relations:
- `possess`;
- `use`;
- `control`;
- `claim`.

Other actors may recognize a claim to different degrees. Later norms, offices or institutions may turn some combinations of claim + recognition + control + enforcement into what an observer calls formal property.

Documents are future information/evidence objects. A deed or registry entry is not globally authoritative by construction; its force depends on who recognizes its issuer and on effective institutions/enforcement.

Read `docs/RESOURCE_CLAIMS_FOUNDATION.md`.

## Current diagnostic principle

Do not make the model complicated merely to produce visible history. If a high-level process stays dormant, first ask whether lower-level heterogeneity/opportunities are missing. Do not add event quotas or artificial narrative triggers.

## Critical invariants

- world truth != actor knowledge;
- asset != property;
- possession != use != control != claim;
- claim != recognition;
- recognition != effective control;
- document != truth;
- formal property requires institutional context;
- need/shock != prescribed action;
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

1. validate M9/M10 across multiple seeds and ensure lower-level disequilibrium can activate exchange/credit without forced events;
2. deterministic RNG substreams by actor/process/domain;
3. movement/encounter process based on actual travel, work, markets and institutions;
4. storage/transport infrastructure and transport loss;
5. spatial possession/use/control/claims on cells/parcels using the same generic asset-relation model;
6. actor/institution-specific recognition and dispute over claims;
7. generic evidence/document objects only when communication/institutions need them;
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
