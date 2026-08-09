from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class NeedState:
    """Pressures felt by an actor, never direct action triggers.

    Values are normalized to [0, 1]. A high need changes incentives and attention;
    it does not select a policy or imply that the actor understands its cause.
    """

    values: dict[str, float] = field(default_factory=dict)

    def set(self, name: str, value: float) -> None:
        self.values[name] = max(0.0, min(1.0, float(value)))

    def get(self, name: str, default: float = 0.0) -> float:
        return self.values.get(name, default)

    def pressure(self, weights: dict[str, float]) -> float:
        return sum(self.get(name) * weight for name, weight in weights.items())
