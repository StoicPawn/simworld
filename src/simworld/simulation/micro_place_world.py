from __future__ import annotations

from dataclasses import dataclass
from random import Random

from simworld.core.event import Event
from simworld.simulation.disequilibrium_world import DisequilibriumSimulationResult, DisequilibriumWorldSimulation
from simworld.simulation.first_world import FirstWorldConfig
from simworld.social.network import SocialTie
from simworld.spatial.activity import CellKey, PlaceActivityLedger, PlaceView, Presence


@dataclass(frozen=True, slots=True)
class MicroPlaceSimulationResult:
    disequilibrium: DisequilibriumSimulationResult
    place_ledger: PlaceActivityLedger
    place_views: tuple[PlaceView, ...]
    encounters: int


class MicroPlaceWorldSimulation(DisequilibriumWorldSimulation):
    """Makes materialized people act at concrete physical cells.

    The layer does not create markets, villages or neighbourhoods. People repeatedly
    visit useful/reachable cells; co-presence creates opportunities for interaction.
    Persistent places are derived afterwards from the sparse activity history.
    """

    def __init__(self, config: FirstWorldConfig) -> None:
        super().__init__(config)
        self.place_rng = Random(config.seed ^ 0x51AE11)
        self.place_ledger = PlaceActivityLedger()
        self._actor_familiarity: dict[str, dict[CellKey, float]] = {}
        self.encounters = 0

    def _coastal(self, x: int, y: int) -> bool:
        if self.generated.water[y, x]:
            return False
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.config.width and 0 <= ny < self.config.height and self.generated.water[ny, nx]:
                return True
        return False

    def _candidate_cells(self, settlement_id: str, radius: int = 3) -> tuple[CellKey, ...]:
        home = self._cells[settlement_id]
        result: list[CellKey] = []
        for y in range(max(0, home.y - radius), min(self.config.height, home.y + radius + 1)):
            for x in range(max(0, home.x - radius), min(self.config.width, home.x + radius + 1)):
                if self.generated.water[y, x]:
                    continue
                result.append((x, y))
        return tuple(result)

    def _activity_for(self, person_id: str, year: int) -> str:
        entity = self.world.entities[person_id]
        age = year - int(entity.attributes["birth_time"])
        if age < 10:
            return "social"
        household = self.households.household_of(person_id)
        food_pressure = 0.0 if household is None else max(0.0, 0.9 - household.food_stock)
        draw = self.place_rng.random()
        if draw < 0.42 + 0.22 * min(1.0, food_pressure):
            return "cultivate"
        if draw < 0.72:
            return "gather"
        return "social"

    def _cell_score(self, person_id: str, cell: CellKey, activity: str, settlement_id: str) -> float:
        x, y = cell
        home = self._cells[settlement_id]
        distance = abs(x - home.x) + abs(y - home.y)
        habitability = float(self.generated.habitability[y, x])
        fertility = float(self.generated.fertility[y, x])
        timber = float(self.generated.timber[y, x])
        coast = 1.0 if self._coastal(x, y) else 0.0
        if activity == "cultivate":
            affordance = 1.35 * fertility + 0.25 * habitability
        elif activity == "gather":
            affordance = 0.55 * timber + 0.55 * coast + 0.25 * fertility
        else:
            affordance = 0.55 * habitability + 0.20 * coast
        familiarity = self._actor_familiarity.get(person_id, {}).get(cell, 0.0)
        return max(0.001, 0.15 + affordance + 0.14 * min(4.0, familiarity) - 0.10 * distance)

    def _choose_cell(self, person_id: str, activity: str) -> CellKey:
        settlement_id = str(self.world.entities[person_id].attributes["settlement_id"])
        candidates = self._candidate_cells(settlement_id)
        if not candidates:
            home = self._cells[settlement_id]
            return (home.x, home.y)
        weights = [self._cell_score(person_id, cell, activity, settlement_id) for cell in candidates]
        return self.place_rng.choices(candidates, weights=weights, k=1)[0]

    def _record_presence(self, person_id: str, cell: CellKey, year: int, activity: str) -> None:
        self.place_ledger.visit(Presence(person_id, cell, year, activity))
        familiarity = self._actor_familiarity.setdefault(person_id, {})
        familiarity[cell] = familiarity.get(cell, 0.0) + 1.0

    def _interact_at_cell(self, cell: CellKey, actors: tuple[str, ...], year: int) -> None:
        if len(actors) < 2:
            return
        shuffled = list(dict.fromkeys(actors))
        self.place_rng.shuffle(shuffled)
        for index in range(0, len(shuffled) - 1, 2):
            a, b = shuffled[index], shuffled[index + 1]
            if not self._alive(a) or not self._alive(b):
                continue
            existing = self.network.connection_strength(a, b, year)
            related = self.kinship.biological_relatedness_hint(a, b)
            competition = self.place_rng.random()
            cooperative_probability = max(0.12, min(0.88, 0.54 + 0.18 * existing + 0.12 * related - 0.20 * competition))
            cooperative = self.place_rng.random() < cooperative_probability
            kind = "cooperative_encounter" if cooperative else "competitive_encounter"
            self.encounters += 1
            if cooperative:
                self.place_ledger.record_interaction(cell, cooperation=1.0)
            else:
                self.place_ledger.record_interaction(cell, conflict=1.0)

            if existing <= 0.08 and self.place_rng.random() < 0.28:
                tie_kind = "friendship" if cooperative else "rivalry"
                self.network.add(
                    SocialTie(
                        a,
                        b,
                        tie_kind,
                        self.place_rng.uniform(0.12, 0.42),
                        year,
                        sentiment=self.place_rng.uniform(0.08, 0.48) if cooperative else self.place_rng.uniform(-0.55, -0.12),
                        trust=self.place_rng.uniform(0.25, 0.55) if cooperative else self.place_rng.uniform(0.05, 0.28),
                    )
                )

            settlement_id = str(self.world.entities[a].attributes["settlement_id"])
            self.world.record_event(
                Event(
                    kind=kind,
                    time=year,
                    participants=(a, b),
                    locations=(settlement_id,),
                    impact=0.08,
                    payload={
                        "cell": [cell[0], cell[1]],
                        "existing_connection": round(existing, 4),
                        "relatedness": round(related, 4),
                    },
                )
            )

    def _run_micro_place_activity(self, year: int) -> None:
        self.place_ledger.forget_presence_before(year)
        for person_id in tuple(self.person_ids):
            if not self._alive(person_id):
                continue
            activity = self._activity_for(person_id, year)
            cell = self._choose_cell(person_id, activity)
            self._record_presence(person_id, cell, year, activity)
        for cell, actors in self.place_ledger.current_presence.get(year, {}).items():
            self._interact_at_cell(cell, tuple(actors), year)

    def _evolve_social_network(self, year: int) -> None:
        # In this layer new weak ties arise from actual co-presence rather than random
        # pairing within a settlement. Existing relationships still evolve elsewhere.
        return

    def run(self) -> MicroPlaceSimulationResult:
        self.initialize()
        for year in range(1, self.config.years + 1):
            self.world.advance_to(year)
            self._resolve_pregnancies(year)
            self._run_obligation_resolution(year)
            food_ratio = self._run_harvests(year)
            self._run_demography(year, food_ratio)
            self._run_material_production(year, food_ratio)
            self._run_micro_place_activity(year)
            before_exchange = len(self.world.events)
            self._run_material_exchange(year)
            self._learn_from_exchange_events(tuple(self.world.events[before_exchange:]))
            self._run_credit_formation(year)
            self._run_organization_emergence(year)
            self._run_organization_processes(year)
            self._update_households(year, food_ratio)
            for settlement_id in self.settlement_ids:
                petition = self._experience_and_request(year, settlement_id, food_ratio[settlement_id])
                self._apply_house_action(year, settlement_id, petition)
                self._verify_reports(year, settlement_id, food_ratio[settlement_id])
            self._run_migration(year, food_ratio)
            self._run_discoveries(year)
            self._evolve_existing_relations(year)
            self._run_reproduction(year)
            self._run_mortality(year)
            self._transmit_memory(year)

        disequilibrium = super().run_result_only()
        return MicroPlaceSimulationResult(
            disequilibrium=disequilibrium,
            place_ledger=self.place_ledger,
            place_views=self.place_ledger.views(min_visits=2.0),
            encounters=self.encounters,
        )
