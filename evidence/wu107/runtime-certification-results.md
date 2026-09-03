# WU-107 — Owner-Observed Runtime Certification Results

Status: RUNTIME_CERT_COMPLETE — 15/15 PASS / FINAL REVIEW COMPLETE
Issue: #67
PR: #68
STAGING workflow: `RtI7hxjNb6Z0JL0D` (`[STAGING] SPM_WU107_HUMAN_HANDOFF_EXECUTION_V1`)
Current STAGING release: `CR-107-02`
Current STAGING version: `79a38b64-336a-4bfd-8c65-ed5b0ef1f247`
Current candidate SHA-256: `5aaa9dea37b449506b033e9ea6d933f217518b1d38f9f82b81a22773a1358e95`
Node count: 151
Remote state: `active=false`
Remote verification: `WU107_CR10702_REMOTE_PASS`
Production mutation allowed: false

## Certification score
Overall WU-107 runtime test coverage: **15 / 15 PASS**

- Owner-observed customer-facing journeys: RT-107-01 through RT-107-09 — PASS, including RT-107-05 after CR-107-01.
- Internal exact-Code-node certification: RT-107-10 through RT-107-15 — PASS after CR-107-02.
- RT-107-02 idempotency received both owner-observed customer-facing evidence and exact executable internal evidence.

| Test | Result | Evidence / finding |
|---|---|---|
| RT-107-01 — EN explicit human request | **PASS** | Queue-truth response; no false human acceptance. |
| RT-107-02 — Same-session repeat / idempotency | **PASS — CUSTOMER + INTERNAL** | Owner saw `already in support queue`; exact decision-node execution proves existing QUEUED record sets `write_required=false`, reuses the same idempotency key, and does not execute a duplicate tool write. |
| RT-107-03 — AR explicit human request | **PASS** | Arabic queue-truth response; no false acceptance. |
| RT-107-04 — FR explicit human request | **PASS** | French queue-truth response; no false acceptance. |
| RT-107-05 — Technical support interrupts sales | **PASS AFTER CR-107-01** | Technical issue interrupted sales and entered truthful support-queue flow. |
| RT-107-06 — Complaint escalation | **PASS** | Complaint interrupted sales and entered truthful support-queue flow. |
| RT-107-07 — Pricing must not hand off | **PASS** | Pure pricing remained normal sales; no handoff/escalation wording. |
| RT-107-08 — Short query must not hand off | **PASS** | `Math` remained ambiguity clarification; no handoff/escalation. |
| RT-107-09 — Handoff after existing sales context | **PASS** | Grade 8 Math discovery/pricing ran normally; explicit person request then interrupted sales and queued handoff truthfully. |
| RT-107-10 — Queue PII minimization inspection | **PASS-INTERNAL** | Exact queue-record JS executed with PII-heavy fixture; raw message/session/contact/secrets and sensitive literals were absent from the record. Only pseudonymous session key and boolean contact-presence flags remained. Marker: `WU107_RT10_PII_MINIMIZATION_EXECUTABLE_PASS`. |
| RT-107-11 — Queue receipt != human acceptance | **PASS-INTERNAL** | Exact verified-queue result JS yields `QUEUED`, `queue_receipt_verified=true`, `human_acceptance_verified=false`. Marker: `WU107_RT11_QUEUE_RECEIPT_NOT_ACCEPTANCE_EXECUTABLE_PASS`. |
| RT-107-12 — Controlled authoritative acceptance fixture | **PASS-INTERNAL AFTER CR-107-02** | Verified receipt + acceptance evidence yields ACCEPTED. Persisted ACCEPTED without acceptance evidence reconciles to QUEUED when receipt remains valid; unsupported ACCEPTED fails closed. Marker: `WU107_RT12_AUTHORITATIVE_ACCEPTANCE_EXECUTABLE_PASS`. |
| RT-107-13 — Corrupt queue record fail-closed | **PASS-INTERNAL** | Corrupt persisted record blocks blind overwrite/success and returns FAILED/fail-closed. Marker: `WU107_RT13_CORRUPT_RECORD_FAIL_CLOSED_EXECUTABLE_PASS`. |
| RT-107-14 — Redis load failure injection | **PASS-INTERNAL** | Exact load-failure Code node preserves REQUESTED, verifies neither queue receipt nor human acceptance, and uses truthful failure wording. Marker: `WU107_RT14_REDIS_LOAD_FAILURE_EXECUTABLE_PASS`. |
| RT-107-15 — Redis save failure injection | **PASS-INTERNAL** | Exact save-failure Code node preserves REQUESTED, verifies neither queue receipt nor human acceptance, and uses truthful failure wording. Marker: `WU107_RT15_REDIS_SAVE_FAILURE_EXECUTABLE_PASS`. |

