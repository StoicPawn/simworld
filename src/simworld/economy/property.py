from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4


def new_asset_id() -> str:
    return f"asset_{uuid4().hex}"


@dataclass(frozen=True, slots=True)
class Asset:
    """A scarce/useful thing in world truth.

    An asset exists independently from any legal or social concept of ownership.
    """

    kind: str
    location: str | None = None
    quantity: float = 1.0
    divisible: bool = True
    productive_capacity: float = 0.0
    id: str = field(default_factory=new_asset_id)
    attributes: dict[str, float | str | bool] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AssetRelation:
    """Minimal temporal actor↔asset relation.

    `kind` is intentionally pre-legal: possess, use, control or claim. None implies
    any other. `strength` may represent a share, degree of effective control, or
    intensity depending on kind.
    """

    asset_id: str
    actor_id: str
    strength: float
    kind: str = "claim"
    started_at: int = 0
    ended_at: int | None = None
    provenance: str | None = None

    def active_at(self, time: int) -> bool:
        return self.started_at <= time and (self.ended_at is None or time < self.ended_at)

    # Compatibility/readability aliases while older vertical slices are migrated.
    @property
    def holder_id(self) -> str:
        return self.actor_id

    @property
    def share(self) -> float:
        return self.strength

    @property
    def right_kind(self) -> str:
        return self.kind

    @property
    def confidence(self) -> float:
        return 1.0


@dataclass(frozen=True, slots=True)
class Recognition:
    """Observer-specific recognition of another actor's claim to an asset."""

    asset_id: str
    claimant_id: str
    recognizer_id: str
    degree: float
    started_at: int = 0
    ended_at: int | None = None
    basis: str | None = None

    def active_at(self, time: int) -> bool:
        return self.started_at <= time and (self.ended_at is None or time < self.ended_at)


@dataclass(frozen=True, slots=True)
class PropertyRight:
    """Compatibility input for older code; not a primitive world fact.

    New code should create `AssetRelation(kind=...)`. A legacy PropertyRight is
    translated to a claim relation. Formal property will later be a derived view
    produced by institutions/rules over claims, recognition and effective control.
    """

    asset_id: str
    holder_id: str
    share: float
    right_kind: str = "claim"
    started_at: int = 0
    ended_at: int | None = None
    confidence: float = 1.0

    def active_at(self, time: int) -> bool:
        return self.started_at <= time and (self.ended_at is None or time < self.ended_at)

    def as_relation(self) -> AssetRelation:
        kind = self.right_kind if self.right_kind in {"possess", "use", "control", "claim"} else "claim"
        return AssetRelation(
            asset_id=self.asset_id,
            actor_id=self.holder_id,
            strength=self.share,
            kind=kind,
            started_at=self.started_at,
            ended_at=self.ended_at,
            provenance="legacy_property_right",
        )


