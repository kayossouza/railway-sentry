# Validation

Tested runtime commit: `a78f8e455866e58ed54d8de8b1c3560d17adde89`.
The unpublished native template `50bZZ5` deployed fourteen services, five volumes,
and two native buckets with zero deployment inputs in the author’s workspace.
Final fresh project: `cc2e40ff-186e-4061-b1d5-f6d0576ca121`, named
`bounty-test-sentry-3`, tested on 2026-10-01 UTC.

Generated administrator credentials worked immediately without an installation
form. Wrong passwords were rejected before and after recovery. The README’s exact
SDK example produced a visible error, structured log with parameters, and linked
parent/child spans. A full stack redeploy produced new deployments for every
service and preserved the original event body, log and span identities.

Each of the fourteen services was then restarted individually. Each recovered,
preserved the original data, and accepted a new SDK error, log and linked trace.
The final issue count was sixteen. See the [per-service receipts](validation/run8-restart-summary.json).
Generated installation and bucket credentials remained stable.

All active `bounty-test-sentry-*` projects were deleted; fresh `railway list --json`
returned zero active matches. Railway retains soft-delete recovery records; see
[cleanup proof](validation/cleanup-proof.json).

## Cost

The final quiet window was 2026-10-01 23:49:50.131926–23:53:19.548163 UTC.
Seven equally spaced provider timestamps inside this window yielded total means
of 9.31265506742857 GB RAM and 0.17020029523809524 vCPU across fourteen services.
An extra provider bucket before the requested window was excluded.
At Railway’s published minute rates, repeating this measured load for thirty days
is **$96.34 compute**. Actual cumulative provider test usage at capture was
**$0.10166570873358699**, including bootstrap and recovery; this is a different
scope from the monthly scenario. Storage, egress, future data growth and plan
minimums/credits are outside the compute scenario. See [raw calculation and scope](validation/final-measured-cost.json)
and [pricing](https://docs.railway.com/reference/pricing/plans).
The raw per-service metric responses are retained in `validation/`.

## Boundaries

Independent-account deployment remains unverified because this source repository
is private and template publication/public pushes were outside authorization.
SDK and service traffic use private networking; native buckets use public TLS
provider endpoints and uploads incur service egress. Internal self-hosting is the
scope; future monetized distribution and kickback clearance remain unresolved.
No Station post or template publication was performed.

Original upstream configuration and licenses are preserved in `runtime/upstream/`.
The unmodified upstream configuration exceeds the authored-file line limit.
