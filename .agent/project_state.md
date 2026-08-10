# SimWorld project state

## Current phase

**Distributed background population + emergent residential nuclei + material/institutional foundations active**

The repository now has thirteen connected foundations:

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
12. persistent household residence, relocation/site improvement and derived residential nuclei;
13. settlement-independent aggregate population raster with local demographic evolution and household materialization sampling.

Every material milestone must be recorded in `docs/DEVELOPMENT_LEDGER.md`.

## Current architecture

```text
TIME + FINE SPACE
    ↓
TERRAIN / WATER / DRAINAGE / LOCAL RESOURCES
    ↓
DISTRIBUTED BACKGROUND POPULATION FIELD
    ↓
SELECTIVE PERSON / HOUSEHOLD MATERIALIZATION
    ↓
RESIDENCE ↔ LOCAL EXCURSIONS / USE / ENCOUNTERS
    ↓
SPARSE CELL HISTORY
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

## M13 distributed population

`PopulationField` is the first demographic state that does not require settlements. Each cell stores aggregate population, local capacity and terrain-derived suitability. Initial density depends on habitability, fertility, freshwater, coastal food and timber plus bounded micro-variation.

Background population evolves through density-dependent local growth and limited neighbour redistribution. Quiet cells therefore continue demographic evolution without creating one entity per person.

Materialized households are now sampled from the background field rather than being forced to occupy the legacy settlement cells. This decouples detailed social history from the bootstrap settlement geometry while preserving compatibility with older layers.

The old settlement population totals still exist temporarily and therefore are not yet the authoritative demographic state. This duplication is explicitly transitional: the raster must become authoritative before the bootstrap settlement layer can be removed.

## Critical invariants

- population != settlement;
- density hotspot != settlement;
- aggregate population != materialized people;
- materialization is refinement, not a separate source of people;
- quiet regions continue evolving at aggregate resolution;
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

1. validate M13 across seeds and confirm detailed household homes/nuclei are no longer structurally tied to bootstrap settlement cells;
2. make `PopulationField` the authoritative aggregate demographic state and turn old settlement population totals into derived summaries;
3. adaptive person/household materialization and de-materialization around causally relevant cells/nuclei;
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