@dataclass(slots=True)
class PropertyRegistry:
    """Compatibility name for the generic asset-relation registry.

    The registry records assets, actor↔asset relations and observer recognition. It
    does not decide who 'really owns' anything.
    """

    assets: dict[str, Asset] = field(default_factory=dict)
    relations: list[AssetRelation] = field(default_factory=list)
    recognitions: list[Recognition] = field(default_factory=list)

    @property
    def rights(self) -> list[AssetRelation]:
        """Legacy accessor. Relations are not universal legal rights."""
        return self.relations

    def add_asset(self, asset: Asset) -> None:
        if asset.id in self.assets:
            raise ValueError(f"duplicate asset: {asset.id}")
        self.assets[asset.id] = asset

    def relate(self, relation: AssetRelation) -> None:
        if relation.asset_id not in self.assets:
            raise KeyError(f"unknown asset: {relation.asset_id}")
        if not (0.0 < relation.strength <= 1.0):
            raise ValueError("relation strength must be in (0, 1]")
        if relation.kind not in {"possess", "use", "control", "claim"}:
            raise ValueError(f"unsupported asset relation kind: {relation.kind}")
        self.relations.append(relation)

    def grant(self, right: PropertyRight | AssetRelation) -> None:
        """Legacy convenience: add a claim/relation without declaring legal truth."""
        self.relate(right.as_relation() if isinstance(right, PropertyRight) else right)

    def recognize(self, recognition: Recognition) -> None:
        if recognition.asset_id not in self.assets:
            raise KeyError(f"unknown asset: {recognition.asset_id}")
        if not (0.0 <= recognition.degree <= 1.0):
            raise ValueError("recognition degree must be in [0, 1]")
        self.recognitions.append(recognition)

    def relations_of(
        self,
        actor_id: str,
        time: int,
        kind: str | None = None,
    ) -> tuple[AssetRelation, ...]:
        return tuple(
            relation
            for relation in self.relations
            if relation.actor_id == actor_id
            and relation.active_at(time)
            and (kind is None or relation.kind == kind)
        )

    def asset_relations(
        self,
        asset_id: str,
        time: int,
        kind: str | None = None,
    ) -> tuple[AssetRelation, ...]:
        return tuple(
            relation
            for relation in self.relations
            if relation.asset_id == asset_id
            and relation.active_at(time)
            and (kind is None or relation.kind == kind)
        )

    def holdings(self, holder_id: str, time: int, right_kind: str | None = None) -> tuple[AssetRelation, ...]:
        """Legacy name for querying actor↔asset relations."""
        return self.relations_of(holder_id, time, right_kind)

    def holders(self, asset_id: str, time: int, right_kind: str = "claim") -> tuple[AssetRelation, ...]:
        """Legacy name for querying relations to an asset."""
        return self.asset_relations(asset_id, time, right_kind)

    def recognition_of(self, claimant_id: str, asset_id: str, time: int) -> float:
        active = [
            r.degree
            for r in self.recognitions
            if r.claimant_id == claimant_id and r.asset_id == asset_id and r.active_at(time)
        ]
        return sum(active) / len(active) if active else 0.0

    def effective_control(self, actor_id: str, asset_id: str, time: int) -> float:
        return min(
            1.0,
            sum(
                relation.strength
                for relation in self.asset_relations(asset_id, time, "control")
                if relation.actor_id == actor_id
            ),
        )

    def control_share(self, holder_id: str, asset_id: str, time: int) -> float:
        """Legacy helper; now explicitly measures effective control only."""
        return self.effective_control(holder_id, asset_id, time)

    def transfer_relation(
        self,
        *,
        asset_id: str,
        from_actor: str,
        to_actor: str,
        strength: float,
        time: int,
        kind: str,
        provenance: str | None = None,
    ) -> None:
        """Transfer a relation, not a universal property title.

        This is suitable for possession/use/control/claim changes. Whether such a
        transfer is socially or legally recognized is a separate process.
        """
        if strength <= 0:
            raise ValueError("strength must be positive")
        active_source = [
            relation
            for relation in self.relations
            if relation.asset_id == asset_id
            and relation.actor_id == from_actor
            and relation.kind == kind
            and relation.active_at(time)
        ]
        available = sum(relation.strength for relation in active_source)
        if available + 1e-9 < strength:
            raise ValueError("insufficient relation strength")

        remaining = strength
        rebuilt: list[AssetRelation] = []
        source_ids = {id(relation) for relation in active_source}
        for relation in self.relations:
            if id(relation) not in source_ids or remaining <= 1e-12:
                rebuilt.append(relation)
                continue

            taken = min(remaining, relation.strength)
            rebuilt.append(
                AssetRelation(
                    asset_id=relation.asset_id,
                    actor_id=relation.actor_id,
                    strength=relation.strength,
                    kind=relation.kind,
                    started_at=relation.started_at,
                    ended_at=time,
                    provenance=relation.provenance,
                )
            )
            residual = relation.strength - taken
            if residual > 1e-12:
                rebuilt.append(
                    AssetRelation(
                        asset_id=relation.asset_id,
                        actor_id=relation.actor_id,
                        strength=residual,
                        kind=relation.kind,
                        started_at=time,
                        provenance=relation.provenance,
                    )
                )
            remaining -= taken

        self.relations = rebuilt
        self.relate(
            AssetRelation(
                asset_id=asset_id,
                actor_id=to_actor,
                strength=strength,
                kind=kind,
                started_at=time,
                provenance=provenance,
            )
        )

    def transfer(
        self,
        *,
        asset_id: str,
        from_holder: str,
        to_holder: str,
        share: float,
        time: int,
        right_kind: str = "claim",
    ) -> None:
        """Legacy wrapper around `transfer_relation`."""
        kind = right_kind if right_kind in {"possess", "use", "control", "claim"} else "claim"
        self.transfer_relation(
            asset_id=asset_id,
            from_actor=from_holder,
            to_actor=to_holder,
            strength=share,
            time=time,
            kind=kind,
            provenance="legacy_transfer",
        )
