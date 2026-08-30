# WU-101 Conversation Analytics — Plan

Status: READY_FOR_FREEZE_REVIEW
Issue: #12
Branch: `wu/101-conversation-analytics`

## 1. Baseline
Current locked production baseline:
- workflow: `SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json`
- exact artifact remains read-only;
- existing observability nodes already create/redact `SPM_TELEMETRY_V2`;
- existing customer response path must remain behaviorally equivalent.

## 2. Smallest safe implementation
Do not refactor unrelated graph sections.

Create a new STAGING candidate derived from the exact production baseline and add only the WU-101-owned changes below.

### Change A — initialize pseudonymous analytics state in WU90 state merge
Add a non-customer-facing `sales_state.analytics` object:

```json
{
  "session_key": "conv-<first-correlation-id>",
  "turn_index": 1
}
```

Rules:
- preserve an existing `session_key`;
- never derive the persisted analytics key from raw PII fields;
- use first-turn `correlation_id` as the seed because it is already a generated non-customer identifier;
- increment `turn_index` once per customer turn;
- persist through the existing Redis state save rather than adding a separate Redis write.

### Change B — build a strict WU-101 analytics event after WU97 redaction
New Code node: `Build WU101 Conversation Analytics Event`.

Input source is the already-redacted final context. Build a new object by explicit field allowlist only. Never spread arbitrary source JSON into the event.

Contract: `contracts/WU101_CONVERSATION_ANALYTICS_EVENT_V1.schema.json`.

### Change C — dispatch to a dedicated analytics logger
Create a new STAGING subworkflow:

`[STAGING] WU101 Conversation Analytics Logger`

Proposed flow:

`Execute Workflow Trigger → Validate WU101 Event → Append CONVERSATION_ANALYTICS Row → Build Logger Result`

Main candidate flow around observability:

`Redact WU97 Observability Telemetry → Build WU101 Conversation Analytics Event → Dispatch WU101 Analytics Logger → Restore Customer Context → existing Save AI Message → existing final response`

Dispatch requirements:
- non-production only during implementation/test;
- no wait for downstream processing where supported;
- fail-open/continue path if dispatch cannot execute;
- final customer response must continue from restored pre-dispatch context;
- analytics logger result never determines business success.

### Change D — initial sink
Proposed V1 sink: new `CONVERSATION_ANALYTICS` sheet tab in the existing SPM runtime workbook already used by the workflow.

The sheet is operational analytics data, not a knowledge source. It must not be loaded into the Sales Agent prompt or source-gate retrieval.

Proposed columns, in contract order:
1. event_schema
2. event_timestamp
3. workflow_release
4. channel
5. analytics_session_key
6. correlation_id
7. turn_index
8. primary_intent
9. secondary_intent
10. confidence
11. language
12. journey_stage
13. source_gate
14. classifier_route
15. clarification_used
16. fallback_used
17. human_requested
18. lead_outcome
19. lead_id_present
20. opt_out
21. action_status
22. degraded
23. recovery_mode
24. duration_ms
25. error_codes
26. pii_redacted
27. raw_message_logged
28. raw_session_logged
29. secret_values_logged

No raw question/message column is allowed in WU-101. Raw/redacted question handling belongs to WU-102.

## 3. Deterministic mappings
### Classifier signals
- primary = `classification.spm_intent`
- secondary = `classification.secondary_spm_intent`
- confidence = validated `classification.confidence`
- language = validated `classification.language`, else `language_hint`, else `unknown`
- classifier route = existing `classifier_route`

### UX signals
- clarification = `customer_clarification_required === true` or classifier route `clarify`
- fallback = classifier route `fallback`

### Human signal
`human_requested=true` if any of:
- primary intent is `human_handoff`;
- secondary intent is `human_handoff`;
- `wu95_handoff_contract.requested === true`;
- support state/decision requires handoff.

This records the request signal only. It must not imply that live handoff execution occurred.

### Lead outcome
Use existing WU95 verified evidence only:
- verified successful operation `created` → `created`;
- verified successful operation `updated` → `updated`;
- lead/registration flow awaiting confirmation/write → `pending`;
- attempted/required write with verified failure → `failed`;
- otherwise → `none`.

Persist only `lead_id_present: boolean`, never the actual lead ID in WU-101 analytics.

## 4. Failure model
Analytics is secondary observability.

Expected behavior on analytics failure:
- customer answer remains unchanged;
- lead result remains unchanged;
- business action truth remains unchanged;
- runtime should expose an analytics-specific warning/error code for engineering evidence;
- no retry storm or duplicate lead/business action may occur.

No hidden retry of business actions is permitted.

## 5. Tests
### Static
- JSON candidate parse.
- unique node IDs/names.
- strict event allowlist.
- forbidden names/value-pattern scan.
- Production workflow artifact unchanged.
- Production workflow ID not used as writable deployment target.

### Contract cases
1. direct FAQ/commercial intent.
2. low-confidence clarification.
3. classifier fallback.
4. human handoff request.
5. lead pending confirmation.
6. verified lead created.
7. verified lead updated.
8. lead write/readback failure.
9. sticky opt-out.
10. degraded/fail-closed runtime.

For every case assert:
- contract valid;
- no forbidden fields;
- correct deterministic booleans/outcome;
- no model-generated reclassification.

### Runtime STAGING
- first turn creates analytics session key + turn index 1;
- second turn reuses same key + turn index 2;
- append/readback row exact match;
- logger unavailable/misconfigured test: response still returned correctly;
- EN/AR/FR representative parity.

### Regression
Compare selected baseline RC4.3.3 outputs and truth fields against the WU-101 STAGING candidate. Analytics fields may differ/add; customer answer and business outcome may not regress.

## 6. Review gate
One material code review after static/contract/runtime evidence.

Review only:
- requirement violation;
- PII/secret leakage;
- behavior regression;
- false business success;
- blocking analytics dependency;
- duplicate/unsafe persistence;
- material architecture defect.

No speculative redesign or style-only loop.

## 7. Release boundary
Passing WU-101 STAGING does not authorize direct Production modification.

After approval:
1. create a new immutable Production RC from the tested candidate;
2. verify exact SHA and regression;
3. use the normal release/human approval process;
4. keep rollback to the current RC4.3.3 baseline available.

## 8. Dependencies / DAG
```text
GitHub cutover complete
        ↓
HARD-001 main protection
        ↓
WU-101 spec freeze
        ↓
Create analytics sheet + STAGING logger
        ↓
Create WU-101 STAGING candidate
        ↓
Static + contract tests
        ↓
STAGING runtime + failure injection
        ↓
One material review
        ↓
Owner approval
        ↓
New Production RC / separate release gate
```

## 9. Not in this WU
- unanswered-question content queue;
- analytics dashboard;
- automatic KB changes;
- handoff adapter execution;
- WhatsApp notification;
- new scheduling/payment capabilities.
