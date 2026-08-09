from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from simworld.simulation.encounter_world import EncounterWorldSimulation
from simworld.simulation.first_world import FirstWorldConfig


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=104729)
    parser.add_argument("--years", type=int, default=20)
    parser.add_argument("--width", type=int, default=44)
    parser.add_argument("--height", type=int, default=34)
    parser.add_argument("--settlements", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    simulation = EncounterWorldSimulation(FirstWorldConfig(
        width=args.width,
        height=args.height,
        settlements=args.settlements,
        years=args.years,
        seed=args.seed,
    ))
    result = simulation.run()
    world = result.institutional.material.generational.social.base.world
    args.output.mkdir(parents=True, exist_ok=True)
    event_types = Counter(event.kind for event in world.events)
    summary = {
        "seed": args.seed,
        "years": args.years,
        "settlements": args.settlements,
        "events": len(world.events),
        "encounters": len(simulation.encounters.encounters),
        "visits": len(simulation.encounters.visits),
        "encounter_formed_ties": sum(
            1 for event in world.events
            if event.kind == "social_tie_formed" and event.payload.get("source") == "encounters"
        ),
        "event_types": dict(sorted(event_types.items())),
    }
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
