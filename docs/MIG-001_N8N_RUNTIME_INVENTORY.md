# MIG-001 — n8n Runtime Identity & Dependency Inventory

Status: **PASS — CURRENT MAIN IDENTITY AND RC4.3.3 DEPENDENCIES RECONCILED**
GitHub issue: #5
Verified date: 2026-08-30

## Purpose
Record the actually live n8n production workflow from runtime evidence and map it to an exact GitHub artifact before any GitHub-driven deployment work.

The original MIG-001 bootstrap plan proposed importing the historical WU99 test SUT/harness because, at that point, the active production workflow was unknown. Later runtime evidence superseded that assumption: WU99 execution had already been completed in the release lineage and RC4.3.3 is now live. Importing old WU99 test artifacts is therefore **not required for current runtime identity reconciliation** and must not be performed merely to satisfy an obsolete bootstrap step.

## Current production workflow — verified

```yaml
workflow_name: SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json
workflow_id: CMBMpxX5AqqK2UTn
environment: production
published: true
active_export_flag: true
role: current_production
n8n_version_id: ee6d40dc-440a-4b3e-9948-090a73ae9222
node_count: 114
disabled_nodes: 0
github_artifact: n8n/workflows/production/SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json
artifact_bytes: 330119
artifact_sha256: 680496f2b68b13dd7105e72fd132a2066d70ec969e6e0675f138ebb1fb16fe39
git_blob_sha1: 58d1e9cc45085909dff91d7a9d07138486e72c76
exact_transport: PASS
execute_workflow_outbound: NONE_FOUND
runtime_execution_evidence: 2539
verified_at: 2026-08-30
```

### Trigger/runtime evidence
- Embedded/public chat trigger is configured for the SPM website origin.
- Successful n8n execution `2539` ran the RC4.3.3 path in the production state namespace.
- The exact export and GitHub copy are byte-identical by Git blob identity and size.

## Dependency / adapter map

| Area | RC4.3.3 evidence | Current conclusion |
|---|---|---|
| Native `Execute Workflow` nodes | Full 114-node export contains `0` | `NONE_FOUND` |
| Lead / CRM write | Production-certified upsert/read-back path present in RC4.3.3 | ENABLED IN CURRENT SCOPE |
| Human handoff contract | Contract logic present | PRESENT |
| Human handoff execution | contract states execution disabled/not configured; no Execute Workflow caller exists | DISABLED / NOT CONFIGURED |
| Scheduling / booking execution | release scope excludes live execution | EXCLUDED |
| Payment execution | excluded | EXCLUDED |
| External follow-up execution | excluded | EXCLUDED |
| Redis state | production namespace path present | ENABLED CURRENT RUNTIME DEPENDENCY |
| Google Sheets / knowledge / lead references | credential references only; secret values not committed | RUNTIME CREDENTIAL DEPENDENCY |
| OpenAI | credential reference only; secret value not committed | RUNTIME CREDENTIAL DEPENDENCY |

There are therefore **no outbound n8n sub-workflow IDs to resolve for the current RC4.3.3 main workflow**.

## Standalone historical handoff workflow

Exact historical Drive artifact is preserved at:
`drive-mirror/03_Workflows_Current/Validated_Human_Handoff_FIXED.json`

Historical n8n identity previously recorded:
- workflow ID: `swhmNa0Goo0uYm1k`
- historical state evidence: active at the earlier checkpoint

This standalone workflow is **not a dependency of current RC4.3.3**, because RC4.3.3 contains no native Execute Workflow call and its handoff execution contract is disabled/not configured. Re-verifying the standalone workflow's present active toggle is therefore not required to identify or safely version the current main production workflow. If WU107 later reconnects human handoff, its exact runtime identity and contract must be revalidated as part of that controlled change.

## Historical references
- R2.5 workflow ID `vSc7cMIMFMEUdi7z` remains a historical rollback/candidate reference, not proof of current main identity.
- WU99 Runtime-Testable SUT, harness, and plan are now exact-mirrored as TEST ONLY evidence. They must not be imported or promoted into production merely for migration bookkeeping.
- `RC4_2 FINAL FROZEN` remains an unresolved historical artifact reference; it does not override verified RC4.3.3 runtime evidence.

## Credential safety
The exact RC4.3.3 export and MIG-002 batch were scanned for common populated secret/API-key/private-key patterns. No obvious secret values were detected. Credential names/IDs may appear as references; credential payloads remain in n8n. This preliminary scan does not replace repository secret scanning or human security review.

## MIG-001 exit gate
- [x] Current active/published main workflow identity evidenced from n8n runtime.
- [x] Exact current production export mapped to GitHub path and checksum.
- [x] Native Execute Workflow dependency inventory completed (`NONE_FOUND`).
- [x] Human handoff current-main status reconciled as disabled/not configured.
- [x] Lead/CRM and excluded adapter scope recorded.
- [x] No production workflow overwritten or activated by MIG-001.
- [x] Credential references recorded without intentional secret-value commits.
- [x] Runtime inventory committed.
- [x] Migration manifest reconciled to RC4.3.3.
- [ ] `docs/STATE.yaml` final reconciliation commit (performed as the next state update in the same migration sequence).

Once `docs/STATE.yaml` is updated, MIG-001 can be closed and MIG-003 may begin in **non-production only**. Production auto-deploy remains forbidden.