## Owner-observed evidence highlights
- RT-107-05 retest session suffix `1c9c8…`: `The portal is not working. I need help.` correctly changed from the pre-CR legacy no-handoff wording to verified support-queue wording.
- RT-107-06 session suffix `8a406…`: complaint stopped sales and entered support queue.
- RT-107-07 session suffix `6faf9…`: pricing did not trigger support.
- RT-107-09 session suffix `b629d…`: existing sales context was interrupted only after explicit human request.

## CR-107-01
Trigger: technical-support routing failure in RT-107-05.

Correction:
- consumes authoritative current-turn WU96/WU106 support signals;
- maps `technical_issue` / `technical_support` to `TECHNICAL_SUPPORT`;
- maps complaint to `COMPLAINT_ESCALATION`;
- prevents sticky historical support state alone from initiating a new handoff;
- changes one WU-107 node; no topology or WU-106 locked-node mutation.

Deployed CR-107-01 remote version: `13b455a8-1318-4f35-8adc-f42f13e49e76`.

## CR-107-02
Trigger: internal RT-107-12 P0 finding.

Initial inconsistency:
- persisted label could be `ACCEPTED` while `downstream_acceptance_present=false`;
- customer wording was cautious, but internal `handoff_state` and `success` still trusted the raw persisted label.

Correction:
- truth is now derived from evidence, not persisted label alone;
- ACCEPTED requires durable queue receipt + authoritative acceptance evidence;
- unverified ACCEPTED with valid receipt reconciles to QUEUED;
- unsupported ACCEPTED/QUEUED truth fails closed;
- changes one WU-107 node only; topology unchanged; WU-106 locked nodes unchanged.

Exact-lineage/offline certification:
- run: `33796151509`
- job: `100784208145`
- candidate SHA: `5aaa9dea37b449506b033e9ea6d933f217518b1d38f9f82b81a22773a1358e95`
- artifact: `9909230931`
- `WU107_INTERNAL_RUNTIME_PATH_CERT_PASS`
- WU-106 48-scenario regression: PASS

STAGING update/readback:
- run: `33796639028`
- job: `100785831605`
- operation: `UPDATE_INACTIVE_NONPROD`
- workflow: `RtI7hxjNb6Z0JL0D`
- pre-version: `13b455a8-1318-4f35-8adc-f42f13e49e76`
- remote version: `79a38b64-336a-4bfd-8c65-ed5b0ef1f247`
- `active=false`
- remote verifier: `WU107_CR10702_REMOTE_PASS`
- evidence artifact: `9909420376`
- production write: false
- publish/activate: false
- one-time update workflow removed after successful readback.

## Execution-API observation
A separate read-only attempt to fetch n8n execution data through the configured API key returned HTTP 403. The audit performed no write and was removed. Internal certification therefore executes the exact JavaScript embedded in the reconstructed candidate Code nodes with controlled fixtures, in addition to the live owner-observed customer-facing journeys and remote candidate readback.

## Final remote confirmation
A fresh read-only remote audit was executed after CR-107-02 deployment and final material review:
- run: `33811422682`
- job: `100833880066`
- `WU107_CR10702_REMOTE_PASS`
- `WU107_FINAL_REMOTE_IDENTITY_ASSERT_PASS`
- remote version remained `79a38b64-336a-4bfd-8c65-ed5b0ef1f247`
- `active=false`
- Production write: false

## Next gate
No additional WU-107 runtime test is pending. The remaining gate is explicit Owner approval for LOCK.

## Lock rule
WU-107 cannot be locked without explicit Owner approval.
