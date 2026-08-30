# WU94 — Trial / Scheduling Truth Layer QA

Status: PROTOTYPE STATIC PASS — runtime live adapter NOT configured
Artifact: SPM_E2E_Sales_Agent_Greenfield_WU94_Trial_Scheduling_Truth_Layer_2026-08-20.json
SHA-256: 3f6263dbe38496ef29b237a8d834ac9da019e54aa3babebbd0a86e097adef22e

## Scope
WU94 adds the deterministic truth boundary for free-trial requests, availability, timezone handling, scheduling, and booking verification. It does not invent or configure an external scheduling endpoint.

## Current Operating Model
- Trial/scheduling remains admin-controlled.
- Request lifecycle contract: WAITING_FOR_ASSIGNMENT → TEACHER_ASSIGNED → SCHEDULED.
- Automatic teacher selection: disabled.
- Automatic slot booking: disabled.
- Availability may be stated only from an approved live scheduling result.
- Booking may be confirmed only when tool success=true AND booking_id is non-empty.
- Country alone is never enough to infer timezone.

## Static QA
Result: 21/21 PASS.
- JSON valid; active=false; no top-level workflow ID/version ID.
- 76 nodes with unique names and IDs.
- Zero dangling graph references.
- No HTTP Request or Execute Workflow scheduling action was invented.
- No Google Sheets production write node added.
- Test Redis namespace remains preserved.
- False availability and false booking claims are rewritten by deterministic guard.

## Contract Tests
Result: 8/8 PASS.
Covered: RT-019 timezone requirement, RT-020 Toronto schedule request without invented timezone, RT-021 country-only timezone refusal, RT-027 booking confirmation truth gate, RT-032 pricing + scheduling multi-intent, ready trial request without false booking, booking_id alone insufficient without live verification, and valid IANA timezone with availability still unverified until tool success.

## Blocking Integration Gap
No approved live scheduling/LMS API endpoint, credential reference, or booking subworkflow identifier is present in the current source set. Therefore WU94 cannot be runtime-certified as live scheduling yet. The safe adapter result is NOT_CONFIGURED.

## Release Decision
Prototype/static PASS only. Production cutover unauthorized. Runtime certification remains dependency-gated from WU88 forward.

## Next Unit
WU95 — deterministic lead conversion, consent, UPSERT, correction, dedupe, and handoff. WU95 must not falsely mark a trial as scheduled; it may persist a request/pipeline state only after the corresponding deterministic write succeeds.
