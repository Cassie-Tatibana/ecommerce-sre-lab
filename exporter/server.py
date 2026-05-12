from __future__ import annotations

import json
import os
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from prometheus_client import generate_latest

from exporter.metrics import build_metrics
from simulator.fulfillment_simulator import FulfillmentSimulator
from simulator.inventory_simulator import InventorySimulator
from simulator.order_simulator import OrderSimulator


class SimulationRuntime:
    def __init__(self) -> None:
        metric_objects = build_metrics()
        self.registry = metric_objects["registry"]
        self.order_simulator = OrderSimulator(
            orders_total=metric_objects["orders_total"],
            order_processing_seconds=metric_objects["order_processing_seconds"],
        )
        self.inventory_simulator = InventorySimulator(
            inventory_level=metric_objects["inventory_level"],
            stockout_events_total=metric_objects["stockout_events_total"],
        )
        self.fulfillment_simulator = FulfillmentSimulator(
            fulfillment_delay_seconds=metric_objects["fulfillment_delay_seconds"],
            fulfillment_failed_total=metric_objects["fulfillment_failed_total"],
        )
        self.interval_seconds = float(os.getenv("SIMULATION_INTERVAL_SECONDS", "2"))
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)

    def start(self) -> None:
        if not self._thread.is_alive():
            self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread.is_alive():
            self._thread.join(timeout=2)

    def inject(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        if action == "simulate_stockout":
            sku_id = payload.get("sku_id", "sku-red-shirt")
            self.inventory_simulator.simulate_stockout(sku_id)
            return {"ok": True, "action": action, "sku_id": sku_id}
        if action == "restock":
            sku_id = payload.get("sku_id", "sku-red-shirt")
            quantity = int(payload.get("quantity", 50))
            level = self.inventory_simulator.restock(sku_id, quantity)
            return {
                "ok": True,
                "action": action,
                "sku_id": sku_id,
                "quantity": quantity,
                "inventory_level": level,
            }
        if action == "simulate_traffic_spike":
            multiplier = int(payload.get("multiplier", 5))
            self.order_simulator.simulate_traffic_spike(multiplier)
            return {"ok": True, "action": action, "multiplier": multiplier}
        if action == "simulate_fulfillment_outage":
            self.fulfillment_simulator.simulate_fulfillment_outage()
            return {"ok": True, "action": action}
        if action == "clear_fulfillment_outage":
            self.fulfillment_simulator.clear_fulfillment_outage()
            return {"ok": True, "action": action}
        if action == "reset_traffic":
            self.order_simulator.reset_traffic()
            return {"ok": True, "action": action}
        return {"ok": False, "error": f"unsupported action: {action}"}

    def snapshot(self) -> dict[str, Any]:
        return {
            "traffic_multiplier": self.order_simulator.current_traffic_multiplier(),
            "inventory": dict(self.inventory_simulator.inventory),
            "fulfillment_outage": self.fulfillment_simulator.outage_active(),
            "order_state_counts": dict(self.order_simulator.order_state_counts),
        }

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            for order_event in self.order_simulator.tick():
                inventory_ok = self.inventory_simulator.reserve(order_event.sku)
                fulfillment_status = order_event.status if inventory_ok else "failed"
                self.fulfillment_simulator.fulfill(fulfillment_status)
            self._stop_event.wait(self.interval_seconds)


RUNTIME = SimulationRuntime()


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/healthz":
            self._send_json(HTTPStatus.OK, {"status": "ok"})
            return
        if self.path == "/state":
            self._send_json(HTTPStatus.OK, RUNTIME.snapshot())
            return
        if self.path == "/metrics":
            payload = generate_latest(RUNTIME.registry)
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})

    def do_POST(self) -> None:
        if not self.path.startswith("/chaos/"):
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length) if content_length else b"{}"
        payload = json.loads(raw_body.decode("utf-8") or "{}")
        action = self.path.removeprefix("/chaos/")
        result = RUNTIME.inject(action, payload)
        status = HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST
        self._send_json(status, result)

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        raw_payload = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw_payload)))
        self.end_headers()
        self.wfile.write(raw_payload)


def main() -> None:
    port = int(os.getenv("EXPORTER_PORT", "8000"))
    RUNTIME.start()
    server = ThreadingHTTPServer(("0.0.0.0", port), RequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        RUNTIME.stop()
        server.server_close()


if __name__ == "__main__":
    main()
