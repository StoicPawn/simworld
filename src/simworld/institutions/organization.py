from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4


def new_organization_id() -> str:
    return f"org_{uuid4().hex}"


@dataclass(frozen=True, slots=True)
class Membership:
    member_id: str
    joined_at: int
    role: str = "member"
    stake: float = 0.0
    recognition: float = 0.5
    left_at: int | None = None

    def active_at(self, time: int) -> bool:
        return self.joined_at <= time and (self.left_at is None or time < self.left_at)


@dataclass(slots=True)
class Organization:
    formed_at: int
    purpose: dict[str, float]
    id: str = field(default_factory=new_organization_id)
    memberships: list[Membership] = field(default_factory=list)
    shared_resources: dict[str, float] = field(default_factory=dict)
    internal_recognition: float = 0.5
    external_recognition: float = 0.0
    active: bool = True

    def members(self, time: int) -> set[str]:
        return {m.member_id for m in self.memberships if m.active_at(time)}

    def add_member(self, membership: Membership) -> None:
        self.memberships.append(membership)


@dataclass(slots=True)
class OrganizationRegistry:
    organizations: dict[str, Organization] = field(default_factory=dict)

    def add(self, organization: Organization) -> None:
        if organization.id in self.organizations:
            raise ValueError(f"duplicate organization: {organization.id}")
        self.organizations[organization.id] = organization

    def active(self, time: int) -> tuple[Organization, ...]:
        return tuple(org for org in self.organizations.values() if org.active and org.formed_at <= time)

    def memberships_of(self, member_id: str, time: int) -> tuple[Organization, ...]:
        return tuple(org for org in self.active(time) if member_id in org.members(time))


@dataclass(slots=True)
class CooperationLedger:
    scores: dict[frozenset[str], float] = field(default_factory=dict)

    def reinforce(self, a_id: str, b_id: str, amount: float) -> None:
        if a_id == b_id or amount <= 0:
            return
        key = frozenset((a_id, b_id))
        self.scores[key] = self.scores.get(key, 0.0) + amount

    def weaken(self, a_id: str, b_id: str, amount: float) -> None:
        key = frozenset((a_id, b_id))
        if key in self.scores:
            self.scores[key] = max(0.0, self.scores[key] - max(0.0, amount))

    def score(self, a_id: str, b_id: str) -> float:
        return self.scores.get(frozenset((a_id, b_id)), 0.0)

    def components(self, *, min_edge_score: float, min_members: int = 3) -> tuple[frozenset[str], ...]:
        adjacency: dict[str, set[str]] = {}
        for key, score in self.scores.items():
            if score < min_edge_score:
                continue
            a, b = tuple(key)
            adjacency.setdefault(a, set()).add(b)
            adjacency.setdefault(b, set()).add(a)

        seen: set[str] = set()
        components: list[frozenset[str]] = []
        for node in adjacency:
            if node in seen:
                continue
            stack = [node]
            component: set[str] = set()
            while stack:
                current = stack.pop()
                if current in seen:
                    continue
                seen.add(current)
                component.add(current)
                stack.extend(adjacency.get(current, set()) - seen)
            if len(component) >= min_members:
                components.append(frozenset(component))
        components.sort(key=lambda c: (-len(c), tuple(sorted(c))))
        return tuple(components)
