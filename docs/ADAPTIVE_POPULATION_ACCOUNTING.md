# Adaptive population accounting

M17 establishes one physical population represented at multiple resolutions.

`PopulationField.population` remains the authoritative physical headcount. `PopulationField.reserved` marks the portion currently represented by detailed people. The unresolved aggregate share is therefore total minus reserved; it is not a second population.

## Representation transitions

Materializing an already-existing person reserves one unit from the field and leaves total population unchanged. Dematerializing releases that reservation and likewise leaves total population unchanged.

A detailed birth is a physical demographic event: it adds one unit to total population and one unit to the reserved layer. A detailed death removes one unit from both. A detailed residence move transfers both total and reserved population between cells while conserving world population.

## Mixed-resolution demography

Aggregate demographic growth and aggregate mobility are applied only to unresolved population. Reserved people already have detailed births, deaths and residence changes, so applying aggregate dynamics to them would double-simulate their history.

This produces the identity

`total population = unresolved aggregate population + materialized population`

at all times.

## Refinement ledger

`PopulationRefinementLedger` maps each detailed person to the cell whose population currently backs that representation. It supports refinement of existing population, detailed births/deaths, physical movement, and collapse back to aggregate representation.

The ledger is accounting/provenance, not a social identity or settlement object.

## Validation

The integrated 24-year reference run finished with 38 living detailed people, 38 units of reserved population, 9,405.701 unresolved people, 9,443.701 total people and an accounting gap of exactly 0.0. Eight detailed births were incorporated into the authoritative population and household residence shifts physically moved their population backing.

Tests additionally verify that materialization/dematerialization conserve headcount, births/deaths change it exactly once, detailed movement conserves world headcount, over-reservation is rejected and every living detailed person has exactly one active backing record.

## Known limitation / next dependency

The unresolved layer still has no explicit age/reproductive composition. Aggregate demographic growth is therefore a scalar net process. The next layer must introduce demographic cohorts so refinement can sample plausible people from the actual local age/reproductive structure and detailed life histories can be collapsed back without losing demographic composition.
