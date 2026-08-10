from random import Random

from simworld.control_tower import WorldBlueprint, load_effective_affordance_catalog
from simworld.culture.effects import apply_effect_specs


def test_control_tower_loads_world_initial_conditions() -> None:
    blueprint = WorldBlueprint.from_json("configs/worlds/control_tower_example.json")
    assert blueprint.simulation.years == 250
    assert blueprint.map.width == 192
    assert len(blueprint.population) == 2
    assert sum(seed.count for seed in blueprint.population) == 1850
    assert len(blueprint.resources) == 2


def test_control_tower_can_remove_technology_from_world_possibility_space() -> None:
    blueprint = WorldBlueprint.from_mapping(
        {
            "simulation": {"root_seed": 1, "years": 10},
            "technology": {
                "catalog_paths": ["configs/affordances/foundation.json"],
                "disabled": ["durable_symbolic_recording"],
            },
        }
    )
    catalog = load_effective_affordance_catalog(blueprint)
    assert "durable_symbolic_recording" not in catalog.affordances
    assert "controlled_heat_processing" in catalog.affordances


def test_writing_only_affects_record_credibility_when_context_supports_it() -> None:
    blueprint = WorldBlueprint.from_mapping(
        {"simulation": {"root_seed": 3, "years": 1}}
    )
    writing = load_effective_affordance_catalog(blueprint).get("durable_symbolic_recording")

    absent = apply_effect_specs(
        writing.effects,
        mastery=1.0,
        base_channels={"claim_credibility": 1.0},
        context={"record_available": 0.0, "reader_accepts_medium": 1.0},
        rng=Random(1),
    )
    assert absent["claim_credibility"] == 1.0

    outcomes = [
        apply_effect_specs(
            writing.effects,
            mastery=1.0,
            base_channels={"claim_credibility": 1.0},
            context={
                "record_created": 1.0,
                "record_used": 1.0,
                "record_available": 1.0,
                "reader_accepts_medium": 1.0,
            },
            rng=Random(seed),
        )["claim_credibility"]
        for seed in range(30)
    ]
    assert any(value > 1.0 for value in outcomes)
    assert any(value == 1.0 for value in outcomes)


def test_iron_knowledge_without_equipment_does_not_improve_combat() -> None:
    blueprint = WorldBlueprint.from_mapping(
        {"simulation": {"root_seed": 4, "years": 1}}
    )
    iron = load_effective_affordance_catalog(blueprint).get("worked_iron_tools")

    no_equipment = apply_effect_specs(
        iron.effects,
        mastery=1.0,
        base_channels={"combat_effectiveness": 1.0},
        context={"iron_equipment_available": 0.0},
        rng=Random(1),
    )
    equipped = apply_effect_specs(
        iron.effects,
        mastery=0.8,
        base_channels={"combat_effectiveness": 1.0},
        context={"iron_equipment_available": 1.0},
        rng=Random(1),
    )
    assert no_equipment["combat_effectiveness"] == 1.0
    assert equipped["combat_effectiveness"] > 1.0
