# WU-107 — STAGING Runtime Certification Plan

Status: STAGING_CREATED_INACTIVE — OWNER-OBSERVED LIVE TESTING READY
STAGING workflow: `RtI7hxjNb6Z0JL0D` (`[STAGING] SPM_WU107_HUMAN_HANDOFF_EXECUTION_V1`)
STAGING version: `f52c7000-539f-4675-9fe8-2addc9354077`
Remote readback: `WU107_REMOTE_PASS`
Candidate SHA-256: `fc4263b6bf029195a58b819ce4b06d6f499090d39017ff6ca906f173b7443f59`
Candidate nodes: 151
Upstream WU-106: LOCKED, SHA `2e219adbdd612106b782993cbcb2f94da6c0737b250264060b473f12f0fcc81f`
Production mutation: PROHIBITED
Activation/publish during certification: PROHIBITED

## Certification objective
Prove in the real inactive n8n STAGING workflow that WU-107 creates one durable, idempotent, privacy-minimized handoff queue record and never converts queue evidence into false human-acceptance truth.

WU-107 runtime certification does **not** certify WhatsApp notification or actual staff acceptance. Those remain WU-108/downstream scope.

## Evidence required per test
Capture, where available:
- Test ID;
- customer message(s);
- detected intent/language;
- `sales_state.analytics.session_key` or safe suffix only;
- `wu107_handoff_request.execution_required`;
- `wu107_handoff_request.reason_code`;
- `wu107_handoff_execution.handoff_state`;
- `wu107_handoff_execution.queue_receipt_verified`;
- `wu107_handoff_execution.human_acceptance_verified`;
- `action_result.status`;
- customer-facing answer;
- Redis queue record existence/state when relevant;
- duplicate logical case count when relevant;
- PASS/FAIL + finding.

Do not paste raw credentials, API keys, full Redis secrets, or unnecessary parent/student PII into evidence.

## Blocking P0 gates
Any one of the following blocks WU-107:
1. customer is told a human accepted/received the case when only Redis queue evidence exists;
2. repeat request creates duplicate logical handoff records for the same active generation;
3. non-handoff conversation creates a handoff queue write;
4. raw chat/session/contact data appears in the WU-107 Redis queue record contrary to the minimized contract;
5. Redis failure is rendered as successful handoff;
6. WU-107 activation/publish or Production mutation occurs;
7. WU-106 locked journey behavior materially regresses.

## Live Test Matrix

### RT-107-01 — English explicit human request
Customer: `I want to speak with a person.`
Expected:
- handoff execution required;
- reason `EXPLICIT_HUMAN_REQUEST`;
- exactly one queue record;
- state `QUEUED` only after Redis write evidence;
- `queue_receipt_verified=true`;
- `human_acceptance_verified=false`;
- customer language says support queue, not human accepted.

### RT-107-02 — Repeat same-session human request / idempotency
Immediately repeat: `Can I speak to a person please?`
Expected:
- same active queue record/generation reused;
- no second logical case;
- state remains `QUEUED`;
- customer is told request is already in queue;
- no invented case/staff/ETA.

### RT-107-03 — Arabic explicit human request
Customer: `بدي احكي مع شخص من الفريق`
Expected:
- reason `EXPLICIT_HUMAN_REQUEST`;
- `QUEUED` after tool evidence;
- Arabic truthful queue wording;
- no statement equivalent to `استلم الموظف طلبك` unless separate acceptance evidence exists.

### RT-107-04 — French explicit human request
Customer: `Je veux parler à une personne de l'équipe.`
Expected:
- same execution truth as EN/AR;
- French queue wording;
- no false acceptance.

### RT-107-05 — Technical support interrupts sales
Start with a normal tutoring sales topic, then: `The portal is not working. I need help.`
Expected:
- `TECHNICAL_SUPPORT` handoff reason where classifier/runtime support signal is present;
- support interrupts sales;
- queue created exactly once;
- sales CTA does not continue in the same response.

### RT-107-06 — Complaint escalation interrupts sales
Customer: `I have a complaint and want someone to help me.`
Expected:
- complaint/support precedence;
- reason `COMPLAINT_ESCALATION` when complaint is the matched handoff signal;
- queue truth only after Redis evidence;
- no attempt to overcome objection or resume sales.

