# ecommerce-sre-lab

A self-contained SRE observability system for a simulated e-commerce supply chain. It combines metrics, dashboards, alerting, runbooks, chaos drills, CI, and smoke testing into a runnable platform for operations practice and service reliability experiments.

[![CI](https://github.com/Cassie-Tatibana/ecommerce-sre-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/Cassie-Tatibana/ecommerce-sre-lab/actions/workflows/ci.yml)
[\u4e2d\u6587 README](README.zh-CN.md)

## Why This Project

- Provides a runnable reliability playground for order flow, inventory health, and fulfillment operations.
- Bundles Prometheus, Grafana, alerting, runbooks, and chaos controls into one local stack.
- Uses simulated events and in-memory state so the system is easy to operate without external APIs or databases.
- Supports incident drills such as stockouts, traffic spikes, and fulfillment outages with observable recovery paths.

## Architecture

```text
+------------------+        scrape         +----------------+
| Python Exporter  | --------------------> | Prometheus     |
| + Simulators     |                       | + Alert Rules  |
+------------------+                       +----------------+
         |                                           |
         | REST chaos endpoints                      | datasource
         v                                           v
+------------------+                        +----------------+
| In-Memory State  |                        | Grafana        |
| Orders/Stock/Ful |                        | Dashboard      |
+------------------+                        +----------------+
```

### Component Walkthrough

- `simulator/`: Generates order, inventory, and fulfillment events in memory.
- `exporter/`: Exposes Prometheus metrics and chaos endpoints such as stockout, traffic spike, fulfillment outage, and restock.
- `prometheus/`: Scrapes the exporter and evaluates alerting rules.
- `grafana/`: Auto-provisions the Prometheus datasource and an operations dashboard.
- `runbooks/`: Stores alert-linked investigation and remediation guides in English.
- `tests/` and `smoke/`: Cover unit-level metrics behavior plus a Grafana availability smoke path.

## Quick Start

```bash
docker compose up --build
```

Services:
- Exporter: [http://localhost:8000/metrics](http://localhost:8000/metrics)
- Prometheus: [http://localhost:9090](http://localhost:9090)
- Grafana admin: [http://localhost:3000](http://localhost:3000) (`admin` / `ecommerce-admin`)
- Dashboard: [http://localhost:3000/d/ecommerce-overview](http://localhost:3000/d/ecommerce-overview) (anonymous viewer access enabled)
- State snapshot: [http://localhost:8000/state](http://localhost:8000/state)

Chaos endpoints:

```bash
curl -X POST http://localhost:8000/chaos/simulate_stockout \
  -H 'Content-Type: application/json' \
  -d '{"sku_id": "sku-red-shirt"}'

curl -X POST http://localhost:8000/chaos/simulate_traffic_spike \
  -H 'Content-Type: application/json' \
  -d '{"multiplier": 10}'

curl -X POST http://localhost:8000/chaos/simulate_fulfillment_outage

curl -X POST http://localhost:8000/chaos/restock \
  -H 'Content-Type: application/json' \
  -d '{"sku_id": "sku-red-shirt", "quantity": 50}'

curl -X POST http://localhost:8000/chaos/clear_fulfillment_outage

curl -X POST http://localhost:8000/chaos/reset_traffic
```

## Metrics

| Metric | Type | Description |
| --- | --- | --- |
| `ecommerce_orders_total{status}` | Counter | Orders by lifecycle state |
| `ecommerce_order_processing_seconds` | Histogram | Order processing duration |
| `ecommerce_inventory_level{sku}` | Gauge | Current inventory level per SKU |
| `ecommerce_stockout_events_total{sku}` | Counter | Stockout event count per SKU |
| `ecommerce_fulfillment_delay_seconds` | Histogram | Fulfillment delay duration |
| `ecommerce_fulfillment_failed_total` | Counter | Fulfillment failure count |

## Alerting Rules

- `HighOrderLatency`: Order processing p95 above 30 seconds for 2 minutes.
- `LowInventoryWarning`: Any SKU inventory below 10 for 5 minutes.
- `FulfillmentOutage`: Fulfillment failure rate above 50 percent for 1 minute.

## Chaos Scenarios

- `simulate_stockout`: Forces an SKU inventory level to zero to validate inventory alerting.
- `simulate_traffic_spike`: Increases synthetic order throughput to stress latency SLOs.
- `simulate_fulfillment_outage`: Forces shipping failures and raises outage indicators.
- `restock`: Restores inventory to support alert recovery drills and runbook validation.

## Runbooks

- [HighOrderLatency](runbooks/high_order_latency.md)
- [LowInventoryWarning](runbooks/inventory_stockout.md)
- [FulfillmentOutage](runbooks/fulfillment_delay.md)

## SLOs

- Order processing latency p95 < 30 seconds.
- Inventory warning condition resolved within 5 minutes.
- Fulfillment success rate > 99 percent.

## CI And Smoke Tests

- GitHub Actions runs Python unit tests and `docker compose build` on every push and pull request.
- A dedicated smoke job boots the full stack and uses Playwright to verify Grafana is reachable and the provisioned dashboard loads.
- Failures can be investigated through compose logs and linked runbooks.

## Testing

```bash
pip install -r requirements.txt
pytest tests/
npm install
docker compose up -d --build
npx playwright install chromium
npm run smoke
docker compose down -v
docker compose build
```

## Tech Stack

Python 3.11 · Prometheus · Grafana · Docker Compose · GitHub Actions · pytest · Playwright
