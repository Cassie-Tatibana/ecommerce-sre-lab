from __future__ import annotations

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram


def build_metrics(registry: CollectorRegistry | None = None) -> dict[str, object]:
    registry = registry or CollectorRegistry()
    orders_total = Counter(
        "ecommerce_orders_total",
        "Total simulated e-commerce orders by status.",
        labelnames=["status"],
        registry=registry,
    )
    order_processing_seconds = Histogram(
        "ecommerce_order_processing_seconds",
        "Simulated order processing duration in seconds.",
        buckets=(5, 10, 15, 20, 30, 45, 60),
        registry=registry,
    )
    inventory_level = Gauge(
        "ecommerce_inventory_level",
        "Current inventory level per SKU.",
        labelnames=["sku"],
        registry=registry,
    )
    stockout_events_total = Counter(
        "ecommerce_stockout_events_total",
        "Total stockout events per SKU.",
        labelnames=["sku"],
        registry=registry,
    )
    fulfillment_delay_seconds = Histogram(
        "ecommerce_fulfillment_delay_seconds",
        "Simulated fulfillment delay in seconds.",
        buckets=(5, 10, 20, 30, 60, 90, 120),
        registry=registry,
    )
    fulfillment_failed_total = Counter(
        "ecommerce_fulfillment_failed_total",
        "Total simulated fulfillment failures.",
        registry=registry,
    )
    return {
        "registry": registry,
        "orders_total": orders_total,
        "order_processing_seconds": order_processing_seconds,
        "inventory_level": inventory_level,
        "stockout_events_total": stockout_events_total,
        "fulfillment_delay_seconds": fulfillment_delay_seconds,
        "fulfillment_failed_total": fulfillment_failed_total,
    }
