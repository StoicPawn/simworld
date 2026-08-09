from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from simworld.simulation.first_world import FirstWorldConfig, write_svg_map
from simworld.simulation.generational_world import GenerationalWorldSimulation


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=104729)
    parser.add_argument("--years", type=int, default=40)
    parser.add_argument("--width", type=int, default=64)
    parser.add_argument("--height", type=int, default=48)
    parser.add_argument("--settlements", type=int, default=6)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    config = FirstWorldConfig(
        width=args.width,
        height=args.height,
        settlements=args.settlements,
        years=args.years,
        seed=args.seed,
    )
    result = GenerationalWorldSimulation(config).run()
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    write_svg_map(result.social.base, out / "map.svg")

    world = result.social.base.world
    event_types = Counter(event.kind for event in world.events)
    tie_types = Counter(tie.kind for tie in result.network.ties)
    births = event_types.get("birth", 0)
    deaths = event_types.get("death", 0)

    people = []
    for person_id in result.person_ids:
        entity = world.entities[person_id]
        record = result.kinship.people[person_id]
        household = result.households.household_of(person_id)
        people.append(
            {
                "id": person_id,
                "name": entity.name,
                "birth_time": record.birth_time,
                "death_time": record.death_time,
                "mother_id": record.mother_id,
                "father_id": record.father_id,
                "settlement_id": entity.attributes["settlement_id"],
                "alive": entity.attributes["alive"],
                "household_id": household.id if household else None,
                "personal_wealth": entity.attributes.get("personal_wealth", 0.0),
                "personal_debt": entity.attributes.get("personal_debt", 0.0),
                "name_claim": entity.attributes.get("name_claim"),
            }
        )
    (out / "people.json").write_text(json.dumps(people, indent=2), encoding="utf-8")

    ties = [
        {
            "source_id": tie.source_id,
            "target_id": tie.target_id,
            "kind": tie.kind,
            "strength": tie.strength,
            "sentiment": tie.sentiment,
            "trust": tie.trust,
            "dependence": tie.dependence,
            "started_at": tie.started_at,
            "ended_at": tie.ended_at,
        }
        for tie in result.network.ties
    ]
    (out / "social_ties.json").write_text(json.dumps(ties, indent=2), encoding="utf-8")

    households = [
        {
            "id": household.id,
            "settlement_id": household.settlement_id,
            "founded_at": household.founded_at,
            "members": sorted(household.members),
            "food_stock": household.food_stock,
            "wealth": household.wealth,
            "debt": household.debt,
            "care_capacity": household.care_capacity,
        }
        for household in result.households.households.values()
    ]
    (out / "households.json").write_text(json.dumps(households, indent=2), encoding="utf-8")

    pregnancies = [
        {
            "id": pregnancy.id,
            "gestational_parent_id": pregnancy.gestational_parent_id,
            "other_parent_id": pregnancy.other_parent_id,
            "conceived_at": pregnancy.conceived_at,
            "due_at": pregnancy.due_at,
            "active": pregnancy.active,
            "outcome": pregnancy.outcome,
        }
        for pregnancy in result.pregnancies.pregnancies.values()
    ]
    (out / "pregnancies.json").write_text(json.dumps(pregnancies, indent=2), encoding="utf-8")

    transfers = [
        {
            "item_key": transfer.item_key,
            "from_id": transfer.from_id,
            "to_id": transfer.to_id,
            "share": transfer.share,
            "contested": transfer.contested,
            "winning_score": transfer.winning_score,
        }
        for transfer in result.inheritance_transfers
    ]
    (out / "inheritance.json").write_text(json.dumps(transfers, indent=2), encoding="utf-8")
    (out / "lineages.json").write_text(json.dumps(result.lineage_candidates, indent=2), encoding="utf-8")

    serialized_events = [
        {
            "id": event.id,
            "kind": event.kind,
            "time": event.time,
            "participants": list(event.participants),
            "locations": list(event.locations),
            "causes": list(event.causes),
            "impact": event.impact,
            "payload": dict(event.payload),
        }
        for event in world.events
    ]
    (out / "events.jsonl").write_text(
        "\n".join(json.dumps(event, sort_keys=True) for event in serialized_events) + "\n",
        encoding="utf-8",
    )

    summary = {
        "seed": args.seed,
        "years": args.years,
        "settlements": args.settlements,
        "people": len(result.person_ids),
        "births": births,
        "deaths": deaths,
        "conceptions": event_types.get("conception", 0),
        "pregnancy_losses": event_types.get("pregnancy_loss", 0),
        "events": len(world.events),
        "event_types": dict(sorted(event_types.items())),
        "social_ties": len(result.network.ties),
        "tie_types": dict(sorted(tie_types.items())),
        "relationship_separations": event_types.get("relationship_separated", 0),
        "households": len(result.households.active_households()),
        "household_stress_events": event_types.get("household_stress", 0),
        "inheritance_transfers": len(result.inheritance_transfers),
        "contested_inheritance_transfers": sum(t.contested for t in result.inheritance_transfers),
        "lineage_candidates": len(result.lineage_candidates),
        "narratives": len(result.social.social_memory.narratives),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
