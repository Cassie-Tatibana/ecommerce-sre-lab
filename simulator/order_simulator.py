from __future__ import annotations

import random
from dataclasses import dataclass
from threading import Lock

from prometheus_client import Counter, Histogram


@dataclass(frozen=True)
class OrderEvent:
    sku: str
    status: str
    processing_seconds: float


class OrderSimulator:
    def __init__(
        self,
        orders_total: Counter,
        order_processing_seconds: Histogram,
        skus: list[str] | None = None,
        seed: int | None = None,
    ) -> None:
        self.orders_total = orders_total
        self.order_processing_seconds = order_processing_seconds
        self.skus = skus or ["sku-red-shirt", "sku-blue-jeans", "sku-sneakers"]
        self.random = random.Random(seed)
        self._traffic_multiplier = 1
        self._lock = Lock()
        self.order_state_counts = {
            "pending": 0,
            "processing": 0,
            "completed": 0,
            "failed": 0,
        }

    def tick(self) -> list[OrderEvent]:
        events: list[OrderEvent] = []
        with self._lock:
            multiplier = max(1, self._traffic_multiplier)

        for _ in range(multiplier):
            sku = self.random.choice(self.skus)
            processing_seconds = round(self.random.uniform(5.0, 45.0), 2)
            status = "completed" if self.random.random() >= 0.15 else "failed"
            self._record_status("pending")
            self._record_status("processing")
            self._record_status(status)
            self.order_processing_seconds.observe(processing_seconds)
            events.append(
                OrderEvent(
                    sku=sku,
                    status=status,
                    processing_seconds=processing_seconds,
                )
            )
        return events

    def simulate_traffic_spike(self, multiplier: int) -> None:
        with self._lock:
            self._traffic_multiplier = max(1, multiplier)

    def current_traffic_multiplier(self) -> int:
        with self._lock:
            return self._traffic_multiplier

    def reset_traffic(self) -> None:
        with self._lock:
            self._traffic_multiplier = 1

    def _record_status(self, status: str) -> None:
        self.order_state_counts[status] += 1
        self.orders_total.labels(status=status).inc()
