from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from simworld.simulation.first_world import FirstWorldConfig, write_svg_map
from simworld.simulation.microgeography_world import MicrogeographyWorldSimulation


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=104729)
    parser.add_argument("--years", type=int, default=20)
    parser.add_argument("--width", type=int, default=48)
    parser.add_argument("--height", type=int, default=36)
    parser.add_argument("--settlements", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result = MicrogeographyWorldSimulation(
        FirstWorldConfig(
            width=args.width,
            height=args.height,
            settlements=args.settlements,
            years=args.years,
            seed=args.seed,
        )
    ).run()
    disequilibrium = result.base
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
        "settlements": args.settlements,
        "people": len(generational.person_ids),
        "active_cells": len(result.activity.cells),
        "derived_places": len(result.place_views),
        "encounters": result.encounters,
        "material_shocks": disequilibrium.material_shocks,
        "exchanges": material.exchange_count,
        "obligations": len(institutional.obligations.obligations),
        "organizations": len(institutional.organizations.organizations),
        "events": len(world.events),
        "event_types": dict(sorted(event_types.items())),
    }
    places = [
        {
            "x": view.cell.x,
            "y": view.cell.y,
            "actors": view.actors,
            "persistence": view.persistence,
            "total_activity": round(view.total_activity, 4),
            "residence_signal": round(view.residence_signal, 4),
            "exchange_signal": round(view.exchange_signal, 4),
            "production_signal": round(view.production_signal, 4),
            "conflict_signal": round(view.conflict_signal, 4),
            "infrastructure_signal": round(view.infrastructure_signal, 4),
        }
        for view in result.place_views[:100]
    ]
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out / "places.json").write_text(json.dumps(places, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
