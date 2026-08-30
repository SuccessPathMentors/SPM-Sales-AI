# SPM GitHub Engineering Source-of-Truth Cutover Review

Date: 2026-08-30  
Status: **APPROVED / COMPLETE**  
PR: #4  
Merge commit: `561788510bea13d9a9fea85d5ce0841b846c8432`

## Owner decision
The owner explicitly approved the engineering cutover on 2026-08-30.

Approved effects:
- GitHub `main` becomes the engineering source of truth.
- Google Drive becomes archive/secondary historical reference.
- n8n remains the runtime/deployment target.
- Live Google Sheets remain mutable runtime/knowledge data where applicable.

Not authorized by this decision:
- n8n Production activation or publish;
- production auto-deploy;
- direct AI/GitHub → Production changes;
- automatic start of WU-101.

## Gate results
| Gate | Result |
|---|---|
| MIG-001 runtime identity/dependencies | PASS / CLOSED |
| MIG-002 exact artifact transport | PASS / CLOSED |
| MIG-003 GitHub → n8n non-production deployment | PASS / CLOSED |
| MIG-004 historical evidence precedence | PASS / CLOSED |
| Final PR-head safety CI | PASS |
| Temporary bootstrap cleanup | PASS |
| Owner cutover approval | APPROVED |
| PR #4 merge to `main` | COMPLETE |

## Final Production baseline
- Workflow: `SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json`
- n8n workflow ID: `CMBMpxX5AqqK2UTn`
- Runtime state: LIVE / PUBLISHED / VERIFIED
- Runtime evidence: execution `2539`
- Exact GitHub SHA-256: `680496f2b68b13dd7105e72fd132a2066d70ec969e6e0675f138ebb1fb16fe39`
- Nodes: 114
- Disabled nodes: 0
- Native Execute Workflow dependencies: 0

Production scope remains bounded:
- Lead/CRM write: enabled current scope
- Scheduling/booking execution: excluded
- Human handoff execution: disabled/not configured
- Payment execution: excluded
- External follow-up execution: excluded

## Artifact integrity
- RC4.3.3 exact-byte GitHub transport: PASS
- Drive transport batch: 30/30 exact matches, 0 mismatches, 3,273,938 bytes
- Historical `PROJECT_STATE.md`: audit snapshot only
- WU99 Runtime-Testable SUT: TEST ONLY
- Historical evidence precedence: `docs/MIG-004_RELEASE_EVIDENCE_PRECEDENCE.md`

## Non-production deployment control
Retained automation:
- `.github/workflows/n8n-nonprod-deploy.yml`
- `scripts/n8n/deploy_nonprod.py`
- `n8n/deployment/nonprod-policy.json`

STAGING proof workflow:
- `[STAGING] MIG003_STAGING_CANARY`
- ID `BIDVhNCRbj9dvH1t`
- inactive/unpublished
- no credentials or external side-effect nodes

Temporary cutover bootstrap artifacts were removed from `main` after explicit approval:
- `.github/workflows/mig-003-bootstrap.yml`
- `docs/MIG-003_BOOTSTRAP_NOTE.md`

## Final invariant
The approved engineering path is:

`GitHub → DEV/STAGING → validation/runtime testing → human approval → separate Production release process`

Production auto-deploy remains `false`, GitHub-driven Production activation remains unauthorized, and future Production changes continue to require an explicit owner/release gate.
