# Primitive Matrix Foundation

## Foundational principle

SimWorld should model **prime causal matrices** whenever feasible: the smallest reusable set of physical, biological, epistemic, social, economic and relational primitives from which a higher-level phenomenon can emerge.

A macro historical category is not a simulation instruction merely because humans have a convenient noun for it.

Examples:

- `family`, `house`, `dynasty` should arise from descent, care, residence, property, names, memory and recognition;
- `alliance` should arise from repeated coordination, expectations, trust, dependence, common interests, institutions and commitments;
- `war` should arise from persistent organized hostile interactions, capabilities, mobilization, harm, claims, retaliation and coordination;
- `state`, `class`, `religion`, `culture`, `market`, `faction`, `rebellion` and similar categories should be decomposed as far as scientifically and computationally useful before they are made causal primitives.

The goal is not infinite reductionism. A primitive is justified when it is reusable across many phenomena, has independently meaningful state, and can be simulated without presupposing the macro outcome we are trying to explain.

## Prime-matrix test

Before adding a new macro mechanic, ask:

1. Can the phenomenon be described as a persistent pattern over lower-level state/interactions?
2. Which lower-level quantities exist even when the phenomenon does not?
3. Can those quantities also explain adjacent phenomena?
4. Does introducing the macro object create a hidden deterministic shortcut?
5. Could a retrospective classifier identify the phenomenon without affecting its occurrence?
6. Can the same primitive conditions produce multiple outcomes depending on information, actors, networks, capabilities and stochastic experience?

If yes, prefer the lower-level matrix.

## Relational substrate

Relations are multiplex, domain-specific and time-dependent. The primitive relational matrix can contain:

- interests and directional preferences;
- claims and perceived entitlements;
- compatibility and incompatibility by target/domain;
- trust and distrust;
- dependence and substitutability;
- contact/opportunity to interact;
- uncertainty;
- capabilities and constraints;
- memory of prior interactions;
- social-network paths;
- spatial access and distance;
- information/beliefs about all of the above.

No scalar `enemy = true`, `ally = true` or `at_war = true` should replace this state when the underlying dimensions are available.

## Conflict is not war

Conflict is not itself a single primitive event. A conflict-like condition can be an emergent concentration of incompatible claims/interests plus interaction and persistence. It can exist between any actors: two individuals, relatives, households, firms, institutions, settlements, coalitions or states.

The same incompatibility may result in:

- avoidance;
- communication;
- bargaining;
- exchange;
- compensation;
- coalition building;
- obstruction;
- threat;
- coercion;
- seizure;
- violence;
- adaptation;
- no meaningful action.

Nothing maps conflict deterministically to violence.

## Cooperation is equally primitive-neutral

Actors can cooperate once without becoming allies. Rivals can trade. Enemies can coordinate against a third risk. Relatives can fight. Friends can compete economically.

Repeated coordination plus memory and expectations may become alliance-like. The label is retrospective unless an institution or explicit agreement itself becomes a real object in the world.

An explicit treaty, oath or organization can later be a first-class entity because it has causal effects through beliefs, sanctions, records and expectations. It still must not magically guarantee compliant behavior.

## Elementary interactions

Current implementation exposes low-level acts such as:

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

These are a starter vocabulary, not a complete ontology. They describe what actors do, not the macro story historians later assign to the period.

## Macro pattern classifiers are observational

`EmergentPattern` can infer labels such as `sustained_cooperation`, `competitive_rivalry`, `violent_feud`, `alliance_like` or `war_like` from an interaction window.

These classifiers are **views**. Removing the classifier must not alter world evolution. Simulation logic should use the underlying interactions/metrics whenever possible rather than branch on the label.

This invariant is central: `WAR` must not become a hidden state machine that generates battles simply because war was previously detected.

## Scale invariance

The relational matrix should work for heterogeneous actor kinds. A person-person dispute and a state-state territorial confrontation should use compatible lower-level concepts where possible, while allowing scale-specific capabilities, institutions and aggregation.

Macro actors are not assumed internally homogeneous. A state's observed action can emerge from networks of persons, offices, factions, commands, logistics and institutions.

## Interaction with epistemics

Actors act on perceived relation matrices, not omniscient truth. They can:

- misunderstand another actor's interests;
- falsely believe a claim exists;
- exaggerate an opponent's capability;
- underestimate dependence;
- misread cooperation as weakness;
- conceal intentions;
- issue threats they cannot or do not intend to execute.

Therefore objective compatibility and perceived compatibility can diverge.

## Interaction with space

Spatial geography constrains contact, access, supply, escape, projection of force, trade, communication and the objects over which claims are made. Geography never labels a location `cause_of_war`; it changes the relational matrix and feasible interactions.

## Development rule

When implementing any future domain, prefer:

```text
primitive state
+ actor perception
+ constraints/capabilities
+ networks/space
+ elementary interactions
+ learning/memory
-> persistent emergent pattern
-> optional retrospective label
```

over:

```text
macro label
-> scripted consequences
```
