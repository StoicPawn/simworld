from __future__ import annotations

from dataclasses import dataclass
from math import exp, hypot, log1p
from random import Random

from simworld.core.event import Event
from simworld.simulation.disequilibrium_world import DisequilibriumSimulationResult, DisequilibriumWorldSimulation
from simworld.simulation.first_world import FirstWorldConfig
from simworld.social.network import SocialTie
from simworld.spatial import CellCoord
from simworld.spatial.activity import CellActivityLedger, PlaceView, derive_place_views


@dataclass(frozen=True, slots=True)
class MicrogeographySimulationResult:
    base: DisequilibriumSimulationResult
    activity: CellActivityLedger
    person_cells: dict[str, CellCoord]
    place_views: tuple[PlaceView, ...]
    encounters: int


class MicrogeographyWorldSimulation(DisequilibriumWorldSimulation):
    """Individual local movement and co-presence over continuous physical affordances.

    Markets, villages and political centres are deliberately absent as primitives.
    Cells accumulate use; higher-level place concepts are retrospective views over that
    history. The sparse ledger means socially irrelevant cells stay cheap.
    """

    def __init__(self, config: FirstWorldConfig) -> None:
        super().__init__(config)
        self.micro_rng = Random(config.seed ^ 0x51A7E011)
        self.activity = CellActivityLedger()
        self.person_cells: dict[str, CellCoord] = {}
        self.encounters = 0

    def initialize(self) -> None:
        super().initialize()
        for person_id in self.person_ids:
            if person_id in self.person_cells:
                continue
            entity = self.world.entities[person_id]
            settlement_id = str(entity.attributes["settlement_id"])
            self.person_cells[person_id] = self._cells[settlement_id]

    def _ensure_person_cell(self, person_id: str) -> CellCoord:
        existing = self.person_cells.get(person_id)
        if existing is not None:
            return existing
        settlement_id = str(self.world.entities[person_id].attributes["settlement_id"])
        cell = self._cells[settlement_id]
        self.person_cells[person_id] = cell
        return cell

    def _candidate_cells(self, origin: CellCoord, radius: int = 2) -> list[CellCoord]:
        cells: list[CellCoord] = []
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                x, y = origin.x + dx, origin.y + dy
                if not (0 <= x < self.config.width and 0 <= y < self.config.height):
                    continue
                if bool(self.generated.water[y, x]):
                    continue
                cells.append(CellCoord(x, y))
        return cells or [origin]

    def _cell_affordances(self, cell: CellCoord) -> tuple[float, float, float]:
        x, y = cell.x, cell.y
        fertility = float(self.generated.fertility[y, x])
        fresh = float(self.generated.freshwater_access[y, x])
        shore_food = float(self.generated.coastal_food[y, x])
        habitability = float(self.generated.habitability[y, x])
        gathering = 0.58 * shore_food + 0.24 * fertility + 0.18 * fresh
        cultivation = fertility * (0.72 + 0.28 * fresh)
        general = 0.62 * habitability + 0.23 * fresh + 0.15 * shore_food
        return gathering, cultivation, general

    def _choose_destination(self, person_id: str, origin: CellCoord) -> CellCoord:
        candidates = self._candidate_cells(origin)
        scores: list[float] = []
        for cell in candidates:
            gathering, cultivation, general = self._cell_affordances(cell)
            previous = self.activity.at(cell).total()
            distance = hypot(cell.x - origin.x, cell.y - origin.y)
            score = 0.34 * gathering + 0.36 * cultivation + 0.30 * general
            score += 0.035 * log1p(previous)
            score -= 0.075 * distance
            scores.append(score)
        maximum = max(scores)
        weights = [exp(4.0 * (score - maximum)) for score in scores]
        return self.micro_rng.choices(candidates, weights=weights, k=1)[0]

    def _perform_local_activity(self, person_id: str, cell: CellCoord, year: int) -> None:
        gathering, cultivation, general = self._cell_affordances(cell)
        entity = self.world.entities[person_id]
        household = self.households.household_of(person_id)
        if household is None:
            self.activity.record(cell, time=year, actor_id=person_id, kind="visit")
            return

        gather_weight = max(0.02, gathering)
        cultivate_weight = max(0.02, cultivation)
        observe_weight = max(0.08, 0.36 + 0.25 * general)
        choice = self.micro_rng.choices(
            ("gather", "cultivate", "visit"),
            weights=(gather_weight, cultivate_weight, observe_weight),
            k=1,
        )[0]
        self.activity.record(cell, time=year, actor_id=person_id, kind="visit", amount=0.35)
        self.activity.record(cell, time=year, actor_id=person_id, kind=choice, amount=1.0)

        if choice in {"gather", "cultivate"}:
            health = float(entity.attributes.get("health", 1.0))
            potential = gathering if choice == "gather" else cultivation
            yield_amount = max(0.0, potential * health * self.micro_rng.uniform(0.035, 0.11))
            inventory = self.inventories.get(household.id)
            if inventory is not None and yield_amount > 0:
                inventory.add("grain", yield_amount)
                household.food_stock = inventory.amount("grain")

    def _run_micro_encounters(self, year: int, co_presence: dict[tuple[int, int], list[str]]) -> None:
        for (x, y), actors in sorted(co_presence.items()):
            unique = sorted(set(actors))
            if len(unique) < 2:
                continue
            pairs: list[tuple[str, str]] = []
            for index, a in enumerate(unique):
                for b in unique[index + 1 :]:
                    pairs.append((a, b))
            self.micro_rng.shuffle(pairs)
            for a, b in pairs[:2]:
                connection = self.network.connection_strength(a, b, year)
                household_a = self.households.household_of(a)
                household_b = self.households.household_of(b)
                food_a = household_a.food_stock if household_a is not None else 0.5
                food_b = household_b.food_stock if household_b is not None else 0.5
                scarcity = max(0.0, 0.7 - min(food_a, food_b))
                hostile_probability = max(0.01, min(0.42, 0.045 + 0.22 * scarcity - 0.08 * min(1.0, connection)))
                friendly_probability = max(0.10, min(0.82, 0.48 + 0.18 * min(1.0, connection) - 0.18 * scarcity))
                draw = self.micro_rng.random()
                if draw < hostile_probability:
                    outcome = "hostile"
                    self.activity.record(CellCoord(x, y), time=year, actor_id=a, kind="conflict", amount=1.0)
                    if connection <= 0.05:
                        self.network.add(
                            SocialTie(
                                a,
                                b,
                                "rivalry",
                                self.micro_rng.uniform(0.12, 0.38),
                                year,
                                sentiment=self.micro_rng.uniform(-0.7, -0.2),
                                trust=self.micro_rng.uniform(0.0, 0.25),
                            )
                        )
                elif draw < hostile_probability + friendly_probability:
                    outcome = "friendly"
                    if connection <= 0.05:
                        self.network.add(
                            SocialTie(
                                a,
                                b,
                                "friendship",
                                self.micro_rng.uniform(0.10, 0.34),
                                year,
                                sentiment=self.micro_rng.uniform(0.1, 0.55),
                                trust=self.micro_rng.uniform(0.18, 0.48),
                            )
                        )
                else:
                    outcome = "neutral"

                settlement_id = str(self.world.entities[a].attributes["settlement_id"])
                self.world.record_event(
                    Event(
                        kind="micro_encounter",
                        time=year,
                        participants=(a, b),
                        locations=(settlement_id,),
                        impact=0.10 if outcome == "hostile" else 0.05,
                        payload={"cell": [x, y], "outcome": outcome, "prior_connection": round(connection, 4)},
                    )
                )
                self.encounters += 1

    def _run_microgeography(self, year: int) -> None:
        co_presence: dict[tuple[int, int], list[str]] = {}
        for person_id in tuple(self.person_ids):
            if not self._alive(person_id):
                continue
            entity = self.world.entities[person_id]
            age = year - int(entity.attributes["birth_time"])
            if age < 8:
                continue
            origin = self._ensure_person_cell(person_id)
            destination = self._choose_destination(person_id, origin)
            self.person_cells[person_id] = destination
            self._perform_local_activity(person_id, destination, year)
            co_presence.setdefault((destination.x, destination.y), []).append(person_id)
        self._run_micro_encounters(year, co_presence)

    def _run_material_production(self, year: int, food_ratio: dict[str, float]) -> None:
        super()._run_material_production(year, food_ratio)
        self._run_microgeography(year)

    def run(self) -> MicrogeographySimulationResult:
        base = super().run()
        return MicrogeographySimulationResult(
            base=base,
            activity=self.activity,
            person_cells=dict(self.person_cells),
            place_views=derive_place_views(self.activity, min_activity=2.5),
            encounters=self.encounters,
        )
