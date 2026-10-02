[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/self-hosted-sentry-errors-logs-and-trace?utm_source=github-readme&utm_medium=referral&utm_campaign=sentry-launch)

[Documentation](https://railway-sentry-docs.vercel.app) · [Source](https://github.com/kayossouza/railway-sentry)

# Deploy and Host Self-Hosted Sentry: Errors, Logs and Traces

Sentry 26.9.0 for errors, structured logs and linked traces from your applications
in the same Railway environment. Fair Source (FSL-1.1-Apache-2.0).
Unofficial community template, not affiliated with or endorsed by Sentry.

## One-click deploy

Use an existing Hobby or Pro workspace; Free/Trial RAM limits cannot run this stack.
Choose your workspace (or an empty existing project) and deploy. Leave every
variable at its default.
Wait for **gateway** to become healthy, then open its public URL.
No CLI, registry login, migration command or secret generator is needed.
Fresh deployment, telemetry, persistence and all service restarts passed in the
author's workspace. [Test record](VALIDATION.md).

## About Hosting Sentry

Sentry UI, private ingestion, automatic bootstrap, per-install passwords,
persistent databases and separate object-storage buckets. Errors appear in
**Issues**, structured logs in **Logs**, and parent/child spans in **Traces**.
The pinned runtime needs PostgreSQL, Valkey, ClickHouse, Kafka, Memcached,
Symbolicator, Taskbroker, Relay, Snuba, processing workers and a gateway.
Only the gateway exposes public HTTP; ingestion is private.

This profile excludes replay, profiling, feedback, uptime, cron monitoring,
AI features and legacy metrics. It is single-node. Indexed retention is seven
days; Kafka queue age is three hours, so a prolonged outage can lose queued data.
Email is disabled by default; optional SMTP setup is in [operations](OPERATIONS.md).

## Why Deploy Sentry on Railway

Keep application errors, logs and linked traces in your own Railway workspace.
The template handles bootstrap, networking and generated credentials.

## Common Use Cases

- Investigate errors in your own applications.
- Connect structured logs to application traces.
- Monitor services sharing a Railway environment.

## Dependencies for Sentry

The template provisions all fourteen services, five persistent volumes and two
object-storage buckets. You need a Railway Hobby or Pro workspace and an
application using a Sentry SDK in the same environment.

## First login

In Railway, open **web → Variables** and copy `ADMIN_EMAIL` and `ADMIN_PASSWORD`.
Use them on the gateway login page. If it says **No Organization Access**, open
`https://YOUR-GATEWAY/organizations/new/`. Create an organization and a Python
project. Installation configuration is automatic; usage statistics are off by
default. Keep the generated password; redeploying preserves the user.

## Send data

In Sentry, open **Settings → Projects → your project → Client Keys (DSN)**.
Copy the DSN's public key and project ID. In your application's Railway
variables, set `SENTRY_DSN` to the following, keeping the reference intact:

```text
http://KEY@${{gateway.RAILWAY_PRIVATE_DOMAIN}}:8081/PROJECT_ID
```

Install `sentry-sdk==2.39.0` in your Python application's dependencies, then run
this inside its Railway service, in the same environment as Sentry:

```python
import os
import sentry_sdk
sentry_sdk.init(dsn=os.environ["SENTRY_DSN"],
                traces_sample_rate=1.0, enable_logs=True)
with sentry_sdk.start_transaction(name="railway-example", op="task"):
    with sentry_sdk.start_span(op="work", description="child span"):
        sentry_sdk.logger.info("Railway structured log {name}", name="example")
        try:
            raise RuntimeError("Railway error example")
        except RuntimeError:
            sentry_sdk.capture_exception()
sentry_sdk.flush(timeout=30)
```

No application yet? Add a GitHub service from `kayossouza/railway-sentry`,
set its root directory to `/sdk`, add the `SENTRY_DSN` above and deploy.
It runs this exact example; delete the sample service afterwards.

Confirm the error in Issues, the log in Logs and both spans in Traces.
For a durability check, use Railway's Redeploy and Restart actions on each service,
wait for the service and gateway to recover, refresh Sentry, and confirm the saved
data still appears. Redeploy the sample application to verify fresh data after recovery.
A laptop running `railway run` cannot reach Railway private networking.
The full sampling rate above is for this check; tune it for your workload.

## Cost

The final healthy test window measured **9.313 GB RAM / 0.170 vCPU** across
all fourteen runtime services. Repeating that window for thirty days gives
**$96.34 compute** at [Railway's minute rates](https://docs.railway.com/pricing/plans).
Storage, egress and growth change the total; your plan's minimum and included credit
also apply. This is a measured-window extrapolation, not a monthly invoice or capacity guarantee.
[Window, raw samples and calculation](VALIDATION.md#cost).

## Troubleshooting

1. **Gateway unavailable:** check Railway deployment logs for the failed service.
   Initial boot waits for database migrations and processing workers; wait for
   gateway readiness before logging in. Do not run migrations manually.
2. **No telemetry:** check the DSN key/project ID, private port `8081`, and that
   your application runs in the same Railway environment. Check Issues, Logs
   and Traces separately; a successful HTTP upload alone proves no storage.
3. **Cannot log in:** use the generated web credentials. Changing
   `ADMIN_PASSWORD` does not reset an existing user's password; follow the
   [operator reset procedure](OPERATIONS.md#mail-and-password-reset).

## Upgrade

Back up the persistent volumes **and both buckets** before a version change.
Test a coordinated pinned release in a throwaway project; do not update an
individual image to `latest`. Redeploy the services and verify an existing
error, log and trace plus a new sample. On failure, restore the matching
backups and compatible release: schema downgrades are not automatic.
[Recovery](RECOVERY.md) · [Licenses](runtime/upstream/LICENSE.md) · [Evidence](VALIDATION.md).

## License and intended use

Sentry is Fair Source (FSL-1.1-Apache-2.0). Copyright Functional Software, Inc. dba Sentry.
Use this template for monitoring your own applications, not for offering Sentry
as a hosted service to third parties. See [Sentry licensing](https://open.sentry.io/licensing/)
and the [upstream LICENSE.md](https://github.com/getsentry/sentry/blob/26.9.0/LICENSE.md).
The runtime uses official unmodified images and preserves upstream licenses.
