from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from simworld.simulation.civilization_world import CivilizationWorldSimulation
from simworld.simulation.first_world import FirstWorldConfig, write_svg_map


def event_dict(event):
    return {
        "id": event.id,
        "kind": event.kind,
        "time": event.time,
        "participants": list(event.participants),
        "locations": list(event.locations),
        "causes": list(event.causes),
        "impact": event.impact,
        "payload": dict(event.payload),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=104729)
    parser.add_argument("--years", type=int, default=30)
    parser.add_argument("--width", type=int, default=54)
    parser.add_argument("--height", type=int, default=40)
    parser.add_argument("--settlements", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    config = FirstWorldConfig(
        width=args.width,
        height=args.height,
        settlements=args.settlements,
        years=args.years,
        seed=args.seed,
    )
    result = CivilizationWorldSimulation(config).run()
    base = result.generational.social.base
    world = base.world
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    write_svg_map(base, out / "map.svg")

    (out / "events.jsonl").write_text(
        "\n".join(json.dumps(event_dict(event), sort_keys=True) for event in world.events) + "\n",
        encoding="utf-8",
    )
    households = [
        {
            "id": hh.id,
            "settlement_id": hh.settlement_id,
            "members": sorted(hh.members),
            "food_stock": hh.food_stock,
            "wealth": hh.wealth,
            "debt": hh.debt,
            "land": hh.land,
            "tools": hh.tools,
        }
        for hh in result.households
    ]
    (out / "households.json").write_text(json.dumps(households, indent=2), encoding="utf-8")

    event_types = Counter(event.kind for event in world.events)
    summary = {
        "seed": args.seed,
        "years": args.years,
        "settlements": args.settlements,
        "people": len(result.generational.person_ids),
        "households": len(result.households),
        "events": len(world.events),
        "event_types": dict(sorted(event_types.items())),
        "conflict_choices": dict(sorted(result.conflict_actions.items())),
        "river_cells": int((result.hydrology.river_strength > 0.45).sum()),
        "mean_grain_suitability": float(result.crop_suitability.mean()),
        "lineage_candidates": len(result.generational.lineage_candidates),
        "narratives": len(result.generational.social.social_memory.narratives),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
