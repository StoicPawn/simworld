# SimWorld project state

## Current phase

**Microgeography + material disequilibrium + institutional emergence active**

The repository now has eleven connected foundations:

1. causal/event kernel;
2. remote automation;
3. spatial/geopolitical substrate;
4. epistemic-social/cultural layer;
5. biological generations + multiplex social networks;
6. household, gestation, relationship evolution and inheritance;
7. assets, inventories, production/consumption and spatial exchange;
8. obligations, cooperation, generic organizations and derived authority/legitimacy;
9. household storage, spoilage, heterogeneous demand and local material shocks;
10. pre-legal asset relations: possession, use, control, claim and recognition;
11. terrain-derived hydrology, cell-level resources, individual local movement/co-presence and sparse emergent-place history.

Every material milestone must be recorded in `docs/DEVELOPMENT_LEDGER.md`.

## Current architecture

```text
TIME + FINE SPACE
    ↓
TERRAIN / WATER / DRAINAGE / LOCAL RESOURCES
    ↓
INDIVIDUAL + HOUSEHOLD LOCATION / MOVEMENT / USE
    ↓
CO-PRESENCE / ENCOUNTER / PRODUCTION / CONFLICT
    ↓
SPARSE CELL HISTORY
    ↓
DERIVED PLACE VIEWS
    ↓
ASSETS / CLAIMS / INVENTORIES / OBLIGATIONS
    ↓
MEMORY / BELIEF / RELATIONSHIPS / GENERATIONS
    ↓
COOPERATION / ORGANIZATIONS / AUTHORITY
    ↓
FUTURE: EMERGENT SETTLEMENTS / MARKETS / HOUSES / STATES
```

## Microgeography foundation

Physical geography now includes continuous `river_strength`, nearby `freshwater_access` and spatially patchy `coastal_food`. These are physical affordances, not labels such as river town, port or good fishing beach.

`CellActivityLedger` is sparse. Only used cells acquire social history. It tracks channels such as visits, gathering, cultivation, exchange, conflict and construction. `PlaceView` is derived from accumulated history and does not itself cause events.

Materialized individuals now have local cell positions in the microgeography vertical slice. Short-range movement is influenced by physical affordances and familiarity. Co-presence creates encounter opportunities; friendly/neutral/hostile outcomes may modify the multiplex social network.

## Complexity rule

Prefer **small generic primitives + derived historical structures**.

Do not add `Market`, `Village`, `House`, `NobleFamily`, `State`, `Port` or similar concepts merely because an observer could name a configuration that way. First ask whether the phenomenon can be reconstructed from physical state, actors, relations, repeated activity, memory, recognition and institutions.

Formal property remains derived from possession/use/control/claim/recognition plus later norms/enforcement. Documents are evidence/information, not truth.

## Critical invariants

- world truth != actor knowledge;
- terrain label != historical role;
- place != place type;
- asset != property;
- possession != use != control != claim;
- claim != recognition != enforcement;
- document != truth;
- movement != guaranteed interaction;
- co-presence != friendship/conflict;
- need/shock != prescribed action;
- kinship != household != loyalty != political identity;
- organization != state;
- authority != legitimacy;
- never tune event quotas to obtain a desired storyline;
- social state over the planet-scale map must stay sparse/adaptive;
- prefer derived concepts over hard-coded historical categories.

## Important transitional limitation

The current vertical slices still seed coarse `settlement` entities before individual history. This is now the largest conceptual mismatch with the ultimate micro→macro objective. The next population/spatial refactor should allow residence clusters and settlements to arise from repeated household/person location, infrastructure and activity, while unresolved background population remains aggregate.

## Next work toward the ultimate objective

1. validate M11 and compare whether high-activity cells correlate with physical affordances without being predetermined by them;
2. de-hardcode settlements into derived residence/activity clusters with adaptive materialization;
3. household relocation, persistent dwellings/site improvements and abandonment;
4. individual movement over longer paths, not only local excursions;
5. connect exchange/credit opportunities to actual co-presence and routes;
6. cell/area possession/use/control/claims using generic asset relations;
7. deterministic RNG substreams by actor/process/domain;
8. richer ecology/resources and terrain dynamics: drainage networks, flood/drought, soils, renewable stocks;
9. norms, sanctions, offices, evidence/documents and dispute resolution only as organizations acquire those capabilities;
10. emergent family/house recognition from people + genealogy + memory + resources + names + outsider recognition;
11. organization competition/protection/extraction and spatial authority;
12. territorial claims/borders and state detection as derived configurations;
13. diplomacy/conflict under imperfect beliefs;
14. counterfactuals, inverse inference and real-world calibration.

## Complexity budget

Before adding a primitive, ask:
1. Can it be state, relation, process, observation or derived view over existing primitives?
2. Does it exist independently of the era/institution being simulated?
3. Does it eliminate special cases rather than create them?

If not, keep it derived.

## Temporary naming warning

The early social vertical slice still contains `house` / `House-XX` placeholders for local authority. They are not genealogical houses and must be refactored before emergent houses are exposed as a first-class derived concept.
