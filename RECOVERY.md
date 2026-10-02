# Backup, restart and recovery

Use a maintenance window. This stack is single-node and Railway volume services
cannot overlap old/new replicas. The final quality gate verifies restart and
redeploy persistence, not a new backup/restore drill. Historical restore drills are separate from this revision’s acceptance run;
see [VALIDATION](VALIDATION.md) for the tested scope.
Production operators must use their own explicit project guards and verify
backups with a restore drill before relying on them.

## Coordinated backup

1. Block SDK ingestion at Gateway and stop the SDK load generator.
2. Let Sentry/Snuba consumers drain; record Kafka consumer lag using
   `kafka-consumer-groups --bootstrap-server localhost:29092 --all-groups --describe`
   inside Kafka. Record the error event ID, log marker and trace ID to recover.
3. Stop the scheduler, taskworker and consumer groups after lag is drained.
4. Export PostgreSQL with the image's `pg_dump -U postgres -d postgres -Fc`;
   preserve roles as needed with `pg_dumpall --globals-only`. Use private runtime
   credentials and keep exported data encrypted, never in a public repo.
5. Stop stateful services and take consistent Railway volume backups for
   PostgreSQL, ClickHouse, Kafka, Valkey and Taskbroker. Record all backup
   identifiers, timestamp, image digests and configuration checksum.
6. Independently copy every object and its metadata from Nodestore and Filestore
   into protected backup storage. Railway has no native bucket snapshot/versioning.
   Preserve `relay/public.json` and the generated `RELAY_KEY_SEED` securely.
   Relay derives the same private identity from that seed; it has no volume.
   Hash each backup/object manifest; preserve key names, encodings and compression.
7. Resume stores, query API, Web, worker groups and Gateway in the documented
   dependency order. Repeat all three queries before reopening ingestion.

Do not rely on a PostgreSQL-only backup: error bodies live in Nodestore,
attachments/sourcemaps in Filestore, queryable logs/spans in ClickHouse, pending
messages in Kafka/Valkey/Taskbroker, and the ingestion trust identity in Relay.

## Restore drill

Restore into an empty throwaway project/environment with the same pinned images
and compatible configuration. Restore all volumes and object buckets while the
applications are stopped. Update runtime bucket references to the restored buckets.
Restore Postgres's logical dump if using a logical rather than physical snapshot.
Do not mix a new Relay keypair with an old public identity.

Start stores, Relay, Snuba, Web, consumers/tasks and Gateway. Startup migrations
must be idempotent against the restored schema; do not delete bootstrap evidence
to hide errors. Query the exact saved event ID, structured log marker and trace ID,
inspect UI detail/attributes, then send a fresh SDK error/log/trace and verify them.
A restorable disk alone is not proof that the application data is recoverable.

## Upgrade and rollback

Stop ingestion, drain queues, and take the coordinated backup above. Review the
new upstream compatibility matrix before updating every Sentry-family image and
associated config together. Deploy during maintenance, query all three telemetry
types and verify admin authentication and cleanup. Keep previous pins and backups.

Consumer deployments intentionally omit Railway deployment healthchecks to avoid
Kafka partition-sharing deadlock during replacement. Internal heartbeat supervision
remains enabled. Wait for service and gateway recovery, then verify stored and fresh
data; do not add a deployment healthcheck without testing overlapping consumers.

If a rollback is required after a schema migration, stop ingestion and restore
**all compatible stores and object data** from the same backup point before
redeploying the previous pins. Reverting container images does not reverse schema
migrations. A compatible forward fix may preserve more data than restoring an
older snapshot; select it only with evidence of compatibility.

Never delete production volumes/buckets to force an upgrade through. Keep Relay's
generated seed and all authoritative generated secrets stable across
redeploys. Initial admin creation never overwrites a user-changed password.
