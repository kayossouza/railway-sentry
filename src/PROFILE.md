# Worker profile audit

Pinned upstream: self-hosted 26.9.0, source SHA in pipeline.json. This profile
retains error symbolication/attachments, outcome accounting, group attributes,
transactions, span processing and EAP storage. These have separate data/repair
responsibilities; consolidating interpreters into a process is not a demonstrated
safe optimization.

Validated ablation: legacy ingest-metrics, metrics_raw storage and subscriptions; all four subscription scheduler/executors. They implement
legacy metrics and metric alert subscriptions, rather than the named error body,
structured log and parent/child span storage/query workflow. Removing them also
requires disabling metric alert UI and explicitly dropping metric alert support.
Fresh named-workflow, maintenance replacement and missing/out-of-range-offset
checks passed in bounty-test-sentry-2. The delivered profile removes those six
commands. Raw meters and qualified sample means are in ../fix-evidence.
No minimum-resource claim or competitor cost comparison is made.

Primary errors, transactions and EAP indexers now reset to earliest surviving
offset, matching ingest/outcomes workers and preventing first-assignment loss of
prequeued records. Earliest cannot recover records already deleted by Kafka.
The live missing-offset and out-of-range replay test queried exactly one parent
and child span for each receipt. This bounded test is not an unqualified replay
guarantee for arbitrary workloads or outages beyond queue retention. Readiness before ingestion prevents the ordinary
initial-assignment window; it does not replace lag monitoring.
