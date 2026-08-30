# QA, Testing, and Release Gate

Last updated: 2026-08-17.

## R1 final result

- Phase: `R1 — Reliable Lead Submission`.
- Result: **10/10 PASS**.
- P0 failures: **0**.
- Blocked tests: **0**.
- Owner approval: **CONFIRMED**.
- Status: **APPROVED AND LOCKED**.
- Locked workflow: `ChatBotMSE_v2_R1_LOCKED_2026-08-17.json`.
- Lock record: `R1_LOCK_RECORD_2026-08-17.md`.

## Permanent R1 regression cases

1. New valid lead creates one complete row.
2. Same-session email correction updates the same row.
3. Repeated confirmation creates no duplicate.
4. Invalid email produces no write.
5. Missing mandatory field requests only that field.
6. No consent produces no write.
7. Natural Arabic/English/French confirmation works.
8. Data correction is not logged as unanswered.
9. Failed write cannot produce a success message.
10. Error handling does not expose secrets/internal data.

## Evidence rule for future phases

Record test ID, timestamp, tester, workflow version, session/execution ID, input, expected/actual route and output, side effect, row reference, and pass/fail result.

Every later change that touches lead behavior must re-run this complete R1 regression set.
