# Sentry runtime source

Use the [one-click README](../README.md) to deploy, sign in and send telemetry.
No source-side CLI deployment or secret generation is needed.

[Operations](OPERATIONS.md) covers retention, optional email and password reset.
[Recovery](RECOVERY.md) covers backups and restoration.
[Runtime inventory](services.json) defines the services and persistent volumes.
[Upstream notices](upstream/LICENSE.md) identify preserved third-party sources.

The `.railway` adapters and SDK fixture are development/validation tools;
`runtime/` is the isolated production Docker build context. See the main evidence
and handoff for tested scope and remaining distribution limitations.
