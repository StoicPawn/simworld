from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from simworld.simulation.emergent_settlement_world import EmergentSettlementWorldSimulation
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

    result = EmergentSettlementWorldSimulation(
        FirstWorldConfig(
            width=args.width,
            height=args.height,
            settlements=args.settlements,
            years=args.years,
            seed=args.seed,
        )
    ).run()
    micro = result.base
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
        "bootstrap_settlements": args.settlements,
        "people": len(generational.person_ids),
        "households": len(generational.households.active_households()),
        "active_cells": len(micro.activity.cells),
        "derived_places": len(micro.place_views),
        "residential_nuclei": len(result.nuclei),
        "residence_shifts": result.residence_shifts,
        "construction_events": result.construction_events,
        "encounters": micro.encounters,
        "exchanges": material.exchange_count,
        "organizations": len(institutional.organizations.organizations),
        "events": len(world.events),
        "event_types": dict(sorted(event_types.items())),
    }
    nuclei = [
        {
            "centre": [view.centre.x, view.centre.y],
            "cells": [[cell.x, cell.y] for cell in view.cells],
            "actors": view.actors,
            "persistence": view.persistence,
            "residence_signal": round(view.residence_signal, 4),
            "production_signal": round(view.production_signal, 4),
            "exchange_signal": round(view.exchange_signal, 4),
            "infrastructure_signal": round(view.infrastructure_signal, 4),
            "conflict_signal": round(view.conflict_signal, 4),
            "total_signal": round(view.total_signal, 4),
        }
        for view in result.nuclei[:100]
    ]
    homes = {
        household_id: [cell.x, cell.y]
        for household_id, cell in sorted(result.household_home_cells.items())
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out / "residential_nuclei.json").write_text(json.dumps(nuclei, indent=2), encoding="utf-8")
    (out / "household_homes.json").write_text(json.dumps(homes, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
