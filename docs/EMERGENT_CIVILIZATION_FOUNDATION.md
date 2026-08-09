# Emergent Civilization Foundation

This layer extends SimWorld from a generational social world into the first coupled civilization substrate.

## Core rule

No historical category exists because a story requires it.

- shortage does not call a farming policy;
- rivalry does not call a war function;
- kinship does not call loyalty;
- a river is not decorative;
- a mountain is not merely a map color;
- a household is not identical to a biological family;
- a lineage is not automatically a house or dynasty.

Instead, physical state, social relations, beliefs, resources and prior experience alter feasible choices and incentives. Outcomes remain contingent.

## Geography as causal substrate

The physical map now supports derived hydrology and ruggedness. Rain falling on elevated cells accumulates downstream and creates river corridors. Water access diffuses locally into neighbouring land. Ruggedness derives from elevation gradients.

These layers can influence:

- crop suitability;
- settlement capacity;
- movement and accessibility;
- concentration of population;
- territorial friction;
- strategic opportunity;
- later roads, bridges, ports and fortifications.

A pass, valley or river crossing becomes strategically important only when other systems make it important.

## Agriculture

Crops have environmental profiles rather than a universal `fertility -> food` relation. Suitability depends on soil/fertility, temperature, rainfall, water access and ruggedness.

The first profiles are grains, pulses and tubers. They are primitives for future crop diversity, technology, irrigation, crop rotation, disease and trade.

Production is continuous. Political behaviour is deliberately outside the agriculture model.

## Households

A household is a co-residential/economic unit, not a biological truth. It may contain kin, partners, dependants or unrelated people.

Households can hold:

- food stocks;
- wealth;
- debt;
- land;
- tools;
- changing membership.

This creates a bridge between aggregate population and materialized individuals.

## Pregnancy and care

Conception no longer needs to produce an instantaneous birth in the deeper simulation. A pregnancy has a conception time, due time and viability. Food security and health can affect outcome.

A birth may create biological and care relations, but does not imply marriage, romance, loyalty or co-residence between the parents.

## Relationship evolution

Social ties have temporal intervals. Partnership/intimacy can lead to co-residence, but not deterministically. Negative sentiment can contribute to separation. Later layers should add reconciliation, caregiving, abandonment, adoption, fostering and household fission/fusion.

## Inheritance

Property transfer is a separate process from biology. `allocate_inheritance` accepts rule weights. Equal division is only a neutral fallback and must not become a universal historical law.

Future rules can emerge from norms, institutions, wills, coercion, claims, gender/age systems, debts, offices and political bargaining.

## Emergent conflict

Conflict is modeled as pressure plus bounded choice, not a scripted event schedule.

Pressure can arise from:

- overlapping resource interests;
- territorial friction;
- rivalry;
- fear;
- grievance;
- perceived opportunity;
- geographic access.

It can be inhibited by:

- interdependence;
- kinship/social ties;
- distance and terrain;
- later norms, treaties, institutions and deterrence.

The available first actions are avoidance, negotiation, threat, raid and attack. Even high pressure does not deterministically produce attack. Violence can increase later grievance, creating path dependence without declaring a `war` because the narrative expects one.

## Important future distinction

Repeated raids and attacks may later be recognized as a feud, campaign, civil conflict or war, but such labels should be derived from persistent event patterns, actor recognition and institutions. The engine should not need to schedule a war first in order for warfare to occur.

## Multi-resolution rule

Most people remain aggregated. Individuals, households and detailed social ties are materialized where causal relevance requires them. The physical map likewise remains chunked and layered. This is necessary for large worlds.
