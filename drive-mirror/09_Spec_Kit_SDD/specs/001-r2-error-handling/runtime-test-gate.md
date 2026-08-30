# 001 R2 Error Handling — Runtime Test Gate

Status: Defined; runtime execution pending n8n access
Date: 2026-08-20

## Focused R2 Cases
R2-F01 — Valid new confirmed lead: expected created, success=true, one row only.

R2-F02 — Same-session correction/update: expected updated, success=true, same row/session identity.

R2-F03 — Invalid payload: expected validation_failed, success=false, no write.

R2-F04 — Multiple rows for same session: expected duplicate_conflict, success=false, no new row.

R2-F05 — Forced lookup failure: expected bounded retry then lookup_failed/LEAD_LOOKUP_FAILED, success=false, no success claim.

R2-F06 — Forced write failure: expected bounded retry then write_failed/LEAD_UPSERT_FAILED, success=false, no success claim.

R2-F07 — Transient lookup failure that recovers on retry: expected normal downstream processing after second attempt.

R2-F08 — Transient upsert failure that recovers on retry: expected created/updated success and no duplicate row.

R2-F09 — Tool returns success=false to AI Agent: expected user response must not claim successful submission.

R2-F10 — Failure output safety: expected no raw stack trace, credential, token, internal sheet ID, or secret in user-facing message.

## Permanent R1 Regression — Must Re-run 10/10
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

## Evidence Required Per Runtime Case
- Test ID.
- Timestamp.
- Tester.
- Main workflow version/ID.
- Handoff subworkflow version/ID.
- Session/execution ID.
- Input/failure injection method.
- Expected route/result.
- Actual route/result.
- Side effect and row reference if applicable.
- User-visible response.
- PASS/FAIL.

## Release Rule
No production promotion if any focused R2 case fails, any R1 regression fails, runtime identity cannot be verified, or a P0/P1 issue remains unresolved.
