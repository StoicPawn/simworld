from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from simworld.simulation.cohort_population_world import CohortPopulationWorldSimulation
from simworld.simulation.first_world import FirstWorldConfig, write_svg_map


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=104729)
    parser.add_argument("--years", type=int, default=24)
    parser.add_argument("--width", type=int, default=48)
    parser.add_argument("--height", type=int, default=36)
    parser.add_argument("--settlements", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    simulation = CohortPopulationWorldSimulation(
        FirstWorldConfig(
            width=args.width,
            height=args.height,
            settlements=args.settlements,
            years=args.years,
            seed=args.seed,
        )
    )
    result = simulation.run()
    refined = result.base
    authoritative = refined.base
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

    event_types = Counter(event.kind for event in world.events)
    age = result.cohorts.totals_by_age()
    reproductive = result.cohorts.totals_by_reproductive_class()
    summary = {
        "seed": args.seed,
        "years": args.years,
        "total_population": round(refined.total_population, 3),
        "materialized_population": round(refined.materialized_population, 3),
        "unresolved_population": round(refined.unresolved_population, 3),
        "accounting_gap": round(
            refined.total_population - refined.materialized_population - refined.unresolved_population,
            9,
        ),
        "living_materialized_people": refined.living_materialized_people,
        "unresolved_age_bands": {
            "0_4": round(float(age[0]), 3),
            "5_14": round(float(age[1]), 3),
            "15_24": round(float(age[2]), 3),
            "25_44": round(float(age[3]), 3),
            "45_64": round(float(age[4]), 3),
            "65_plus": round(float(age[5]), 3),
        },
        "unresolved_reproductive_classes": {
            "gestational": round(float(reproductive[0]), 3),
            "non_gestational": round(float(reproductive[1]), 3),
        },
        "residential_nuclei": len(emergent.nuclei),
        "residence_shifts": emergent.residence_shifts,
        "births_detailed": event_types.get("birth", 0),
        "deaths_detailed": event_types.get("death", 0),
        "events": len(world.events),
        "event_types": dict(sorted(event_types.items())),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
