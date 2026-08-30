# WU90 — Durable Sales State & Journey Static QA

Status: PASS — static/test-only architecture validated; n8n Redis runtime still required.
Artifact: SPM_E2E_Sales_Agent_Greenfield_WU90_Durable_State_Journey_2026-08-20.json
SHA-256: 18a8487a50b53bf9638bcfdc251cc39a05f2989531a1de8e4c9e8df0ff484b77

## Implemented
- Redis state load enabled only after the Greenfield test-session guard.
- Test namespace: spm:test:sales:*; non-test namespace is blocked before Redis operations.
- Non-destructive state merge retains known values and does not clear them with empty extraction.
- Student profiles merge by stable student_ref and remain separate.
- Sticky opt-out: explicit opt_out=true or not_interested sets opt-out; later empty/false state cannot silently clear it.
- Support, human handoff and recovery override ordinary sales progression.
- Journey stage and next-best-action are derived from the 62-intent classification and durable state.
- required_missing_fields are computed from current state; known data is not re-asked.
- Scheduling intents require timezone; country alone is insufficient.
- State is serialized and saved only to the test Redis namespace with TTL.
- Redis load/save use bounded retry and explicit safe fallback/failure context.
- No Lead, CRM, booking, payment, handoff or production Google Sheets write exists in WU90.

## Static QA
16/16 PASS:
- inactive workflow; no top-level workflow ID/versionId;
- 40/40 unique node names and IDs;
- zero dangling graph connections;
- test and blocked namespaces enforced;
- Redis load/save retry/error paths present;
- sticky opt-out, student separation, no-reask, timezone, support and recovery rules present;
- only write node is Save Sales State [TEST NAMESPACE ONLY].

## Runtime Boundary
Redis persistence across real n8n executions/refresh/re-entry has not yet been certified. Because WU88 semantic runtime remains upstream, WU90 is a completed prototype/static gate, not a production-certified unit.

## Decision
WU90 prototype/static gate: PASS.
Production release: NOT AUTHORIZED.
Next build unit may be prototyped: WU91 — Knowledge Retrieval & Source Gates.
Certification dependency remains: WU88 runtime → WU89 runtime → WU90 Redis runtime.
