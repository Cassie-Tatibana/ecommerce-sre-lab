# Runbook: HighOrderLatency

## Summary
This alert fires when simulated order processing latency p95 stays above 30 seconds for more than two minutes.

## Impact
Checkout-like order flow becomes visibly slower and the platform may accumulate a backlog of orders waiting for fulfillment.

## Diagnosis Steps
1. Confirm the alert in Prometheus or Grafana.
2. Review `ecommerce_order_processing_seconds` p50 and p95 trends.
3. Check whether a traffic spike has been injected through `/chaos/simulate_traffic_spike`.
4. Inspect `/state` to verify current traffic multiplier and order state counts.

## Remediation
1. Reset traffic to normal by calling `/chaos/reset_traffic`.
2. Validate exporter health on `/healthz` and confirm metrics are still advancing.
3. If latency remains elevated, restart the exporter container and watch the histogram recover.

## Escalation
Escalate if p95 latency remains above threshold for more than 15 minutes after traffic normalization.
