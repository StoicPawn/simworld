from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from simworld.simulation.first_world import FirstWorldConfig
from simworld.simulation.micro_place_world import MicroPlaceWorldSimulation


def main() -> int:
    parser = argparse.ArgumentParser(description="Run geography-driven individual micro-place simulation")
    parser.add_argument("--seed", type=int, default=104729)
    parser.add_argument("--years", type=int, default=20)
    parser.add_argument("--width", type=int, default=48)
    parser.add_argument("--height", type=int, default=36)
    parser.add_argument("--settlements", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result = MicroPlaceWorldSimulation(
        FirstWorldConfig(
            seed=args.seed,
            years=args.years,
            width=args.width,
            height=args.height,
            settlements=args.settlements,
        )
    ).run()
    args.output.mkdir(parents=True, exist_ok=True)

    world = result.disequilibrium.institutional.material.generational.social.base.world
    event_types = Counter(event.kind for event in world.events)
    top_places = [
        {
            "cell": list(view.cell),
            "visits": round(view.visits, 3),
            "unique_visitors": view.unique_visitors,
            "persistence": view.persistence,
            "gathering": round(view.gathering, 3),
            "cultivation": round(view.cultivation, 3),
            "cooperation": round(view.cooperation, 3),
            "conflict": round(view.conflict, 3),
        }
        for view in result.place_views[:20]
    ]
    summary = {
        "seed": args.seed,
        "years": args.years,
        "settlements": args.settlements,
        "people": len(result.disequilibrium.institutional.material.generational.person_ids),
        "active_cells": len(result.place_ledger.sites),
        "derived_place_views": len(result.place_views),
        "encounters": result.encounters,
        "event_types": dict(sorted(event_types.items())),
        "top_places": top_places,
    }
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
