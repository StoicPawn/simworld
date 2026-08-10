# SimWorld project state

## Current phase

**Adaptive multi-resolution population + cultural knowledge + causal technology effects + Control Tower foundation active**

The most advanced branch now combines deterministic replay, keyed RNG substreams, one authoritative terrain population field, adaptive individual representation, unresolved demographic cohorts, emergent cultural knowledge, data-defined technology, and the first declarative Control Tower for world configuration.

Every material milestone must update `docs/DEVELOPMENT_LEDGER.md`, this file and `.agent/roadmap.yaml`.

## Current architecture

```text
CONTROL TOWER / WORLD BLUEPRINT
    ├─ root seed / horizon
    ├─ map source / dimensions / resolution
    ├─ initial population distribution
    ├─ resource overrides
    ├─ enabled technical possibility catalogs
    ├─ initial knowledge
    └─ generic model parameters
             ↓
ROOT SEED + CONFIG SNAPSHOT
             ↓
KEYED RNG NAMESPACES + DETERMINISTIC CAUSAL ORDER
             ↓
TIME + FINE PHYSICAL SPACE
             ↓
PHYSICAL AFFORDANCES / RESOURCES / TERRAIN
             ↓
AUTHORITATIVE TOTAL POPULATION FIELD
    ├─ unresolved share → demographic cohorts / aggregate dynamics
    └─ reserved share   → detailed people / life histories
                             ↓
                    residence / encounters / work / birth / death
                             ↓
                    same physical population truth
             ↓
ACTOR EXPERIENCE / MEMORY / BELIEF
             ↓
GENERIC LEARNED STATE
    ├─ know-how / skills / practices
    ├─ conventions
    ├─ claims / interpretations
    └─ future rituals / symbols / linguistic elements
             ↓
IMPERFECT TRANSMISSION + DRIFT + LOSS + INNOVATION OPPORTUNITY
             ↓
ACTOR-LOCAL TECHNICAL CAPABILITIES
             ↓
GENERIC CAUSAL EFFECT CHANNELS
    ├─ production / storage / construction
    ├─ combat / transport / information
    ├─ record persistence / transmission fidelity
    └─ later domain-specific channels
             ↓
DERIVED HIGHER-ORDER PATTERNS
    ├─ technological traditions/capabilities
    ├─ languages/dialects
    ├─ religions/cults
    ├─ identities/ethnicities
    └─ later institutions/civilizations
             ↓
ASSETS / OBLIGATIONS / ORGANIZATIONS / AUTHORITY
             ↓
FUTURE TERRITORIAL POLITICS / STATES / CONFLICT / INFERENCE
```

## M18 unresolved demographic cohorts

The unresolved population is no longer only scalar headcount. It carries age-band and minimal reproductive biological composition per cell. Cohort totals equal unresolved population and evolve through aging, mortality, births and local mobility while detailed people continue through explicit life-history processes. This preserves one demographic truth across resolutions.

## M19 cultural knowledge and technical affordances

The cultural substrate deliberately does **not** create `Language`, `Religion`, `Ethnicity`, `Agriculture`, `Metallurgy` or a chronological tech tree as primitive world objects.

It includes sparse actor-specific knowledge, partial mastery/confidence, imperfect transmission, decay/loss, generic convention dynamics, retrospective cluster views, data-defined technical affordances, actor-local innovation and a JSON possibility catalog. Technology therefore uses a bounded compromise: SimWorld does not simulate full chemistry/biology/physics, but it also does not script historical unlock sequences.

Read `docs/CULTURE_TECHNOLOGY_FOUNDATION.md`.

## M20 Control Tower and causal technology effects

Technology can no longer be only a discovered label. Every technology loaded from the configured catalog must expose at least one generic causal effect channel. Effects are actor-local, mastery-scaled and context-gated.

Examples now present in the foundation catalog:

- `managed_water_channel` can change cultivation output and drought resilience when usable water is actually available;
- `worked_iron_tools` can affect cultivation, construction and combat only when iron equipment is materially available;
- `durable_symbolic_recording` can enable creation of durable narrative records, improve transmission fidelity and sometimes increase perceived claim credibility when a reader recognizes/accepts the medium;
- writing never converts a claim into truth. A durable record can preserve a false story.

`actor_effect_channels()` resolves the effects available to one actual knowledge holder. There is no civilization-wide technology bonus.

`SocialMemory` now supports `NarrativeRecord`: a record fixes one narrative version and can affect later transmission. Record persistence/credibility are information-social properties, not truth certification.

The first Control Tower lives in `src/simworld/control_tower.py`. `WorldBlueprint` loads a portable JSON experiment definition with simulation seed/horizon, map configuration, population seeds, resource overrides, technology catalogs, enabled/disabled possibilities, initial knowledge and generic parameters. `load_effective_affordance_catalog()` resolves which technical possibilities exist in that particular universe.

Read `docs/CONTROL_TOWER_FOUNDATION.md` and `configs/worlds/control_tower_example.json`.

## Cultural/macroscopic interpretation policy

