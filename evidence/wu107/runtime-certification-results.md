# WU-107 — Owner-Observed Runtime Certification Results

Status: IN_PROGRESS — CR-107-01 DEPLOYED / RT-107-07 PASSED
Issue: #67
PR: #68
STAGING workflow: `RtI7hxjNb6Z0JL0D` (`[STAGING] SPM_WU107_HUMAN_HANDOFF_EXECUTION_V1`)
Current STAGING release: `CR-107-01`
Current STAGING version: `13b455a8-1318-4f35-8adc-f42f13e49e76`
Current candidate SHA-256: `a258d9c294fe56c43ea120b14739119f294f7254b03cbecd9f21bf7831ac8809`
Node count: 151
Remote state: `active=false`
Remote verification: `WU107_CR10701_REMOTE_PASS`
Production mutation allowed: false

## Automated prerequisites / CR-107-01 status
- Exact locked WU-106 lineage: PASS
- WU-107 V1 static candidate: PASS
- WU-107 handoff contract: PASS
- 24-scenario deterministic matrix: PASS
- 10 provider-neutral executable runtime cases: PASS
- WU-106 48-scenario regression matrix: PASS
- CR-107-01 support-signal regression: PASS (`10` cases)
- `technical_issue` recovery: PASS
- stale support state alone guard: PASS
- WU-106 locked nodes mutated: false
- CR-107-01 STAGING update: PASS (`UPDATE_INACTIVE_NONPROD`)
- Remote readback after update: PASS
- One-time CR-107-01 update workflow removed after deployment: PASS
- Production write: false
- Publish/activate: false

## Owner-observed live score
Customer-facing checkpoints passed so far: `7 / 15`

| Test | Result | Evidence / finding |
|---|---|---|
| RT-107-01 — EN explicit human request | PASS-CUSTOMER-FACING / INTERNAL PENDING | Queue-truth response, no false human acceptance. |
| RT-107-02 — Same-session repeat / idempotency | PASS-CUSTOMER-FACING / INTERNAL PENDING | Existing queue request reused visibly; internal duplicate-record evidence pending. |
| RT-107-03 — AR explicit human request | PASS-CUSTOMER-FACING / INTERNAL PENDING | Arabic queue-truth response, no false acceptance. |
| RT-107-04 — FR explicit human request | PASS-CUSTOMER-FACING / INTERNAL PENDING | French queue-truth response, no false acceptance. |
| RT-107-05 — Technical support interrupts sales | **PASS AFTER CR-107-01 — CUSTOMER-FACING / INTERNAL PENDING** | Retest session suffix `1c9c8…`: pricing answered first; technical issue stopped sales and entered truthful support-queue flow. |
| RT-107-06 — Complaint escalation | **PASS-CUSTOMER-FACING / INTERNAL PENDING** | Session suffix `8a406…`: complaint interrupted sales and entered truthful support-queue flow. |
| RT-107-07 — Pricing must not hand off | **PASS-CUSTOMER-FACING** | Session suffix `6faf9…`: `How much are your tutoring packages?` returned the normal pricing answer only. No support queue, handoff, complaint, or escalation wording appeared. |
| RT-107-08 — Short query must not hand off | READY TO RUN | Next owner test. |
| RT-107-09 — Handoff after existing sales context | PENDING | — |
| RT-107-10 — Queue PII minimization inspection | PENDING | — |
| RT-107-11 — Queue receipt != human acceptance | PENDING | — |
| RT-107-12 — Controlled authoritative acceptance fixture | PENDING | — |
| RT-107-13 — Corrupt queue record fail-closed | PENDING | — |
| RT-107-14 — Redis load failure injection | PENDING | — |
| RT-107-15 — Redis save failure injection | PENDING | — |

## CR-107-01 root cause and correction
The initial RT-107-05 failure was caused by WU-107 V1 consuming a narrower classifier allowlist than the authoritative WU96/WU106 current-turn support signals. CR-107-01 consumes the current-turn support decision/override, maps technical support and complaints into the WU-107 execution contract, and explicitly prevents sticky historical support state alone from initiating a new handoff. Only one WU-107 node changed; topology and all 141 locked WU-106 nodes remain unchanged.

## CR-107-01 deployment evidence
- GitHub Actions update run: `33790623526`
- job: `100766072749`
- operation: `UPDATE_INACTIVE_NONPROD`
- artifact SHA: `a258d9c294fe56c43ea120b14739119f294f7254b03cbecd9f21bf7831ac8809`
- workflow: `RtI7hxjNb6Z0JL0D`
- remote version: `13b455a8-1318-4f35-8adc-f42f13e49e76`
- `active=false`
- remote verifier: `WU107_CR10701_REMOTE_PASS`
- update evidence artifact: `9907166309`
- production write: false

## RT-107-07 pricing no-handoff evidence
Owner-observed session suffix: `6faf9…`

Input:
`How much are your tutoring packages?`

Observed response:
`Our tutoring packages are priced as follows: 4 classes for USD 110, 8 classes for USD 220, and 12 classes for USD 280. The 12-class package offers the lowest price per lesson.`

Customer-facing acceptance criteria:
- normal pricing flow preserved: PASS
- no support queue wording: PASS
- no human handoff wording: PASS
- no complaint/support escalation: PASS
- no sales interruption: PASS

## Required next owner test — RT-107-08 Short query must not hand off
Run in a new Test Chat session.

Expected behavior:
- a short ambiguous sales query must stay in normal clarification/sales handling;
- WU-107 must not create or claim a support queue request;
- no support/handoff wording should appear solely because the message is short or ambiguous.

## Lock rule
WU-107 cannot advance to READY_FOR_REVIEW until remaining runtime/internal evidence gates pass.
