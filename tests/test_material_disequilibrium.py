from random import Random

from simworld.economy.production import Inventory
from simworld.economy.storage import HouseholdDemandProfile, StorageProfile, age_stock
from simworld.simulation.disequilibrium_world import DisequilibriumWorldSimulation
from simworld.simulation.first_world import FirstWorldConfig


def test_storage_can_lose_stock_without_social_consequence_being_prescribed() -> None:
    inventory = Inventory("hh", {"grain": 3.0})
    result = age_stock(
        inventory,
        "grain",
        StorageProfile(capacity=2.0, preservation=0.35, exposure=0.9),
        climate_stress=1.0,
        rng=Random(7),
    )
    assert result.overflow_lost == 1.0
    assert result.spoiled > 0.0
    assert inventory.amount("grain") < 2.0


def test_household_demand_depends_on_age_structure() -> None:
    profile = HouseholdDemandProfile(adult_food_need=0.5, child_food_factor=0.6, elder_food_factor=0.8)
    assert profile.annual_food_need((5, 30, 70)) == 0.3 + 0.5 + 0.4


def test_disequilibrium_world_creates_local_material_variation() -> None:
    result = DisequilibriumWorldSimulation(
        FirstWorldConfig(width=42, height=32, settlements=4, years=10, seed=104729)
    ).run()
    institutional = result.institutional
    world = institutional.material.generational.social.base.world
    kinds = {event.kind for event in world.events}
    assert "material_production" in kinds
    assert result.storage_profiles
    assert result.demand_profiles
    assert result.material_shocks + result.spoilage_events > 0
    assert "local_material_shock" in kinds or "storage_loss" in kinds
