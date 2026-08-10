from __future__ import annotations

from dataclasses import dataclass
from random import Random


@dataclass(frozen=True, slots=True)
class ConventionState:
    """Small continuous representation of one transmitted convention.

    The values have no intrinsic interpretation. Future domains may use collections
    of conventions for speech, ritual, etiquette, symbols or other learned systems.
    """

    dimensions: tuple[float, ...]

    def distance(self, other: "ConventionState") -> float:
        if len(self.dimensions) != len(other.dimensions):
            raise ValueError("convention dimensionality mismatch")
        if not self.dimensions:
            return 0.0
        return sum(abs(a - b) for a, b in zip(self.dimensions, other.dimensions, strict=True)) / len(self.dimensions)

    def compatibility(self, other: "ConventionState") -> float:
        return max(0.0, min(1.0, 1.0 - self.distance(other)))


@dataclass(frozen=True, slots=True)
class ConventionClusterView:
    """Retrospective cluster only; it has no causal force in the simulation."""

    members: tuple[str, ...]
    mean_internal_compatibility: float


def evolve_convention(
    current: ConventionState,
    *,
    interaction_model: ConventionState | None,
    contact_strength: float,
    transmission_pressure: float,
    drift_rate: float,
    identity_resistance: float,
    rng: Random,
) -> ConventionState:
    """One generic cultural update.

    Contact can pull conventions together, while stochastic drift can separate
    isolated lineages. Identity resistance reduces convergence but never creates a
    predefined ethnicity/language/religion.
    """

    contact = min(1.0, max(0.0, contact_strength))
    transmission = min(1.0, max(0.0, transmission_pressure))
    drift = min(1.0, max(0.0, drift_rate))
    resistance = min(1.0, max(0.0, identity_resistance))
    values: list[float] = []
    for index, value in enumerate(current.dimensions):
        target = value
        if interaction_model is not None:
            if len(interaction_model.dimensions) != len(current.dimensions):
                raise ValueError("convention dimensionality mismatch")
            target = interaction_model.dimensions[index]
        pull = (target - value) * contact * transmission * (1.0 - resistance) * 0.45
        noise = rng.uniform(-drift, drift) * (1.0 - 0.55 * contact)
        values.append(min(1.0, max(0.0, value + pull + noise)))
    return ConventionState(tuple(values))


def cluster_conventions(
    states: dict[str, ConventionState],
    *,
    compatibility_threshold: float,
) -> tuple[ConventionClusterView, ...]:
    """Derive connected compatibility clusters without creating world entities.

    This deliberately uses a simple connected-component view. Future language or
    ritual analyses can define domain-specific similarity metrics while preserving
    the invariant that the detected cluster is an analyst view, not a causal object.
    """

    threshold = min(1.0, max(0.0, compatibility_threshold))
    remaining = set(states)
    clusters: list[ConventionClusterView] = []
    while remaining:
        root = min(remaining)
        component = {root}
        frontier = [root]
        remaining.remove(root)
        while frontier:
            actor = frontier.pop()
            neighbours = [
                other
                for other in sorted(remaining)
                if states[actor].compatibility(states[other]) >= threshold
            ]
            for other in neighbours:
                remaining.remove(other)
                component.add(other)
                frontier.append(other)

        members = tuple(sorted(component))
        compatibilities: list[float] = []
        for index, a in enumerate(members):
            for b in members[index + 1 :]:
                compatibilities.append(states[a].compatibility(states[b]))
        mean = 1.0 if not compatibilities else sum(compatibilities) / len(compatibilities)
        clusters.append(ConventionClusterView(members, mean))

    return tuple(sorted(clusters, key=lambda cluster: (-len(cluster.members), cluster.members)))
