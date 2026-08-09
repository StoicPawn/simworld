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
    (out / "lineages.json").write_text(
        json.dumps(result.lineage_candidates, indent=2), encoding="utf-8"
    )
    (out / "events.jsonl").write_text(
        "\n".join(json.dumps(event.to_dict(), sort_keys=True) for event in world.events) + "\n",
        encoding="utf-8",
    )

    summary = {
        "seed": args.seed,
        "years": args.years,
        "settlements": args.settlements,
        "people": len(result.person_ids),
        "births": births,
        "deaths": deaths,
        "events": len(world.events),
        "event_types": dict(sorted(event_types.items())),
        "social_ties": len(result.network.ties),
        "tie_types": dict(sorted(tie_types.items())),
        "lineage_candidates": len(result.lineage_candidates),
        "narratives": len(result.social.social_memory.narratives),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
