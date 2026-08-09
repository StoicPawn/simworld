from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from simworld.simulation.disequilibrium_world import DisequilibriumWorldSimulation
from simworld.simulation.first_world import FirstWorldConfig, write_svg_map


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=104729)
    parser.add_argument("--years", type=int, default=30)
    parser.add_argument("--width", type=int, default=52)
    parser.add_argument("--height", type=int, default=40)
    parser.add_argument("--settlements", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result = DisequilibriumWorldSimulation(
        FirstWorldConfig(
            width=args.width,
            height=args.height,
            settlements=args.settlements,
            years=args.years,
            seed=args.seed,
        )
    ).run()
    institutional = result.institutional
    material = institutional.material
    generational = material.generational
    world = generational.social.base.world
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    write_svg_map(generational.social.base, out / "map.svg")

    event_types = Counter(event.kind for event in world.events)
    summary = {
        "seed": args.seed,
        "years": args.years,
        "settlements": args.settlements,
        "people": len(generational.person_ids),
        "households": len(generational.households.active_households()),
        "material_shocks": result.material_shocks,
        "spoilage_events": result.spoilage_events,
        "exchanges": material.exchange_count,
        "obligations": len(institutional.obligations.obligations),
        "settled_obligations": sum(1 for obligation in institutional.obligations.obligations.values() if obligation.settled),
        "organizations": len(institutional.organizations.organizations),
        "authority_relations": len(institutional.authority.states),
        "events": len(world.events),
        "event_types": dict(sorted(event_types.items())),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out / "storage_profiles.json").write_text(
        json.dumps(
            {
                household_id: {
                    "capacity": profile.capacity,
                    "preservation": profile.preservation,
                    "exposure": profile.exposure,
                }
                for household_id, profile in result.storage_profiles.items()
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
