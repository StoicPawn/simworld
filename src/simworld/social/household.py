from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Household:
    settlement_id: str
    founded_at: int
    id: str
    members: set[str] = field(default_factory=set)
    food_stock: float = 1.0
    wealth: float = 1.0
    debt: float = 0.0
    shelter_quality: float = 0.6
    care_capacity: float = 1.0
    shared_name: str | None = None

    @property
    def formed_at(self) -> int:
        return self.founded_at

    def add_member(self, person_id: str) -> None:
        self.members.add(person_id)

    def remove_member(self, person_id: str) -> None:
        self.members.discard(person_id)

    def net_resources(self) -> float:
        return self.wealth + self.food_stock - self.debt

    def care_pressure(self, dependants: int, carers: int) -> float:
        effective_carers = max(0.25, carers * self.care_capacity)
        return dependants / effective_carers


@dataclass(slots=True)
class HouseholdRegistry:
    households: dict[str, Household] = field(default_factory=dict)
    membership: dict[str, str] = field(default_factory=dict)
    _next_id: int = 1

    def create(self, settlement_id: str, founded_at: int, members: tuple[str, ...] = ()) -> Household:
        household = Household(
            settlement_id=settlement_id,
            founded_at=founded_at,
            id=f"hh_{self._next_id:08d}",
        )
        self._next_id += 1
        self.households[household.id] = household
        for person_id in members:
            self.move(person_id, household.id)
        return household

    def move(self, person_id: str, household_id: str) -> None:
        if household_id not in self.households:
            raise KeyError(f"unknown household: {household_id}")
        previous = self.membership.get(person_id)
        if previous is not None and previous in self.households:
            self.households[previous].remove_member(person_id)
        self.membership[person_id] = household_id
        self.households[household_id].add_member(person_id)

    def household_of(self, person_id: str) -> Household | None:
        household_id = self.membership.get(person_id)
        return self.households.get(household_id) if household_id else None

    def remove_person(self, person_id: str) -> None:
        household_id = self.membership.pop(person_id, None)
        if household_id and household_id in self.households:
            self.households[household_id].remove_member(person_id)

    def active_households(self) -> tuple[Household, ...]:
        return tuple(h for h in self.households.values() if h.members)
