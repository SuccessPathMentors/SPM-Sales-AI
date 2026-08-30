# WU87 Architecture Contracts — Greenfield E2E Sales Agent

Status: BASELINE CONTRACTS v1.0
Feature: 011-e2e-sales-agent-greenfield
Scope: Architecture only; no production writes or irreversible actions.

## 1. Session Envelope — SPM_E2E_V1
Required fields:
- schema_version
- workflow_release
- workflow_mode
- correlation_id
- session_id
- sales_state_key
- received_at
- test_mode
- synthetic_session
- channel
- language_hint
- message.raw

Safety rule: WU87 is TEST_ONLY. Non-test traffic must stop before state, model, knowledge, or action nodes.

## 2. Durable Sales State — SPM_SALES_STATE_V1
Top-level domains:
- session_id / lead_id / preferred_language
- journey
- classifier
- entities.global + entities.students[]
- commercial
- trial
- scheduling
- conversion
- support
- nurture
- recovery
- flags

Merge rule: non-destructive. Existing durable values survive unless an approved current-turn source explicitly updates them. Latest explicit customer correction wins for customer-owned fields. System/live-source fields remain source-owned.

Critical state rules:
- opt_out=true is sticky until an approved opt-in rule is satisfied.
- booking confirmation requires successful scheduling plus booking_id.
- multiple children remain separate student profiles; grades/subjects are never merged across children.
- known fields are not re-asked unless validation/correction requires it.

## 3. Classifier Output — SPM_CLASSIFIER_OUTPUT_V1
Catalog: SPM_V2_62_INTENTS.

Required output:
- spm_intent
- confidence 0..1
- threshold
- ambiguous
- source_gate
- risk_tier
- sales_stage

Optional:
- secondary_spm_intent
- required_entities[]
- language
- rationale_code

Default threshold: 0.85 unless the intent catalog overrides it.
Low-confidence rule: no irreversible action may be executed from an unresolved/low-confidence classification.

## 4. Entity Output — SPM_ENTITY_OUTPUT_V1
Entity record shape:
- entity
- raw
- canonical
- confidence
- source
- status = valid | needs_validation | rejected

Canonical entity domains include subject, grade, curriculum, country, province, city, timezone, preferred schedule, teaching/preferred language, teacher preference, academic goal/topic/exam, package, number_of_students, parent/student names, phone, email, lead/student/teacher/booking/lesson identifiers, payment fields, currency, lead stage/score, trial/registration status, classifier fields and opt_out.

Critical entity rules:
- timezone is never derived from country alone.
- province/state must belong to country.
- teacher gender/language/origin are preferences or verified facts only; never guarantees.
- names are not aggressively normalized.
- email and phone are validated before CRM persistence.
- PII is excluded from telemetry payloads.

## 5. Journey + Next Best Action — SPM_NEXT_BEST_ACTION_V1
Supported stages:
none, discovery, need, consideration, pricing, trial, scheduling, conversion, objection, nurturing, support, recovery.

Decision fields:
- stage
- goal
- next_best_action
- required_missing_fields[]
- support_override
- opt_out_override
- handoff_override

Override precedence:
opt_out → support → human_handoff → recovery → normal sales journey.

Question policy: answer first, then ask at most one purposeful question for the smallest missing qualifier; never restart qualification.

## 6. Source / Tool Gate — SPM_SOURCE_GATE_V1
Allowed gates from the current 62-intent catalog:
- APPROVED_KB_OR_LOGIC
- APPROVED_CURRICULUM_SOURCE
- PACKAGES_LIVE_CONFIG
- AUTHORIZED_OFFER_REQUIRED
- MARKET_PAYMENT_CONFIG
- PAYMENT_LIVE
- POLICY_AND_LIVE_STATE
- VERIFIED_TEACHER_OR_POLICY
- SCHEDULING_LIVE
- CRM_VALIDATION

Truth rule: commercial and operational facts require their approved/config/live source. Unsupported claims are blocked, not improvised.

## 7. Sales Agent Output — SPM_SALES_AGENT_OUTPUT_V1
Primary identity: consultative Sales Agent, not FAQ bot.

Structured fields:
- answer_text
- purpose
- recommendation
- purposeful_question
- proposed_action
- action_requires_gateway
- claims_source_refs[]
- handoff_requested
- stop_nurture

Behavior:
- answer first;
- acknowledge context;
- ask one purposeful question when needed;
- preserve known information;
- guide toward the next useful sales step;
- no pressure, unsupported promise, invented price, invented availability, invented teacher claim, or false confirmation.

Hard boundary: the model may propose an action but may not directly perform irreversible business actions.

## 8. Deterministic Action Gateway — SPM_ACTION_GATEWAY_V1
Irreversible action examples:
- lead_upsert
- booking_create / booking_change
- payment_action
- human_handoff_create
- contact_update
- opt_out_write

Required before success:
1. deterministic validation;
2. authorization/source gate;
3. tool execution;
4. explicit success result/reference where applicable;
5. only then may the customer-facing response claim success.

WU87 allowlist: none. Gateway is NOOP only.

## 9. Telemetry — SPM_TELEMETRY_V1
Required correlation fields:
- timestamp
- correlation_id
- session_id
- workflow_release
- test_mode
- intent / confidence
- journey_stage
- source_gate
- proposed_action
- action_status / action_executed
- duration_ms
- pii_redacted=true

Telemetry must never copy raw phone, email, names, transaction references, or sensitive lesson/payment data.

## 10. WU87 Test Safeguards
- top-level workflow active=false;
- no top-level workflow id/versionId in export;
- non-test branch stops immediately;
- Redis load exists only as a disabled architecture placeholder until WU90;
- no Redis writes;
- no Google Sheets writes;
- no CRM/booking/handoff execution;
- no OpenAI/model node in WU87;
- no production success message can be generated.

WU87 completion means the backbone/contracts are statically valid. It does not certify classifier, Sales Agent, Redis, scheduling, CRM, or production runtime behavior.
