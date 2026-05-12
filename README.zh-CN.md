# ecommerce-sre-lab

一个面向电商供应链场景的自包含 SRE 可观测性系统。它把指标采集、看板、告警、Runbook、故障演练、CI 和 smoke tests 组合成一个可运行的平台，用于可靠性演练与系统运维实践。

[![CI](https://github.com/Cassie-Tatibana/ecommerce-sre-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/Cassie-Tatibana/ecommerce-sre-lab/actions/workflows/ci.yml)
[English README](README.md)

## 项目价值

- 提供一个可直接运行的可靠性实验环境，覆盖订单、库存、履约三个核心链路。
- 将 Prometheus、Grafana、告警规则、Runbook 和 chaos 控制整合进同一套本地栈。
- 使用模拟事件和内存状态，不依赖外部 API 或数据库，启动成本低。
- 支持缺货、流量洪峰、履约故障等演练场景，并能观察恢复过程。

## 架构

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

### 组件说明

- `simulator/`：生成订单、库存、履约事件并维护内存状态。
- `exporter/`：暴露 Prometheus 指标与 chaos API。
- `prometheus/`：负责抓取 exporter 并评估告警规则。
- `grafana/`：自动加载数据源与默认看板。
- `runbooks/`：存放与告警对应的排障与恢复文档。
- `tests/` 与 `smoke/`：覆盖单元测试和 Grafana 可访问性 smoke test。

## 快速开始

```bash
docker compose up --build
```

服务地址：

- Exporter 指标：`http://localhost:8000/metrics`
- Prometheus：`http://localhost:9090`
- Grafana 管理入口：`http://localhost:3000`（`admin` / `ecommerce-admin`）
- Dashboard：`http://localhost:3000/d/ecommerce-overview`（已开启匿名只读访问）
- 状态快照：`http://localhost:8000/state`

## Chaos 接口

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
```

## 关键指标

- `ecommerce_orders_total{status}`
- `ecommerce_order_processing_seconds`
- `ecommerce_inventory_level{sku}`
- `ecommerce_stockout_events_total{sku}`
- `ecommerce_fulfillment_delay_seconds`
- `ecommerce_fulfillment_failed_total`

## 告警规则

- `HighOrderLatency`：订单处理 P95 高于 30 秒并持续 2 分钟。
- `LowInventoryWarning`：任意 SKU 库存低于 10 并持续 5 分钟。
- `FulfillmentOutage`：履约失败率高于 50% 并持续 1 分钟。

## 测试

```bash
pip install -r requirements.txt
pytest tests/
npm install
docker compose up -d --build
npx playwright install chromium
npm run smoke
docker compose down -v
```

## 技术栈

Python 3.11 · Prometheus · Grafana · Docker Compose · GitHub Actions · pytest · Playwright
