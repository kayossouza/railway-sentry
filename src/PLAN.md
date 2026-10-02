# Historical implementation plan

Current gate status is in [EVIDENCE.md](../EVIDENCE.md); the checks below describe
the earlier implementation and are not a claim about the final native run.

Reused official self-hosted 26.9.0 configuration and image compatibility matrix;
small Railway wrappers supply private DNS, bootstrap, storage and supervision.
Competitor wrappers were references only; none copied. All-in-one databases
were rejected because they couple persistence and recovery without removing RAM.

- [x] Resume existing work; read RECON.md and inspect workspace/Git state.
- [x] Pin images/configuration; retain upstream licenses unchanged.
- [x] Supply Dockerfiles, configs, per-service railway.json and variables.json.
- [x] Generate per-install credentials and persist Relay's unique identity.
- [x] Supply current Railway IaC adapter for deprecated JSON compatibility.
- [x] Validate empty-state deployment and private errors/logs/parent-child spans.
- [x] Verify authentication, readiness, restart persistence and snapshot recovery.
- [x] Finish interrupted backlog test; query every receipt and measure usage.
- [x] Fix supervisor clock portability; verify workers and fresh SDK data.
- [x] Document maintenance rollout, limitations, recovery and measured cost inputs.
- [x] Delete test projects immediately; assert final railway list contains none.
- [x] Redact captured secrets, split long data, verify integrity and tests.

Exact evidence and limitations are in VALIDATION.md. No delegation or publication.
