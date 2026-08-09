# SimWorld project state

## Current phase

**First real world + epistemic/cultural + generational + household/inheritance process foundation active**

The repository now has six connected foundations:

1. causal/event kernel;
2. remote automation;
3. spatial/geopolitical substrate;
4. epistemic-social/cultural layer;
5. biological generations + multiplex social networks;
6. household, gestation, relationship evolution and inheritance processes.

Every material milestone must also be recorded chronologically in `docs/DEVELOPMENT_LEDGER.md`.

## Current architecture

```text
TIME + SPACE
    ↓
OBJECTIVE PHYSICAL / SOCIAL WORLD
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
EMERGENT GROUPS / INSTITUTIONS / POLITICS
```

## Implemented substrate

### Core and space
- persistent entities and immutable events;
- concurrent timestamps, causal graph, relevance/resolution and seeded scheduling;
- fine raster/chunk map, aligned layers and terrain-sensitive routing;
- generated land/water, elevation, rainfall, temperature, fertility, timber, ore and habitability;
- settlement sites constrained by geography;
- hidden resource truth can exist before actor discovery.

### Material history
- local harvests and demography;
- geography-constrained migration;
- simultaneous local histories that may remain isolated or converge;
- reproducible runs.

### Epistemic/cultural layer
- needs as pressures, never policies;
- beliefs and memory separate from world truth;
- contextual trust and distorted communication;
- perceived learning separate from latent effects;
- bounded stochastic action choice;
- branching narrative objects and transmission.

### Biological/social layer
- biological persons and kinship graph;
- probabilistic reproductive opportunities;
- births/deaths and ancestor/descendant/sibling relations;
- multiplex temporal social ties;
- higher-order social-network queries;
- lineages as derived views, not primitive houses.

### New life-process layer

#### Households
`Household` and `HouseholdRegistry` represent co-residence/resource-sharing units independently of kinship. Members can move between households. Households carry food stock, wealth, debt, shelter quality and care capacity. Household stress can become a historical event.

#### Gestation
Conception now creates a `Pregnancy` state with a due time. Birth happens only after gestation resolves. Pregnancy may resolve as live birth or pregnancy loss. Partnership/intimacy still does not guarantee conception.

#### Relationship evolution
Existing romantic/intimate/friendship ties can change in sentiment, trust, strength and dependence from repeated interaction, cooperation, stress, betrayal signals and separation pressure. Relationships can end; no relationship label is permanent.

#### Inheritance / succession
Death can open an `Estate`. Wealth, debt, name usage and memory custody are distinct items. Candidate successors receive competing claims based on several independent inputs: biological relatedness, dependence, social relationship, expressed preference, norms and power. Divisible assets may split; different items may pass to different people; contested outcomes are explicit.

This is intentionally not a universal inheritance law. Future institutions, wills, customs, coercion and legal systems can alter claim weights and resolution.

## Critical invariants

- world truth != actor knowledge;
- need != action;
- kinship != affection != loyalty != household != political identity;
- conception != birth;
- offspring != romance;
- co-residence != family;
- inheritance != biological descent;
- a single death can generate different successors for wealth, debt, name, office, claims or memory;
- relationship labels are temporal states, not immutable essences;
- family/house/dynasty must emerge from interacting biological, social, material, mnemonic and recognition processes;
- detailed persons remain an adaptive refinement over aggregate population.

## Next work toward the ultimate objective

1. deterministic RNG substreams by actor/process/domain;
2. spatial/social encounter process for endogenous partner, friendship and rivalry formation;
3. child dependency, caregiving, education and socialization;
4. explicit ownership/property registry and household production/consumption;
5. inheritance of land, offices, claims, debts, names and narrative custody against real registries;
6. household fission/fusion, adoption/incorporation and family recognition;
7. memory retrieval/forgetting and intergenerational narrative transfer through actual kin/social networks;
8. norms, sanctions, religion, identity and endogenous value formation;
9. organizations and authority emerging from networks/resources/recognition;
10. territorial control, diplomacy and conflict using actor beliefs rather than omniscient truth;
11. batch counterfactual simulation and trajectory analysis;
12. inverse inference over hidden resources, information, beliefs and incentives;
13. real-world geospatial ingestion/calibration for uncertainty-aware geopolitical scenario analysis.

## Temporary naming warning

The earlier social vertical slice still contains entities internally named `house`/`House-XX`. They are placeholders for local political authorities, **not genealogical houses**. They must be renamed/refactored before true emergent houses are introduced.
