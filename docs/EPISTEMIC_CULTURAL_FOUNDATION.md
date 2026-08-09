# SimWorld — Epistemic and Cultural Foundation

This document is a foundational architectural contract. It exists to prevent SimWorld from collapsing complex social causality into deterministic response functions.

## Core rule

A need, pressure, shortage, threat or grievance must **never imply one prescribed response**.

Forbidden pattern:

```text
food shortage -> expand fields
high instability -> repress
low legitimacy -> distribute food
```

Required pattern:

```text
objective world
-> local experience
-> partial observation
-> memory
-> communication
-> belief
-> interpretation
-> needs / incentives
-> feasible actions
-> bounded stochastic choice
-> consequence
-> perceived consequence
-> learning
-> social transmission
-> changed future behaviour
```

The actor can misunderstand both the problem and the result of its own action.

## World truth is not actor knowledge

At minimum distinguish:

1. objective world state;
2. what an actor directly experiences;
3. what an actor observes;
4. what others tell the actor;
5. what the actor remembers;
6. what the actor believes;
7. what the actor says;
8. what the actor does.

These may disagree.

Actors are not omniscient. Information can be missing, delayed, distorted, strategically withheld or false. A truthful message may be disbelieved. A lie may be believed. Correct information can be interpreted through a wrong causal model.

## Needs are pressures, not policies

Food, safety, wealth, status, belonging, legitimacy, authority and other needs modify incentives and attention. They do not call action functions.

A house suffering food pressure may expand fields, import food, ration, distribute stores, investigate, threaten dependants, raid neighbours, do nothing, or choose another feasible action introduced by later domains.

The action-selection system must support multiple plausible choices under similar pressure.

## Trust is contextual and historical

Trust should be relational and domain-specific.

An actor can trust an adviser in military matters and distrust the same adviser on finance or food.

Trust changes after later experience makes claims more or less credible. This must not require the speaker to have intended to lie: honest mistakes can reduce trust and successful deception can temporarily increase it.

## Perceived learning is not causal truth

Actors learn from outcomes they perceive.

A coercive policy may immediately suppress visible protest, causing a ruling house to learn that coercion works. At the same time it can increase latent resentment, reduce truthful reporting and create long-run fragility.

Therefore store separately where possible:

```text
perceived reward != latent / modelled effect
```

This distinction is essential for path dependence and institutional failure.

## Communication and deception

A message has at least:

- sender;
- receiver;
- proposition;
- asserted confidence/probability;
- domain;
- motive/provenance where known to the simulator;
- truth relationship, which may remain unknown to receiver.

People can omit, exaggerate, understate, misremember or deliberately deceive. Fear and incentives may affect what is said independently of what is believed.

## Memory

Individual memories should have time, content, confidence and salience. Memory can decay and later be reactivated.

The simulator must not equate event log with actor memory. The event log is world provenance; memory is an actor state.

## Social memory and stories

Stories are first-class information objects derived from events, not authoritative replacements for events.

A story can have:

- one or more origin events;
- competing versions;
- holders/transmitters;
- confidence;
- emotional valence;
- transmission ancestry;
- mutation/drift.

Family transmission with high trust can preserve a story strongly. Rumours can spread with lower acceptance. Repetition can increase perceived certainty while details drift.

Different narratives may arise from the same event. A ruling house and local population can remember the same famine differently.

## Culture must emerge

Do not assign `warrior_culture = true`, `authoritarian_culture = true`, or equivalent labels as unexplained primitives when they can be derived.

Culture is a persistent statistical pattern in beliefs, narratives, norms, learned strategies, institutions and transmission networks.

Example emergence:

```text
famine
-> coercive response
-> visible order returns
-> rulers infer firmness works
-> family narrative celebrates firmness
-> story is transmitted
-> later leaders receive prior expectations
-> institutions reward similar choices
-> a durable political culture emerges
```

The same original event may produce a counter-narrative among subjects and therefore competing cultures.

## No canonical historical interpretation

Events are objective simulation records insofar as the model defines them. Their meaning is not canonical.

Histories can be queried from perspectives:

- ruler;
- house;
- family;
- settlement;
- institution;
- religious group;
- trader network;
- later historian.

Each perspective can have different evidence and narrative inheritance.

## LLM role later

LLMs may help interpret ambiguous information or produce semantic content, but must not bypass this architecture.

A future LLM actor receives only information available to that actor, proposes bounded actions/messages, and has outputs validated by Python. It must never receive hidden world truth unless the modeled actor legitimately knows it.

## Current implementation

The first implementation provides:

- `NeedState`;
- `EpistemicState` and probabilistic beliefs;
- decaying `MemoryTrace`;
- domain-specific `TrustProfile`;
- messages with asserted content and hidden truth provenance;
- trust updates after later verification;
- `StrategyLearner` that learns from perceived reward separately from latent effects;
- softmax bounded action choice;
- `Narrative`, narrative versions and social transmission with drift;
- derived culture signals;
- an integrated house/settlement vertical slice.

This is an architectural seed, not a finished cognitive model. Later work should add richer memory retrieval, causal models, social networks, identity, norms, institutions, generations, role succession, strategic deception and uncertainty-aware learning.
