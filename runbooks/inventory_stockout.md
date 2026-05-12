# Runbook: LowInventoryWarning

## Summary
This alert fires when any simulated SKU stays below an inventory level of 10 for more than five minutes.

## Impact
New orders for the affected SKU are more likely to fail and can increase customer-facing fulfillment failure.

## Diagnosis Steps
1. Identify the impacted SKU from `ecommerce_inventory_level`.
2. Review `ecommerce_stockout_events_total` for repeated depletion events.
3. Inspect `/state` to see the current inventory snapshot.
4. Confirm whether a manual stockout was injected through `/chaos/simulate_stockout`.

## Remediation
1. Restock the SKU by calling `/chaos/restock` with a safe quantity for the impacted SKU.
2. If this is a drill, document the exact stockout injection time for later review.
3. Watch inventory gauges until the affected SKU returns above the warning threshold.

## Escalation
Escalate if multiple SKUs remain below threshold or fulfillment failure begins to climb.
