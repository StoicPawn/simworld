from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from simworld.simulation.distributed_population_world import DistributedPopulationWorldSimulation
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

    result = DistributedPopulationWorldSimulation(
        FirstWorldConfig(
            width=args.width,
            height=args.height,
            settlements=args.settlements,
            years=args.years,
            seed=args.seed,
        )
    ).run()
    emergent = result.base
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
    high_density = result.population_field.high_density_cells(minimum_population=1.0)
    summary = {
        "seed": args.seed,
        "years": args.years,
        "bootstrap_settlements": args.settlements,
        "people": len(generational.person_ids),
        "households": len(generational.households.active_households()),
        "initial_background_population": round(result.initial_background_population, 3),
        "final_background_population": round(result.final_background_population, 3),
        "background_cells_ge_1": len(high_density),
        "bootstrap_home_overlap": result.bootstrap_home_overlap,
        "residential_nuclei": len(emergent.nuclei),
        "residence_shifts": emergent.residence_shifts,
        "construction_events": emergent.construction_events,
        "encounters": micro.encounters,
        "exchanges": material.exchange_count,
        "organizations": len(institutional.organizations.organizations),
        "events": len(world.events),
        "event_types": dict(sorted(event_types.items())),
    }
    density = [
        {
            "cell": [cell.x, cell.y],
            "population": round(result.population_field.population_at(cell), 4),
            "capacity": round(result.population_field.capacity_at(cell), 4),
            "suitability": round(float(result.population_field.suitability[cell.y, cell.x]), 4),
        }
        for cell in high_density[:200]
    ]
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out / "population_hotspots.json").write_text(json.dumps(density, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
