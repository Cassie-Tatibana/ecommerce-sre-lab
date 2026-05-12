from __future__ import annotations

import random
from threading import Lock

from prometheus_client import Counter, Histogram


class FulfillmentSimulator:
    def __init__(
        self,
        fulfillment_delay_seconds: Histogram,
        fulfillment_failed_total: Counter,
        seed: int | None = None,
    ) -> None:
        self.fulfillment_delay_seconds = fulfillment_delay_seconds
        self.fulfillment_failed_total = fulfillment_failed_total
        self.random = random.Random(seed)
        self._outage = False
        self._lock = Lock()

    def fulfill(self, order_status: str) -> dict[str, float | bool]:
        with self._lock:
            outage = self._outage

        failed = outage or order_status == "failed"
        delay_seconds = round(self.random.uniform(8.0, 90.0), 2)
        self.fulfillment_delay_seconds.observe(delay_seconds)
        if failed:
            self.fulfillment_failed_total.inc()
        return {"delay_seconds": delay_seconds, "failed": failed}

    def simulate_fulfillment_outage(self) -> None:
        with self._lock:
            self._outage = True

    def clear_fulfillment_outage(self) -> None:
        with self._lock:
            self._outage = False

    def outage_active(self) -> bool:
        with self._lock:
            return self._outage
