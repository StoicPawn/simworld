from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from simworld.simulation.first_world import FirstWorldConfig, write_svg_map
from simworld.simulation.institutional_world import InstitutionalWorldSimulation


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=104729)
    parser.add_argument("--years", type=int, default=30)
    parser.add_argument("--width", type=int, default=56)
    parser.add_argument("--height", type=int, default=42)
    parser.add_argument("--settlements", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result = InstitutionalWorldSimulation(
        FirstWorldConfig(
            width=args.width,
            height=args.height,
            settlements=args.settlements,
            years=args.years,
            seed=args.seed,
        )
    ).run()
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    generational = result.material.generational
    world = generational.social.base.world
    write_svg_map(generational.social.base, out / "map.svg")

    event_types = Counter(event.kind for event in world.events)
    obligations = [
        {
            "id": obligation.id,
            "debtor_id": obligation.debtor_id,
            "creditor_id": obligation.creditor_id,
            "kind": obligation.kind,
            "resource": obligation.resource,
            "amount": obligation.amount,
            "fulfilled": obligation.fulfilled,
            "outstanding": obligation.outstanding,
            "created_at": obligation.created_at,
            "due_at": obligation.due_at,
        }
        for obligation in result.obligations.obligations.values()
    ]
    organizations = [
        {
            "id": organization.id,
            "formed_at": organization.formed_at,
            "members": sorted(organization.members(args.years)),
            "purpose": organization.purpose,
            "shared_resources": organization.shared_resources,
            "internal_recognition": organization.internal_recognition,
        }
        for organization in result.organizations.active(args.years)
    ]
    authority_rows = []
    for authority_id, subject_id, domain in sorted(result.authority.states):
        signal = result.authority.signal(authority_id, subject_id, domain)
        authority_rows.append(
            {
                "authority_id": authority_id,
                "subject_id": subject_id,
                "domain": domain,
                "effective_authority": round(signal.effective_authority, 6),
                "legitimacy_signal": round(signal.legitimacy_signal, 6),
                "compliance": round(signal.compliance, 6),
                "dependency": round(signal.dependency, 6),
                "recognition": round(signal.recognition, 6),
                "provision": round(signal.provision, 6),
                "coercion": round(signal.coercion, 6),
            }
        )

    (out / "obligations.json").write_text(json.dumps(obligations, indent=2), encoding="utf-8")
    (out / "organizations.json").write_text(json.dumps(organizations, indent=2), encoding="utf-8")
    (out / "authority.json").write_text(json.dumps(authority_rows, indent=2), encoding="utf-8")

    summary = {
        "seed": args.seed,
        "years": args.years,
        "settlements": args.settlements,
        "people": len(generational.person_ids),
        "households": len(generational.households.active_households()),
        "obligations": len(result.obligations.obligations),
        "settled_obligations": sum(1 for obligation in result.obligations.obligations.values() if obligation.settled),
        "organizations": len(result.organizations.organizations),
        "authority_relations": len(result.authority.states),
        "events": len(world.events),
        "event_types": dict(sorted(event_types.items())),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