### Language
A future language is a derived cluster over many communicative conventions and mutual intelligibility. Contact, mobility, trade, family transmission, prestige, administration and schooling may drive convergence; isolation, drift, local networks and identity resistance may drive divergence. A valid run may retain one broad language network or fragment into many; there is no target language count.

### Religion
A religion is a future derived configuration over beliefs, narratives, rituals, norms, symbols, trusted transmitters and institutions. Private belief, ritual participation and social membership remain distinct.

### Human ancestry / ethnicity / race-like categories
Biological ancestry, heritable phenotype and actor-created social classification are distinct. Social categories must never be inferred automatically from phenotype. Genuinely distinct fantasy species may be physical biological primitives only when the world definition explicitly contains different species.

### Technology
High-level technologies are derived capability configurations. A technique may be independently rediscovered, remain local, diffuse, mutate or disappear. `possible != discovered != widespread != institutionally retained`.

A technology may alter many processes, but only through explicit generic channels consumed by those processes. Knowledge without required materials/equipment may have little or no practical effect.

## Critical invariants

- hard-code laws/constraints/opportunity spaces, not historical outcomes;
- Control Tower configuration selects initial conditions and possibility spaces, not storylines;
- a run configuration must eventually be snapshotable/versioned for exact reproducibility;
- no chronological tech tree in the causal kernel;
- meeting technological prerequisites does not guarantee discovery;
- discovery changes actor knowledge, never a universal civilization tech level;
- every configured technical affordance must expose causal world effects;
- technology effects require actual actor knowledge/mastery and relevant context/materials;
- technology must not create unexplained global bonuses;
- writing/records can affect persistence, fidelity and perceived credibility but never truth;
- technology can be lost when carriers/practice/transmission disappear;
- knowledge != truth;
- knowledge possessed by one actor != knowledge possessed by society;
- convention similarity != named language;
- belief cluster != religion;
- biological ancestry != phenotype != social identity;
- no target count for languages, religions, technologies, states or wars;
- cultural convergence and divergence are competing endogenous forces;
- derived cultural labels cannot create causality merely because an analyst detected them;
- `total population = unresolved population + materialized population`;
- resolution change != demographic change;
- same seed + same config + same code => same semantic history;
- unrelated stochastic scopes must not share a random cursor;
- relevance can change simulation resolution, never causal likelihood;
- one authoritative demographic truth;
- population != settlement; residence != settlement; place != place type;
- world truth != actor knowledge;
- kinship != household != loyalty != political identity;
- asset != property; claim != recognition != control;
- organization != state; authority != legitimacy;
- quiet regions continue evolving at aggregate resolution;
- never tune event counts to obtain a desired storyline.

## Next work toward the ultimate objective

1. wire `WorldBlueprint` into the actual world factory so map/population/resources are created from one configuration source;
2. snapshot the exact effective configuration and catalog versions into every run artifact;
3. cohort-aware materialization/dematerialization so detailed people are sampled from and returned to the exact local cohort represented;
4. relevance-driven automatic resolution changes using keyed RNG without perturbing unrelated history;
5. integrate `KnowledgeLedger` with detailed people, encounters, parent/child socialization and household practice;
6. give material activities experience traces so repeated gathering, cultivation, heat use, construction etc. create real capability experience;
7. bind low-level affordance requirements to actual world materials/environment rather than placeholder capability names;
8. wire effect channels into production, storage, construction and later combat/transport/information equations;
9. emit innovation/history events when actor-local discovery occurs in the integrated world;
10. transmission across actual social/spatial contact and intergenerational teaching;
11. background/aggregate cultural summaries for unresolved population so quiet regions can culturally evolve without materializing every person;
12. generic convention bundles and mutual-comprehension metrics; derive language clusters only as views;
13. belief/ritual/norm transmission over the same substrate; derive cult/religion views later;
14. heritable continuous biological traits and ancestry flow, kept separate from social identity formation;
15. route-based migration/transport and actual exchange/contact networks;
16. household fission/fusion, education/socialization and endogenous inhabited-place evolution;
17. evidence/documents, offices, norms, institutional memory and enforcement;
18. emergent family/casata recognition from genealogy + name + memory + resources + outside recognition;
19. organization competition/protection/extraction and spatial authority;
20. territorial claims, borders and state detection as derived configurations;
21. diplomacy/conflict under imperfect beliefs and unequal technology/information;
22. historical/narrative extraction without a canonical story;
23. Control Tower UI, batch experiments, counterfactual overlays, inverse inference and real-world calibration.

## Complexity budget

Before adding a primitive ask whether it can instead be represented as state, relation, process, observation, transmissible information or derived view. In particular, do not create new primitive classes merely because historians have a noun for a macroscopic configuration.

For technology, the exception is an explicit **possibility catalog**: chemical/physical affordances that SimWorld does not derive from first-principles physics may be supplied as data. Those definitions constrain what is possible and expose generic causal effects; they never prescribe when or whether history reaches them.

For world setup, prefer declarative Control Tower fields and validated catalog/config composition over simulation-code edits. The long-term UI should compile to the same portable configuration model rather than creating a second source of truth.

## Temporary naming warning

The early social slice still contains `house` / `House-XX` placeholders for local authority. They are not genealogical houses and must be renamed/refactored before true emergent casate are exposed.
