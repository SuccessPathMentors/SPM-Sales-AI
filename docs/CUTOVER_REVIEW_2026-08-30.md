# SPM GitHub Engineering Source-of-Truth Cutover Review

Date: 2026-08-30
Status: **READY FOR OWNER DECISION — NOT YET APPROVED**
PR: #4

## Decision being requested
Approve GitHub `main` as the engineering source of truth for the SPM Sales AI Agent after PR #4 is merged.

This decision does **not** authorize n8n production activation, production auto-deploy, or any AI-driven direct-to-production change.

## Migration gates
| Gate | Result | Evidence |
|---|---|---|
| MIG-001 runtime identity/dependencies | PASS / CLOSED | Issue #5; RC4.3.3 workflow `CMBMpxX5AqqK2UTn`, execution `2539` |
| MIG-002 exact artifact transport | PASS / CLOSED | Issue #6; 30/30 exact Drive batch match + exact RC4.3.3 export |
| MIG-003 GitHub → n8n non-production | PASS / CLOSED | Issue #7; API smoke, dry-run, inactive STAGING create, fail-closed test, deterministic update |
| MIG-004 historical evidence precedence | PASS / CLOSED | Issue #8; `docs/MIG-004_RELEASE_EVIDENCE_PRECEDENCE.md` |

## Current runtime baseline
- Workflow: `SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json`
- n8n workflow ID: `CMBMpxX5AqqK2UTn`
- Runtime state: LIVE / PUBLISHED / VERIFIED
- Runtime evidence: execution `2539`
- Exact GitHub SHA-256: `680496f2b68b13dd7105e72fd132a2066d70ec969e6e0675f138ebb1fb16fe39`
- Nodes: 114
- Disabled nodes: 0
- Native Execute Workflow dependencies: 0

Current production scope remains explicitly bounded:
- Lead/CRM write: enabled current scope
- Scheduling/booking execution: excluded
- Human handoff execution: disabled/not configured
- Payment execution: excluded
- External follow-up execution: excluded

## Artifact integrity
- RC4.3.3: exact-byte GitHub transport PASS.
- Drive exact-transport batch: 30/30 PASS, 0 mismatches, 3,273,938 bytes.
- `PROJECT_STATE.md`: preserved exact historical snapshot; not current authority.
- WU99 Runtime-Testable SUT: exact mirrored, TEST ONLY, not promotable directly.
- Preliminary secret scan: no obvious secret values found; credential references may remain where expected.

## Non-production deployment controls
Long-term reviewed workflow: `.github/workflows/n8n-nonprod-deploy.yml`.

Safety invariants:
- DEV/STAGING only.
- Production workflow ID hard-denied.
- Active/published targets refused.
- Exact SHA required for apply.
- Implicit create denied.
- No publish/activate/deactivate/delete endpoint in deployer.
- Post-write target GET + inactive validation required.
- Production auto-deploy remains false.

STAGING proof target:
- `[STAGING] MIG003_STAGING_CANARY`
- ID `BIDVhNCRbj9dvH1t`
- inactive/unpublished
- side-effect-free Manual Trigger only

## Historical evidence policy
- `docs/STATE.yaml` is reconciled current-state authority during migration.
- Historical Drive snapshots/runbooks/ledgers remain immutable audit evidence.
- Older `NOT_RUN` statements cannot override later dated verified evidence.
- Missing RC3→RC4.3.3 intermediate canary-stage history is not inferred.
- RC4.2 reference remains unverified and cannot override RC4.3.3.

## Branch / PR review
- PR #9 non-production deployer: reviewed, CI PASS, merged into migration branch.
- PR #4 head was fast-forwarded to the complete migration head without force.
- Original PR head is an ancestor of the final migration head; no migration commit history was discarded.
- Latest PR-head `n8n non-production deploy` CI run `33329815518`: SUCCESS.
- PR #4 is mergeable.

## Remaining cleanup before merge
`main` contains temporary `.github/workflows/mig-003-bootstrap.yml`, used only to prove the first MIG-003 live API gates. It should be removed before/with cutover so the reviewed generic non-production workflow is the only deployment automation.

Deletion from `main` requires explicit owner authorization because it is a destructive default-branch mutation.

## Owner decision gate
All engineering migration gates are PASS. Remaining decisions:

1. Authorize deletion of the temporary `mig-003-bootstrap.yml` from `main`.
2. Authorize merge of PR #4 to `main`.
3. Authorize changing migration state from `MIGRATION_IN_PROGRESS` to GitHub engineering source-of-truth cutover complete.

Even after approval:
- `production_auto_deploy` remains `false`;
- `github_driven_production_activation_authorized` remains `false`;
- n8n Production workflow is not modified;
- WU-101 is not started automatically.
