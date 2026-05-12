from __future__ import annotations

from threading import Lock

from prometheus_client import Counter, Gauge


class InventorySimulator:
    def __init__(
        self,
        inventory_level: Gauge,
        stockout_events_total: Counter,
        initial_inventory: dict[str, int] | None = None,
    ) -> None:
        self.inventory_level = inventory_level
        self.stockout_events_total = stockout_events_total
        self._lock = Lock()
        self.inventory = initial_inventory or {
            "sku-red-shirt": 120,
            "sku-blue-jeans": 95,
            "sku-sneakers": 60,
        }
        for sku, level in self.inventory.items():
            self.inventory_level.labels(sku=sku).set(level)

    def reserve(self, sku_id: str, quantity: int = 1) -> bool:
        with self._lock:
            current_level = self.inventory.get(sku_id, 0)
            if current_level < quantity:
                self.stockout_events_total.labels(sku=sku_id).inc()
                self.inventory_level.labels(sku=sku_id).set(current_level)
                return False

            updated_level = current_level - quantity
            self.inventory[sku_id] = updated_level
            self.inventory_level.labels(sku=sku_id).set(updated_level)
            if updated_level == 0:
                self.stockout_events_total.labels(sku=sku_id).inc()
            return True

    def restock(self, sku_id: str, quantity: int) -> int:
        with self._lock:
            updated_level = self.inventory.get(sku_id, 0) + max(0, quantity)
            self.inventory[sku_id] = updated_level
            self.inventory_level.labels(sku=sku_id).set(updated_level)
            return updated_level

    def simulate_stockout(self, sku_id: str) -> None:
        with self._lock:
            self.inventory[sku_id] = 0
            self.inventory_level.labels(sku=sku_id).set(0)
            self.stockout_events_total.labels(sku=sku_id).inc()

    def get_level(self, sku_id: str) -> int:
        with self._lock:
            return self.inventory.get(sku_id, 0)
