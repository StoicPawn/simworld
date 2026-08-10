# SimWorld project state

## Current phase

**True multi-resolution population accounting + adaptive-resolution-safe randomness + deterministic replay active**

The repository now has seventeen connected foundations. M17 adds the first genuine aggregate↔individual demographic bridge: detailed people are no longer a parallel population but a reserved high-resolution representation of the authoritative raster.

## Current architecture

```text
ROOT SEED
    ↓
KEYED RNG NAMESPACES + DETERMINISTIC CAUSAL ORDER
    ↓
TIME + FINE PHYSICAL SPACE
    ↓
AUTHORITATIVE TOTAL POPULATION FIELD
    ├─ unresolved share → aggregate demographic dynamics
    └─ reserved share   → detailed people / life histories
                             ↓
                    births / deaths / residence movement
                             ↓
                    same physical population field
    ↓
RESIDENCE / LOCAL USE / ENCOUNTERS / SPARSE CELL HISTORY
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

## M17 adaptive population accounting

`PopulationField.population` is total physical headcount. `PopulationField.reserved` marks the share currently represented by detailed people. `PopulationRefinementLedger` records the backing cell of every detailed person.

Materializing/dematerializing existing people changes only resolution. Detailed births and deaths alter physical headcount exactly once. Detailed residence movement transfers both total and reserved population between cells while conserving the world total. Aggregate demographic growth and mobility operate only on unresolved population.

The 24-year reference run closed with total population 9,443.701, 38 materialized people, 9,405.701 unresolved people and accounting gap 0.0. Every living detailed person had one active backing record.

## Critical invariants

- `total population = unresolved population + materialized population`;
- resolution change != birth/death/migration;
- every living detailed person has exactly one population backing record;
- detailed birth/death changes population exactly once;
- aggregate demographic dynamics exclude detailed/reserved people;
- detailed spatial relocation moves physical population, not only metadata;
- same seed + same configuration + same code => same semantic history;
- unrelated stochastic scopes must not advance each other's RNG state;
- relevance may change resolution, never causal likelihood;
- one authoritative demographic truth;
- population != settlement; residence != settlement; place != place type;
- reporting partition != region/border/territory;
- derived views must not create causality;
- world truth != actor knowledge;
- kinship != household != loyalty != political identity;
- asset != property; claim != recognition != control;
- organization != state; authority != legitimacy;
- never tune event counts to obtain a desired storyline;
- quiet regions continue evolving at aggregate resolution;
- social state over planet-scale space must remain sparse/adaptive.

## Next work toward the ultimate objective

1. demographic cohorts over the unresolved field: age structure and reproductive role/composition;
2. coherent refinement from cohorts and collapse back into cohorts;
3. relevance-driven automatic materialization/dematerialization that changes resolution only;
4. route-based authoritative long-range population migration;
5. household fission/fusion and endogenous abandonment/growth of inhabited nuclei;
6. exchange/credit from actual co-presence and transport networks;
7. cell/area possession-use-control-claim relations and refinable infrastructure;
8. richer ecology, hazards and physical dynamics;
9. norms, offices, evidence/documents and institutional memory;
10. emergent family/casata recognition from genealogy + memory + resources + names + recognition;
11. organization competition/protection/extraction and spatial authority;
12. territorial claims, borders and state detection as derived configurations;
13. diplomacy/conflict under imperfect beliefs;
14. historical/narrative extraction without a canonical story;
15. counterfactuals, inverse inference and real-world calibration.

## Complexity budget

Prefer generic state, relations, processes and derived views over era-specific primitive objects. Refinement must remove computational cost, not create parallel truths.

## Temporary naming warning

The early social slice still contains `house` / `House-XX` placeholders for local authority. They are not genealogical houses and must be renamed/refactored before true emergent casate are exposed.
