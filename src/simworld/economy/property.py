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
        return min(
            1.0,
            sum(
                right.share * right.confidence
                for right in self.holders(asset_id, time)
                if right.holder_id == holder_id
            ),
        )

    def transfer(
        self,
        *,
        asset_id: str,
        from_holder: str,
        to_holder: str,
        share: float,
        time: int,
        right_kind: str = "ownership",
    ) -> None:
        if share <= 0:
            raise ValueError("share must be positive")
        active_source = [
            right
            for right in self.rights
            if right.asset_id == asset_id
            and right.holder_id == from_holder
            and right.right_kind == right_kind
            and right.active_at(time)
        ]
        available = sum(right.share for right in active_source)
        if available + 1e-9 < share:
            raise ValueError("insufficient property share")

        remaining = share
        rebuilt: list[PropertyRight] = []
        source_ids = {id(right) for right in active_source}
        for right in self.rights:
            if id(right) not in source_ids or remaining <= 1e-12:
                rebuilt.append(right)
                continue

            taken = min(remaining, right.share)
            rebuilt.append(
                PropertyRight(
                    asset_id=right.asset_id,
                    holder_id=right.holder_id,
                    share=right.share,
                    right_kind=right.right_kind,
                    started_at=right.started_at,
                    ended_at=time,
                    confidence=right.confidence,
                )
            )
            residual = right.share - taken
            if residual > 1e-12:
                rebuilt.append(
                    PropertyRight(
                        asset_id=right.asset_id,
                        holder_id=right.holder_id,
                        share=residual,
                        right_kind=right.right_kind,
                        started_at=time,
                        confidence=right.confidence,
                    )
                )
            remaining -= taken

        self.rights = rebuilt
        self.grant(
            PropertyRight(
                asset_id=asset_id,
                holder_id=to_holder,
                share=share,
                right_kind=right_kind,
                started_at=time,
            )
        )
