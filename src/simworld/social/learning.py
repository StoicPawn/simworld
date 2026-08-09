from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Experience:
    time: int
    strategy: str
    domain: str
    perceived_reward: float
    latent_effect: float | None = None
    context: tuple[tuple[str, float], ...] = ()


@dataclass(slots=True)
class StrategyLearner:
    """Learns from perceived outcomes, which may differ from real long-run effects."""

    values: dict[tuple[str, str], float] = field(default_factory=dict)
    counts: dict[tuple[str, str], int] = field(default_factory=dict)
    experiences: list[Experience] = field(default_factory=list)

    def estimate(self, strategy: str, domain: str = "general") -> float:
        return self.values.get((strategy, domain), 0.0)

    def record(self, experience: Experience, *, learning_rate: float = 0.24) -> float:
        key = (experience.strategy, experience.domain)
        old = self.values.get(key, 0.0)
        new = old + learning_rate * (experience.perceived_reward - old)
        self.values[key] = new
        self.counts[key] = self.counts.get(key, 0) + 1
        self.experiences.append(experience)
        return new
