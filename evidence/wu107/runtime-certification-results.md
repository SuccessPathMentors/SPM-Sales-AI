# WU-107 — Owner-Observed Runtime Certification Results

Status: BLOCKED_RUNTIME_FINDING — CR-107-01 REQUIRED
Issue: #67
PR: #68
STAGING workflow: `RtI7hxjNb6Z0JL0D` (`[STAGING] SPM_WU107_HUMAN_HANDOFF_EXECUTION_V1`)
STAGING version before CR-107-01: `f52c7000-539f-4675-9fe8-2addc9354077`
Candidate SHA-256 before CR-107-01: `fc4263b6bf029195a58b819ce4b06d6f499090d39017ff6ca906f173b7443f59`
Node count: 151
Remote state: `active=false`
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
Customer-facing checkpoints passed before block: `4 / 15`

| Test | Result | Evidence / finding |
|---|---|---|
| RT-107-01 — EN explicit human request | PASS-CUSTOMER-FACING / INTERNAL PENDING | Session suffix `c9543…`: queue-truth response, no false human acceptance. |
| RT-107-02 — Same-session repeat / idempotency | PASS-CUSTOMER-FACING / INTERNAL PENDING | Same session: response says request is already in queue; internal duplicate-record evidence pending. |
| RT-107-03 — AR explicit human request | PASS-CUSTOMER-FACING / INTERNAL PENDING | Arabic queue-truth response, no false acceptance. |
| RT-107-04 — FR explicit human request | PASS-CUSTOMER-FACING / INTERNAL PENDING | French queue-truth response, no false acceptance. |
| RT-107-05 — Technical support interrupts sales | **FAIL — BLOCKING** | Session suffix `66b75…`. Pricing turn passed. On `The portal is not working. I need help.` sales stopped, but the response was the locked WU-106 legacy support text: `I have preserved your support request and the known conversation context. Automatic human handoff is not enabled in this release candidate.` WU-107 queue execution did not occur. |
| RT-107-06 — Complaint escalation | BLOCKED BY CR-107-01 | Not run after blocking routing failure. |
| RT-107-07 — Pricing must not hand off | PENDING | — |
| RT-107-08 — Short query must not hand off | PENDING | — |
| RT-107-09 — Handoff after existing sales context | PENDING | — |
| RT-107-10 — Queue PII minimization inspection | PENDING | — |
| RT-107-11 — Queue receipt != human acceptance | PENDING | — |
| RT-107-12 — Controlled authoritative acceptance fixture | PENDING | — |
| RT-107-13 — Corrupt queue record fail-closed | PENDING | — |
| RT-107-14 — Redis load failure injection | PENDING | — |
| RT-107-15 — Redis save failure injection | PENDING | — |

## RT-107-05 blocking finding
Expected:
- technical support interrupts sales;
- WU-107 handoff execution creates/reuses a durable queue record;
- customer sees queue truth only after tool evidence.

Observed:
- sales was interrupted correctly;
- customer received the pre-WU-107 legacy support message saying automatic human handoff is not enabled;
- therefore the technical-support branch did not reach/consume the WU-107 handoff execution path used successfully by explicit `human_handoff` requests.

### Initial root-cause hypothesis to prove before patch
WU-107 V1 is inserted only after `Deterministic Action Gateway [RC3 SCOPE LOCK]`. Explicit `human_handoff` reaches that insertion point, while locked technical-support handling may bypass the gateway and rejoin later at telemetry/final response. A second possible cause is that the support route reaches the WU-107 node but no longer exposes a supported current `classification.spm_intent` at that point.

CR-107-01 must diagnose exact topology first and make the smallest additive WU-107-only correction. Locked WU-106 nodes must remain byte-for-byte unchanged.

## P0 stop conditions
Testing remains stopped until CR-107-01 is deployed and RT-107-05 is re-tested. Production remains untouched.

## Lock rule
WU-107 cannot advance to READY_FOR_REVIEW while this blocking runtime finding is open.
