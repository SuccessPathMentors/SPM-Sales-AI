# WU97 — Reliability / Privacy / Security QA

Status: PROTOTYPE STATIC PASS — runtime certification NOT RUN
Artifact: SPM_E2E_Sales_Agent_Greenfield_WU97_Reliability_Privacy_Security_2026-08-21.json
SHA-256: 9946d7de5cbcfd15feb1dcb91a5f97aec9c5ab9900794e855e5f20de092d93dc

## Scope
WU97 hardens the inactive Greenfield stack for bounded retries, fail-closed behavior, observability, privacy, and security without enabling production writes.

## Reliability Controls
- Input security guard executes before Redis, Google Sheets, or model calls.
- Messages above 8,000 characters or with excessive control characters are blocked before external processing.
- Classifier, entity extractor, and Sales Agent model calls use bounded retries only.
- Read-only Lead lookup now has bounded retry plus an explicit error branch; lookup failure becomes LEAD_LOOKUP_FAILED and can_upsert=false.
- Existing Google Sheets/Redis error-output branches remain wired to safe fallback paths.
- No retry is allowed for business validation failures.
- Irreversible write retries require an idempotency key.
- State-persistence failure forces the deterministic gateway into fail-closed mode.

## Error Taxonomy
INPUT_SECURITY, MODEL, SOURCE_READ, STATE_READ, STATE_WRITE, VALIDATION, LIVE_TOOL, CRM, PRIVACY, CONFIG, INTERNAL.

## Privacy / Security Controls
- User input is explicitly treated as untrusted and cannot override system instructions.
- Telemetry V2 contains correlation_id but no raw session_id or raw customer message.
- Telemetry includes error/warning codes only and scrubs email/phone patterns.
- Secrets/password/token/authorization/API-key fields are prohibited from telemetry.
- Redis persistence remains restricted to test namespace state only.
- Lead UPSERT remains disabled and disconnected.
- Sticky opt-out remains preserved through WU97 fail-closed handling.

## Static QA
Result: 54/54 PASS.
Verified JSON validity, inactive state, no workflow identity reuse, 108 unique nodes, zero dangling references, WU97 security/reliability topology, retry coverage, wired error outputs, telemetry redaction, no active production Sheets/HTTP/ExecuteWorkflow writes, disabled/disconnected lead UPSERT, test-only Redis writes, and fail-closed/idempotency controls.

## Contract Regression
Result: 18/18 PASS.
Covered input-size/control-character blocking, model retries, lead lookup failure, state-save failure, missing scheduling/support/follow-up adapters, fail-closed action gateway, sticky opt-out preservation, telemetry PII/session exclusion, and disabled production lead write.

## Release Decision
WU97 is Prototype/Static PASS only. It is not production-certified. The first blocking runtime gate remains WU88 semantic classifier runtime, followed by dependency-ordered certification of downstream units.

## Next Unit
WU98 — multilingual/conversation regression and red-team expansion across EN/AR/FR, code-switching, ambiguity, prompt-injection resistance, PII safety, opt-out, support overrides, pricing/source gates, scheduling truth, and conversion truth.
