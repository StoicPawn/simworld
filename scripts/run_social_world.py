from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from simworld.simulation.first_world import FirstWorldConfig, write_svg_map
from simworld.simulation.social_world import SocialWorldSimulation


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the epistemic-cultural SimWorld vertical slice")
    parser.add_argument("--seed", type=int, default=104729)
    parser.add_argument("--years", type=int, default=40)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=96)
    parser.add_argument("--height", type=int, default=72)
    parser.add_argument("--settlements", type=int, default=10)
    args = parser.parse_args()

    config = FirstWorldConfig(
        width=args.width,
        height=args.height,
        settlements=args.settlements,
        years=args.years,
        seed=args.seed,
    )
    result = SocialWorldSimulation(config).run()
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    write_svg_map(result.base, output / "map.svg")

    events = result.base.world.events
    with (output / "events.jsonl").open("w", encoding="utf-8") as handle:
        for event in events:
            handle.write(
                json.dumps(
                    {
                        "id": event.id,
                        "kind": event.kind,
                        "time": event.time,
                        "participants": event.participants,
                        "causes": event.causes,
                        "payload": dict(event.payload),
                    },
                    sort_keys=True,
                )
                + "\n"
            )

    houses = []
    for house_id in result.house_ids:
        entity = result.base.world.entities[house_id]
        houses.append({"id": house_id, "name": entity.name, **entity.attributes})
    (output / "houses.json").write_text(json.dumps(houses, indent=2), encoding="utf-8")

    narratives = {
        narrative_id: {
            "origin_event_ids": narrative.origin_event_ids,
            "versions": [
                {
                    "time": version.time,
                    "teller_id": version.teller_id,
                    "claims": version.claims,
                    "confidence": version.confidence,
                    "emotional_valence": version.emotional_valence,
                    "parent_index": version.parent_index,
                }
                for version in narrative.versions
            ],
        }
        for narrative_id, narrative in result.social_memory.narratives.items()
    }
    (output / "narratives.json").write_text(json.dumps(narratives, indent=2), encoding="utf-8")

    kinds = Counter(event.kind for event in events)
    action_counts = Counter(
        str(event.payload["action"])
        for event in events
        if event.kind == "house_action"
    )
    misleading_reports = sum(
        1
        for event in events
        if event.kind == "petition_or_report"
        and abs(float(event.payload["asserted_shortage"]) - float(event.payload["actual_shortage_hidden_from_house"])) > 0.12
    )
    summary = {
        "seed": args.seed,
        "years": args.years,
        "settlements": len(result.base.settlement_ids),
        "houses": len(result.house_ids),
        "events": len(events),
        "event_types": dict(sorted(kinds.items())),
        "house_actions": dict(sorted(action_counts.items())),
        "misleading_or_distorted_reports": misleading_reports,
        "narratives": len(result.social_memory.narratives),
        "narrative_versions": sum(len(item.versions) for item in result.social_memory.narratives.values()),
        "final_population": result.base.final_population,
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
