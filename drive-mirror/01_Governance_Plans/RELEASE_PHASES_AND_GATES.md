# Next Release Phases and Approval Gates

Last updated: 2026-08-17.

## R1 — Reliable Lead Submission (APPROVED AND LOCKED)

Completed and owner-approved on 2026-08-17. Baseline artifact: `ChatBotMSE_v2_R1_LOCKED_2026-08-17.json`.

### Locked scope

1. Complete confirmed lead write.
2. Same-session correction/update.
3. Duplicate prevention.
4. Validation and consent enforcement.
5. Success-on-write behavior.
6. Operational lead routing outside unanswered questions.

### Gate result

- 10/10 focused tests passed.
- One complete row created for a new confirmed lead.
- Same row updated after confirmed correction.
- No duplicate after repeated confirmation.
- No false success on tool/subworkflow failure.
- No P0/P1 defect in R1 scope.
- Owner recorded approval and phase lock.

## R2 — Reliability and Error Handling (READY / NOT STARTED)

- bounded retry/backoff for OpenAI, Sheets, Redis, and notifications;
- timeout and partial-failure behavior;
- multilingual safe failure messages;
- error workflow coverage and idempotency checks.

R2 becomes ACTIVE only after its first task and acceptance criteria are explicitly approved.

## Later phases — locked

- R3 Refactor and maintainability.
- R4 Token, latency, and cost optimization.
- R5 Knowledge quality and retrieval.
- R6 Security, privacy, and operations.
- R7 PostgreSQL/Supabase migration pilot.
- R8 Controlled expansion: CRM, voice, channels, analytics.

No R3+ phase may start before R2 is approved and locked.
