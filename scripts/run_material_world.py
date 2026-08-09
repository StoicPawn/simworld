from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from simworld.simulation.first_world import FirstWorldConfig, write_svg_map
from simworld.simulation.material_world import MaterialWorldSimulation


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=104729)
    parser.add_argument("--years", type=int, default=30)
    parser.add_argument("--width", type=int, default=60)
    parser.add_argument("--height", type=int, default=44)
    parser.add_argument("--settlements", type=int, default=6)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    config = FirstWorldConfig(
        width=args.width,
        height=args.height,
        settlements=args.settlements,
        years=args.years,
        seed=args.seed,
    )
    result = MaterialWorldSimulation(config).run()
    generational = result.generational
    world = generational.social.base.world
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    write_svg_map(generational.social.base, out / "map.svg")

    event_types = Counter(event.kind for event in world.events)
    inventory_rows = [
        {
            "household_id": household_id,
            "stocks": {good: round(quantity, 6) for good, quantity in inventory.stocks.items()},
        }
        for household_id, inventory in result.inventories.items()
    ]
    property_rows = [
        {
            "asset_id": asset.id,
            "kind": asset.kind,
            "location": asset.location,
            "productive_capacity": asset.productive_capacity,
            "holders": [
                {
                    "holder_id": right.holder_id,
                    "share": right.share,
                    "right_kind": right.right_kind,
                }
                for right in result.property_registry.holders(asset.id, args.years)
            ],
        }
        for asset in result.property_registry.assets.values()
    ]
    (out / "inventories.json").write_text(json.dumps(inventory_rows, indent=2), encoding="utf-8")
    (out / "property.json").write_text(json.dumps(property_rows, indent=2), encoding="utf-8")

    summary = {
        "seed": args.seed,
        "years": args.years,
        "settlements": args.settlements,
        "people": len(generational.person_ids),
        "households": len(generational.households.active_households()),
        "assets": len(result.property_registry.assets),
        "exchanges": result.exchange_count,
        "events": len(world.events),
        "event_types": dict(sorted(event_types.items())),
        "final_population": generational.social.base.final_population,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
