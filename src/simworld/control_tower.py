from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from simworld.culture.catalog import AffordanceCatalog


@dataclass(frozen=True, slots=True)
class MapConfig:
    source: str = "procedural"
    width: int = 96
    height: int = 72
    cell_size_km: float = 5.0
    seed: int | None = None
    path: str | None = None

    def __post_init__(self) -> None:
        if self.source not in {"procedural", "file", "real_world"}:
            raise ValueError("map source must be procedural, file or real_world")
        if self.width <= 0 or self.height <= 0 or self.cell_size_km <= 0:
            raise ValueError("map dimensions and cell size must be positive")
        if self.source == "file" and not self.path:
            raise ValueError("file map source requires path")


@dataclass(frozen=True, slots=True)
class PopulationSeed:
    count: float
    x: int | None = None
    y: int | None = None
    radius_cells: int = 0
    label: str | None = None

    def __post_init__(self) -> None:
        if self.count < 0:
            raise ValueError("population seed count cannot be negative")
        if (self.x is None) != (self.y is None):
            raise ValueError("population seed requires both x and y or neither")
        if self.radius_cells < 0:
            raise ValueError("population radius cannot be negative")


@dataclass(frozen=True, slots=True)
class ResourceOverride:
    layer: str
    value: float
    x: int | None = None
    y: int | None = None
    radius_cells: int = 0


@dataclass(frozen=True, slots=True)
class TechnologyConfig:
    catalog_paths: tuple[str, ...] = ("configs/affordances/foundation.json",)
    enabled: frozenset[str] | None = None
    disabled: frozenset[str] = frozenset()
    initially_known: dict[str, tuple[str, ...]] = field(default_factory=dict)
    innovation_rate_multiplier: float = 1.0

    def __post_init__(self) -> None:
        if self.innovation_rate_multiplier < 0:
            raise ValueError("innovation_rate_multiplier cannot be negative")
        if self.enabled is not None and self.enabled & self.disabled:
            raise ValueError("a technology cannot be both enabled and disabled")


@dataclass(frozen=True, slots=True)
class SimulationConfig:
    root_seed: int
    years: int
    resolution_mode: str = "adaptive"
    event_recording: str = "causal"

    def __post_init__(self) -> None:
        if self.years < 0:
            raise ValueError("years cannot be negative")
        if self.resolution_mode not in {"adaptive", "aggregate", "detailed"}:
            raise ValueError("invalid resolution_mode")
        if self.event_recording not in {"causal", "all", "minimal"}:
            raise ValueError("invalid event_recording")


@dataclass(frozen=True, slots=True)
class WorldBlueprint:
    """Single declarative entry point for a SimWorld experiment.

    This object is configuration, not causal state. It controls initial conditions
    and which possibility catalogs exist in a run, while the simulator remains free
    to produce very different histories from those conditions.
    """

    simulation: SimulationConfig
    map: MapConfig = MapConfig()
    population: tuple[PopulationSeed, ...] = ()
    resources: tuple[ResourceOverride, ...] = ()
    technology: TechnologyConfig = TechnologyConfig()
    parameters: dict[str, float | int | bool | str] = field(default_factory=dict)
    metadata: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, raw: dict[str, Any]) -> "WorldBlueprint":
        sim_raw = raw.get("simulation", {})
        if "root_seed" not in sim_raw or "years" not in sim_raw:
            raise ValueError("simulation.root_seed and simulation.years are required")
        simulation = SimulationConfig(
            root_seed=int(sim_raw["root_seed"]),
            years=int(sim_raw["years"]),
            resolution_mode=str(sim_raw.get("resolution_mode", "adaptive")),
            event_recording=str(sim_raw.get("event_recording", "causal")),
        )
        map_raw = raw.get("map", {})
        map_config = MapConfig(
            source=str(map_raw.get("source", "procedural")),
            width=int(map_raw.get("width", 96)),
            height=int(map_raw.get("height", 72)),
            cell_size_km=float(map_raw.get("cell_size_km", 5.0)),
            seed=None if map_raw.get("seed") is None else int(map_raw["seed"]),
            path=map_raw.get("path"),
        )
        population = tuple(
            PopulationSeed(
                count=float(item["count"]),
                x=None if item.get("x") is None else int(item["x"]),
                y=None if item.get("y") is None else int(item["y"]),
                radius_cells=int(item.get("radius_cells", 0)),
                label=item.get("label"),
            )
            for item in raw.get("population", [])
        )
        resources = tuple(
            ResourceOverride(
                layer=str(item["layer"]),
                value=float(item["value"]),
                x=None if item.get("x") is None else int(item["x"]),
                y=None if item.get("y") is None else int(item["y"]),
                radius_cells=int(item.get("radius_cells", 0)),
            )
            for item in raw.get("resources", [])
        )
        tech_raw = raw.get("technology", {})
        enabled_raw = tech_raw.get("enabled")
        technology = TechnologyConfig(
            catalog_paths=tuple(str(v) for v in tech_raw.get("catalog_paths", ["configs/affordances/foundation.json"])),
            enabled=None if enabled_raw is None else frozenset(str(v) for v in enabled_raw),
            disabled=frozenset(str(v) for v in tech_raw.get("disabled", [])),
            initially_known={
                str(actor): tuple(str(v) for v in values)
                for actor, values in tech_raw.get("initially_known", {}).items()
            },
            innovation_rate_multiplier=float(tech_raw.get("innovation_rate_multiplier", 1.0)),
        )
        return cls(
            simulation=simulation,
            map=map_config,
            population=population,
            resources=resources,
            technology=technology,
            parameters={str(k): v for k, v in raw.get("parameters", {}).items()},
            metadata={str(k): str(v) for k, v in raw.get("metadata", {}).items()},
        )

    @classmethod
    def from_json(cls, path: str | Path) -> "WorldBlueprint":
        with Path(path).open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
        if not isinstance(raw, dict):
            raise ValueError("world blueprint root must be an object")
        return cls.from_mapping(raw)


def load_effective_affordance_catalog(
    blueprint: WorldBlueprint,
    *,
    project_root: str | Path = ".",
) -> AffordanceCatalog:
    """Merge configured possibility catalogs and apply world-level filters.

    This determines what is possible in the universe, not what is known. Initial
    knowledge is kept separately in `TechnologyConfig.initially_known`.
    """

    root = Path(project_root)
    merged = {}
    version = 1
    for configured_path in blueprint.technology.catalog_paths:
        path = Path(configured_path)
        if not path.is_absolute():
            path = root / path
        catalog = AffordanceCatalog.from_json(path)
        version = max(version, catalog.version)
        overlap = set(merged) & set(catalog.affordances)
        if overlap:
            raise ValueError(f"duplicate affordance ids across catalogs: {sorted(overlap)}")
        merged.update(catalog.affordances)

    known_ids = set(merged)
    requested = set(blueprint.technology.enabled or known_ids)
    disabled = set(blueprint.technology.disabled)
    unknown = (requested | disabled) - known_ids
    if unknown:
        raise ValueError(f"unknown configured affordance ids: {sorted(unknown)}")

    selected = requested - disabled
    for actor_id, units in blueprint.technology.initially_known.items():
        missing = set(units) - selected
        if missing:
            raise ValueError(
                f"initial knowledge for {actor_id!r} references disabled/unavailable affordances: {sorted(missing)}"
            )
    return AffordanceCatalog(
        affordances={key: merged[key] for key in sorted(selected)},
        version=version,
    )
