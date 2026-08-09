# Kinship and social-network foundation

SimWorld treats biological descent and social relations as separate but interacting graph structures.

## Biological substrate

A person may have biological parents and descendants. Birth creates parent-child kinship and makes sibling/cousin/ancestor/descendant relations derivable from the graph. Kinship is not equivalent to affection, loyalty, residence, property, political alignment or identity.

No `House` or `Dynasty` category is required for biological continuity. A lineage is a query/view over the ancestry graph.

## Social substrate

Social relations are multiplex. Two people may simultaneously be:

- biological relatives;
- friends;
- rivals;
- lovers or intimate partners;
- co-parents;
- caregivers/dependants;
- creditors/debtors;
- employer/worker;
- political allies or enemies;
- trusted in one domain and distrusted in another.

A tie carries independent dimensions such as strength, sentiment, trust, dependence, visibility and duration.

## Reproduction

Reproduction is probabilistic. An intimate or romantic connection does not deterministically create offspring. Reproductive probability depends on biological capability, age, health, contact intensity, resources, intent and later technology/norms.

Birth creates biological parent links. It also creates a co-parent social relationship between the biological parents, but does not force romance, affection, co-residence, marriage or cooperation.

## Networks of networks

The social world must support first-, second- and higher-order connections. A person can be influenced by a friend of a sibling, a spouse's creditor, a cousin's patron, a priest trusted by a parent, or a story carried through several family branches.

This means social effects propagate through a graph, not through hard-coded family or class boxes.

## Families, houses and dynasties must emerge

Terms such as family, clan, house and dynasty are derived social/institutional categories. They may emerge when some combination of the following becomes persistent:

- shared biological descent;
- common residence;
- shared property or economic interests;
- inherited offices or claims;
- surname/name continuity;
- mutual recognition;
- social cohesion;
- shared narratives and memories;
- external recognition by other actors;
- marriage and alliance networks.

Different branches of the same biological lineage may become separate houses. Unrelated people may be incorporated socially into a house. A biological family may never become politically relevant at all.

Therefore code must never assume `same blood -> same political unit`.

## Cultural transmission

Kinship provides one high-trust pathway for memory transmission, but not the only one. Family stories may persist because repeated trusted transmission makes them resilient. They may also branch, mutate, conflict with other family branches, or disappear.

Later culture and institutions should be derived from repeated behaviours, learning, narratives, norms and network structure rather than assigned labels.

## Architectural invariants

1. Biological kinship and social relationships are separate layers.
2. Reproduction is probabilistic and not a deterministic consequence of partnership.
3. Offspring creates biological parenthood and co-parent linkage, not mandatory romance.
4. Social graphs are multiplex and time-dependent.
5. Higher-order connections must be queryable.
6. Family/house/dynasty are derived views or emergent institutions, not primitive truths.
7. Branches can split, merge socially, lose cohesion or acquire unrelated members.
8. Kinship can affect trust and information flow, but never guarantees loyalty or truthfulness.
9. Demographic, social, epistemic, economic and political layers remain distinct enough to disagree.
10. The system must scale by materializing detailed persons selectively while background populations remain aggregated.
