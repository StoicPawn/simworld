# SimWorld project state

## Current phase

**First real world + epistemic/cultural foundation active**

The repository now has four connected foundations:

1. causal/event kernel;
2. remote automation;
3. spatial/geopolitical substrate;
4. first epistemic-social layer.

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
FUTURE ACTIONS
```

This feedback loop is now part of the project's permanent architecture. Read `docs/EPISTEMIC_CULTURAL_FOUNDATION.md`.

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

## New epistemic/social implementation

### Needs
`NeedState` represents pressures such as food security, stability, legitimacy and authority. Needs alter incentives but never directly invoke policies.

### Knowledge and belief
`EpistemicState` separates beliefs and memories from world truth. Actors update beliefs only through observations or messages available to them.

### Trust
`TrustProfile` is contextual. One source can be trusted differently for food, military, finance or other domains. Trust can update when later evidence allows a claim to be evaluated.

### Communication
`Message` separates asserted content from simulator-side truth provenance. Reports can be distorted by fear, grievance, limited honesty or noise. Receivers update beliefs using their trust, not hidden truth.

### Learning
`StrategyLearner` stores perceived rewards separately from latent/modelled effects. This permits actors to learn the wrong causal lesson.

Example now possible in code:

```text
coercion
-> visible stability rises
-> house learns coercion works
-> latent resentment rises
-> future truthful reporting can worsen
```

### Decision-making
`choose_action` uses bounded stochastic choice over feasible actions. Similar needs can produce different policies because beliefs, resources, dispositions, past learning and randomness differ.

The first action menu includes field expansion, food procurement, reserve distribution, coercion, investigation and inaction. This is a vertical-slice menu, not a hard-coded mapping from shortage to solution.

### Social memory
`Narrative` and `SocialMemory` make stories first-class information objects linked to origin events. Narratives can have versions, confidence, emotional valence, transmission ancestry and mutation.

A ruling house and local population can form different memories of the same hardship. Repeated transmission can preserve or distort claims. Culture is intended to be derived from persistent distributions of such beliefs/narratives, not assigned as a stereotype.

## Integrated social-world vertical slice

Each settlement receives:
- a local house/political actor;
- a local representative;
- contextual trust relations;
- private epistemic state;
- strategy learning state;
- political needs.

Each simulated year can now produce:
- harvest and demographic events;
- experienced shortage;
- petitions/reports that may misstate reality;
- house belief updates;
- stochastic policy choice;
- immediate political effects;
- latent resentment effects;
- later report verification and trust updating;
- narrative formation;
- narrative transmission and drift;
- migration/discovery from the physical layer.

The event graph therefore contains both material and informational causality.

## Still deliberately incomplete

The implementation is an architectural seed, not a full cognitive or political model. Next work should deepen:

1. deterministic RNG substreams by actor/domain;
2. typed relations and social networks;
3. households, generations and role succession;
4. richer memory retrieval/forgetting;
5. internal causal models and mistaken causal theories;
6. strategic deception and information networks;
7. production, inventories and real trade;
8. endogenous settlement founding/abandonment;
9. institutional memory, norms and sanctions;
10. competing narrative branches rather than a single latest-version view;
11. endogenous identities, religions, ideologies and cultures;
12. territorial authority and state formation;
13. diplomacy/conflict using actor beliefs rather than omniscient state;
14. counterfactual and inverse inference over hidden information/beliefs.

## Architectural warnings

- Never encode `problem -> correct action` as a historical law.
- Never give political actors direct access to hidden world state.
- Never equate what an actor says with what it believes.
- Never equate immediate perceived success with true long-run success.
- Never make a narrative replace event provenance.
- Never assign culture as an unexplained static trope when it can emerge from transmission and institutions.
- Preserve many simultaneous histories and allow chains to remain isolated, branch or converge.
