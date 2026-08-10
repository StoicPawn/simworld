# SimWorld project state

## Current phase

**Microgeography + emergent residential nuclei + material/institutional foundations active**

The repository now has twelve connected foundations:

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
11. terrain-derived hydrology, cell-level resources, local movement/co-presence and sparse place history;
12. persistent household residence, relocation/site improvement and derived residential nuclei.

Every material milestone must be recorded in `docs/DEVELOPMENT_LEDGER.md`.

## Current architecture

```text
TIME + FINE SPACE
    ↓
TERRAIN / WATER / DRAINAGE / LOCAL RESOURCES
    ↓
INDIVIDUALS + HOUSEHOLDS
    ↓
RESIDENCE ↔ LOCAL EXCURSIONS / USE / ENCOUNTERS
    ↓
SPARSE CELL HISTORY
    ↓
RESIDENCE / PRODUCTION / EXCHANGE / CONFLICT / CONSTRUCTION SIGNALS
    ↓
DERIVED PLACE VIEWS + RESIDENTIAL NUCLEI
    ↓
ASSETS / CLAIMS / INVENTORIES / OBLIGATIONS
    ↓
MEMORY / BELIEF / RELATIONSHIPS / GENERATIONS
    ↓
COOPERATION / ORGANIZATIONS / AUTHORITY
    ↓
FUTURE: NAMED SETTLEMENTS / MARKETS / HOUSES / STATES AS EMERGENT STRUCTURES
```

## M12 residence and settlement de-hardcoding

A household now has a persistent residential anchor that is distinct from an individual's short-range activity location. Annual micro-activity is treated as an excursion from that anchor, so random walk drift is not mistaken for migration.

Households can probabilistically shift residence toward nearby cells that offer persistently better physical/material opportunities. Residence and generic site improvement are recorded in the existing sparse cell ledger.

`SettlementNucleusView` clusters adjacent residentially used cells and summarizes actors, persistence, residence, production, exchange, construction and conflict. It is a retrospective projection only: it does not create a village/town/city object and cannot itself affect causal probability.

Bootstrap `settlement` entities still exist because older vertical slices need them for initial aggregate population and founder placement. They are now explicitly compatibility coordinates, not proof that a social settlement already exists.

## Critical invariants

- world truth != actor knowledge;
- terrain label != historical role;
- place != place type;
- residence != settlement;
- settlement nucleus != named settlement;
- construction != building type;
- local movement != migration;
- derived views must not create causality;
- asset != property;
- possession != use != control != claim;
- claim != recognition != enforcement;
- document != truth;
- co-presence != relationship;
- kinship != household != loyalty != political identity;
- organization != state;
- authority != legitimacy;
- never tune event quotas to obtain a desired storyline;
- social state over planet-scale space must remain sparse/adaptive;
- prefer generic primitives and derived structures.

## Next work toward the ultimate objective

1. validate M12 across seeds and inspect whether nuclei relocate/concentrate around terrain affordances without being predetermined;
2. remove bootstrap settlements from initial population placement: use a distributed population field over habitable terrain;
3. adaptive person/household materialization around causally relevant cells and nuclei;
4. household fission/fusion, abandonment and true migration over route networks;
5. connect exchange/credit to actual co-presence and transport routes;
6. cell/area possession/use/control/claims using generic asset relations;
7. persistent site improvements refined into specific assets only when causally relevant;
8. deterministic RNG substreams by actor/process/domain;
9. richer ecology/resources and terrain dynamics;
10. norms, offices, evidence/documents and dispute resolution only as organizations acquire those capabilities;
11. emergent family/house recognition from people + genealogy + memory + resources + names + outsider recognition;
12. organization competition/protection/extraction and spatial authority;
13. territorial claims/borders and state detection as derived configurations;
14. diplomacy/conflict under imperfect beliefs;
15. counterfactuals, inverse inference and real-world calibration.

## Complexity budget

Before adding a primitive, ask whether it can instead be state, relation, process, observation or derived view over existing primitives, whether it exists independently of the era/institution, and whether it removes rather than adds special cases.

## Temporary naming warning

The early social vertical slice still contains `house` / `House-XX` placeholders for local authority. They are not genealogical houses and must be refactored before emergent houses are exposed as a first-class derived concept.
