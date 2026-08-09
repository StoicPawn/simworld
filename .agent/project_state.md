# SimWorld project state

## Current phase

**First real world + epistemic/cultural + generational + household/inheritance + material economy foundation active**

The repository now has seven connected foundations:

1. causal/event kernel;
2. remote automation;
3. spatial/geopolitical substrate;
4. epistemic-social/cultural layer;
5. biological generations + multiplex social networks;
6. household, gestation, relationship evolution and inheritance processes;
7. explicit assets/property, inventories, household production/consumption and spatially constrained exchange.

Every material milestone must also be recorded chronologically in `docs/DEVELOPMENT_LEDGER.md`.

## Current architecture

```text
TIME + SPACE
    ↓
OBJECTIVE PHYSICAL / SOCIAL WORLD
    ↓
RESOURCES / ASSETS / RIGHTS / INVENTORIES
    ↓
PRODUCTION / CONSUMPTION / EXCHANGE / OBLIGATIONS
    ↓
EVENTS + EXPERIENCES
    ↓
OBSERVATION / COMMUNICATION
    ↓
MEMORY / BELIEF / NEEDS
    ↓
DECISION / ACTION
    ↓
MATERIAL + SOCIAL CONSEQUENCES
    ↓
RELATIONSHIP / HOUSEHOLD / RESOURCE CHANGE
    ↓
PERCEIVED LEARNING + SOCIAL MEMORY
    ↓
BIOLOGICAL GENERATIONS + SUCCESSION
    ↓
EMERGENT GROUPS / ORGANIZATIONS / AUTHORITY
    ↓
TERRITORIAL POLITICS / STATES / CONFLICT
```

## Implemented substrate

### Core and geography
- persistent entities and immutable events;
- concurrent timestamps, causal graph, relevance/resolution and seeded scheduling;
- fine raster/chunk map, aligned layers and terrain-sensitive least-cost routing;
- generated land/water, elevation, rainfall, temperature, fertility, timber, ore and habitability;
- settlement sites constrained by geography;
- hidden resource truth can exist before actor discovery.

### Population, social and epistemic processes
- local harvests, demography and geography-constrained migration;
- biological persons, kinship, births/deaths and multiplex social ties;
- households independent of blood;
- pregnancy/gestation, relationship evolution and contested succession;
- needs as pressures, beliefs/memory separate from truth, contextual trust and distorted communication;
- perceived learning distinct from latent effect;
- branching narrative objects and transmission.

### Material economy foundation

#### Assets / rights
`Asset`, `PropertyRight` and `PropertyRegistry` represent material things and historically reconstructible partial rights. Ownership/control is no longer reducible to a scalar wealth field.

#### Inventories
`Inventory` holds actual quantities such as grain, timber and tools. Material availability is therefore distinct from wealth, status or belief about availability.

#### Production / consumption
`ProductionProcess` combines labour with land quality, climate, tools, security and other inputs. Household output varies continuously with geography and circumstances; households are not assigned fixed economic castes. Living household members generate labour capacity. Real grain stocks are consumed; shortages may raise debt/stress but never directly prescribe a political action.

#### Spatial exchange
Households with complementary stocks may attempt barter. Same-settlement contact is easiest; cross-settlement exchange depends on least-cost spatial accessibility. Existing social connection can affect acceptance without determining it. Rejected exchanges are also historical events.

Read `docs/MATERIAL_ECONOMY_FOUNDATION.md`.

## Critical invariants

- world truth != actor knowledge;
- need != action;
- kinship != affection != loyalty != household != political identity;
- conception != birth;
- co-residence != family;
- inheritance != biological descent;
- resource truth != access != possession != ownership != control != wealth;
- wealth != inventory != food security != productive capacity;
- ownership/right must remain temporal and historically reconstructible;
- scarcity changes constraints and incentives but does not directly create revolts, trade, migration or policy;
- family/house/dynasty must emerge from interacting biological, social, material, mnemonic and recognition processes;
- detailed people/households remain adaptive refinements over aggregate population.

## Next work toward the ultimate objective

1. deterministic RNG substreams by actor/process/domain;
2. real encounter/movement process for endogenous friendship, partnership, work and exchange networks;
3. explicit parcel/cell ownership and contested possession/control distinct from legal/social right;
4. storage, spoilage, transport capacity and infrastructure;
5. credit contracts, debt networks, rent, tribute, taxation and labour obligations;
6. personal/household land inheritance wired directly into the property registry;
7. household fission/fusion, incorporation/adoption and emergent family self/outsider recognition;
8. organizations (work groups, guilds, religious bodies, armed groups) emerging from repeated cooperation and resources;
9. norms, sanctions, religion, identity, education/socialization and endogenous value formation;
10. authority emerging from protection, extraction, dependency, resources, information and recognition;
11. territorial control/claims/borders as derived spatial states;
12. diplomacy and conflict using actor beliefs rather than omniscient truth;
13. batch counterfactual simulation and trajectory analysis;
14. inverse inference over hidden resources, information, beliefs and incentives;
15. real-world geospatial ingestion/calibration for uncertainty-aware geopolitical scenario analysis.

## Temporary naming warning

The earlier social vertical slice still contains entities internally named `house`/`House-XX`. They are placeholders for local political authorities, **not genealogical houses**. They must be renamed/refactored before true emergent houses are introduced.
