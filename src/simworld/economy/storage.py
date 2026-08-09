from __future__ import annotations

from dataclasses import dataclass
from random import Random

from .production import Inventory


@dataclass(frozen=True, slots=True)
class StorageProfile:
    capacity: float
    preservation: float
    exposure: float = 0.5


@dataclass(frozen=True, slots=True)
class StorageResult:
    spoiled: float
    overflow_lost: float
    remaining: float


def age_stock(
    inventory: Inventory,
    good: str,
    profile: StorageProfile,
    *,
    climate_stress: float,
    rng: Random,
) -> StorageResult:
    """Age a perishable stock without prescribing any behavioural response."""
    amount = inventory.amount(good)
    if amount <= 0:
        return StorageResult(0.0, 0.0, 0.0)

    capacity = max(0.0, profile.capacity)
    overflow = max(0.0, amount - capacity)
    if overflow > 0:
        inventory.remove(good, overflow)
        amount -= overflow

    preservation = max(0.0, min(1.0, profile.preservation))
    exposure = max(0.0, min(1.0, profile.exposure))
    stress = max(0.0, min(1.5, climate_stress))
    stochastic = max(0.0, rng.gauss(0.0, 0.025 + 0.04 * exposure))
    spoilage_rate = min(
        0.75,
        max(0.0, (1.0 - preservation) * (0.10 + 0.20 * stress) + stochastic),
    )
    spoiled = min(amount, amount * spoilage_rate)
    if spoiled > 0:
        inventory.remove(good, spoiled)
    return StorageResult(spoiled, overflow, inventory.amount(good))


@dataclass(frozen=True, slots=True)
class HouseholdDemandProfile:
    adult_food_need: float
    child_food_factor: float = 0.65
    elder_food_factor: float = 0.85
    reserve_target_per_person: float = 0.45

    def annual_food_need(self, ages: tuple[int, ...]) -> float:
        total = 0.0
        for age in ages:
            if age < 14:
                total += self.adult_food_need * self.child_food_factor
            elif age > 65:
                total += self.adult_food_need * self.elder_food_factor
            else:
                total += self.adult_food_need
        return total
