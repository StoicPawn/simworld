# SimWorld project state

## Current phase

**First real world + epistemic/cultural + generational social-network foundation active**

The repository now has five connected foundations:

1. causal/event kernel;
2. remote automation;
3. spatial/geopolitical substrate;
4. epistemic-social/cultural layer;
5. biological generations + multiplex social networks.

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
DECISION / ACTION
    ↓
CONSEQUENCES
    ↓
PERCEIVED LEARNING + SOCIAL MEMORY
    ↓
BIOLOGICAL GENERATIONS + SOCIAL NETWORK PROPAGATION
    ↓
FUTURE ACTIONS / EMERGENT GROUPS / INSTITUTIONS
```

Read `docs/EPISTEMIC_CULTURAL_FOUNDATION.md` and `docs/KINSHIP_SOCIAL_NETWORK_FOUNDATION.md`.

## Implemented world substrate

### Core
- persistent entities;
- immutable events;
- concurrent timestamps;
- append-only event history;
- causal graph;
- relevance/resolution;
- seeded scheduling.

### Space and first physical world
- fine raster/chunk map;
- terrain-sensitive routing;
- generated land/water, elevation, rainfall, temperature, fertility, timber, ore and habitability;
- settlement location constrained by geography;
- ore truth can exist before discovery.

### First historical dynamics
- simultaneous local harvest histories;
- food-linked demographic change;
- geography-constrained migration;
- migration joins previously separate causal histories;
- reproducible long runs.

## Epistemic/social implementation

### Needs
`NeedState` represents pressures such as food security, stability, legitimacy and authority. Needs alter incentives but never directly invoke policies.

### Knowledge and belief
`EpistemicState` separates beliefs and memories from world truth. Actors update beliefs only through observations or messages available to them.

### Trust and communication
`TrustProfile` is contextual. `Message` separates asserted content from simulator-side truth provenance. Reports can be distorted; receivers update beliefs using trust, not hidden truth.

### Learning and decision
`StrategyLearner` stores perceived rewards separately from latent/modelled effects. `choose_action` uses bounded stochastic choice over feasible actions, so the same shortage need can lead to different policies or inaction.

### Social memory
`Narrative` and `SocialMemory` make stories first-class information objects linked to origin events. Narrative versions may branch, mutate and persist through trusted transmission. Culture is derived rather than assigned.

## New biological/generational foundation

### Biological persons
`PersonRecord` stores birth/death and biological parentage separately from social identity. Parent, child, sibling, ancestor, descendant and shared-ancestor relationships are derived through `KinshipGraph`.

### Reproduction
`ReproductiveProfile` and `conception_probability` provide a probabilistic reproductive substrate. Intimacy or partnership creates opportunity, never a guaranteed birth. Probability may depend on biological capability, age, health, contact, resources, intent and later prevention/technology.

A birth creates:
- biological parent links;
- parent-child social ties;
- sibling ties where applicable;
- a co-parent relation between the two parents.

It does **not** force romance, affection, marriage, co-residence, loyalty or cooperation.

### Multiplex social network
`SocialGraph` and `SocialTie` support simultaneous time-dependent relations such as:
- friendship;
- rivalry;
- romantic/intimate connection;
- parent-child;
- sibling;
- co-parenting;
- later care, debt, employment, patronage, political alliance and other domains.

Each tie can carry strength, sentiment, trust, dependence, visibility and temporal extent. First-, second- and higher-order network connections are queryable.

### Emergent family/house concept
`LineageView` is a derived view over biological descent. The simulation can identify lineage candidates retrospectively from descent size plus social cohesion, but does not declare a `House` from blood alone.

Future family/house/dynasty formation must combine some subset of:
- descent;
- shared residence;
- property;
- inherited roles/claims;
- names;
- social cohesion;
- memory/narratives;
- self-recognition;
- recognition by outsiders;
- alliance/marriage networks.

Branches of one biological lineage may split into different houses. Unrelated people may be incorporated into the same social/institutional family. Kin may become enemies.

## Integrated generational vertical slice

The current generational runner materializes a small number of people per settlement and then permits:
- heterogeneous romantic/intimate ties;
- friendship and rivalry;
- probabilistic births;
- deaths;
- derived siblings/ancestors/descendants;
- co-parent relations without forced affection;
- new local social connections;
- networks-of-networks queries;
- retrospective lineage candidates;
- interaction with existing geography, food, politics, imperfect information, learning and narratives.

Detailed persons are **not** intended to replace aggregate population. Planet-scale simulations must keep most people aggregated and materialize individuals/families only when causal relevance, requested observation or institutional role requires it.

## Next work

1. deterministic RNG substreams by actor/domain;
2. relationship evolution: formation, decay, separation, reconciliation, caregiving and household co-residence;
3. mate/partner meeting through spatial/social networks rather than initial pair seeding;
4. pregnancy/gestation and infant/child dependency rather than instantaneous annual birth;
5. household resource pools and care burdens;
6. inheritance of property, debt, office, claims, names and stories as distinct processes;
7. family branching, incorporation and explicit recognition mechanisms;
8. richer memory retrieval/forgetting and intergenerational narrative transmission;
9. internal causal models and mistaken causal theories;
10. production, inventories and trade;
11. norms, sanctions, religion, identities and culture emerging over generations;
12. authority/state formation from networks, resources, institutions and recognition;
13. diplomacy/conflict using actor beliefs rather than omniscient truth;
14. counterfactual and inverse inference over hidden information/beliefs.

## Architectural warnings

- Never encode `problem -> correct action` as a historical law.
- Never give political actors direct access to hidden world state.
- Never equate speech, belief and reality.
- Never equate immediate perceived success with true long-run success.
- Never make a narrative replace event provenance.
- Never assign culture as an unexplained static trope.
- Never equate biological kinship with loyalty, affection or political identity.
- Never make partnership deterministically produce children.
- Never make offspring imply romance between parents.
- Never make `House` or `Dynasty` a primitive biological truth.
- Preserve many simultaneous histories and allow chains to remain isolated, branch or converge.
