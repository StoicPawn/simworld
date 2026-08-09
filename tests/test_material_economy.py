from random import Random

from simworld.economy.exchange import ExchangeProposal, execute_exchange
from simworld.economy.production import Inventory, ProductionContext, ProductionProcess, produce
from simworld.economy.property import Asset, PropertyRegistry, PropertyRight
from simworld.simulation.first_world import FirstWorldConfig
from simworld.simulation.material_world import MaterialWorldSimulation


def test_property_transfer_preserves_history_and_residual_share() -> None:
    registry = PropertyRegistry()
    asset = Asset("field_plot")
    registry.add_asset(asset)
    registry.grant(PropertyRight(asset.id, "A", 1.0, started_at=0))

    registry.transfer(asset_id=asset.id, from_holder="A", to_holder="B", share=0.4, time=7)

    assert registry.control_share("A", asset.id, 6) == 1.0
    assert round(registry.control_share("A", asset.id, 7), 6) == 0.6
    assert round(registry.control_share("B", asset.id, 7), 6) == 0.4


def test_production_is_constrained_by_material_context() -> None:
    inv = Inventory("hh", {"tools": 1.0})
    process = ProductionProcess("grain", labour_per_unit=1.0, base_productivity=1.0)
    poor = produce(process, inv, ProductionContext(labour=2.0, land_quality=0.2, climate_factor=0.5))
    rich = produce(process, inv, ProductionContext(labour=2.0, land_quality=1.0, climate_factor=1.0))
    assert rich.quantity > poor.quantity


def test_exchange_requires_stock_and_acceptance() -> None:
    inventories = {
        "A": Inventory("A", {"timber": 1.0, "grain": 0.0}),
        "B": Inventory("B", {"timber": 0.0, "grain": 1.0}),
    }
    proposal = ExchangeProposal("A", "B", "timber", 0.3, "grain", 0.4)
    rejected = execute_exchange(proposal, inventories, 0.2)
    assert not rejected.accepted
    accepted = execute_exchange(proposal, inventories, 0.9)
    assert accepted.accepted
    assert inventories["A"].amount("grain") == 0.4
    assert inventories["B"].amount("timber") == 0.3


def test_material_world_produces_property_and_material_events() -> None:
    config = FirstWorldConfig(width=44, height=34, settlements=4, years=8, seed=104729)
    result = MaterialWorldSimulation(config).run()
    world = result.generational.social.base.world
    kinds = {event.kind for event in world.events}

    assert result.property_registry.assets
    assert result.inventories
    assert "material_production" in kinds
    assert "material_household_initialized" in kinds
    assert all(inventory.owner_id in result.generational.households.households for inventory in result.inventories.values())
