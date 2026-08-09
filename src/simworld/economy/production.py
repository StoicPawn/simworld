from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Inventory:
    owner_id: str
    stocks: dict[str, float] = field(default_factory=dict)

    def amount(self, good: str) -> float:
        return max(0.0, self.stocks.get(good, 0.0))

    def add(self, good: str, quantity: float) -> None:
        if quantity < 0:
            raise ValueError("cannot add a negative quantity")
        self.stocks[good] = self.amount(good) + quantity

    def remove(self, good: str, quantity: float) -> None:
        if quantity < 0:
            raise ValueError("cannot remove a negative quantity")
        if self.amount(good) + 1e-9 < quantity:
            raise ValueError(f"insufficient {good}")
        self.stocks[good] = max(0.0, self.amount(good) - quantity)


@dataclass(frozen=True, slots=True)
class ProductionContext:
    labour: float
    land_quality: float = 1.0
    climate_factor: float = 1.0
    tool_factor: float = 1.0
    security_factor: float = 1.0


@dataclass(frozen=True, slots=True)
class ProductionProcess:
    output_good: str
    labour_per_unit: float
    base_productivity: float
    input_goods: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ProductionResult:
    output_good: str
    quantity: float
    labour_used: float
    limiting_factor: str | None


def produce(process: ProductionProcess, inventory: Inventory, context: ProductionContext) -> ProductionResult:
    if context.labour <= 0 or process.labour_per_unit <= 0:
        return ProductionResult(process.output_good, 0.0, 0.0, "labour")

    effective_productivity = max(
        0.0,
        process.base_productivity
        * max(0.0, context.land_quality)
        * max(0.0, context.climate_factor)
        * max(0.0, context.tool_factor)
        * max(0.0, context.security_factor),
    )
    labour_capacity = context.labour / process.labour_per_unit
    capacity = labour_capacity
    limiting: str | None = "labour"
    for good, required_per_unit in process.input_goods.items():
        if required_per_unit <= 0:
            continue
        input_capacity = inventory.amount(good) / required_per_unit
        if input_capacity < capacity:
            capacity = input_capacity
            limiting = good

    units = max(0.0, capacity * effective_productivity)
    if units <= 0:
        return ProductionResult(process.output_good, 0.0, 0.0, limiting)

    normalized_units = units / max(effective_productivity, 1e-12)
    for good, required_per_unit in process.input_goods.items():
        inventory.remove(good, required_per_unit * normalized_units)
    inventory.add(process.output_good, units)
    labour_used = min(context.labour, normalized_units * process.labour_per_unit)
    return ProductionResult(process.output_good, units, labour_used, limiting)
