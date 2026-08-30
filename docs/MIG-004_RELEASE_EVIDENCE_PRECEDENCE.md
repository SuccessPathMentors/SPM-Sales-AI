# MIG-004 — Release Evidence Precedence and Historical Snapshot Reconciliation

Status: PASS CANDIDATE
Date: 2026-08-30
Issue: #8

## Purpose
Preserve historical Drive evidence exactly as it existed while preventing stale `NOT_RUN`, preparation-only, or unknown-runtime statements from overriding later verified evidence.

No historical artifact is rewritten by MIG-004. Reconciliation happens only in current GitHub control documents such as `docs/STATE.yaml`, this precedence record, and `docs/MIGRATION_MANIFEST.md`.

## Authority order
When release evidence conflicts, use this order:

1. **Verified current runtime identity + exact current runtime export** for the question “what is live now?”
   - Current production workflow: `SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json`
   - n8n workflow ID: `CMBMpxX5AqqK2UTn`
   - Exact GitHub artifact SHA-256: `680496f2b68b13dd7105e72fd132a2066d70ec969e6e0675f138ebb1fb16fe39`
   - Runtime execution evidence: n8n execution `2539`

2. **Later dated release/certification evidence** for completed WU99/WU100 facts.
   - Greenfield `tasks.md` records WU99 runtime execution complete with 96/96 automated PASS, 15/15 failure-injection PASS, protected R1 10/10 PASS, and manual semantic remediation closed.
   - `SPM_WU100_Production_Approval_Checklist_2026-08-21.md`, updated 2026-08-25, records the later WU99 certification results, Lead/CRM adapter certification, clean RC3/static QA, rollback drill execution `2276`, and owner-approved canary operational thresholds.

3. **Older WU99/WU100 execution templates/runbooks** remain historical preparation evidence only.
   - `SPM_WU99_Runtime_Certification_Runbook_2026-08-21.md` says `PREPARED — RUNTIME NOT RUN`; this describes the state at that checkpoint and is not current authority after later execution evidence.
   - Historical WU99 ledgers, failure-injection templates, WU100 preparation/rollback/checklist documents are retained verbatim. A later result is never backfilled into an older template unless that file was actually updated at the time by its source process.

4. **`drive-mirror/00_START_HERE/PROJECT_STATE.md` is an immutable historical snapshot**, not current release authority.
   - The snapshot states WU99 `PREPARED, NOT RUN` and WU100 preparation-only / production release `NOT_RUN`.
   - `docs/ARTIFACT_INTEGRITY_REGISTER.yaml` explicitly classifies it as `HISTORICAL_SNAPSHOT_ONLY` and points current-state authority to `docs/STATE.yaml`.

## Explicit supersession map

| Historical statement / artifact | Historical meaning | Superseded for current-state use by | Current interpretation |
|---|---|---|---|
| `PROJECT_STATE.md` WU99 = PREPARED / NOT RUN | valid checkpoint snapshot | later Greenfield task evidence + current `docs/STATE.yaml` | WU99 runtime suite completed; historical snapshot remains unchanged |
| `SPM_WU99_Runtime_Certification_Runbook_2026-08-21.md` = PREPARED / RUNTIME NOT RUN | runbook before execution | later Greenfield task evidence | WU99 execution later completed; runbook remains historical |
| `PROJECT_STATE.md` WU100 = preparation-only / actual canary not run | valid checkpoint snapshot | WU100 checklist updated 2026-08-25 + verified RC4.3.3 live runtime | do not infer missing intermediate canary-stage history; only later explicitly documented facts are current |
| old current-runtime identity unknown / RC3-only assumptions | earlier migration uncertainty | RC4.3.3 exact export + n8n execution 2539 | RC4.3.3 is verified current live production runtime |
| `SPM_E2E_Sales_Agent_RC4_2_FINAL_FROZEN_2026-08-26.json` reference | later historical reference without located exact artifact | exact RC4.3.3 runtime/export evidence | remains `UNVERIFIED_HISTORICAL_REFERENCE`; cannot override RC4.3.3 |

## Non-inference rule
The fact that RC4.3.3 is currently live does **not** prove undocumented 5%/20%/50%/100% canary-stage execution history. Missing release-stage evidence remains missing. MIG-004 reconciles contradictions but does not fabricate events.

## Agent rule
Agents must:
- read `docs/STATE.yaml` first;
- treat `drive-mirror/**` historical snapshots/runbooks/ledgers as audit evidence unless a current control document explicitly promotes them;
- never use an older `NOT_RUN` statement to override a later dated verified result;
- never rewrite historical files to make chronology look cleaner;
- mark `RECONCILIATION_REQUIRED` when chronology is not supported by evidence.

## Current reconciled release facts
- RC4.3.3 current production identity: VERIFIED.
- RC4.3.3 exact GitHub artifact transport: PASS.
- WU99 later aggregate certification: 96/96 runtime PASS; 106/106 invocations; 15/15 failure injection PASS; R1 10/10 PASS; manual semantic review complete; multilingual parity accepted; open P0/P1 = 0.
- WU99 runtime-testable SUT remains TEST ONLY and is not a production promotion artifact.
- WU100 later checklist records clean RC3/static QA, Lead/CRM adapter certification, rollback drill `2276`, and approved canary operational thresholds; several historical RC3/canary/final-freeze checklist items remained unchecked at that dated checkpoint.
- Current RC4.3.3 live runtime is verified independently; do not backfill undocumented RC3→RC4.3.3 release-stage steps.
- Scheduling/booking live execution is excluded in current RC4.3.3 scope.
- Human handoff execution is disabled/not configured in current RC4.3.3 scope.
- Payment and external follow-up execution are excluded in current RC4.3.3 scope.

## Current-state authority
`docs/STATE.yaml` is the reconciled current engineering/release state during migration.

Until explicit owner cutover approval:
- migration status remains `MIGRATION_IN_PROGRESS`;
- Google Drive remains archive authority for original historical evidence;
- GitHub is the engineering target source of truth, not yet the sole approved authority;
- production auto-deploy remains disabled.
