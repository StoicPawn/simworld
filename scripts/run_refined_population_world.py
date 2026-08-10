from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from simworld.simulation.first_world import FirstWorldConfig, write_svg_map
from simworld.simulation.refined_population_world import RefinedPopulationWorldSimulation


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=104729)
    parser.add_argument("--years", type=int, default=24)
    parser.add_argument("--width", type=int, default=48)
    parser.add_argument("--height", type=int, default=36)
    parser.add_argument("--settlements", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    simulation = RefinedPopulationWorldSimulation(
        FirstWorldConfig(
            width=args.width,
            height=args.height,
            settlements=args.settlements,
            years=args.years,
            seed=args.seed,
        )
    )
    result = simulation.run()
    authoritative = result.base
    distributed = authoritative.base
    emergent = distributed.base
    micro = emergent.base
    disequilibrium = micro.base
    institutional = disequilibrium.institutional
    material = institutional.material
    generational = material.generational
    world = generational.social.base.world

    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    write_svg_map(generational.social.base, out / "map.svg")

    living = [person_id for person_id in simulation.person_ids if simulation._alive(person_id)]
    active_records = result.refinement.active_records()
    event_types = Counter(event.kind for event in world.events)
    summary = {
        "seed": args.seed,
        "years": args.years,
        "total_population": round(result.total_population, 3),
        "materialized_population": round(result.materialized_population, 3),
        "unresolved_population": round(result.unresolved_population, 3),
        "accounting_gap": round(
            result.total_population - result.materialized_population - result.unresolved_population,
            9,
        ),
        "living_materialized_people": len(living),
        "active_refinement_records": len(active_records),
        "reservation_people_gap": len(active_records) - len(living),
        "bootstrap_home_overlap": distributed.bootstrap_home_overlap,
        "residential_nuclei": len(emergent.nuclei),
        "residence_shifts": emergent.residence_shifts,
        "births": event_types.get("birth", 0),
        "deaths": event_types.get("death", 0),
        "encounters": micro.encounters,
        "events": len(world.events),
        "event_types": dict(sorted(event_types.items())),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
