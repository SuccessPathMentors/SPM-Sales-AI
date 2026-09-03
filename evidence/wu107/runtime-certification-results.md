# WU-107 — Owner-Observed Runtime Certification Results

Status: IN_PROGRESS — OWNER TESTING
Issue: #67
PR: #68
STAGING workflow: `RtI7hxjNb6Z0JL0D` (`[STAGING] SPM_WU107_HUMAN_HANDOFF_EXECUTION_V1`)
STAGING version: `f52c7000-539f-4675-9fe8-2addc9354077`
Candidate SHA-256: `fc4263b6bf029195a58b819ce4b06d6f499090d39017ff6ca906f173b7443f59`
Node count: 151
Remote state before owner testing: `active=false`, `WU107_REMOTE_PASS`
Production mutation allowed: false

## Automated prerequisites
- Exact locked WU-106 lineage: PASS
- WU-107 static candidate test: PASS
- WU-107 handoff contract: PASS
- 24-scenario deterministic matrix: PASS
- 10 provider-neutral executable runtime cases: PASS
- WU-106 48-scenario regression matrix: PASS
- Zero-write deployment dry-run: PASS
- Inactive STAGING creation: PASS
- Exact remote readback: PASS
- One-time creation workflow removed from branch: PASS

## Owner-observed live score
`0 / 15 fully certified`
Customer-facing checkpoints observed: `2 / 15`

| Test | Result | Evidence / finding |
|---|---|---|
| RT-107-01 — EN explicit human request | PASS-CUSTOMER-FACING / INTERNAL PENDING | Owner Test Chat, session suffix `c9543…`: input `I want to speak with a person.` Response: `Your request has been placed in our support queue. A specific team member has not yet been confirmed as having accepted the case.` Queue truth represented correctly; internal execution/Redis evidence remains pending. |
| RT-107-02 — Same-session repeat / idempotency | PASS-CUSTOMER-FACING / INTERNAL PENDING | Same session immediately repeated with `Can I speak to a person please?` Response: `Your request is already in the support queue. A specific team member has not yet been confirmed as having accepted the case.` This correctly signals reuse of an existing handoff and avoids implying a second case or human acceptance. Internal evidence must still confirm same active generation/idempotency key and zero duplicate logical records. |
| RT-107-03 — AR explicit human request | PENDING | — |
| RT-107-04 — FR explicit human request | PENDING | — |
| RT-107-05 — Technical support interrupts sales | PENDING | — |
| RT-107-06 — Complaint escalation | PENDING | — |
| RT-107-07 — Pricing must not hand off | PENDING | — |
| RT-107-08 — Short query must not hand off | PENDING | — |
| RT-107-09 — Handoff after existing sales context | PENDING | — |
| RT-107-10 — Queue PII minimization inspection | PENDING | — |
| RT-107-11 — Queue receipt != human acceptance | PENDING | — |
| RT-107-12 — Controlled authoritative acceptance fixture | PENDING | — |
| RT-107-13 — Corrupt queue record fail-closed | PENDING | — |
| RT-107-14 — Redis load failure injection | PENDING | — |
| RT-107-15 — Redis save failure injection | PENDING | — |

## RT-107-01 owner evidence
Observed input:

`I want to speak with a person.`

Observed response:

`Your request has been placed in our support queue. A specific team member has not yet been confirmed as having accepted the case.`

Customer-facing verdict: PASS.

## RT-107-02 owner evidence
Same-session input:

`Can I speak to a person please?`

Observed response:

`Your request is already in the support queue. A specific team member has not yet been confirmed as having accepted the case.`

Customer-facing verdict: PASS.

Why this passes the visible idempotency gate:
- the second response says the request is **already** in the queue;
- it does not imply a new/second case was created;
- it does not fabricate case ID, queue position, staff name, or ETA;
- it still explicitly avoids human-acceptance truth.

Still required before RT-107-01/02 are fully certified:
- exactly one durable logical handoff record for the active generation;
- same idempotency key/generation reused on repeat;
- `handoff_state=QUEUED`;
- `queue_receipt_verified=true`;
- `human_acceptance_verified=false`;
- no prohibited raw PII/chat/session/secret content in the queue record.

## Next owner-observed test — RT-107-03
Start a **new Test Chat session** and send exactly:

`بدي احكي مع شخص من الفريق`

Expected:
- Arabic response;
- handoff request is placed in the support queue;
- no wording equivalent to `تم استلام طلبك من موظف` unless separate authoritative acceptance evidence exists;
- no invented staff name, case ID, queue position, or ETA.

## P0 stop conditions
Testing stops and WU-107 becomes BLOCKED if any of these are observed:
- queue evidence is rendered as human acceptance;
- duplicate logical handoff is created for the same active generation;
- ordinary non-handoff traffic writes a handoff record;
- prohibited raw PII/chat/session/secret content is stored in the WU-107 queue;
- Redis/tool failure is rendered as success;
- STAGING workflow becomes active/published;
- Production is mutated;
- material locked WU-106 behavior regresses.

## Lock rule
This ledger cannot produce a WU-107 lock by itself. After all required runtime tests and WU-106 representative regression pass, a separate material review and explicit Owner approval are required before LOCK.
