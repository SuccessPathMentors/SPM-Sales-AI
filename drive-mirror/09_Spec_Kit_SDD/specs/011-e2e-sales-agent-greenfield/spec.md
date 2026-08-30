# 011 Greenfield End-to-End Sales Agent — System Specification

Status: Greenfield implementation baseline
Parent: 000 Master System Specification
Governance: Engineering Constitution / Spec Kit
Legacy workflows: reference and rollback only; not implementation templates

## 1. Decision
Build a new end-to-end n8n workflow from scratch. Do not continue patching, refactoring, or cloning the current production graph as the primary engineering path.

The new product is a Sales Agent, not an FAQ bot. Its primary job is to understand the family, discover need, qualify fit, answer verified commercial/service questions, handle objections, recommend the next best action, progress the sales journey, and safely convert or hand off the lead.

FAQ and knowledge retrieval are supporting capabilities used for grounded facts. They are not the agent's primary identity or routing model.

## 2. Inputs From Prior Work
The greenfield build reuses approved business knowledge and controls, not the old node topology.

Required design inputs:
- WU01–WU83: curated knowledge, intent, state, commercial, scheduling, lead, handoff, nurture, and safety decisions already locked where applicable.
- WU84: 62-intent integration/mapping architecture, detailed intent plus legacy compatibility concepts, durable state expansion, and deterministic control concepts.
- WU85: offline classifier/integration regression evidence; 23/23 offline checks passed, but runtime certification was not completed.
- WU86: certification/business reconciliation controls and unresolved runtime/business gates.
- SPM_INTENTS_V2: 62-intent detailed semantic taxonomy.
- SPM_ENTITY_SCHEMA_V2 and SPM_NORMALIZATION_V2: canonical entity and normalization rules.
- SPM_SALES_PLAYBOOK_V2: sales journey objectives, next-best-actions, source/tool gates, and guardrails.
- SPM_CONFIG_V2: runtime thresholds and locked configuration controls.
- SPM_RUNTIME_TESTS: current runtime regression cases and expected behaviors.

## 3. Core Architecture Principle
The system separates semantic intelligence from deterministic business authority.

AI Sales Agent owns:
- conversation understanding;
- consultative sales reasoning;
- discovery and qualification dialogue;
- objection handling language;
- natural multilingual response generation;
- interpretation of ambiguous user language;
- recommendation of an allowed next best action.

Deterministic workflow owns:
- intent contract validation;
- state transitions;
- entity validation and normalization;
- source/tool authorization gates;
- prices/currency lookup;
- policy/live-data verification;
- scheduling and booking execution;
- lead persistence and idempotency;
- opt-out enforcement;
- human handoff execution;
- telemetry, retries, and success/failure truth.

The model may recommend an action. It may not declare a deterministic action successful unless the workflow returns verified success.

## 4. End-to-End Sales Journey
The workflow must support the sales playbook journey areas as one coherent state machine:
1. Discovery — identify the smallest missing academic qualifier.
2. Academic Need — understand goal, gap, urgency, topic, or exam need.
3. Pricing — answer approved package facts first, then continue fit qualification.
4. Discount — check authorized offers only; never invent discounts.
5. Trial — progress toward a free trial using live availability when needed.
6. Teacher — build trust and capture preferences using verified teacher/policy sources.
7. Scheduling — resolve timezone/window and use live scheduling.
8. Existing Lesson — support-first handling for reschedule/cancel/missed lesson.
9. Service — remove friction using approved service configuration.
10. Academic Progress — explain verified assessment/reporting/curriculum processes.
11. Conversion — registration, ready-to-register, contact share, and booking confirmation.
12. Objection — address price, competitor, online learning, attention, and teacher concerns without unsupported claims.
13. Nurturing — respect timing and eligibility for follow-up.
14. Stop — sticky opt-out/not-interested state overrides nurture.
15. Support — complaint, technical, login, contact update, and explicit human request override sales pressure.
16. Fallback/Out of Scope — redirect safely without hallucinating unrelated facts.

## 5. Intent and Routing Contract
- Use the 62-intent SPM V2 taxonomy as the detailed semantic contract.
- Preserve a compatibility alias only where downstream integrations still require a legacy route.
- Intent confidence uses the configured default threshold and may use per-intent overrides.
- Low-confidence or materially ambiguous classification must not trigger irreversible business actions.
- Multi-topic requests may carry primary and secondary intents/entities, but business actions remain explicitly gated.
- Arabic, English, French, mixed-language, spelling errors, and common dialect usage must normalize without destructive semantic changes.

