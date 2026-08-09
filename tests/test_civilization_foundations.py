from __future__ import annotations

from random import Random

import numpy as np

from simworld.conflict.model import ConflictContext, choose_conflict_action, conflict_pressure
from simworld.economy.agriculture import GRAINS, crop_suitability
from simworld.geography.hydrology import derive_hydrology
from simworld.simulation.civilization_world import CivilizationWorldSimulation
from simworld.simulation.first_world import FirstWorldConfig
from simworld.social.household import Household, Pregnancy, allocate_inheritance


def test_hydrology_builds_river_corridors_from_terrain() -> None:
    elevation = np.array(
        [
            [9, 8, 7, 6, 5],
            [8, 7, 6, 5, 4],
            [7, 6, 5, 4, 3],
            [6, 5, 4, 3, 2],
            [5, 4, 3, 2, -1],
        ],
        dtype=np.float32,
    )
    water = elevation < 0
    rainfall = np.full_like(elevation, 900.0)
    hydro = derive_hydrology(elevation, water, rainfall)
    assert hydro.flow_accumulation[3, 3] > hydro.flow_accumulation[0, 0]
    assert hydro.water_access[3, 3] > 0.0
    assert hydro.river_strength.shape == elevation.shape


def test_crop_suitability_depends_on_land_water_and_climate() -> None:
    fertility = np.array([[0.9, 0.2]], dtype=np.float32)
    temp = np.array([[17.0, 35.0]], dtype=np.float32)
    rain = np.array([[850.0, 250.0]], dtype=np.float32)
    water = np.array([[0.8, 0.0]], dtype=np.float32)
    rugged = np.array([[0.05, 0.9]], dtype=np.float32)
    score = crop_suitability(fertility, temp, rain, water, rugged, GRAINS)
    assert score[0, 0] > score[0, 1]


def test_household_is_not_identical_to_biological_family() -> None:
    household = Household("h", "s")
    household.add_member("unrelated-a", 0)
    household.add_member("unrelated-b", 3)
    assert household.members == {"unrelated-a", "unrelated-b"}
    household.remove_member("unrelated-a")
    assert household.members == {"unrelated-b"}


def test_inheritance_rule_is_parameterized_not_universal() -> None:
    equal = allocate_inheritance(90.0, ("a", "b", "c"))
    weighted = allocate_inheritance(90.0, ("a", "b", "c"), custom_weights={"a": 4.0, "b": 1.0, "c": 1.0})
    assert equal["a"] == 30.0
    assert weighted["a"] > weighted["b"]


def test_conflict_pressure_does_not_deterministically_mean_attack() -> None:
    context = ConflictContext(
        "a", "b",
        resource_overlap=0.9,
        territorial_friction=0.9,
        rivalry=0.9,
        fear=0.8,
        grievance=0.8,
        opportunity=0.8,
        interdependence=0.1,
        kinship_inhibition=0.0,
        geographic_access=0.9,
    )
    assert conflict_pressure(context) > 0.5
    outcomes = {choose_conflict_action(context, Random(seed)).action for seed in range(80)}
    assert "attack" in outcomes or "raid" in outcomes
    assert "negotiate" in outcomes or "avoid" in outcomes


def test_pregnancy_has_duration_not_instant_birth() -> None:
    pregnancy = Pregnancy("m", "o", conceived_at=4, due_at=5, viability=0.9)
    assert not pregnancy.due(4)
    assert pregnancy.due(5)


def test_integrated_civilization_world_links_all_foundations() -> None:
    config = FirstWorldConfig(width=42, height=32, settlements=4, years=18, seed=19417)
    result = CivilizationWorldSimulation(config).run()
    world = result.generational.social.base.world
    kinds = [event.kind for event in world.events]

    assert result.hydrology.river_strength.shape == (config.height, config.width)
    assert len(result.households) >= config.settlements
    assert "household_formed" in kinds
    assert "conception" in kinds
    assert any(kind in kinds for kind in ("birth", "pregnancy_loss"))
    assert isinstance(result.conflict_actions, dict)
    assert sum(result.conflict_actions.values()) > 0
    assert "intergroup_action" in kinds or result.conflict_actions.get("avoid", 0) > 0
