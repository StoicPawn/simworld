"""Run the first spatially grounded SimWorld vertical slice and export artifacts."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

from simworld.simulation.first_world import FirstWorldConfig, FirstWorldSimulation, write_svg_map


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/worlds/first_world.json")
    parser.add_argument("--output", default="runs/first-world")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--years", type=int)
    return parser.parse_args()


def event_dict(event: Any) -> dict[str, Any]:
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


def main() -> int:
    args = parse_args()
    raw = json.loads(Path(args.config).read_text(encoding="utf-8"))
    if args.seed is not None:
        raw["seed"] = args.seed
    if args.years is not None:
        raw["years"] = args.years
    config = FirstWorldConfig(**raw)
    result = FirstWorldSimulation(config).run()

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    events = result.world.events
    with (output / "events.jsonl").open("w", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event_dict(event), sort_keys=True) + "\n")

    settlements = []
    for entity_id in result.settlement_ids:
        entity = result.world.entities[entity_id]
        settlements.append({"id": entity.id, "name": entity.name, **dict(entity.attributes)})
    (output / "settlements.json").write_text(json.dumps(settlements, indent=2), encoding="utf-8")

    counts = Counter(event.kind for event in events)
    summary = {
        "seed": config.seed,
        "years": config.years,
        "grid": {
            "width": config.width,
            "height": config.height,
            "cell_size_m": config.cell_size_m,
            "cells": config.width * config.height,
        },
        "settlements": len(result.settlement_ids),
        "initial_population": sum(
            int(next(e for e in events if e.kind == "settlement_founded" and entity_id in e.participants).payload["initial_population"])
            for entity_id in result.settlement_ids
        ),
        "final_population": result.final_population,
        "events": len(events),
        "event_types": dict(sorted(counts.items())),
        "land_fraction": float(np.mean(~result.generated.water)),
        "mean_land_fertility": float(np.mean(result.generated.fertility[~result.generated.water])),
        "known_ore_settlements": sum(
            bool(result.world.entities[entity_id].attributes["known_ore"])
            for entity_id in result.settlement_ids
        ),
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    np.savez_compressed(
        output / "physical_layers.npz",
        elevation_m=result.generated.elevation_m,
        water=result.generated.water,
        rainfall_mm=result.generated.rainfall,
        temperature_c=result.generated.temperature_c,
        fertility=result.generated.fertility,
        timber=result.generated.timber,
        ore_truth=result.generated.ore,
        habitability=result.generated.habitability,
    )
    write_svg_map(result, output / "map.svg")

    markdown = [
        "# SimWorld first real simulation",
        "",
        f"Seed: `{config.seed}`  ",
        f"Years simulated: `{config.years}`  ",
        f"Settlements: `{len(result.settlement_ids)}`  ",
        f"Events: `{len(events)}`  ",
        f"Final population: `{result.final_population}`",
        "",
        "## Event types",
        "",
    ]
    markdown.extend(f"- {kind}: {count}" for kind, count in sorted(counts.items()))
    (output / "README.md").write_text("\n".join(markdown) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
