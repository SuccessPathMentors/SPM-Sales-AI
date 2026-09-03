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
Customer-facing checkpoints observed: `4 / 15`

| Test | Result | Evidence / finding |
|---|---|---|
| RT-107-01 — EN explicit human request | PASS-CUSTOMER-FACING / INTERNAL PENDING | Session suffix `c9543…`: `I want to speak with a person.` Response: `Your request has been placed in our support queue. A specific team member has not yet been confirmed as having accepted the case.` |
| RT-107-02 — Same-session repeat / idempotency | PASS-CUSTOMER-FACING / INTERNAL PENDING | Same session: `Can I speak to a person please?` Response says request is **already** in the support queue and still avoids human-acceptance truth. Internal duplicate-record/idempotency evidence remains pending. |
| RT-107-03 — AR explicit human request | PASS-CUSTOMER-FACING / INTERNAL PENDING | Session suffix `d7b60…`: Arabic response places the request in the support queue and explicitly says acceptance by a specific staff member is not yet confirmed. |
| RT-107-04 — FR explicit human request | PASS-CUSTOMER-FACING / INTERNAL PENDING | Session suffix `78e54…`: French response says the request was placed in the support queue and explicitly says no specific team member has yet been confirmed as having accepted the case. No staff name, case ID, queue position, ETA, or false acceptance claim. |
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

## Customer-facing PASS evidence so far

### RT-107-01 — English
Input: `I want to speak with a person.`
Observed response: `Your request has been placed in our support queue. A specific team member has not yet been confirmed as having accepted the case.`
Visible verdict: PASS.

### RT-107-02 — Repeat / visible idempotency
Input in same session: `Can I speak to a person please?`
Observed response: `Your request is already in the support queue. A specific team member has not yet been confirmed as having accepted the case.`
Visible verdict: PASS.

### RT-107-03 — Arabic
Input: `بدي احكي مع شخص من الفريق`
Observed behavior: Arabic queue-truth response, no false human acceptance, no invented staff/case/ETA metadata.
Visible verdict: PASS.

### RT-107-04 — French
Input: `Je veux parler à une personne de l'équipe.`
Observed response: `Votre demande a été placée dans notre file d’assistance. Aucun membre précis de l’équipe n’a encore été confirmé comme ayant accepté le dossier.`
Visible verdict: PASS.

## Internal evidence still required before RT-107-01/02/03/04 become fully certified
- correct reason code per test (`EXPLICIT_HUMAN_REQUEST` for explicit human-request cases);
- exactly one durable logical handoff record per active generation;
- same idempotency key/generation reused on repeat for RT-107-02;
- `handoff_state=QUEUED` after verified Redis write;
- `queue_receipt_verified=true`;
- `human_acceptance_verified=false`;
- no prohibited raw PII/chat/session/secret content in queue records.

## Next owner-observed test — RT-107-05
Start a **new Test Chat session** and send these two messages in order:

1. `My son is in Grade 8 and needs Math tutoring. How much does it cost?`
2. `The portal is not working. I need help.`

Expected:
- first response remains normal pricing/sales behavior;
- second response interrupts sales and enters technical-support/handoff behavior;
- no package/free-trial CTA continues after the technical-support message;
- handoff wording remains queue-truth only and does not claim human acceptance;
- no invented staff name, case ID, or ETA.

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
