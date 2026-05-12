from prometheus_client import CollectorRegistry, generate_latest

from exporter.metrics import build_metrics
from simulator.fulfillment_simulator import FulfillmentSimulator
from simulator.inventory_simulator import InventorySimulator
from simulator.order_simulator import OrderSimulator


def test_metrics_output_contains_expected_families() -> None:
    metrics = build_metrics(CollectorRegistry())
    order_simulator = OrderSimulator(
        orders_total=metrics["orders_total"],
        order_processing_seconds=metrics["order_processing_seconds"],
        seed=11,
    )
    inventory_simulator = InventorySimulator(
        inventory_level=metrics["inventory_level"],
        stockout_events_total=metrics["stockout_events_total"],
    )
    fulfillment_simulator = FulfillmentSimulator(
        fulfillment_delay_seconds=metrics["fulfillment_delay_seconds"],
        fulfillment_failed_total=metrics["fulfillment_failed_total"],
        seed=13,
    )

    for event in order_simulator.tick():
        inventory_simulator.reserve(event.sku)
        fulfillment_simulator.fulfill(event.status)

    output = generate_latest(metrics["registry"]).decode("utf-8")

    assert "ecommerce_orders_total" in output
    assert "ecommerce_order_processing_seconds_bucket" in output
    assert "ecommerce_inventory_level" in output
    assert "ecommerce_stockout_events_total" in output
    assert "ecommerce_fulfillment_delay_seconds_bucket" in output
    assert "ecommerce_fulfillment_failed_total" in output


def test_inventory_levels_remain_non_negative() -> None:
    metrics = build_metrics(CollectorRegistry())
    inventory_simulator = InventorySimulator(
        inventory_level=metrics["inventory_level"],
        stockout_events_total=metrics["stockout_events_total"],
        initial_inventory={"sku-1": 2},
    )

    assert inventory_simulator.reserve("sku-1") is True
    assert inventory_simulator.reserve("sku-1") is True
    assert inventory_simulator.reserve("sku-1") is False
    assert inventory_simulator.get_level("sku-1") == 0


def test_restock_recovers_inventory_after_stockout() -> None:
    metrics = build_metrics(CollectorRegistry())
    inventory_simulator = InventorySimulator(
        inventory_level=metrics["inventory_level"],
        stockout_events_total=metrics["stockout_events_total"],
        initial_inventory={"sku-1": 1},
    )

    assert inventory_simulator.reserve("sku-1") is True
    assert inventory_simulator.get_level("sku-1") == 0
    assert inventory_simulator.restock("sku-1", 25) == 25
    assert inventory_simulator.get_level("sku-1") == 25
