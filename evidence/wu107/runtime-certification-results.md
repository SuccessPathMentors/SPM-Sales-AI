# WU-107 — Owner-Observed Runtime Certification Results

Status: IN_PROGRESS — CR-107-01 DEPLOYED / RT-107-05 RETEST PENDING
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
Customer-facing checkpoints passed so far: `4 / 15`

| Test | Result | Evidence / finding |
|---|---|---|
| RT-107-01 — EN explicit human request | PASS-CUSTOMER-FACING / INTERNAL PENDING | Queue-truth response, no false human acceptance. |
| RT-107-02 — Same-session repeat / idempotency | PASS-CUSTOMER-FACING / INTERNAL PENDING | Existing queue request reused visibly; internal duplicate-record evidence pending. |
| RT-107-03 — AR explicit human request | PASS-CUSTOMER-FACING / INTERNAL PENDING | Arabic queue-truth response, no false acceptance. |
| RT-107-04 — FR explicit human request | PASS-CUSTOMER-FACING / INTERNAL PENDING | French queue-truth response, no false acceptance. |
| RT-107-05 — Technical support interrupts sales | **RETEST PENDING AFTER CR-107-01** | Initial V1 attempt failed: technical support stopped sales but returned legacy `Automatic human handoff is not enabled...` wording. Root cause fixed and CR-107-01 is now deployed/remote-verified. Re-run only this test. |
| RT-107-06 — Complaint escalation | PENDING | Run only after RT-107-05 retest passes. |
| RT-107-07 — Pricing must not hand off | PENDING | — |
| RT-107-08 — Short query must not hand off | PENDING | — |
| RT-107-09 — Handoff after existing sales context | PENDING | — |
| RT-107-10 — Queue PII minimization inspection | PENDING | — |
| RT-107-11 — Queue receipt != human acceptance | PENDING | — |
| RT-107-12 — Controlled authoritative acceptance fixture | PENDING | — |
| RT-107-13 — Corrupt queue record fail-closed | PENDING | — |
| RT-107-14 — Redis load failure injection | PENDING | — |
| RT-107-15 — Redis save failure injection | PENDING | — |

## RT-107-05 initial failure and root cause
Initial sequence:
1. `My son is in Grade 8 and needs Math tutoring. How much does it cost?`
2. `The portal is not working. I need help.`

Initial V1 response on the support turn:
`I have preserved your support request and the known conversation context. Automatic human handoff is not enabled in this release candidate.`

Root cause proved from exact-lineage code/topology:
- the technical-support turn did reach the WU-107 insertion point;
- WU96 identifies `technical_issue` as current-turn support and sets `support_requires_handoff=true`;
- WU-107 V1 used a narrower classifier allowlist and did not consume the authoritative WU96/WU106 current-turn support metadata.

CR-107-01 correction:
- consumes current-turn WU96 support decision + WU106 support override metadata;
- maps `technical_issue` / `technical_support` to `TECHNICAL_SUPPORT`;
- maps complaint to `COMPLAINT_ESCALATION`;
- does not allow sticky historical support state alone to initiate a new handoff;
- changes only one WU-107 node; topology and all 141 locked WU-106 nodes remain unchanged.

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

## Required next owner test — RT-107-05 Retest only
Start a new Test Chat session and repeat exactly:
1. `My son is in Grade 8 and needs Math tutoring. How much does it cost?`
2. `The portal is not working. I need help.`

Expected second-turn behavior after CR-107-01:
- sales stops;
- technical support is routed to WU-107 queue execution;
- customer sees truthful support-queue wording;
- old `Automatic human handoff is not enabled in this release candidate.` wording must not appear;
- no claim that a specific human accepted the case.

## Lock rule
WU-107 cannot advance to READY_FOR_REVIEW until RT-107-05 retest and remaining runtime/internal evidence gates pass.
