from __future__ import annotations

from dataclasses import dataclass
from random import Random

import numpy as np

from simworld.core.entity import Entity
from simworld.core.event import Event
from simworld.simulation.first_world import FirstWorldConfig, FirstWorldSimulation, SimulationResult
from simworld.social.communication import Message, communicate, evaluate_message_accuracy
from simworld.social.decision import ActionOption, DecisionContext, choose_action
from simworld.social.epistemics import EpistemicState
from simworld.social.learning import Experience, StrategyLearner
from simworld.social.narrative import Narrative, NarrativeVersion, SocialMemory
from simworld.social.needs import NeedState


@dataclass(frozen=True, slots=True)
class SocialSimulationResult:
    base: SimulationResult
    house_ids: tuple[str, ...]
    representative_ids: tuple[str, ...]
    social_memory: SocialMemory


class SocialWorldSimulation(FirstWorldSimulation):
    """Adds imperfect knowledge, political choice, learning and social memory.

    Nothing in this layer maps a shortage to a prescribed solution. Shortage changes
    experiences and signals; actors then perceive, communicate, believe and choose.
    """

    ACTIONS = (
        ActionOption(
            "expand_fields",
            need_weights={"food_security": 0.8, "stability": 0.15},
            belief_weights={"food_shortage": 0.9},
            cost=0.42,
            domain="governance",
        ),
        ActionOption(
            "procure_food",
            need_weights={"food_security": 0.9, "stability": 0.25},
            belief_weights={"food_shortage": 1.0},
            cost=0.55,
            domain="governance",
        ),
        ActionOption(
            "distribute_reserves",
            need_weights={"stability": 0.65, "legitimacy": 0.55},
            belief_weights={"food_shortage": 0.75, "unrest": 0.35},
            cost=0.32,
            domain="governance",
        ),
        ActionOption(
            "coerce",
            need_weights={"stability": 0.9, "authority": 0.65},
            belief_weights={"unrest": 0.9, "food_shortage": -0.15},
            cost=0.12,
            domain="governance",
        ),
        ActionOption(
            "investigate",
            need_weights={"stability": 0.25},
            belief_weights={"uncertainty": 0.9},
            cost=0.16,
            domain="governance",
        ),
        ActionOption(
            "ignore",
            need_weights={"authority": 0.1},
            belief_weights={"food_shortage": -0.45, "unrest": -0.25},
            base_bias=0.05,
            cost=0.0,
            domain="governance",
        ),
    )

    def __init__(self, config: FirstWorldConfig) -> None:
        super().__init__(config)
        self.social_rng = Random(config.seed ^ 0x5EEDC0DE)
        self.house_ids: list[str] = []
        self.representative_ids: list[str] = []
        self._house_for_settlement: dict[str, str] = {}
        self._representative_for_settlement: dict[str, str] = {}
        self._epistemics: dict[str, EpistemicState] = {}
        self._learners: dict[str, StrategyLearner] = {}
        self._needs: dict[str, NeedState] = {}
        self._last_messages: dict[str, Message] = {}
        self.social_memory = SocialMemory()

    def initialize(self) -> None:
        super().initialize()
        if self.house_ids:
            return
        for index, settlement_id in enumerate(self.settlement_ids, start=1):
            settlement = self.world.entities[settlement_id]
            house = Entity(
                kind="house",
                name=f"House-{index:02d}",
                created_at=0,
                attributes={
                    "settlement_id": settlement_id,
                    "stability": float(self.social_rng.uniform(0.48, 0.76)),
                    "legitimacy": float(self.social_rng.uniform(0.45, 0.78)),
                    "authority": float(self.social_rng.uniform(0.35, 0.8)),
                    "resentment": float(self.social_rng.uniform(0.02, 0.12)),
                    "treasury": float(self.social_rng.uniform(0.45, 0.9)),
                    "food_buffer": 0.0,
                    "farm_factor": 1.0,
                    "inspection_quality": float(self.social_rng.uniform(0.25, 0.62)),
                },
                tags={"house", "political_actor"},
            )
            representative = Entity(
                kind="representative",
                name=f"Speaker-{index:02d}",
                created_at=0,
                attributes={
                    "settlement_id": settlement_id,
                    "house_id": house.id,
                    "honesty": float(self.social_rng.uniform(0.52, 0.94)),
                    "fear": float(self.social_rng.uniform(0.05, 0.45)),
                    "grievance": float(self.social_rng.uniform(0.02, 0.2)),
                },
                tags={"person", "local_representative"},
            )
            self.world.add_entity(house)
            self.world.add_entity(representative)
            self.house_ids.append(house.id)
            self.representative_ids.append(representative.id)
            self._house_for_settlement[settlement_id] = house.id
            self._representative_for_settlement[settlement_id] = representative.id
            self._epistemics[house.id] = EpistemicState()
            self._epistemics[representative.id] = EpistemicState()
            self._learners[house.id] = StrategyLearner()
            self._needs[house.id] = NeedState()
            self._epistemics[house.id].trust.set(representative.id, 0.62, "food")
            self.world.record_event(
                Event(
                    kind="house_established",
                    time=0,
                    participants=(house.id, representative.id, settlement_id),
                    locations=(settlement_id,),
                    impact=0.6,
                    payload={"house": house.name, "representative": representative.name},
                )
            )

    def _local_capacity(self, entity_id: str) -> float:
        base = super()._local_capacity(entity_id)
        house_id = self._house_for_settlement.get(entity_id)
        if house_id is None:
            return base
        house = self.world.entities[house_id]
        farm_factor = float(house.attributes["farm_factor"])
        buffer = float(house.attributes["food_buffer"])
        house.attributes["food_buffer"] = buffer * 0.25
        return base * farm_factor + buffer

    def _experience_and_request(self, year: int, settlement_id: str, food_ratio: float) -> str:
        house_id = self._house_for_settlement[settlement_id]
        representative_id = self._representative_for_settlement[settlement_id]
        house = self.world.entities[house_id]
        representative = self.world.entities[representative_id]
        actual_shortage = float(np.clip(1.0 - food_ratio, 0.0, 1.0))
        resentment = float(house.attributes["resentment"])
        fear = float(representative.attributes["fear"]) * float(house.attributes["authority"])
        honesty = float(representative.attributes["honesty"])
        grievance = float(representative.attributes["grievance"])

        experienced = float(np.clip(actual_shortage + self.social_rng.gauss(0.0, 0.09), 0.0, 1.0))
        self._epistemics[representative_id].observe(
            "food_shortage",
            experienced,
            reliability=0.78,
            time=year,
            source_id=settlement_id,
            salience=0.35 + 0.6 * experienced,
        )

        distortion = (1.0 - honesty) * self.social_rng.uniform(-0.25, 0.25)
        distortion -= 0.28 * fear
        distortion += 0.22 * grievance + 0.12 * resentment
        asserted = float(np.clip(experienced + distortion, 0.0, 1.0))
        motive = "fear_underreporting" if distortion < -0.08 else "grievance_exaggeration" if distortion > 0.08 else "report"
        message = Message(
            sender_id=representative_id,
            receiver_id=house_id,
            proposition="food_shortage",
            asserted_probability=asserted,
            truthful_probability=actual_shortage,
            domain="food",
            motive=motive,
        )
        trust = communicate(message, self._epistemics[house_id], time=year)
        self._last_messages[settlement_id] = message
        event = Event(
            kind="petition_or_report",
            time=year,
            participants=(representative_id, house_id, settlement_id),
            locations=(settlement_id,),
            causes=(self._last_harvest[settlement_id],),
            impact=0.25 + experienced,
            payload={
                "asserted_shortage": round(asserted, 5),
                "actual_shortage_hidden_from_house": round(actual_shortage, 5),
                "motive": motive,
                "receiver_trust": round(trust, 5),
            },
        )
        self.world.record_event(event)
        return event.id

    def _house_needs_and_beliefs(self, house_id: str) -> tuple[NeedState, dict[str, float]]:
        house = self.world.entities[house_id]
        epistemic = self._epistemics[house_id]
        shortage_belief = epistemic.belief("food_shortage")
        unrest_belief = epistemic.belief("unrest")
        uncertainty = 1.0 - max(shortage_belief.confidence, unrest_belief.confidence)
        stability = float(house.attributes["stability"])
        legitimacy = float(house.attributes["legitimacy"])
        authority = float(house.attributes["authority"])
        needs = self._needs[house_id]
        needs.set("food_security", shortage_belief.probability)
        needs.set("stability", 1.0 - stability)
        needs.set("legitimacy", 1.0 - legitimacy)
        needs.set("authority", 1.0 - authority)
        beliefs = {
            "food_shortage": shortage_belief.probability,
            "unrest": unrest_belief.probability,
            "uncertainty": uncertainty,
        }
        return needs, beliefs

    def _apply_house_action(self, year: int, settlement_id: str, petition_event_id: str) -> None:
        house_id = self._house_for_settlement[settlement_id]
        house = self.world.entities[house_id]
        needs, beliefs = self._house_needs_and_beliefs(house_id)
        context = DecisionContext(
            needs=needs,
            beliefs=beliefs,
            learner=self._learners[house_id],
            resources=float(house.attributes["treasury"]),
            temperature=0.42,
        )
        action = choose_action(self.ACTIONS, context, self.social_rng)
        stability_before = float(house.attributes["stability"])
        legitimacy_before = float(house.attributes["legitimacy"])
        resentment_before = float(house.attributes["resentment"])
        treasury = float(house.attributes["treasury"])

        if action.name == "expand_fields" and treasury >= 0.18:
            house.attributes["treasury"] = max(0.0, treasury - 0.18)
            house.attributes["farm_factor"] = min(1.75, float(house.attributes["farm_factor"]) * 1.035)
            house.attributes["stability"] = min(1.0, stability_before + 0.015)
        elif action.name == "procure_food" and treasury >= 0.22:
            house.attributes["treasury"] = max(0.0, treasury - 0.22)
            house.attributes["food_buffer"] = float(house.attributes["food_buffer"]) + 480.0
            house.attributes["stability"] = min(1.0, stability_before + 0.025)
        elif action.name == "distribute_reserves" and treasury >= 0.12:
            house.attributes["treasury"] = max(0.0, treasury - 0.12)
            house.attributes["food_buffer"] = float(house.attributes["food_buffer"]) + 240.0
            house.attributes["legitimacy"] = min(1.0, legitimacy_before + 0.045)
            house.attributes["resentment"] = max(0.0, resentment_before - 0.035)
            house.attributes["stability"] = min(1.0, stability_before + 0.035)
        elif action.name == "coerce":
            house.attributes["stability"] = min(1.0, stability_before + 0.075)
            house.attributes["authority"] = min(1.0, float(house.attributes["authority"]) + 0.035)
            house.attributes["resentment"] = min(1.0, resentment_before + 0.085)
            house.attributes["legitimacy"] = max(0.0, legitimacy_before - 0.025)
        elif action.name == "investigate":
            house.attributes["inspection_quality"] = min(0.95, float(house.attributes["inspection_quality"]) + 0.06)
        else:
            house.attributes["stability"] = max(0.0, stability_before - 0.015 * beliefs["food_shortage"])

        # Latent resentment acts slowly and may remain invisible while coercion appears successful.
        house.attributes["stability"] = max(
            0.0,
            float(house.attributes["stability"]) - 0.018 * float(house.attributes["resentment"]),
        )
        stability_after = float(house.attributes["stability"])
        legitimacy_after = float(house.attributes["legitimacy"])
        resentment_after = float(house.attributes["resentment"])
        perceived_reward = (stability_after - stability_before) * 5.0 + (legitimacy_after - legitimacy_before) * 1.5
        latent_effect = perceived_reward - (resentment_after - resentment_before) * 4.0
        self._learners[house_id].record(
            Experience(
                time=year,
                strategy=action.name,
                domain="governance",
                perceived_reward=perceived_reward,
                latent_effect=latent_effect,
                context=tuple(sorted((key, float(value)) for key, value in beliefs.items())),
            )
        )
        action_event = Event(
            kind="house_action",
            time=year,
            participants=(house_id, settlement_id),
            locations=(settlement_id,),
            causes=(petition_event_id,),
            impact=0.3 + abs(perceived_reward),
            payload={
                "action": action.name,
                "believed_shortage": round(beliefs["food_shortage"], 5),
                "stability_before": round(stability_before, 5),
                "stability_after": round(stability_after, 5),
                "resentment_before": round(resentment_before, 5),
                "resentment_after": round(resentment_after, 5),
                "perceived_reward": round(perceived_reward, 5),
                "latent_effect": round(latent_effect, 5),
            },
        )
        self.world.record_event(action_event)
        self._maybe_create_narrative(year, settlement_id, action_event)

    def _verify_reports(self, year: int, settlement_id: str, food_ratio: float) -> None:
        house_id = self._house_for_settlement[settlement_id]
        representative_id = self._representative_for_settlement[settlement_id]
        house = self.world.entities[house_id]
        message = self._last_messages[settlement_id]
        actual_shortage = float(np.clip(1.0 - food_ratio, 0.0, 1.0))
        inspection = float(house.attributes["inspection_quality"])
        if self.social_rng.random() < inspection:
            observed = float(np.clip(actual_shortage + self.social_rng.gauss(0.0, 0.08 * (1.0 - inspection)), 0.0, 1.0))
            self._epistemics[house_id].observe(
                "food_shortage",
                observed,
                reliability=0.55 + 0.4 * inspection,
                time=year,
                source_id=settlement_id,
                salience=0.5,
            )
            accuracy = evaluate_message_accuracy(message, actual_shortage)
            new_trust = self._epistemics[house_id].trust.reinforce(representative_id, accuracy, "food")
            self.world.record_event(
                Event(
                    kind="report_evaluated",
                    time=year,
                    participants=(house_id, representative_id, settlement_id),
                    locations=(settlement_id,),
                    causes=(self._last_harvest[settlement_id],),
                    impact=0.2 + abs(0.5 - accuracy),
                    payload={"accuracy": round(accuracy, 5), "new_food_trust": round(new_trust, 5)},
                )
            )

    def _maybe_create_narrative(self, year: int, settlement_id: str, action_event: Event) -> None:
        action = str(action_event.payload["action"])
        shortage = float(action_event.payload["believed_shortage"])
        if shortage < 0.3 and action not in {"coerce", "distribute_reserves"}:
            return
        house_id = self._house_for_settlement[settlement_id]
        representative_id = self._representative_for_settlement[settlement_id]
        if action == "coerce":
            house_claim = "firmness preserved order"
            local_claim = "the house answered hardship with force"
            valence = -0.45
        elif action == "distribute_reserves":
            house_claim = "the house protected the settlement in hardship"
            local_claim = "shared stores helped people endure"
            valence = 0.55
        else:
            house_claim = f"{action} was the response to hardship"
            local_claim = f"people remember the year of {action}"
            valence = 0.05
        narrative_id = f"nar-{action_event.id}"
        narrative = Narrative(
            id=narrative_id,
            origin_event_ids=(action_event.id,),
            versions=[
                NarrativeVersion(
                    time=year,
                    teller_id=house_id,
                    claims=(house_claim,),
                    confidence=0.72,
                    emotional_valence=valence,
                )
            ],
        )
        self.social_memory.add(narrative, house_id)
        self.social_memory.held_by.setdefault(representative_id, set()).add(narrative_id)
        # Local counter-memory is stored as a second version instead of forcing one canonical story.
        narrative.versions.append(
            NarrativeVersion(
                time=year,
                teller_id=representative_id,
                claims=(local_claim,),
                confidence=0.68,
                emotional_valence=valence,
                parent_index=0,
            )
        )
        self.world.record_event(
            Event(
                kind="narrative_formed",
                time=year,
                participants=(house_id, representative_id, settlement_id),
                locations=(settlement_id,),
                causes=(action_event.id,),
                impact=0.35 + abs(valence),
                payload={"narrative_id": narrative_id, "house_claim": house_claim, "local_claim": local_claim},
            )
        )

    def _transmit_memory(self, year: int) -> None:
        for settlement_id in self.settlement_ids:
            house_id = self._house_for_settlement[settlement_id]
            representative_id = self._representative_for_settlement[settlement_id]
            held = tuple(self.social_memory.held_by.get(house_id, set()))
            if not held or self.social_rng.random() > 0.34:
                continue
            narrative_id = held[self.social_rng.randrange(len(held))]
            trust = self._epistemics[representative_id].trust.get(house_id, "general")
            version = self.social_memory.transmit(
                narrative_id,
                teller_id=house_id,
                receiver_id=representative_id,
                trust=trust,
                time=year,
                rng=self.social_rng,
            )
            if version is not None:
                narrative = self.social_memory.narratives[narrative_id]
                self.world.record_event(
                    Event(
                        kind="narrative_transmitted",
                        time=year,
                        participants=(house_id, representative_id, settlement_id),
                        locations=(settlement_id,),
                        causes=narrative.origin_event_ids,
                        impact=0.25 + version.confidence * 0.25,
                        payload={"narrative_id": narrative_id, "claims": list(version.claims), "confidence": round(version.confidence, 5)},
                    )
                )

    def run(self) -> SocialSimulationResult:
        self.initialize()
        for year in range(1, self.config.years + 1):
            food_ratio = self._run_harvests(year)
            self._run_demography(year, food_ratio)
            for settlement_id in self.settlement_ids:
                petition_id = self._experience_and_request(year, settlement_id, food_ratio[settlement_id])
                self._apply_house_action(year, settlement_id, petition_id)
                self._verify_reports(year, settlement_id, food_ratio[settlement_id])
            self._run_migration(year, food_ratio)
            self._run_discoveries(year)
            self._transmit_memory(year)
        base = SimulationResult(
            config=self.config,
            generated=self.generated,
            world=self.world,
            settlement_ids=tuple(self.settlement_ids),
        )
        return SocialSimulationResult(
            base=base,
            house_ids=tuple(self.house_ids),
            representative_ids=tuple(self.representative_ids),
            social_memory=self.social_memory,
        )