### RT-107-07 — Ordinary pricing question must not hand off
Customer: `How much are the packages?`
Expected:
- WU-105/WU-106 answer behavior preserved;
- `execution_required=false`;
- no WU-107 Redis queue write;
- no handoff customer wording.

### RT-107-08 — Short-query behavior remains unchanged
Customer: `price?`
Expected:
- locked WU-104/WU-105 answer-first behavior;
- no WU-107 queue write;
- no regression to forced handoff.

### RT-107-09 — Handoff after prior registration/scheduling context
Build a small sales context, then ask for a person.
Expected:
- handoff does not fabricate or mutate registration/booking truth;
- minimal context summary may indicate stage/known-contact booleans only;
- queue record excludes raw parent/student/contact values by default.

### RT-107-10 — PII minimization inspection
Inspect the WU-107 Redis record created by a test handoff.
Expected default record must not contain:
- raw conversation;
- raw session ID;
- parent/student full name;
- phone number;
- email address;
- password/token/API key/payment data.
Allowed context is bounded operational metadata and presence booleans defined by the WU-107 contract.

### RT-107-11 — Queue evidence must not equal human acceptance
Using a normal queued record with no downstream acceptance evidence:
Expected:
- `handoff_state=QUEUED`;
- `downstream_receipt_present=true`;
- `downstream_acceptance_present=false`;
- `human_acceptance_verified=false`;
- customer-facing answer explicitly avoids claiming a specific team member accepted it.

### RT-107-12 — Existing verified acceptance truth gate
Controlled STAGING-only fixture: update/create a test queue record that already has authoritative acceptance evidence according to the WU-107 schema.
Expected:
- only then may runtime return `ACCEPTED`;
- `human_acceptance_verified=true`;
- evidence must come from the record, not generated text/classifier output.
This test is fixture-only and does not certify the future WU-108 acceptance provider.

### RT-107-13 — Corrupt queue record fails closed
Controlled STAGING-only fixture: same queue key, invalid/corrupt schema.
Expected:
- no overwrite claiming success;
- no `QUEUED`/`ACCEPTED` customer claim from corrupt data;
- fail-closed/degraded behavior recorded.

### RT-107-14 — Redis load failure
Controlled failure injection against the isolated STAGING handoff dependency/path.
Expected:
- request remains preserved as `REQUESTED` truth;
- `queue_receipt_verified=false`;
- `human_acceptance_verified=false`;
- degraded error code `WU107_HANDOFF_QUEUE_LOAD_FAILED`;
- no success claim.

### RT-107-15 — Redis save failure
Controlled failure injection against the isolated STAGING queue write.
Expected:
- `REQUESTED`, not `QUEUED`;
- degraded error code `WU107_HANDOFF_QUEUE_SAVE_FAILED`;
- no success claim;
- unrelated registration/sales truth remains unchanged.

## Regression pack after handoff-specific tests
After RT-107-01 through RT-107-15, rerun the locked WU-106 representative journey pack, prioritizing:
- pricing -> trial -> scheduling;
- short query -> answer-first;
- explicit registration action truth;
- support interruption;
- correction/context retention;
- availability without invented slots;
- refund-policy truth;
- multi-turn scheduling context.

Minimum exit expectation:
- WU-107 handoff tests: all blocking cases PASS;
- no P0/P1 open;
- WU-106 material regression: none;
- remote workflow remains inactive;
- Production remains untouched.

## Current gate
All automated pre-runtime gates are complete: exact-lineage CI, handoff contract, provider-neutral executable tests, zero-write dry-run, inactive STAGING creation, and remote exact-content readback.

The next required gate is **owner-observed n8n Test Chat / manual execution evidence on the inactive STAGING workflow**. The workflow must remain inactive throughout testing.

## Runtime exit states
After execution, WU-107 may advance to:
- `STAGING_RUNTIME_PASS_OWNER_TEST_PENDING`, or
- `BLOCKED_RUNTIME_FINDING`.

It may not advance directly from offline/dry-run evidence to LOCKED.
