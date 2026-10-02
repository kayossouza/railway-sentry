# Operational controls

## Retention and queue recovery

Kafka's configured three-hour retention is a queue age policy, not guaranteed
recovery for seven days. Segment rolls/deletion sweeps influence the actual
horizon. Indexed event retention remains seven days. This default tolerates only
short outages; no longer outage/disk capacity claim is made. Monitor consumer lag
and broker disk on the cadence needed for your operational response. Alert while
lag is growing or retained offsets approach the consumer's committed offset;
resolve before records leave the retained range. Never silently reset an offset:
record the missing range, take backups, use earliest surviving data, and verify
every known receipt. Out-of-range recovery cannot recreate deleted records.

Raw nodestore writes now persist `expires-at` from the original TTL, with the
configured retention as fallback. Rewrites preserve existing metadata. Backup and
restore preserve metadata. Legacy objects lacking metadata are retained until an
operator can establish their age from authoritative event records; no original
age is invented. This conservative migration can retain old legacy blobs longer.
Cleanup only visits nodestore/, preserving Relay identity and filestore. Relational
cleanup and ClickHouse TTL are independent; raw expiry is not proof of either.

## Cleanup and progress monitoring

Cleanup has a bounded run, retry backoff and atomic `/tmp/cleanup-status.json`
status. Transient failures do not terminate taskworker/scheduler. Alert on a
non-null last_error or missing/old last_completed relative to the configured daily
schedule plus the bounded run; inspect storage and relational errors, fix forward,
and verify a subsequent successful run. Invalid retention aborts startup.

Worker /ready is current heartbeat freshness and process state. Deployment-only
Railway readiness is not continuous monitoring. Scheduler and accepted-outcomes
lack upstream heartbeat flags: prove scheduler activity by a scheduled task
completing and monitor accepted_outcomes Kafka committed-offset progress against
its input. Do not interpret a live PID as functional health. No synthetic progress
probe can claim an empty queue is processing work.

## Mail and password reset

Optional SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_TLS and SMTP_FROM
are optional variables added on Web. When enabling mail, add matching
`${{web.SMTP_*}}` references on sentry-consumers and sentry-tasks.
Empty SMTP_HOST keeps dummy email. Port/TLS defaults are configuration choices,
not proof an arbitrary provider accepts them. Use a provider-authorized sender.
No resident SMTP service is deployed. Verify invitation and password-reset
messages with your configured provider before depending on mail.

For a no-email reset, an authenticated Railway operator uses SSH to Sentry Web:
`railway ssh --service web -- /docker-entrypoint.sh django changepassword EMAIL`.
Enter the new password interactively. This uses Django's password hashing and
validation; it does not expose the password in CLI arguments or logs. Redeploying
with a new ADMIN_PASSWORD never resets an existing user.

## Ingestion and cost

Only gateway port 8080 has a public domain. Port 8081 is private SDK ingress;
Port8080 denies ingestion regardless of Host or forwarded headers. Public UI remains reachable. Do not add public TCP/domain routing to
8081. Public browser/mobile ingestion is outside this private-only profile. Configure Sentry project quotas, inbound filters, SDK sampling and
Railway usage/spend alerts according to measured workload. No arbitrary rate cap
or invented cost is imposed here.

## Regions, scope and licensing

The native personal template uses Railway's default service region and two
buckets fixed in AMS; the final test used EU West/AMS. The development IaC
regions.json is not a deployment input for template users. Native S3 uses public TLS; uploads incur
service egress. Never apply a region change as an in-place storage migration.
Feedback UI is disabled because its ingest worker is absent. Upstream licenses
remain preserved. Internal self-hosting is the documented scope; authoritative
licensing guidance remains required before future monetized distribution.
