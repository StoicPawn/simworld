from random import Random

from simworld.economy.exchange import ExchangeProposal, execute_exchange
from simworld.economy.production import Inventory, ProductionContext, ProductionProcess, produce
from simworld.economy.property import Asset, AssetRelation, PropertyRegistry, Recognition
from simworld.simulation.first_world import FirstWorldConfig
from simworld.simulation.material_world import MaterialWorldSimulation


def test_asset_relations_separate_use_control_claim_and_recognition() -> None:
    registry = PropertyRegistry()
    asset = Asset("field_plot")
    registry.add_asset(asset)
    registry.relate(AssetRelation(asset.id, "A", 1.0, "use", started_at=0))
    registry.relate(AssetRelation(asset.id, "A", 0.8, "control", started_at=0))
    registry.relate(AssetRelation(asset.id, "B", 1.0, "claim", started_at=0))
    registry.recognize(Recognition(asset.id, "B", "C", 0.9, started_at=2, basis="custom"))

    assert registry.effective_control("A", asset.id, 3) == 0.8
    assert registry.effective_control("B", asset.id, 3) == 0.0
    assert registry.recognition_of("B", asset.id, 3) == 0.9
    assert registry.relations_of("A", 3, "use")
    assert registry.relations_of("B", 3, "claim")


def test_relation_transfer_preserves_history_and_residual_strength() -> None:
    registry = PropertyRegistry()
    asset = Asset("field_plot")
    registry.add_asset(asset)
    registry.relate(AssetRelation(asset.id, "A", 1.0, "control", started_at=0))

    registry.transfer_relation(
        asset_id=asset.id,
        from_actor="A",
        to_actor="B",
        strength=0.4,
        time=7,
        kind="control",
        provenance="occupation_change",
    )

    assert registry.effective_control("A", asset.id, 6) == 1.0
    assert round(registry.effective_control("A", asset.id, 7), 6) == 0.6
    assert round(registry.effective_control("B", asset.id, 7), 6) == 0.4


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


def test_material_world_produces_asset_relations_and_material_events() -> None:
    config = FirstWorldConfig(width=44, height=34, settlements=4, years=8, seed=104729)
    result = MaterialWorldSimulation(config).run()
    world = result.generational.social.base.world
    kinds = {event.kind for event in world.events}

    assert result.property_registry.assets
    assert result.property_registry.relations
    assert any(relation.kind == "use" for relation in result.property_registry.relations)
    assert any(relation.kind == "control" for relation in result.property_registry.relations)
    assert result.inventories
    assert "material_production" in kinds
    assert "material_household_initialized" in kinds
    assert all(inventory.owner_id in result.generational.households.households for inventory in result.inventories.values())
