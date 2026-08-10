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
