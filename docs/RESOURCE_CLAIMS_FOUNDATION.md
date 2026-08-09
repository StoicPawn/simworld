# Resource claims foundation

## Why this replaces primitive property

SimWorld must not assume that a modern legal concept of property exists before institutions capable of defining, recording, recognizing and enforcing it.

The minimal substrate is therefore:

```text
RESOURCE / ASSET
   ↓
ACTOR ↔ ASSET RELATIONS
   - possession
   - use
   - control
   - claim
   ↓
RECOGNITION BY OTHER ACTORS
   ↓
possible enforcement / convention / institution
   ↓
possible formal property regime
```

A deed, title, cadastral entry or contract is not physical truth. It is an information/evidence object whose practical meaning depends on who recognizes the issuer and whether some actor or institution can make the claim effective.

## Primitive concepts

### Asset
Something scarce/useful in the world: land, field, tool, animal, stored food, building, route access, etc.

### AssetRelation
A temporal relation between an actor and an asset.

Kinds are deliberately generic:
- `possess`: actor physically possesses or occupies it;
- `use`: actor makes use of it;
- `control`: actor can effectively exclude/direct access;
- `claim`: actor asserts an entitlement over it.

A relation has strength/share, start/end time and provenance. None of these relations automatically implies another.

### Recognition
Another actor may recognize an actor's claim to an asset, with a degree of confidence/acceptance. Recognition may be local, social, customary, institutional or coercive. It may conflict across observers.

## Derived property

`property` is a derived view, not a primitive world fact. A later institutional layer may infer a relatively stable property relation when claim + recognition + effective control + enforcement become sufficiently aligned under some rule system.

Different institutions or observers may derive different property views over the same asset.

## Documents and registries

Future `EvidenceObject` / document types may attest claims, transfers, inheritance, boundaries or obligations. Their force is relational:

```text
document issued
    ↓
actor/institution recognizes issuer?
    ↓
claim credibility changes
    ↓
enforcement / dispute / compliance may change
```

No document is globally authoritative by construction.

## Historical scaling

This substrate works for:
- a person occupying and cultivating a plot without formal title;
- customary communal land;
- conquest and contested possession;
- feudal/use rights;
- modern registered ownership;
- competing cadastral/legal systems;
- informal control despite formal ownership elsewhere.

The later system becomes more sophisticated by adding recognition/enforcement institutions, not by changing the primitive asset model.

## Invariants

- asset != property;
- possession != use != control != claim;
- claim != recognized claim;
- recognized claim != effective control;
- document != truth;
- legal/formal property requires an institutional context;
- the simulator must not hard-code a universal property law.
