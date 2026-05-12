from prometheus_client import CollectorRegistry

from exporter.metrics import build_metrics
from simulator.fulfillment_simulator import FulfillmentSimulator
from simulator.inventory_simulator import InventorySimulator
from simulator.order_simulator import OrderSimulator


def test_simulate_stockout_sets_inventory_to_zero() -> None:
    metrics = build_metrics(CollectorRegistry())
    simulator = InventorySimulator(
        inventory_level=metrics["inventory_level"],
        stockout_events_total=metrics["stockout_events_total"],
    )

    simulator.simulate_stockout("sku-red-shirt")

    assert simulator.get_level("sku-red-shirt") == 0


def test_restock_increases_inventory_level() -> None:
    metrics = build_metrics(CollectorRegistry())
    simulator = InventorySimulator(
        inventory_level=metrics["inventory_level"],
        stockout_events_total=metrics["stockout_events_total"],
        initial_inventory={"sku-red-shirt": 0},
    )

    assert simulator.restock("sku-red-shirt", 30) == 30
    assert simulator.get_level("sku-red-shirt") == 30


def test_simulate_traffic_spike_updates_multiplier() -> None:
    metrics = build_metrics(CollectorRegistry())
    simulator = OrderSimulator(
        orders_total=metrics["orders_total"],
        order_processing_seconds=metrics["order_processing_seconds"],
        seed=7,
    )

    simulator.simulate_traffic_spike(8)

    assert simulator.current_traffic_multiplier() == 8


def test_simulate_fulfillment_outage_forces_failures() -> None:
    metrics = build_metrics(CollectorRegistry())
    simulator = FulfillmentSimulator(
        fulfillment_delay_seconds=metrics["fulfillment_delay_seconds"],
        fulfillment_failed_total=metrics["fulfillment_failed_total"],
        seed=3,
    )

    simulator.simulate_fulfillment_outage()
    result = simulator.fulfill("completed")

    assert result["failed"] is True
