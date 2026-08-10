from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from simworld.simulation.first_world import FirstWorldConfig
from simworld.simulation.spatial_life_world import SpatialLifeWorldSimulation


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=104729)
    parser.add_argument("--years", type=int, default=20)
    parser.add_argument("--width", type=int, default=46)
    parser.add_argument("--height", type=int, default=34)
    parser.add_argument("--settlements", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result = SpatialLifeWorldSimulation(
        FirstWorldConfig(
            width=args.width,
            height=args.height,
            settlements=args.settlements,
            years=args.years,
            seed=args.seed,
        )
    ).run()
    world = result.disequilibrium.institutional.material.generational.social.base.world
    event_types = Counter(event.kind for event in world.events)
    active_sites = []
    for cell, intensity in result.presence.active_sites(minimum_intensity=3.0)[:20]:
        active_sites.append(
            {
                "x": cell.x,
                "y": cell.y,
                "intensity": round(intensity, 4),
                "visits": result.presence.visits.get(cell, 0),
                "unique_visitors": len(result.presence.unique_visitors.get(cell, set())),
                "encounters": result.presence.encounters.get(cell, 0),
                "productive_uses": result.presence.productive_uses.get(cell, 0),
            }
        )

    summary = {
        "seed": args.seed,
        "years": args.years,
        "settlements": args.settlements,
        "people": len(result.presence.positions),
        "movement_events": result.movement_events,
        "encounter_events": result.encounter_events,
        "encounter_created_ties": result.encounter_ties,
        "active_site_count": len(result.presence.active_sites(minimum_intensity=3.0)),
        "top_active_sites": active_sites,
        "events": len(world.events),
        "event_types": dict(sorted(event_types.items())),
    }

    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
