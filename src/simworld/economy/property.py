from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4


def new_asset_id() -> str:
    return f"asset_{uuid4().hex}"


@dataclass(frozen=True, slots=True)
class Asset:
    kind: str
    location: str | None = None
    quantity: float = 1.0
    divisible: bool = True
    productive_capacity: float = 0.0
    id: str = field(default_factory=new_asset_id)
    attributes: dict[str, float | str | bool] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class PropertyRight:
    asset_id: str
    holder_id: str
    share: float
    right_kind: str = "ownership"
    started_at: int = 0
    ended_at: int | None = None
    confidence: float = 1.0

    def active_at(self, time: int) -> bool:
        return self.started_at <= time and (self.ended_at is None or time < self.ended_at)


@dataclass(slots=True)
class PropertyRegistry:
    assets: dict[str, Asset] = field(default_factory=dict)
    rights: list[PropertyRight] = field(default_factory=list)

    def add_asset(self, asset: Asset) -> None:
        if asset.id in self.assets:
            raise ValueError(f"duplicate asset: {asset.id}")
        self.assets[asset.id] = asset

    def grant(self, right: PropertyRight) -> None:
        if right.asset_id not in self.assets:
            raise KeyError(f"unknown asset: {right.asset_id}")
        if not (0.0 < right.share <= 1.0):
            raise ValueError("share must be in (0, 1]")
        self.rights.append(right)

    def holdings(self, holder_id: str, time: int, right_kind: str | None = None) -> tuple[PropertyRight, ...]:
        return tuple(
            right for right in self.rights
            if right.holder_id == holder_id
            and right.active_at(time)
            and (right_kind is None or right.right_kind == right_kind)
        )

    def holders(self, asset_id: str, time: int, right_kind: str = "ownership") -> tuple[PropertyRight, ...]:
        return tuple(
            right for right in self.rights
            if right.asset_id == asset_id
            and right.right_kind == right_kind
            and right.active_at(time)
        )

    def control_share(self, holder_id: str, asset_id: str, time: int) -> float:
        return min(1.0, sum(r.share * r.confidence for r in self.holders(asset_id, time) if r.holder_id == holder_id))

    def transfer(self, *, asset_id: str, from_holder: str, to_holder: str, share: float, time: int, right_kind: str = "ownership") -> None:
        if share <= 0:
            raise ValueError("share must be positive")
        available = sum(
            r.share for r in self.holders(asset_id, time, right_kind)
            if r.holder_id == from_holder
        )
        if available + 1e-9 < share:
            raise ValueError("insufficient property share")
        remaining = share
        updated: list[PropertyRight] = []
        for right in self.rights:
            if (
                remaining > 0
                and right.asset_id == asset_id
                and right.holder_id == from_holder
                and right.right_kind == right_kind
                and right.active_at(time)
            ):
                take = min(remaining, right.share)
                updated.append(PropertyRight(right.asset_id, right.holder_id, right.share - take, right.right_kind, right.started_at, time, right.confidence)) if right.share - take > 1e-9 else updated.append(PropertyRight(right.asset_id, right.holder_id, right.share, right.right_kind, right.started_at, time, right.confidence))
                if right.share - take > 1e-9:
                    updated.append(PropertyRight(right.asset_id, right.holder_id, right.share - take, right.right_kind, time, None, right.confidence))
                remaining -= take
            else:
                updated.append(right)
        self.rights = updated
        self.grant(PropertyRight(asset_id, to_holder, share, right_kind, time))
