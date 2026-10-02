> Historical revision evidence. The current native-template quality gate is in
> [EVIDENCE.md](../EVIDENCE.md); do not substitute these earlier runs for it.

# Review-fix validation

Current source identity, 16 passing local tests, fresh private SDK/UI, recovery,
retention, mail transport and teardown: [EVIDENCE.md](../EVIDENCE.md) and
[executed checklist](../fix-evidence/VALIDATION.md). Native registry inputs remain
unresolved. The results below belong to the earlier revision.

# Validation results — 2026-10-01

The named error, structured-log and trace pipelines worked on Railway. Tests
used only `bounty-test-sentry-1` through `bounty-test-sentry-4`. No Station post,
public GitHub push or template publication was performed.

| Acceptance check | Result and raw evidence under `evidence/` |
|---|---|
| Pinned official Sentry | PASS: `package-audit.txt`, `pins.txt`; `images.lock.json` in the package; upstream SHA `667094ad0b11bb27e6380fc757754c66516b59b4` |
| Empty-state deployment | PASS: corrected bootstrap candidate in project 4, `cold4-iac-apply.json`, `cold4-upload-*.txt`, `cold4-status3.json`, `cold4-queries.txt`; no migration/schema shell repair |
| Usable authenticated UI | PASS: authenticated trace/error/log UI in `ui-trace.png`, `ui-log.png`; first admin created at bootstrap, project fixture creation is test data setup |
| Private-network errors | PASS: `final-sdk.log`, `final-query-error.json`; event `3550a7c515434b4bb2f966e35e44efa5` |
| Structured logs | PASS: `final-query-logs.json`; body and marker/pipeline attributes, not breadcrumbs |
| Parent/child traces | PASS: `final-query-spans.json`; trace `9192bd1aa236454ca31da45f8622e150`; final verifier asserts parent relationship |
| Authentication boundary | PASS: `final-http-checks.json`: protected API rejects anonymous requests with 401; generated admin login evidenced by UI captures |
| Dependency readiness | PASS: `readiness4-drill.json`, `readiness4-test.txt`; no 2xx while Web or Relay stopped, 200 after each recovery |
| Restart persistence | PASS: `restart-all.txt`, `restart-status2.json`, `restart-queries2.txt`; original error, structured log and spans remain queryable |
| Restore drill | PASS for executed drill: six stopped volume snapshots restored in project 1 and raw objects copied back, then exact IDs queried; `restore-test.txt`, `bucket-restore.txt`, `restore-queries-final.txt` |
| Supervision | PASS: `resume-unit-tests-green.txt`: child failure, sibling termination, SIGTERM and missing-heartbeat failure; independent heartbeat paths; accepted-outcomes/scheduler lack upstream heartbeat options |
| Final worker rollout | PASS: `final-healthy-status.json`; corrected supervisor in both consumer groups and tasks; fresh SDK results verified afterward |
| Backlog recovery | PASS: `backlog4-lag-paused.txt`, `backlog4-lag-recovered.txt`, `backlog4-queries.txt`; all 20 errors, 20 logs and 20 linked traces recovered; 41 queryable spans include an additional SDK HTTP span |
| Resource measurements | PASS as observations, not minimum-capacity proof: `cold4-bootstrap-*`, `cold4-idle-*`, `backlog4-recovery-*`, `query-load-*`; COST.md records bounds and caveats |
| Cleanup | `cleanup-railway-list.txt` and `.json` are final CLI proof; finalizer asserts no name begins with `bounty-test-sentry-` |

## Commands and reproducibility

The workspace has no Git repository, so no candidate commit SHA exists. The
upstream SHA identifies copied configuration; `PACKAGE.sha256` and the per-file
parts under `integrity/` identify the delivered candidate. Image digests are in
`images.lock.json`; deployment IDs/image digests are in status evidence.

Executed commands include:

```sh
python3 -m unittest discover -s tests -v
python3 audit-package.py
python3 final-query-test.py
python3 final-backlog-query-test.py
python3 measure-test.py query-load <since> test4 <until>
python3 summarize-metrics.py query-load
railway usage projects --project <throwaway-id> --workspace <workspace-id> --json
railway delete --project <throwaway-id> --yes --json
railway api 'mutation($id:String!){projectScheduleDeleteForce(id:$id)}' --var id=<throwaway-id>
railway list
railway list --json
python3 evidence_files.py verify
```

Metric command files retain exact project/service IDs, timestamps and exit codes.
CLI uploads and IaC responses retain deployment/provisioning evidence. Test-only
scripts have explicit project guards; private fixture tokens are outside `src/`
and are not part of the deployment package.

Long raw output is split without changing bytes. Read a pointer file with
`python3 evidence_files.py read evidence/<filename>`; reconstruction checks
each part and the original SHA256. Known secrets in earlier API captures were
redacted; `redaction-report.json` records filenames and original digests. These
sanitized captures are not claimed to be byte-identical raw output.

## Discovered defects and limits

- Earlier candidates needed bootstrap, symbolicator and Relay fixes. Failed
  evidence remains archived. Project 4 cold deployment validated the corrected
  configuration; initial UI configuration and creating a project are normal user
  setup, not schema repair.
- System Python exposed a monotonic-clock origin assumption in the supervisor.
  `resume-unit-tests.txt` is the failed run, followed by the corrected code,
  passing tests and final worker rollout.
- Railway healthchecked replacement keeps old consumers alive despite
  `overlapSeconds=0`. Partition sharing prevented new consumer heartbeats.
  Stopping old deployments completed rollout; RECOVERY.md specifies the procedure.
- Restore used Railway snapshot replacement in the existing stopped test
  project, not a separately provisioned cross-project restore. It recovered the
  exact error/log/trace IDs. Automated cross-project restore is not supplied.
- Short-window query metrics contained no samples (`backlog4-query-summary.json`);
  this is not zero usage. The longer query-load window includes worker replacement
  overhead and is explicitly labeled in COST.md.
- No HA, load-capacity guarantee, profiling/replay/uptime/cron-monitoring support,
  retention-duration soak test or award claim. README.md defines supported scope.
