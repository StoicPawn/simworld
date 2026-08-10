# SimWorld project state

## Current phase

**Authoritative terrain-distributed demography + emergent residential nuclei + material/institutional foundations active**

The repository now has fourteen connected foundations:

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
13. settlement-independent aggregate population raster and household placement;
14. authoritative raster demography with legacy settlement populations reduced to derived compatibility summaries.

Every material milestone must be recorded in `docs/DEVELOPMENT_LEDGER.md`.

## Current architecture

```text
TIME + FINE SPACE
    ↓
TERRAIN / WATER / DRAINAGE / LOCAL RESOURCES
    ↓
AUTHORITATIVE POPULATION FIELD
    ↓                         ↓
BACKGROUND DEMOGRAPHY     DERIVED REPORTING SUMMARIES
    ↓                         ↓
SELECTIVE MATERIALIZATION   LEGACY COMPATIBILITY ONLY
    ↓
RESIDENCE ↔ LOCAL USE / MOVEMENT / ENCOUNTERS
    ↓
SPARSE CELL HISTORY
    ↓
DERIVED PLACES + RESIDENTIAL NUCLEI
    ↓
ASSETS / CLAIMS / INVENTORIES / OBLIGATIONS
    ↓
MEMORY / BELIEF / RELATIONSHIPS / GENERATIONS
    ↓
COOPERATION / ORGANIZATIONS / AUTHORITY
    ↓
FUTURE HIGHER-ORDER STRUCTURES
```

## M14 single demographic truth

`PopulationField` is the sole authoritative aggregate demographic state in the newest vertical slice. Old `settlement.population` values are overwritten from reporting-only summaries and never advance population independently.

The compatibility partition assigns land cells to the nearest old bootstrap anchor only so legacy social processes can receive local summaries. It is not a region, border or territory and has no causal force.

Population advances exactly once per year on the raster. The previous background-population hook is disabled in this layer to prevent double stepping. Old settlement-to-settlement migration is disabled because changing summary values would create a second population truth; future long-range migration must transfer population directly on the field along feasible routes.

## Critical invariants

- one authoritative aggregate demographic state;
- population != settlement;
- density hotspot != settlement;
- reporting partition != region/border/territory;
- legacy settlement population is a projection, not state;
- materialized people must eventually reserve/release aggregate population rather than create a parallel population universe;
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

1. adaptive materialization accounting: reserve people from cells/cohorts when creating detailed persons/households and return compatible aggregate state when detail is collapsed;
2. deterministic RNG substreams before adaptive resolution becomes widespread;
3. demographic cohorts so aggregate births/deaths/age structure and detailed life histories reconcile;
4. long-range household/person migration that moves authoritative population along terrain-constrained routes;
5. household fission/fusion and settlement abandonment/growth from residence history;
6. exchange/credit from actual co-presence and transport routes;
7. cell/area possession/use/control/claims using generic asset relations;
8. refinable persistent site improvements and emergent transport infrastructure;
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
