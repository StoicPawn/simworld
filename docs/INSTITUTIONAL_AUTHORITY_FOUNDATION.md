# SimWorld institutional and authority foundation

## Purpose

This layer connects material/social history to future politics without declaring states, rulers, classes, houses or institutions in advance. It provides generic obligations, repeated cooperation, organizations and derived authority signals.

## Separation of concepts

The simulator must preserve these distinctions:

- request != obligation;
- obligation != debt only;
- compliance != consent;
- dependency != loyalty;
- coercion != legitimacy;
- provision != benevolence;
- organization != institution;
- organization != government;
- authority != legitimacy;
- authority != territorial sovereignty;
- political state != any single organization.

## Obligations

`Obligation` can connect arbitrary actors. It stores debtor, creditor, kind, resource, amount, creation/due time, fulfilment, debtor acceptance, external recognition, enforceability and provenance.

This is intentionally broader than financial debt. Future kinds may include rent, tribute, tax, labour service, protection, military service, religious dues, contractual delivery, care and office duties.

Obligations may be fulfilled, partially fulfilled, renegotiated, ignored, defaulted, enforced or later contested by norms/institutions.

## Cooperation and organizations

`CooperationLedger` accumulates evidence of repeated successful or failed interactions. Connected components above a cooperation threshold are *candidates* for durable grouping.

`Organization` is generic. It has members, purpose weights, shared resources and recognition. It is not intrinsically a guild, clan, company, church, army, house or state. Those categories can later be derived from persistent structure, behaviour, self-description and recognition.

The integrated vertical slice allows an organization to emerge probabilistically from repeated household cooperation. This is an early mechanism, not a universal law of institution formation.

## Authority

`AuthorityIndex` records observed relationships by actor, subject and domain. Authority is derived from separate signals:

- compliance;
- dependency;
- recognition;
- provision;
- coercion.

`effective_authority` and `legitimacy_signal` are deliberately different. A coercive actor may have high effective authority and low legitimacy. A highly legitimate actor may have recognition but little effective capacity.

Authority is domain-specific. Economic/material authority does not automatically imply military, religious, familial or territorial authority.

## Current integrated process

1. Material household shortage may create a credit request.
2. A possible creditor is constrained by actual stock, geography, previous cooperation and social connection.
3. Credit acceptance transfers real grain and creates an explicit obligation.
4. Repayment, partial repayment or default becomes history.
5. Repeated successful interaction reinforces cooperation; failure may weaken it.
6. Dependency/compliance/provision feed authority signals without granting a title.
7. Repeated cooperation among several households may probabilistically produce a generic organization.
8. Organization members may contribute shared resources or receive aid.
9. Repeated contribution/provision can create organization-level authority over members in the resource-coordination domain.

No step invokes `create_state()`, `create_ruler()` or `create_house()`.

## Long-term geopolitical direction

Future layers will extend these foundations into:

- rent, tribute, taxation and labour-service obligations;
- enforcement and protection arrangements;
- coercive capacity and armed organizations;
- norms/law determining which obligations are recognized;
- organizations splitting, merging, competing and nesting;
- offices and role succession;
- institutional memory;
- spatial control and exclusion;
- territorial claims and borders;
- authority across multiple domains;
- coalitions and diplomacy;
- state formation as a derived persistent configuration of organizations, territorial control, recognition, extraction and provision;
- international systems whose actors hold imperfect beliefs;
- counterfactual and inverse geopolitical inference.

## Invariants

1. Authority must be derived from historical relationships, not assigned as a title alone.
2. Legitimacy and effective authority remain distinct.
3. Compliance may result from trust, dependency, norms, incentives, fear or mistakes.
4. Organizations must be able to exist without becoming political entities.
5. Obligations retain provenance and may be differently recognized by different actors.
6. Economic dependency may become political power but must not automatically do so.
7. No organization is a state merely because it is large or durable.
8. Future LLM decisions must see only obligations/authority/recognition known to the modeled actor.
