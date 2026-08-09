# SimWorld project state

## Current phase

**First real world + epistemic/cultural + generational social-network + primitive relational-matrix foundations active**

The repository now has six connected foundations:

1. causal/event kernel;
2. remote automation;
3. spatial/geopolitical substrate;
4. epistemic-social/cultural layer;
5. biological generations + multiplex social networks;
6. prime relational matrices for emergent macro phenomena.

## Foundational architecture

```text
TIME + SPACE
    ↓
OBJECTIVE WORLD
    ↓
EVENTS / EXPERIENCES
    ↓
OBSERVATION / COMMUNICATION
    ↓
MEMORY / BELIEF / NEEDS
    ↓
INTERESTS / CLAIMS / CAPABILITIES / CONSTRAINTS
    ↓
RELATIONAL MATRICES
    ↓
ELEMENTARY INTERACTIONS
    ↓
CONSEQUENCES / LEARNING / SOCIAL MEMORY
    ↓
BIOLOGICAL GENERATIONS + SOCIAL NETWORK PROPAGATION
    ↓
PERSISTENT EMERGENT PATTERNS
    ↓
OPTIONAL HISTORICAL LABELS
```

Macro historical labels are not primitive causes. Read `docs/PRIMITIVE_MATRIX_FOUNDATION.md`.

## Implemented substrate

### Core and space
- persistent entities and immutable events;
- concurrent timestamps and causal graph;
- relevance/adaptive resolution and seeded scheduling;
- fine raster/chunk geography;
- terrain-sensitive routing;
- generated elevation, water, climate baselines, fertility, timber, ore and habitability;
- geography-constrained settlements and migration.

### Epistemics, decisions and social memory
- needs as pressures, not prescribed actions;
- probabilistic beliefs and memory traces;
- contextual trust;
- messages that may be distorted or false;
- later report verification;
- perceived strategy learning separated from latent effects;
- bounded stochastic choices;
- narratives as first-class information objects with branching transmission and mutation.

### Biological generations and networks
- biological persons with birth/death and parentage;
- probabilistic reproduction;
- kinship graph and lineage views;
- multiplex temporal social graph;
- friendship, rivalry, intimacy, parent-child, sibling and co-parent ties;
- higher-order network paths;
- lineage candidates derived retrospectively rather than hard-coded houses.

Detailed persons remain compatible with aggregate population: individuals are materialized where causal relevance warrants it.

## Prime causal matrix doctrine

SimWorld now permanently applies this rule:

> Before adding a macro historical mechanism, seek the smallest reusable matrix of lower-level state, perceptions, constraints, capabilities and interactions that can generate it spontaneously.

The test applies not only to war and alliances but to families, houses, dynasties, factions, states, markets, classes, religions, cultures, rebellions and future macro concepts.

The project must avoid infinite reductionism: a primitive is acceptable when it has independent causal meaning, is reusable across adjacent phenomena and does not presuppose the macro result being explained.

## Primitive relational foundation now implemented

### Interests and claims
`Interest` stores actor preferences by domain/target. `Claim` stores perceived entitlement/control separately from objective truth.

### Relation matrix
`RelationMatrix` derives domain-specific compatibility/incompatibility and combines them with trust, dependence, contact and uncertainty. `ActorRelationProfile` holds capabilities and constraints.

A single pair can simultaneously contain cooperative and conflicting dimensions. There is no global `enemy` or `ally` scalar replacing this state.

### Elementary interactions
The initial low-level vocabulary includes:
- communicate;
- negotiate;
- exchange;
- coordinate;
- withhold;
- threaten;
- obstruct;
- seize;
- attack;
- avoid.

Choice among feasible elementary interactions is bounded and stochastic. Relational pressure does not prescribe a response.

### Conflict and cooperation
Conflict is not synonymous with violence and is not a primitive `WAR` state. It may occur between any actor kinds, including two individuals. The same incompatibility can produce negotiation, avoidance, exchange, threat, coercion, violence or no meaningful action.

Cooperation can be one-off, repeated, domain-specific or simultaneous with hostility elsewhere. Repeated coordination can become alliance-like, but a single cooperative act never creates an alliance automatically.

### Observational macro patterns
`infer_patterns` can retrospectively recognize:
- sustained cooperation;
- competitive rivalry;
- violent feud;
- alliance-like interaction;
- war-like interaction.

These labels are causally inert views. Removing the pattern classifier must not change the underlying simulated trajectory. In particular:
- detecting `war_like` must not generate battles;
- detecting `alliance_like` must not guarantee assistance.

Future simulation logic should use underlying interaction history, capabilities, beliefs, logistics, networks and resources rather than macro labels whenever possible.

## Next work

1. deterministic RNG substreams by actor/domain;
2. relationship evolution: formation, decay, separation, reconciliation, caregiving and co-residence;
3. pregnancy/gestation and child dependency;
4. household resources, inheritance of property/debt/office/claims/names/stories;
5. family branching, incorporation and recognition;
6. perceived relation matrices: actors can misread interests, claims and capabilities;
7. interaction memory feeding future trust, expectations and strategy learning;
8. third-party mediation and multi-actor claim collisions;
9. coalition formation/dissolution from social networks rather than faction flags;
10. explicit commitments, treaties and oaths as causal information/institution objects without guaranteed compliance;
11. mobilization, logistics, command and compliance as lower-level processes;
12. escalation/de-escalation emerging without a war state machine;
13. production, inventories and trade;
14. norms, sanctions, religions, identities and cultures emerging over generations;
15. authority/state formation from networks, resources, institutions and recognition;
16. counterfactual and inverse inference over hidden information, beliefs and relational matrices.

## Architectural warnings

- Never encode `problem -> correct action` as a historical law.
- Never give actors direct access to hidden world state.
- Never equate speech, belief and reality.
- Never equate immediate perceived success with true long-run success.
- Never make narrative replace event provenance.
- Never assign culture as an unexplained static trope.
- Never equate biological kinship with loyalty, affection or political identity.
- Never make partnership deterministically produce children.
- Never make offspring imply romance between parents.
- Never make `House`, `Dynasty`, `Alliance`, `Faction` or `War` a magical primitive when lower-level matrices suffice.
- Never let a macro classifier alter the trajectory it classifies.
- Preserve many simultaneous histories and allow chains to remain isolated, branch or converge.
