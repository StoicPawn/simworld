from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from simworld.simulation.authoritative_population_world import AuthoritativePopulationWorldSimulation
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

    result = AuthoritativePopulationWorldSimulation(
        FirstWorldConfig(
            width=args.width,
            height=args.height,
            settlements=args.settlements,
            years=args.years,
            seed=args.seed,
        )
    ).run()
    distributed = result.base
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
    summary = {
        "seed": args.seed,
        "years": args.years,
        "compatibility_anchors": args.settlements,
        "field_population": round(result.field_total, 3),
        "derived_legacy_population_total": round(result.legacy_summary_total, 3),
        "summary_gap": round(result.legacy_summary_total - result.field_total, 3),
        "bootstrap_home_overlap": distributed.bootstrap_home_overlap,
        "residential_nuclei": len(emergent.nuclei),
        "residence_shifts": emergent.residence_shifts,
        "people_materialized": len(generational.person_ids),
        "households_materialized": len(generational.households.active_households()),
        "encounters": micro.encounters,
        "exchanges": material.exchange_count,
        "organizations": len(institutional.organizations.organizations),
        "events": len(world.events),
        "event_types": dict(sorted(event_types.items())),
    }
    summaries = {
        anchor_id: {
            "population": round(view.population, 3),
            "capacity": round(view.capacity, 3),
            "capacity_ratio": round(view.capacity_ratio, 4),
            "mean_suitability": round(view.mean_suitability, 4),
            "cell_count": view.cell_count,
        }
        for anchor_id, view in sorted(result.summaries.items())
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out / "compatibility_population_summaries.json").write_text(
        json.dumps(summaries, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
