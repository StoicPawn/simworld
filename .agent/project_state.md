# SimWorld project state

## Current phase

**Adaptive multi-resolution population + first generic cultural/knowledge substrate active**

The most advanced branch now combines deterministic replay, keyed RNG substreams, one authoritative terrain population field, adaptive individual representation, unresolved demographic cohorts, and the first substrate from which technology/language/religion/identity can later emerge without primitive historical labels.

Every material milestone must update `docs/DEVELOPMENT_LEDGER.md`, this file and `.agent/roadmap.yaml`.

## Current architecture

```text
ROOT SEED
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

The new cultural substrate deliberately does **not** create `Language`, `Religion`, `Ethnicity`, `Agriculture`, `Metallurgy` or a chronological tech tree as primitive world objects.

It now includes:

- sparse actor-specific `KnowledgeUnit` / `KnowledgeState`;
- partial mastery and confidence;
- imperfect knowledge transmission controlled by trust, communication fit, exposure, complexity and demonstrability;
- knowledge decay/loss moderated by practice, social reinforcement and records;
- generic continuous `ConventionState` with contact-driven convergence and isolation-driven drift;
- non-causal `ConventionClusterView` for retrospective clustering;
- data-defined technical `Affordance` objects;
- `AffordanceCatalog` loaded from JSON rather than domain-specific code branches;
- an initial deliberately small low-level catalog at `configs/affordances/foundation.json`;
- technical opportunity checks based on actual materials, prior capabilities and environment;
- bounded innovation probability from opportunity + experience + experimentation + contact/problem pressure;
- zero discovery probability when hard prerequisites are absent;
- no guarantee of discovery even when all prerequisites exist;
- `attempt_innovation()` which creates/improves knowledge only for the discovering actor rather than changing a global technology level.

Technology therefore uses a deliberately bounded compromise: SimWorld does not simulate full chemistry/biology/physics, but it also does not script historical unlock sequences. The possibility space is data-defined; history chooses whether, where, when and by whom a capability is discovered, spread, modified or lost.

Read `docs/CULTURE_TECHNOLOGY_FOUNDATION.md`.

## Cultural/macroscopic interpretation policy

### Language
A future language is a derived cluster over many communicative conventions and mutual intelligibility. Contact, mobility, trade, family transmission, prestige, administration and schooling may drive convergence; isolation, drift, local networks and identity resistance may drive divergence. A valid run may retain one broad language network or fragment into many; there is no target language count.

### Religion
A religion is a future derived configuration over beliefs, narratives, rituals, norms, symbols, trusted transmitters and institutions. Private belief, ritual participation and social membership remain distinct.

### Human ancestry / ethnicity / race-like categories
Biological ancestry, heritable phenotype and actor-created social classification are distinct. Social categories must never be inferred automatically from phenotype. Genuinely distinct fantasy species may be physical biological primitives only when the world definition explicitly contains different species.

### Technology
High-level technologies are derived capability configurations. A technique may be independently rediscovered, remain local, diffuse, mutate or disappear. `possible != discovered != widespread != institutionally retained`.

## Critical invariants

- hard-code laws/constraints/opportunity spaces, not historical outcomes;
- no chronological tech tree in the causal kernel;
- meeting technological prerequisites does not guarantee discovery;
- discovery changes actor knowledge, never a universal civilization tech level;
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

1. cohort-aware materialization/dematerialization so detailed people are sampled from and returned to the exact local cohort represented;
2. relevance-driven automatic resolution changes using keyed RNG without perturbing unrelated history;
3. integrate `KnowledgeLedger` with detailed people, encounters, parent/child socialization and household practice;
4. give material activities experience traces so repeated gathering, cultivation, heat use, construction etc. create real capability experience;
5. bind low-level affordance requirements to actual world materials/environment rather than placeholder capability names;
6. emit innovation/history events when actor-local discovery occurs in the integrated world;
7. transmission across actual social/spatial contact and intergenerational teaching;
8. background/aggregate cultural summaries for unresolved population so quiet regions can culturally evolve without materializing every person;
9. generic convention bundles and mutual-comprehension metrics; derive language clusters only as views;
10. belief/ritual/norm transmission over the same substrate; derive cult/religion views later;
11. heritable continuous biological traits and ancestry flow, kept separate from social identity formation;
12. route-based migration/transport and actual exchange/contact networks;
13. household fission/fusion, education/socialization and endogenous inhabited-place evolution;
14. evidence/documents, offices, norms, institutional memory and enforcement;
15. emergent family/casata recognition from genealogy + name + memory + resources + outside recognition;
16. organization competition/protection/extraction and spatial authority;
17. territorial claims, borders and state detection as derived configurations;
18. diplomacy/conflict under imperfect beliefs and unequal technology/information;
19. historical/narrative extraction without a canonical story;
20. counterfactuals, inverse inference and real-world calibration.

## Complexity budget

Before adding a primitive ask whether it can instead be represented as state, relation, process, observation, transmissible information or derived view. In particular, do not create new primitive classes merely because historians have a noun for a macroscopic configuration.

For technology, the exception is an explicit **possibility catalog**: chemical/physical affordances that SimWorld does not derive from first-principles physics may be supplied as data. Those definitions constrain what is possible; they must never prescribe when or whether history reaches it.

## Temporary naming warning

The early social slice still contains `house` / `House-XX` placeholders for local authority. They are not genealogical houses and must be renamed/refactored before true emergent casate are exposed.
