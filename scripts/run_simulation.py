"""Run a configured SimWorld kernel simulation and write portable artifacts.

This is intentionally a thin Phase-0 runner. Domain modules will extend the config schema later;
the workflow interface can remain stable while the simulator grows underneath it.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from simworld.core.engine import SimulationEngine
from simworld.core.entity import Entity
from simworld.core.event import Event


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("world config root must be a JSON object")
    return value


def event_factory(spec: dict[str, Any]):
    def factory(_world, _rng):
        return Event(
            id=str(spec["id"]),
            kind=str(spec["kind"]),
            time=int(spec["time"]),
            participants=tuple(spec.get("participants", ())),
            locations=tuple(spec.get("locations", ())),
            causes=tuple(spec.get("causes", ())),
            impact=float(spec.get("impact", 1.0)),
            payload=dict(spec.get("payload", {})),
        )

    return factory


def serialize_event(event: Event) -> dict[str, Any]:
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
    parser = argparse.ArgumentParser(description="Run a SimWorld configured simulation")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--horizon", type=int, required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if args.horizon < 0:
        raise ValueError("horizon must be non-negative")

    config = load_json(args.config)
    engine = SimulationEngine(seed=args.seed)
    engine.world.metadata.update(
        {
            "world_name": config.get("name", args.config.stem),
            "config": str(args.config),
            "seed": args.seed,
        }
    )

    for raw in config.get("entities", []):
        entity = Entity(
            id=str(raw["id"]),
            kind=str(raw["kind"]),
            name=str(raw["name"]),
            created_at=int(raw.get("created_at", 0)),
            active=bool(raw.get("active", True)),
            attributes=dict(raw.get("attributes", {})),
            tags=set(raw.get("tags", [])),
        )
        engine.world.add_entity(entity)

    for raw in config.get("events", []):
        spec = dict(raw)
        event_time = int(spec["time"])
        engine.schedule(event_time, event_factory(spec), label=str(spec.get("kind", "event")))

    engine.run_until(args.horizon)

    args.output.mkdir(parents=True, exist_ok=True)
    events = [serialize_event(event) for event in engine.world.events]
    snapshot = engine.snapshot()

    metadata = {
        "config_name": config.get("name", args.config.stem),
        "seed": args.seed,
        "horizon": args.horizon,
        "snapshot": snapshot,
    }
    (args.output / "metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with (args.output / "events.jsonl").open("w", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event, sort_keys=True) + "\n")

    entities: list[dict[str, Any]] = []
    for entity in engine.world.entities.values():
        entities.append(
            {
                "id": entity.id,
                "kind": entity.kind,
                "name": entity.name,
                "created_at": entity.created_at,
                "active": entity.active,
                "attributes": entity.attributes,
                "tags": sorted(entity.tags),
                "relevance": engine.world.relevance.score(entity.id, at_time=engine.world.current_time),
                "resolution": engine.world.resolution_of(entity.id).name,
            }
        )
    (args.output / "world_final.json").write_text(
        json.dumps({"time": engine.world.current_time, "entities": entities}, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )

    summary = (
        f"# SimWorld run\n\n"
        f"- world: `{metadata['config_name']}`\n"
        f"- seed: `{args.seed}`\n"
        f"- horizon: `{args.horizon}`\n"
        f"- entities: `{snapshot['entities']}`\n"
        f"- events: `{snapshot['events']}`\n"
        f"- pending actions: `{snapshot['pending_actions']}`\n"
    )
    (args.output / "summary.md").write_text(summary, encoding="utf-8")
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
