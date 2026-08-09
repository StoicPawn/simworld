from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from pathlib import Path

import numpy as np

from simworld.core.entity import Entity
from simworld.core.event import Event
from simworld.core.randomness import RandomStreams
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
    """First vertical slice where physical geography creates demographic history.

    This is intentionally pre-state and pre-dynasty. It proves the causal pipeline:
    physical map -> settlement -> local production -> demographic pressure -> movement ->
    intersecting event histories.
    """

    def __init__(self, config: FirstWorldConfig) -> None:
        self.config = config
        # Legacy NumPy stream remains unchanged for this vertical slice. New processes
        # should prefer semantic streams from ``random_streams`` so adding an unrelated
        # module cannot perturb existing stochastic histories merely by consuming RNG.
        self.rng = np.random.default_rng(config.seed)
        self.random_streams = RandomStreams(config.seed)
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
                impact=abs(1.0 - ratio),
                payload={
                    "food_ratio": ratio,
                    "fertility": fertility,
                    "production_factor": production_factor,
                },
            )
            self.world.record_event(event)
            self._last_harvest[entity_id] = event.id
        return food_ratio

    def _run_demography(self, year: int, food_ratio: dict[str, float]) -> None:
        for entity_id in self.settlement_ids:
            entity = self.world.entities[entity_id]
            population = max(1, int(entity.attributes["population"]))
            ratio = food_ratio[entity_id]
            capacity = self._local_capacity(entity_id)
            density_pressure = max(0.0, population / max(capacity, 1.0) - 0.75)
            base_growth = 0.018 + float(self.rng.normal(0.0, 0.006))
            food_effect = 0.035 * max(-1.0, min(0.8, ratio - 0.9))
            growth_rate = max(-0.11, min(0.055, base_growth + food_effect - 0.035 * density_pressure))
            next_population = max(20, int(round(population * (1.0 + growth_rate))))
            entity.attributes["population"] = next_population
            entity.attributes["peak_population"] = max(int(entity.attributes["peak_population"]), next_population)
            self.world.record_event(
                Event(
                    kind="population_change",
                    time=year,
                    participants=(entity_id,),
                    locations=(entity_id,),
                    causes=(self._last_harvest[entity_id],),
                    impact=abs(next_population - population) / max(population, 1),
                    payload={
                        "before": population,
                        "after": next_population,
                        "growth_rate": growth_rate,
                        "food_ratio": ratio,
                    },
                )
            )

    def _run_migration(self, year: int, food_ratio: dict[str, float]) -> None:
        origins = sorted(self.settlement_ids, key=lambda entity_id: food_ratio[entity_id])
        destinations = sorted(self.settlement_ids, key=lambda entity_id: food_ratio[entity_id], reverse=True)
        for origin_id in origins:
            origin_ratio = food_ratio[origin_id]
            origin = self.world.entities[origin_id]
            if origin_ratio >= 0.82 or int(origin.attributes["population"]) < 180:
                continue
            best: tuple[float, str] | None = None
            for destination_id in destinations:
                if destination_id == origin_id or food_ratio[destination_id] <= origin_ratio + 0.18:
                    continue
                path = self.generated.spatial_map.path(
                    self._cells[origin_id],
                    self._cells[destination_id],
                    max_expansions=20_000,
                )
                if path is None:
                    continue
                attractiveness = food_ratio[destination_id] - 0.00000018 * path.cost
                if best is None or attractiveness > best[0]:
                    best = (attractiveness, destination_id)
            if best is None:
                continue
            destination_id = best[1]
            destination = self.world.entities[destination_id]
            movers = max(1, int(int(origin.attributes["population"]) * min(0.035, 0.012 + 0.03 * (0.82 - origin_ratio))))
            origin.attributes["population"] = max(20, int(origin.attributes["population"]) - movers)
            destination.attributes["population"] = int(destination.attributes["population"]) + movers
            self.world.record_event(
                Event(
                    kind="migration",
                    time=year,
                    participants=(origin_id, destination_id),
                    locations=(origin_id, destination_id),
                    causes=(self._last_harvest[origin_id], self._last_harvest[destination_id]),
                    impact=movers / max(int(origin.attributes["population"]), 1),
                    payload={"movers": movers, "origin_food": origin_ratio, "destination_food": food_ratio[destination_id]},
                )
            )

    def _run_discoveries(self, year: int) -> None:
        for entity_id in self.settlement_ids:
            entity = self.world.entities[entity_id]
            if bool(entity.attributes["known_ore"]):
                continue
            cell = self._cells[entity_id]
            ore_truth = float(self.generated.ore[cell.y, cell.x])
            probability = min(0.22, 0.008 + 0.11 * ore_truth)
            if self.rng.random() < probability:
                entity.attributes["known_ore"] = True
                self.world.record_event(
                    Event(
                        kind="ore_discovery",
                        time=year,
                        participants=(entity_id,),
                        locations=(entity_id,),
                        impact=0.25 + ore_truth,
                        payload={"ore_truth": ore_truth, "previously_known": False},
                    )
                )

    def run(self) -> SimulationResult:
        self.initialize()
        for year in range(1, self.config.years + 1):
            self.world.advance_to(year)
            food_ratio = self._run_harvests(year)
            self._run_demography(year, food_ratio)
            self._run_migration(year, food_ratio)
            self._run_discoveries(year)
        return SimulationResult(self.config, self.generated, self.world, tuple(self.settlement_ids))


def save_result(result: SimulationResult, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    # Serialization remains deliberately minimal in this vertical slice.
    np.savez_compressed(
        output_dir / "physical_layers.npz",
        elevation=result.generated.elevation,
        water=result.generated.water,
        rainfall=result.generated.rainfall,
        temperature=result.generated.temperature,
        fertility=result.generated.fertility,
        timber=result.generated.timber,
        ore=result.generated.ore,
        habitability=result.generated.habitability,
    )
