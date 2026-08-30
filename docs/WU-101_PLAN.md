# WU-101 Conversation Analytics — Implementation Plan

Status: SPEC_FROZEN — READY_FOR_IMPLEMENTATION
Issue: #12
Branch: `wu/101-conversation-analytics`

## 1. Baseline
Locked current Production baseline:
- workflow: `SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json`;
- exact Production artifact remains read-only;
- existing WU97 observability creates and redacts `SPM_TELEMETRY_V2`;
- current customer response/business path must remain behaviorally equivalent.

## 2. Freeze-review correction
RC4.3.3 allows `input.correlation_id`, so correlation ID is not guaranteed to be internally generated. WU-101 therefore does not persist correlation ID and does not use it to construct analytics session grouping.

Frozen identifier rules:
- create a new internal `event_id` for every analytics event;
- create a new internal random `analytics_session_key` on first Redis-backed state initialization;
- preserve that session key through the existing non-destructive Redis state merge;
- never derive the key from session ID, correlation ID, raw message, contact data, names, phone or email;
- increment `turn_index` once per customer turn.

## 3. Smallest safe implementation
Do not refactor unrelated graph sections. Create a new STAGING candidate derived from the exact locked baseline and add only WU-101-owned changes.

### Change A — analytics state in WU90 state merge
Add:

```json
{
  "analytics": {
    "session_key": "conv-<internally-generated-random-id>",
    "turn_index": 1
  }
}
```

Rules:
- preserve existing `session_key`;
- initialize only when absent;
- increment `turn_index` exactly once per incoming customer turn;
- persist via the existing Redis state save, not a second Redis write;
- generated values must be system-generated and independent of customer-controlled identifiers.

### Change B — strict event builder after WU97 redaction
Add Code node:
`Build WU101 Conversation Analytics Event`

Build `SPM_WU101_CONVERSATION_ANALYTICS_V1` with explicit field assignment only. Never spread arbitrary runtime JSON into the event.

Contract:
`contracts/WU101_CONVERSATION_ANALYTICS_EVENT_V1.schema.json`

Create `event_id` internally for each emitted event. Do not persist `correlation_id`.

### Change C — dedicated analytics logger path
Create a new STAGING logger path/subworkflow:

`[STAGING] WU101 Conversation Analytics Logger`

Target flow:

`Validate WU101 Event → Append CONVERSATION_ANALYTICS Row → Build Logger Result`

Main candidate around observability:

`Redact WU97 Observability Telemetry → Build WU101 Conversation Analytics Event → Dispatch Analytics Logger → Restore Customer Context → existing response persistence/final response`

Requirements:
- STAGING only during implementation;
- analytics result never determines business success;
- customer path restores original response/business context after dispatch;
- logger failure must be fail-open and observable;
- no analytics retry may repeat lead/booking/handoff/payment operations.

### Change D — V1 analytics sink
Use a dedicated `CONVERSATION_ANALYTICS` tab in the existing SPM runtime workbook.

Column order:
1. event_schema
2. event_id
3. event_timestamp
4. workflow_release
5. channel
6. analytics_session_key
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
29. correlation_id_logged
30. secret_values_logged

No raw question/message, raw session ID, correlation ID, lead ID, phone, email, names or contact data column is allowed.

The sheet is operational analytics data only. It must not be used as Sales Agent prompt input or a knowledge/source-gate source.

## 4. Deterministic mappings
- primary intent: `classification.spm_intent`
- secondary intent: `classification.secondary_spm_intent`
- confidence: validated classifier confidence
- language: validated classifier language, else safe language hint, else `unknown`
- journey stage: existing journey decision
- source gate: existing source-gate decision/result
- classifier route: existing route
- clarification: existing clarification route/flag
- fallback: existing fallback route
- human requested: existing handoff/support request signal only
- lead outcome: existing verified WU95 write/state truth only
- lead ID: boolean presence only
- opt-out: existing nurture state
- action/degraded/recovery/duration/error codes: existing runtime/WU97 evidence

No second model call is permitted to create analytics fields.

## 5. Failure model
Analytics is secondary observability.

On logger/sink failure:
- answer remains unchanged;
- lead/business result remains unchanged;
- response still returns;
- an analytics-specific warning/error is recorded for engineering evidence;
- no retry storm;
- no duplicate business write.

## 6. Tests
### Static
- candidate JSON parse;
- unique node IDs/names;
- event schema validity;
- `additionalProperties=false`;
- exact allowlist;
- forbidden-field/value scan for message/session/correlation/contact/secret data;
- Production SHA unchanged;
- Production workflow ID absent from writable target configuration.

### Contract cases
1. direct intent;
2. clarification;
3. fallback;
4. human request;
5. lead pending;
6. verified lead created;
7. verified lead updated;
8. lead failed;
9. opt-out;
10. degraded/recovery.

Every contract case must validate schema, privacy invariants, deterministic booleans/outcomes and absence of second-model inference.

### Runtime STAGING
- first turn: internal session key + turn 1;
- second turn: same key + turn 2;
- append/readback exact field match;
- logger unavailable/misconfigured: chat response/business truth preserved;
- EN/AR/FR representative parity.

### Regression
Compare selected RC4.3.3 customer-facing response and business truth fields against WU-101 STAGING. Analytics may add observability only; customer/business outcome may not regress.

## 7. Review gate
After static/contract/runtime evidence, run one material review only. Report only requirement violation, PII/secret leakage, behavior regression, false success, blocking analytics dependency, duplicate/unsafe persistence or material architecture defect.

## 8. Release boundary
Passing WU-101 STAGING does not authorize Production modification.

After WU-101 approval:
1. create a new immutable Production RC from the tested candidate;
2. verify SHA and regression;
3. run the normal release/human approval gate;
4. retain rollback to locked RC4.3.3.

## 9. DAG
```text
GitHub cutover complete
        ↓
HARD-001 PASS
        ↓
WU-101 SPEC FROZEN
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

## 10. Not in WU-101
- unanswered-question queue/content;
- analytics dashboard/KPIs;
- automatic KB updates;
- live human-handoff execution;
- WhatsApp notification;
- scheduling/payment enablement.
