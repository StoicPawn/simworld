from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from pathlib import Path

import numpy as np

from simworld.core.entity import Entity
from simworld.core.event import Event
from simworld.core.world import WorldState
from simworld.geography import GeneratedWorld, generate_world
from simworld.spatial import CellCoord, GridSpec


@dataclass(frozen=True, slots=True)
class FirstWorldConfig:
    width: int = 96
    height: int = 72
    cell_size_m: float = 5_000.0
    chunk_size: int = 32
    settlements: int = 10
    years: int = 40
    seed: int = 1
    sea_fraction: float = 0.34


@dataclass(frozen=True, slots=True)
class SimulationResult:
    config: FirstWorldConfig
    generated: GeneratedWorld
    world: WorldState
    settlement_ids: tuple[str, ...]

    @property
    def final_population(self) -> int:
        return sum(int(self.world.entities[entity_id].attributes["population"]) for entity_id in self.settlement_ids)


class FirstWorldSimulation:
    """First vertical slice where physical geography creates demographic history."""

    def __init__(self, config: FirstWorldConfig) -> None:
        self.config = config
        self.rng = np.random.default_rng(config.seed)
        spec = GridSpec(
            width=config.width,
            height=config.height,
            cell_size_m=config.cell_size_m,
            chunk_size=config.chunk_size,
        )
        self.generated = generate_world(spec, seed=config.seed, sea_fraction=config.sea_fraction)
        self.world = WorldState()
        self.settlement_ids: list[str] = []
        self._cells: dict[str, CellCoord] = {}
        self._last_harvest: dict[str, str] = {}

    def _settlement_candidates(self) -> list[tuple[float, CellCoord]]:
        score = self.generated.habitability.astype(np.float64).copy()
        score += 0.08 * self.generated.ore + 0.08 * self.generated.timber
        candidates: list[tuple[float, CellCoord]] = []
        for y in range(self.config.height):
            for x in range(self.config.width):
                if self.generated.water[y, x]:
                    continue
                value = float(score[y, x])
                if value > 0.18:
                    candidates.append((value, CellCoord(x, y)))
        candidates.sort(key=lambda item: (-item[0], item[1].y, item[1].x))
        return candidates

    def initialize(self) -> None:
        if self.settlement_ids:
            return
        selected: list[CellCoord] = []
        min_spacing = max(4.0, min(self.config.width, self.config.height) / max(4.0, self.config.settlements**0.5 * 2.2))

        for score, cell in self._settlement_candidates():
            if any(hypot(cell.x - other.x, cell.y - other.y) < min_spacing for other in selected):
                continue
            selected.append(cell)
            index = len(selected)
            base_population = int(320 + 1250 * score + self.rng.integers(0, 220))
            entity = Entity(
                kind="settlement",
                name=f"Settlement-{index:02d}",
                created_at=0,
                id=f"settlement_{index:04d}",
                attributes={
                    "x": cell.x,
                    "y": cell.y,
                    "population": base_population,
                    "peak_population": base_population,
                    "known_ore": False,
                    "known_timber": float(self.generated.timber[cell.y, cell.x]),
                    "founded_at": 0,
                },
                tags={"settlement"},
            )
            self.world.add_entity(entity)
            self.settlement_ids.append(entity.id)
            self._cells[entity.id] = cell
            self.world.record_event(
                Event(
                    kind="settlement_founded",
                    time=0,
                    participants=(entity.id,),
                    locations=(entity.id,),
                    impact=1.5 + score,
                    payload={
                        "cell": [cell.x, cell.y],
                        "initial_population": base_population,
                        "habitability": score,
                    },
                )
            )
            if len(selected) >= self.config.settlements:
                break

        if len(selected) < 2:
            raise RuntimeError("generated world did not contain enough habitable settlement sites")

    def _local_capacity(self, entity_id: str) -> float:
        cell = self._cells[entity_id]
        fertility = float(self.generated.fertility[cell.y, cell.x])
        timber = float(self.generated.timber[cell.y, cell.x])
        return 450.0 + 5900.0 * fertility + 650.0 * timber

    def _run_harvests(self, year: int) -> dict[str, float]:
        food_ratio: dict[str, float] = {}
        for entity_id in self.settlement_ids:
            entity = self.world.entities[entity_id]
            population = max(1, int(entity.attributes["population"]))
            cell = self._cells[entity_id]
            fertility = float(self.generated.fertility[cell.y, cell.x])
            climate_noise = float(self.rng.normal(0.0, 0.16))
            rare_shock = float(self.rng.normal(-0.42, 0.08)) if self.rng.random() < 0.055 else 0.0
            production_factor = max(0.22, 1.0 + climate_noise + rare_shock)
            food = self._local_capacity(entity_id) * production_factor
            ratio = food / population
            food_ratio[entity_id] = ratio
            event = Event(
                kind="harvest",
                time=year,
                participants=(entity_id,),
                locations=(entity_id,),
                impact=abs(1.0 - ratio) + 0.2,
                payload={
                    "population_before": population,
                    "food_capacity": round(food, 3),
                    "food_ratio": round(ratio, 5),
                    "fertility": round(fertility, 5),
                    "shock": round(climate_noise + rare_shock, 5),
                },
            )
            self.world.record_event(event)
            self._last_harvest[entity_id] = event.id
        return food_ratio

    def _run_demography(self, year: int, food_ratio: dict[str, float]) -> None:
        for entity_id in self.settlement_ids:
            entity = self.world.entities[entity_id]
            before = int(entity.attributes["population"])
            ratio = food_ratio[entity_id]
            growth_rate = float(np.clip(0.012 + 0.055 * (ratio - 1.0), -0.095, 0.032))
            demographic_noise = float(self.rng.normal(0.0, 0.004))
            after = max(25, int(round(before * (1.0 + growth_rate + demographic_noise))))
            entity.attributes["population"] = after
            entity.attributes["peak_population"] = max(int(entity.attributes["peak_population"]), after)
            self.world.record_event(
                Event(
                    kind="population_change",
                    time=year,
                    participants=(entity_id,),
                    locations=(entity_id,),
                    causes=(self._last_harvest[entity_id],),
                    impact=abs(after - before) / max(1, before) + 0.1,
                    payload={"before": before, "after": after, "growth_rate": round(growth_rate, 6)},
                )
            )

    def _best_destination(self, source_id: str, food_ratio: dict[str, float]) -> tuple[str, float] | None:
        source = self._cells[source_id]
        best: tuple[str, float] | None = None
        for destination_id in self.settlement_ids:
            if destination_id == source_id or food_ratio[destination_id] <= 1.03:
                continue
            path = self.generated.spatial_map.path(source, self._cells[destination_id], max_expansions=30_000)
            if path is None:
                continue
            attractiveness = food_ratio[destination_id] - path.cost / 4_000_000.0
            if best is None or attractiveness > best[1]:
                best = (destination_id, attractiveness)
        return best

    def _run_migration(self, year: int, food_ratio: dict[str, float]) -> None:
        for source_id in self.settlement_ids:
            if food_ratio[source_id] >= 0.88:
                continue
            destination = self._best_destination(source_id, food_ratio)
            if destination is None or destination[1] <= 0.7:
                continue
            destination_id, _ = destination
            source_entity = self.world.entities[source_id]
            destination_entity = self.world.entities[destination_id]
            source_population = int(source_entity.attributes["population"])
            migrants = min(max(5, int(source_population * (0.018 + 0.045 * (0.88 - food_ratio[source_id])))), source_population // 8)
            if migrants < 5:
                continue
            source_entity.attributes["population"] = source_population - migrants
            destination_entity.attributes["population"] = int(destination_entity.attributes["population"]) + migrants
            self.world.record_event(
                Event(
                    kind="migration",
                    time=year,
                    participants=(source_id, destination_id),
                    locations=(source_id, destination_id),
                    causes=(self._last_harvest[source_id], self._last_harvest[destination_id]),
                    impact=migrants / max(1, source_population) + 0.35,
                    payload={
                        "people": migrants,
                        "from": source_entity.name,
                        "to": destination_entity.name,
                        "source_food_ratio": round(food_ratio[source_id], 5),
                        "destination_food_ratio": round(food_ratio[destination_id], 5),
                    },
                )
            )

    def _run_discoveries(self, year: int) -> None:
        for entity_id in self.settlement_ids:
            entity = self.world.entities[entity_id]
            if bool(entity.attributes["known_ore"]):
                continue
            cell = self._cells[entity_id]
            ore = float(self.generated.ore[cell.y, cell.x])
            if self.rng.random() < 0.012 + 0.035 * ore:
                entity.attributes["known_ore"] = True
                self.world.record_event(
                    Event(
                        kind="ore_discovery",
                        time=year,
                        participants=(entity_id,),
                        locations=(entity_id,),
                        impact=0.4 + ore,
                        payload={"local_ore_signal": round(ore, 5)},
                    )
                )

    def run(self) -> SimulationResult:
        self.initialize()
        for year in range(1, self.config.years + 1):
            food_ratio = self._run_harvests(year)
            self._run_demography(year, food_ratio)
            self._run_migration(year, food_ratio)
            self._run_discoveries(year)
        return SimulationResult(
            config=self.config,
            generated=self.generated,
            world=self.world,
            settlement_ids=tuple(self.settlement_ids),
        )


def write_svg_map(result: SimulationResult, path: Path, *, scale: int = 5) -> None:
    generated = result.generated
    height, width = generated.water.shape
    max_elevation = max(1.0, float(np.max(generated.elevation_m)))
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width * scale}" height="{height * scale}" viewBox="0 0 {width} {height}">'
    ]
    for y in range(height):
        for x in range(width):
            if generated.water[y, x]:
                color = "#5f91b8"
            else:
                fertility = float(generated.fertility[y, x])
                elevation = max(0.0, float(generated.elevation_m[y, x])) / max_elevation
                r = int(np.clip(154 - 55 * fertility + 65 * elevation, 70, 220))
                g = int(np.clip(129 + 92 * fertility - 45 * elevation, 70, 220))
                b = int(np.clip(76 + 48 * fertility + 38 * elevation, 55, 190))
                color = f"#{r:02x}{g:02x}{b:02x}"
            parts.append(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{color}"/>')

    for entity_id in result.settlement_ids:
        entity = result.world.entities[entity_id]
        x = int(entity.attributes["x"])
        y = int(entity.attributes["y"])
        population = int(entity.attributes["population"])
        radius = float(np.clip(0.8 + np.log10(max(10, population)) * 0.45, 1.0, 2.4))
        parts.append(f'<circle cx="{x + 0.5}" cy="{y + 0.5}" r="{radius}" fill="#221c17" stroke="#f5efe6" stroke-width="0.25"/>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")
