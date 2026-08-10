# Culture and technology foundation

## Goal

SimWorld should hard-code **laws, constraints and opportunity spaces**, not historical outcomes.

Language, religion, ethnicity, technological eras and cultural identities must not be primitive labels assigned to populations. They should be retrospective/derived structures over lower-level learned state, transmission, interaction, drift, institutions and biology.

## Shared cultural substrate

The generic substrate now begins with:

- actor-specific knowledge;
- partial mastery and confidence;
- learning by observation/teaching;
- imperfect transmission;
- drift and future mutation;
- forgetting/loss through knowledge decay;
- preservation through practice, social reinforcement and future records;
- contact-driven convention convergence;
- isolation-driven convention divergence;
- retrospective compatibility clustering with no causal force;
- prestige, institutions and richer identity resistance as future pressures over the same mechanism.

A transmitted unit does not declare itself to be linguistic, religious or technological. Domain-specific views interpret clusters later.

## Language

Do not create `Language A/B/C` as primitive historical objects.

Future language state should be built from many transmitted conventions. Mutual intelligibility becomes a derived similarity/compatibility measure. Contact, migration, intermarriage, trade, administration and prestige can create convergence; isolation, local transmission and drift can create divergence.

Therefore a valid simulation may contain one broad mutually intelligible convention network, or many hundreds/thousands of linguistic clusters. No target count is calibrated.

The generic `ConventionState` / `cluster_conventions()` foundation already allows convergence, divergence and retrospective cluster detection without declaring those clusters to be languages. A future `LanguageView` must remain reporting/analysis only unless speakers themselves institutionalize names/norms around it.

## Religion

Do not create a religion because a random event fires.

Beliefs, narratives, rituals, prescriptions, symbols and trusted transmitters already have lower-level substrates. A `ReligionView` may later detect persistent clusters of these elements plus collective practice/identity/institutions.

Private belief, ritual participation and social membership must remain distinct.

## Identity / race / ethnicity

For human-like populations, biological ancestry, phenotype and social classification are separate.

- heritable biological traits may evolve/mix geographically;
- ancestry is genealogical/population history;
- ethnicity/people/race-like categories are actor-created social classifications and identities;
- a social category must never be inferred automatically from phenotype.

For genuinely different fantasy species, species biology can be a separate physical primitive if the world definition requires it.

## Technology

Full chemistry/biology/physics discovery is out of scope for the initial engine. SimWorld therefore uses a middle layer: **technical affordances**.

An affordance is a data-defined possible capability with requirements such as:

- materials/resources;
- previously learned capabilities;
- environmental conditions;
- experience;
- experimentation;
- observability/complexity.

Meeting requirements only makes discovery possible; it never guarantees it.

There is no chronological tech tree. Multiple affordances can be discovered independently, in different orders, repeatedly in different regions, or never discovered during a run. Knowledge can remain local or disappear if transmission/practice fails.

`AffordanceCatalog` loads these possibilities from data instead of domain-specific historical branching code. The initial foundation catalog is deliberately small and low-level; its purpose is to test the architecture, not to encode a canonical human technology sequence.

`attempt_innovation()` changes only the discovering actor's `KnowledgeLedger`. There is no civilization-wide `technology_level` or automatic global unlock. Diffusion must occur later through actual transmission/contact mechanisms.

High-level labels such as `agriculture`, `metallurgy`, `oceanic_navigation` or `industrialization` should eventually be derived configurations of many lower-level capabilities, not one unlock event.

## Equilibrium and path dependence

There is no global equilibrium target such as one language, one religion or technological progress.

Observed macroscopic patterns arise from competing local forces:

- convergence: contact, communication value, network centrality, prestige, administration, education, mobility;
- divergence: isolation, drift, local inheritance, network closure, resistance/identity, institutional fragmentation;
- persistence: repeated successful transmission, material usefulness, social reinforcement, records/institutions;
- loss: death, forgetting, disrupted networks, environmental/material change, institutional collapse.

These forces may create temporary attractors, but nothing is immutable.

## Current implementation boundary

M19 provides the generic mechanics and a small data-driven technology possibility catalog. It does **not yet** connect those mechanics to the complete world loop. The next integration work is:

1. detailed people's activities generate experience/capability traces;
2. local physical state supplies real material/environment affordance requirements;
3. innovation attempts create explicit historical events and actor-local knowledge;
4. real encounters/relationships allow teaching and diffusion;
5. parent-child socialization carries knowledge/conventions across generations;
6. death, loss of practice and institutional collapse can remove knowledge;
7. unresolved/background population receives aggregate cultural state so quiet regions still evolve;
8. domain-specific derived views interpret convention/belief/capability clusters as languages, religions or technological traditions only when justified.

## Core rule

> Hard-code what is physically/socially possible and how information can move; do not hard-code which civilization, language, religion or technological sequence must appear.
