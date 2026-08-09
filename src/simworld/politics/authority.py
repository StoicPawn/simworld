from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class AuthorityObservation:
    authority_id: str
    subject_id: str
    domain: str
    time: int
    compliance: float = 0.0
    dependency: float = 0.0
    recognition: float = 0.0
    provision: float = 0.0
    coercion: float = 0.0


@dataclass(frozen=True, slots=True)
class AuthoritySignal:
    authority_id: str
    subject_id: str
    domain: str
    compliance: float
    dependency: float
    recognition: float
    provision: float
    coercion: float

    @property
    def effective_authority(self) -> float:
        return max(
            0.0,
            min(
                1.0,
                0.30 * self.compliance
                + 0.24 * self.dependency
                + 0.22 * self.recognition
                + 0.18 * self.provision
                + 0.06 * self.coercion,
            ),
        )

    @property
    def legitimacy_signal(self) -> float:
        return max(
            0.0,
            min(1.0, 0.48 * self.recognition + 0.34 * self.provision + 0.18 * self.compliance - 0.22 * self.coercion),
        )


@dataclass(slots=True)
class _AuthorityState:
    compliance: float = 0.0
    dependency: float = 0.0
    recognition: float = 0.0
    provision: float = 0.0
    coercion: float = 0.0
    observations: int = 0


@dataclass(slots=True)
class AuthorityIndex:
    states: dict[tuple[str, str, str], _AuthorityState] = field(default_factory=dict)

    def observe(self, observation: AuthorityObservation, learning_rate: float = 0.28) -> AuthoritySignal:
        key = (observation.authority_id, observation.subject_id, observation.domain)
        state = self.states.setdefault(key, _AuthorityState())
        lr = max(0.01, min(1.0, learning_rate if state.observations else 1.0))
        for attr in ("compliance", "dependency", "recognition", "provision", "coercion"):
            old = getattr(state, attr)
            incoming = max(0.0, min(1.0, getattr(observation, attr)))
            setattr(state, attr, old * (1.0 - lr) + incoming * lr)
        state.observations += 1
        return self.signal(*key)

    def signal(self, authority_id: str, subject_id: str, domain: str) -> AuthoritySignal:
        state = self.states.get((authority_id, subject_id, domain), _AuthorityState())
        return AuthoritySignal(
            authority_id,
            subject_id,
            domain,
            state.compliance,
            state.dependency,
            state.recognition,
            state.provision,
            state.coercion,
        )

    def subjects_of(self, authority_id: str, domain: str, threshold: float = 0.35) -> tuple[str, ...]:
        subjects = []
        for (candidate, subject, candidate_domain), _ in self.states.items():
            if candidate != authority_id or candidate_domain != domain:
                continue
            if self.signal(candidate, subject, candidate_domain).effective_authority >= threshold:
                subjects.append(subject)
        return tuple(sorted(set(subjects)))
