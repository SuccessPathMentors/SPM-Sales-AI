# WU99 — Full Runtime / E2E Certification Runbook

Status: **PREPARED — RUNTIME NOT RUN**

## System under test
- Testable SUT: `SPM_E2E_Sales_Agent_Greenfield_WU99_Runtime_Testable_2026-08-21.json`
- Based on WU97 semantics; only adds an Execute Workflow Trigger for synthetic WU99 testing.
- SUT remains inactive on import and retains the Greenfield TEST_ONLY guard.
- SUT SHA-256: `a74b6443151eca02d3cc0b28126be96344a68326a389f6ac2951f54bcce0c6fc`

## Automated runner
- Harness: `SPM_WU99_Runtime_Certification_Harness_96_2026-08-21.json`
- Runtime cases: 96
- Actual invocations including prelude turns: 106
- Taxonomy coverage: 62/62 intents
- Harness SHA-256: `965ae82f03cd8e3f7cfbf0bcd12ac859cf5618373c25590b861e02858f6f06ab`
- The `Execute Greenfield SUT [CONFIGURE TARGET THEN ENABLE]` node is deliberately DISABLED and has no workflow ID.
- After importing the SUT as a new inactive workflow, select that new SUT workflow ID in this node, then enable only this node in the harness.

## Required execution order
1. Import the testable SUT as a **new inactive** workflow. Do not overwrite production or R1/R2/R2.5.
2. Resolve Google Sheets, Redis, and OpenAI credentials only in the test copy.
3. Import the WU99 harness as a separate inactive workflow.
4. In the harness, select the imported WU99 testable SUT in `Execute Greenfield SUT [CONFIGURE TARGET THEN ENABLE]`.
5. Keep all existing real Lead UPSERT / scheduling / handoff adapters disabled or NOT_CONFIGURED as designed.
6. Run the harness manually. Capture n8n execution IDs and export the final JSON result.
7. Populate `SPM_WU99_Runtime_Evidence_Ledger_96_2026-08-21.csv`.
8. Require exact intent and source-gate match for all critical cases. Review every answer manually for business-outcome parity and sales quality.
9. Execute the 15-case failure-injection matrix on a disposable test copy only.
10. Re-run R1 protected lead outcomes after any runtime fix.

## Blocking gates
- 0 missing runtime results.
- 0 critical intent/source-gate failures.
- No false lead, booking, scheduling, discount, refund, payment, or handoff success.
- Sticky opt-out preserved across later support.
- Support overrides sales.
- No cross-student merge.
- No raw PII/session/message/secrets in telemetry.
- No production write enabled during certification.
- Failure injection must fail closed and remain observable.
- Manual semantic review of all 96 final responses is required.
- No P0/P1 defects before WU100.

## Current limitation
This environment has no n8n execution connector. Therefore the harness can be built and statically verified here, but **WU99 cannot be marked PASS or Certified until the actual n8n execution evidence is supplied or an n8n connection is available**.

## Next step after runtime PASS
WU100 — Canary Release / Production Certification / Lock.