## 6. Sales State Contract
Maintain one durable sales_state object in Redis/session persistence. It must be non-destructive across turns and support at minimum:
- session/contact identity;
- language;
- detailed intent and route alias;
- journey stage;
- next best action;
- known academic qualifiers;
- goal/problem/urgency;
- country/province/city/timezone/currency;
- teacher preferences;
- scheduling preferences and live references;
- lead fields and validation state;
- consent and confirmation state;
- lead_saved / booking status and identifiers;
- human_handoff state;
- nurture eligibility;
- sticky opt_out;
- failure/recovery state;
- multi-student profiles without merging child-specific grade/subject data.

Do not ask again for a clear current value already present in durable state unless validation failed or the user explicitly corrects it.

## 7. Knowledge and Source Gates
Knowledge retrieval is targeted by intent/domain and must send only relevant approved context to the Sales Agent.

Source gates include:
- APPROVED_KB_OR_LOGIC;
- PACKAGES_LIVE_CONFIG;
- AUTHORIZED_OFFER_REQUIRED;
- VERIFIED_TEACHER_OR_POLICY;
- SCHEDULING_LIVE;
- POLICY_AND_LIVE_STATE;
- MARKET_PAYMENT_CONFIG;
- PAYMENT_LIVE;
- CRM_VALIDATION;
- APPROVED_CURRICULUM_SOURCE;
- approved support/handoff tools.

Stable knowledge can be retrieved from approved ACTIVE records. Volatile facts must use live tools. Absence of a fact must never be converted into a negative claim.

## 8. Conversion and Lead Rules
- Do not collect PII merely because the visitor shows buying signals.
- Begin contact/registration collection only after explicit request or acceptance of a sales next step.
- Collect only missing required fields.
- Validate PII and canonical fields before persistence.
- Final write is deterministic and idempotent.
- Correction updates the intended lead/session instead of creating a duplicate.
- Success is shown only after confirmed write success.
- Human handoff receives the current sales summary and known verified state.

## 9. Scheduling and Booking Rules
- Country alone is insufficient to infer timezone when multiple zones are possible.
- Resolve location/timezone deterministically.
- Teacher/slot/weekend/evening availability requires live scheduling lookup.
- Booking confirmation requires scheduling success plus a valid booking_id.
- Failed or unavailable live checks must produce truthful recovery or handoff, not invented availability.

## 10. Sales Behavior
The agent should behave like a skilled consultative sales representative:
Acknowledge → Clarify → Recommend → Confirm interest → Next step.

Rules:
- answer the immediate question first;
- ask at most one purposeful next question unless a structured confirmation summary is required;
- use known state naturally;
- explain value using verified facts;
- never pressure, create false urgency, disparage competitors, diagnose a child, or guarantee outcomes;
- a factual question must not automatically become a sales pitch;
- support and explicit human requests override sales progression.

## 11. Multilingual Requirement
English, Arabic, and French must share the same business logic, state transitions, source gates, and deterministic safeguards. Language changes wording only, not truth, pricing, policy, consent, validation, or operational outcome.

## 12. Reliability and Observability
Every critical transition must emit structured telemetry containing at minimum:
- execution/session ID;
- detected detailed intent and confidence;
- route alias;
- journey stage and next action;
- source gate and source result;
- entity validation result;
- state transition;
- tool/action result;
- lead/booking/handoff reference when successful;
- failure category and retry/recovery path;
- latency/model/tool usage sufficient for performance review.

No false success is permitted.

## 13. Greenfield Safety Boundary
The existing R1/R2/R2.5 workflows remain available for reference and rollback. Their proven business outcomes become regression requirements, but their node graph is not inherited by default.

The greenfield workflow must have a new workflow identity and remain inactive until certification. Production cutover is a separate release decision after all gates pass.

## 14. Acceptance Criteria
The greenfield system is eligible for release only when:
- all 62 intents have an explicit route/playbook/source-gate contract;
- critical entity normalization and durable state tests pass;
- approved knowledge is grounded and volatile facts are live-verified;
- deterministic lead write, correction, deduplication, and failure behavior pass;
- live scheduling/booking truth gates pass;
- opt-out is sticky;
- human handoff preserves sales context;
- multilingual parity passes;
- offline regression, runtime regression, red-team, and failure-injection gates pass;
- no P0/P1 open defect remains;
- old production remains untouched until approved cutover.

## 15. Implementation Sequence
This greenfield build starts at WU87. WU84–WU86 are source inputs/control evidence, not the new implementation sequence. Detailed WU87+ scope is maintained in work-units.md.
