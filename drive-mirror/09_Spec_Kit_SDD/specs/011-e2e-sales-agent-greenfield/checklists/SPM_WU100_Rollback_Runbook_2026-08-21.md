# SPM WU100 — Rollback Runbook

Date: 2026-08-21
Status: PREPARED; not yet runtime-verified for the Greenfield release.

## Rollback target
Primary rollback target remains the last approved and locked production baseline, **R1 — Reliable Lead Submission**, unless a later production release is explicitly approved before WU100 execution.

## Rollback triggers
Trigger immediate rollback for any hard-stop invariant in the WU100 Canary Plan, including false success, duplicate/corrupt lead behavior, opt-out violation, booking/availability false claim, PII/secret leak, P0/P1 defect, or unsafe production write.

## Procedure
1. Pause new canary traffic / deactivate the Greenfield production workflow.
2. Re-enable or route traffic to the approved rollback workflow/baseline.
3. Do not delete the failed release candidate or execution evidence.
4. Freeze affected credentials/integrations only if evidence indicates misuse or leakage.
5. Export failing execution IDs and telemetry/error codes.
6. Compare leads created/updated during the canary window for duplicates, incorrect corrections, or partial writes.
7. Verify opt-out state and any booking/handoff side effects.
8. Record rollback timestamp, reason, affected stage, release hash, and owner/operator.
9. Update PROJECT_STATE and CHANGELOG to `ROLLED_BACK`; do not relaunch until the root cause and regression suite pass.

## Verification after rollback
- Baseline workflow responds successfully.
- Lead write/correction/duplicate protections remain intact.
- No new Greenfield canary executions are occurring.
- No queued nurture/handoff/booking action remains from the failed canary unless intentionally retained.
- Incident evidence is preserved.

Runtime rollback drill status: **NOT_RUN**.
