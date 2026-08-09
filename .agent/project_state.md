# SimWorld project state

## Current phase

**Institutional-emergence foundation active above the material world**

The repository now has eight connected foundations:

1. causal/event kernel;
2. remote automation;
3. spatial/geopolitical substrate;
4. epistemic-social/cultural layer;
5. biological generations + multiplex social networks;
6. household, gestation, relationship evolution and inheritance;
7. explicit assets/property, inventories, production/consumption and spatial exchange;
8. obligations, cooperation, generic organizations and derived authority/legitimacy signals.

Every material milestone must be recorded in `docs/DEVELOPMENT_LEDGER.md`. Read also `docs/INSTITUTIONAL_AUTHORITY_FOUNDATION.md`.

## Current architecture

```text
TIME + SPACE
    ↓
OBJECTIVE PHYSICAL / SOCIAL WORLD
    ↓
RESOURCES / ASSETS / RIGHTS / INVENTORIES
    ↓
PRODUCTION / CONSUMPTION / EXCHANGE
    ↓
OBLIGATIONS / DEPENDENCIES / COOPERATION
    ↓
EVENTS + EXPERIENCES
    ↓
OBSERVATION / COMMUNICATION / MEMORY / BELIEF
    ↓
NEEDS / DECISION / ACTION
    ↓
HOUSEHOLDS / RELATIONSHIPS / GENERATIONS / SUCCESSION
    ↓
GENERIC ORGANIZATIONS
    ↓
DERIVED AUTHORITY + LEGITIMACY SIGNALS
    ↓
FUTURE: NORMS / OFFICES / CONTROL / CLAIMS / STATES / CONFLICT
```

## Implemented material/institutional bridge

### Obligations
`ObligationRegistry` represents historically explicit duties between arbitrary actors. Current vertical slice uses grain credit, but the primitive is general enough for future rent, tribute, taxation, labour service, protection, military service and contractual delivery.

Credit formation depends on actual stock, geography, social connection and previous cooperation. Accepted credit moves real grain and creates an obligation. Repayment, partial repayment and default are explicit events.

### Cooperation
`CooperationLedger` reinforces repeated successful interactions and can weaken after failure. It derives connected cooperation components without declaring those components to be families, houses, guilds, states or any other predetermined institution.

### Organizations
`Organization` is generic: membership, purpose weights, pooled resources and recognition. Repeated cooperation may probabilistically produce an organization. Organizations can pool voluntary grain and redistribute aid. They remain non-political unless later history gives them political roles.

### Authority
`AuthorityIndex` derives domain-specific relationships from separate observations of compliance, dependency, recognition, provision and coercion.

`effective_authority` != `legitimacy_signal`.

A coercive actor can have effective authority with low legitimacy. A recognized actor may have legitimacy but little effective capacity. Material authority does not imply territorial, military, religious or familial authority.

## Critical invariants

- world truth != actor knowledge;
- need != action;
- kinship != household != loyalty != political identity;
- resource truth != access != possession != ownership != control != wealth;
- request != obligation;
- compliance != consent;
- dependency != loyalty;
- coercion != legitimacy;
- organization != institution != government != state;
- authority is historical, relational and domain-specific;
- economic dependency may become political power later but never automatically;
- family/house/dynasty and state remain emergent categories;
- no event is generated merely because it makes a better story.

## Next work toward the ultimate objective

1. deterministic RNG substreams by actor/process/domain;
2. spatial/social encounter process based on actual movement, workplaces, markets and institutions;
3. cell/parcel ownership, possession and contested effective control;
4. transport, storage, spoilage, roads, ports and market infrastructure;
5. richer obligations: rent, tribute, taxation, labour service, protection and military duties;
6. norms, sanctions and actor-specific recognition determining which obligations are considered valid;
7. offices/roles with succession distinct from organizations and biological lines;
8. organization fission, merger, competition, nesting and institutional memory;
9. protection/extraction and material coercive capacity;
10. emergent family/house recognition from descent + property + memory + names + roles + outsider recognition;
11. spatial authority/control fields, territorial claims and borders as derived states;
12. coalitions, diplomacy and conflict using imperfect actor beliefs;
13. state detection/formation as a retrospective configuration, not a primitive constructor;
14. batch counterfactual simulation and causal attribution;
15. inverse inference over hidden resources, information, beliefs, incentives and institutions;
16. real-world geospatial ingestion/calibration for uncertainty-aware geopolitical analysis.

## Temporary naming warning

The early social vertical slice still contains `house` / `House-XX` placeholder entities for local authority. They are **not genealogical houses** and must be removed/refactored before emergent houses are exposed as a first-class derived concept.
