from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from simworld.culture.effects import EffectSpec
from simworld.culture.technology import Affordance


@dataclass(frozen=True, slots=True)
class AffordanceCatalog:
    """Versionable data catalog of technical possibilities.

    The catalog constrains what the simplified engine can discover; it does not
    define a historical order and does not imply that any listed possibility will
    ever be discovered in a run.
    """

    affordances: dict[str, Affordance]
    version: int = 1

    def get(self, affordance_id: str) -> Affordance:
        return self.affordances[affordance_id]

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "AffordanceCatalog":
        raw = data.get("affordances", [])
        if not isinstance(raw, list):
            raise ValueError("affordances must be a list")
        affordances: dict[str, Affordance] = {}
        for item in raw:
            if not isinstance(item, dict):
                raise ValueError("each affordance must be an object")
            raw_effects = item.get("effects", [])
            if not isinstance(raw_effects, list):
                raise ValueError("affordance effects must be a list")
            effects = tuple(
                EffectSpec(
                    channel=str(effect["channel"]),
                    operation=str(effect.get("operation", "multiply")),
                    magnitude=float(effect.get("magnitude", 0.0)),
                    activation_chance=float(effect.get("activation_chance", 1.0)),
                    required_context={
                        str(key): float(value)
                        for key, value in effect.get("required_context", {}).items()
                    },
                )
                for effect in raw_effects
            )
            if not effects:
                raise ValueError(
                    f"configured technical affordance {item.get('id')!r} has no causal effects"
                )
            affordance = Affordance(
                id=str(item["id"]),
                required_materials=frozenset(str(value) for value in item.get("required_materials", [])),
                required_capabilities={
                    str(key): float(value)
                    for key, value in item.get("required_capabilities", {}).items()
                },
                min_environment={
                    str(key): float(value)
                    for key, value in item.get("min_environment", {}).items()
                },
                complexity=float(item.get("complexity", 0.5)),
                observability=float(item.get("observability", 0.5)),
                effects=effects,
            )
            if affordance.id in affordances:
                raise ValueError(f"duplicate affordance id: {affordance.id}")
            affordances[affordance.id] = affordance
        return cls(affordances=affordances, version=int(data.get("version", 1)))

    @classmethod
    def from_json(cls, path: str | Path) -> "AffordanceCatalog":
        with Path(path).open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise ValueError("catalog root must be an object")
        return cls.from_mapping(data)
