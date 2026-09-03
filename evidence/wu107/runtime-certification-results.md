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
Customer-facing checkpoints observed: `1 / 15`

| Test | Result | Evidence / finding |
|---|---|---|
| RT-107-01 — EN explicit human request | PASS-CUSTOMER-FACING / INTERNAL PENDING | Owner Test Chat, session suffix `c9543…`: input `I want to speak with a person.` Response: `Your request has been placed in our support queue. A specific team member has not yet been confirmed as having accepted the case.` This correctly represents queue truth and explicitly avoids false human-acceptance truth. Internal execution/Redis evidence (`EXPLICIT_HUMAN_REQUEST`, one durable record, `queue_receipt_verified=true`, `human_acceptance_verified=false`) remains to be confirmed before the test is fully certified. |
| RT-107-02 — Same-session repeat / idempotency | PENDING | — |
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

Observed customer-visible response:

`Your request has been placed in our support queue. A specific team member has not yet been confirmed as having accepted the case.`

Customer-facing verdict: PASS.

Why this passes the truth-language gate:
- the bot states that the request is in the support queue;
- it does not claim that a named/specific staff member received or accepted it;
- it explicitly says acceptance has not yet been confirmed;
- there is no invented ETA, case owner, or staff identity.

Still required for full RT-107-01 certification:
- execution reason `EXPLICIT_HUMAN_REQUEST`;
- exactly one durable WU-107 queue record;
- `handoff_state=QUEUED`;
- `queue_receipt_verified=true`;
- `human_acceptance_verified=false`;
- no prohibited PII in the queue record.

## Next owner-observed test — RT-107-02
Use the **same Test Chat session** immediately after RT-107-01 and send:

`Can I speak to a person please?`

Expected customer-facing behavior:
- the request is already in the support queue / existing handoff is reused;
- no second logical case is implied;
- no new staff acceptance is claimed;
- no fabricated case ID, staff name, or ETA.

Internal evidence later must confirm that the same active handoff generation/record was reused and no duplicate logical queue record was created.

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
