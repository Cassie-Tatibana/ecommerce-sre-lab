# Runbook: FulfillmentOutage

## Summary
This alert fires when simulated fulfillment failures exceed 50 percent of completed and failed orders for more than one minute.

## Impact
Orders appear processed but cannot be shipped reliably, reducing end-to-end order success rate.

## Diagnosis Steps
1. Review the failure-rate stat in Grafana.
2. Check `ecommerce_fulfillment_failed_total` and fulfillment delay histograms.
3. Inspect `/state` to confirm whether fulfillment outage mode is active.
4. Verify whether `/chaos/simulate_fulfillment_outage` was triggered recently.

## Remediation
1. Clear outage mode with `/chaos/clear_fulfillment_outage`.
2. Confirm new orders are being fulfilled successfully.
3. Continue monitoring for at least two alert windows to ensure recovery is stable.

## Escalation
Escalate if failures remain above threshold after outage mode is cleared or if exporter health is degraded.
