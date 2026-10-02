# Cost: published meters and measured usage only

Current native-template measurement and project usage are in
[the final quality gate](../EVIDENCE.md) and
[its cost capture](../quality-evidence/final-measured-cost.json).
The tables below preserve earlier revisions; they are not the final native run.

Do not budget this stack using an invented monthly figure or multiply its limits
by published RAM prices. Grouped workers still consume individual interpreter
memory. Native S3 removes a resident object-store process but incurs upload egress.

[Railway container prices](https://docs.railway.com/pricing/plans), captured in
[evidence/pricing.md](evidence/pricing.md), list RAM $0.000231/GB-minute,
CPU $0.000463/vCPU-minute, service egress $0.05/GB and volume storage
$0.000003472222222/GB-minute. [Bucket billing](https://docs.railway.com/storage-buckets/billing)
lists $0.015/GB-month, free bucket downloads/API operations and service-upload
egress charges. Bucket billing rounds aggregate fractional GB-month usage upward.
Plan subscriptions/included usage are separate from incremental project usage.
Do not attribute an existing workspace subscription to this test stack.

For integrated resource meters R (GB-minutes RAM), C (vCPU-minutes),
V (GB-minutes billable volume storage), E (GB service egress), and B (billable
bucket GB-month), the published-rate model is:

```text
USD = 0.000231 R + 0.000463 C + 0.000003472222222 V + 0.05 E + 0.015 B
```

Raw measurements are collected with measure-test.py, exclusively from the named
throwaway project's service IDs. Each service's command/exit/CLI data is retained
under evidence/. summarize-metrics.py integrates raw memory and CPU observations
with the trapezoidal rule. The summary is a sampled compute estimate for its exact
window, not invoice reconciliation, unobserved peaks or a monthly forecast.
Use the saved `*-usage.json` provider usage response for billing reconciliation;
provider reporting may lag. Disk used and volume capacity are different meters.
NETWORK_TX_GB is retained raw, not silently interpreted as a cumulative counter.

A useful comparison requires the same measured idle, ingestion/query, retention
and backlog-recovery workload for every candidate. Failed/bootstrapping containers
are not an idle operating baseline. This package makes no competitor savings claim.
See VALIDATION.md and evidence/ for which operating phases were actually measured.

## Observed test windows

All times below are UTC on 2026-10-01. Values are rounded from the linked raw
summaries and include the test SDK when it ran. They are sampled RAM+CPU costs
only: storage, buckets, egress, subscription and reporting delays are separate.

| Phase | Window | Sampled compute USD | Evidence |
|---|---|---:|---|
| Cold bootstrap | 18:29:00–18:37:37 | 0.014227 | `cold4-bootstrap-summary.json` |
| Idle, healthy named pipelines | 18:38:00–18:42:35 | 0.011548 | `cold4-idle-summary.json` |
| SDK workload, paused queues and recovery | 18:50:00–18:58:11 | 0.015031 | `backlog4-recovery-summary.json` |
| Query load during worker replacement | 19:01:35–19:03:38 | 0.008058 | `query-load-summary.json` |

The last window executed six repetitions of the recorded 41-request verification
burst (246 successful requests), with the same 20 errors, 20 logs and linked
traces checked each time. Worker replacement was also running: this is not an
isolated steady-state query benchmark. Command windows and each successful
burst are in `query-load-window.json` and `query-load-0.txt` through `-5.txt`.
The earlier short query window returned no samples; its numerical zero must
not be interpreted as free CPU/RAM.

Idle aggregate RAM was 10.564886528–10.879778816 GB, summing only simultaneous
observations containing all 14 user-stack services and excluding the test SDK.
See `idle-total-memory.json`. Sentry and Snuba consumer groups dominate the
observed memory: their per-service idle sample peaks were 3.748368384 GB and
3.251695616 GB (`cold4-idle-summary.json`). These are observations for this
configuration, not resource limits or a proven minimum.

Kafka apparent bytes were 1,763,973,554 while paused and 1,764,583,364 after
recovery (`backlog4-log-bytes-paused.txt`, `backlog4-log-bytes-recovered.txt`).
Those are total filesystem bytes reported by `du -sb`, including pre-existing
segments and Kafka overhead, not serialized event sizes or billable allocation.
The direct-topic lag fell from 20 on errors/transactions/EAP to zero; see the
paired `backlog4-lag-*.txt` captures. Empty topics can report `-` offsets.

`test1-final-usage.json`, `test3-final-usage.json` and `test4-final-usage.json`
retain provider usage snapshots. Test 2 was an aborted provisioning attempt;
no complete reconciled invoice for all trials is claimed. Final usage reporting
can lag deletion. The resumed final audit adds an explicit measured-idle 30-day compute extrapolation in ../EVIDENCE.md and evidence/monthly-cost.json; it is not a complete monthly bill. No competitor savings claim is made.
The published rates above were rechecked against Railway's pricing page during
this resumed run.

## Review-fix measured profile

See [complete calculation](../fix-evidence/compute-scenarios.json) and raw
`baseline-steady-metrics-*` / `ablation-steady-metrics-*` captures. Each window
contains equally spaced provider samples; arithmetic means are labeled explicitly.
The full stack mean RAM changed from 10.858278229333333 GB to 8.796489045333333 GB;
mean CPU changed from 0.2403985777777778 to 0.19390657777777778 vCPU. Repeating
those short measured means for `30*24*60` minutes at the verified published
minute rates yields $113.16528629944321 and $91.6603652872704 compute respectively.
Excludes storage, egress, workload growth and plan fees; not an invoice, minimum,
capacity benchmark or competitor comparison. Background activity and startup/cache
history differ. The paired consumer-group means are separately recorded and the
named workflow/recovery checks passed after removal of six optional commands.
