# 011 Greenfield End-to-End Sales Agent — Technical Plan

Status: Ready for architecture implementation

## 1. Build Strategy
Create a brand-new n8n workflow with a new workflow ID. The current production workflow remains untouched and serves only as behavior reference, rollback, and regression baseline.

Do not copy the old graph wholesale. Reuse only approved business rules, sheet contracts, prompts/phrasing where still valid, and verified integration credentials during runtime wiring.

## 2. Target High-Level Flow
Chat Trigger
→ Input Sanitization / Session Envelope
→ Load Durable Sales State
→ Normalize Language + Message
→ Detailed 62-Intent Classifier
→ Entity Extraction / Normalization
→ Merge Non-Destructive State
→ Determine Journey Stage + Next-Best-Action
→ Source/Tool Gate Resolver
→ Targeted Knowledge / Live Tool Retrieval
→ Sales Agent Reasoning + Response Draft
→ Deterministic Action Gateway
→ Action Subflows: Lead / Scheduling / Handoff / Support / Nurture
→ Save Durable State
→ Telemetry + Response

Operational and support events may bypass Sales Agent generation when deterministic user-facing messaging is safer.

## 3. Logical Components
A. Session Envelope
- canonical session_id;
- language;
- channel/source;
- customer message;
- request timestamp;
- correlation/execution identifiers.

B. Classifier Contract
- detailed spm_intent from 62-intent taxonomy;
- confidence;
- optional secondary intent;
- legacy_route_intent compatibility value only if needed;
- ambiguity flags;
- source gate recommendation.

C. Entity Contract
Extract/normalize only schema-approved entities, including grade, subject, package, country, city, province/state, timezone, preferred day/time, teacher preferences, lesson/booking identifiers, PII fields, request type, and student profile references.

D. Durable State
Single non-destructive sales_state object in Redis. Use deterministic merge rules, correction precedence, sticky opt-out, and separate child profiles.

E. Journey Engine
Determine sales stage and allowed next actions from the Sales Playbook, current intent, known state, consent, source availability, and prior outcomes.

F. Source Gate Resolver
Map each request/action to the authoritative source/tool before the Sales Agent receives factual context.

G. Sales Agent
One primary conversational agent optimized for sales consultation rather than FAQ retrieval. It receives:
- user message;
- current state summary;
- detailed intent/entities;
- current journey stage;
- allowed next actions;
- verified context/tool results;
- commercial/safety guardrails.

The agent returns a constrained response contract, not arbitrary workflow commands.

H. Deterministic Action Gateway
Validates any requested operational action against state, consent, required entities, source/tool availability, and idempotency rules before execution.

## 4. Action Subflows
Create separate bounded subworkflows where useful:
- Lead Registration / Update / Deduplication;
- Human Handoff;
- Scheduling / Availability / Booking;
- Policy + Existing Lesson support;
- Payment/booking verification when integrated;
- Nurture / Opt-Out;
- Notification / CRM downstream actions;
- Error Recovery / Dead Letter evidence.

## 5. Knowledge Design
The knowledge base is not sent wholesale to the model.

Pipeline:
intent/domain → ACTIVE record filter → keyword/entity relevance → small ranked context → source gate validation → Sales Agent.

Pricing must remain dynamic from approved package configuration. Teacher availability, scheduling, booking, payment, and other volatile facts require live sources.

## 6. Model Call Strategy
Prefer a small number of purposeful model calls.

Recommended initial architecture:
1. classifier/entity call, structured JSON output;
2. final Sales Agent call after deterministic source retrieval.

Where classifier reliability allows, entity extraction may share call 1. Do not use the Sales Agent itself as the sole router for irreversible actions.

## 7. Sales Agent Output Contract
The Sales Agent should return structured fields such as:
- response_text;
- conversation_goal;
- proposed_next_action;
- missing_qualifier;
- objection_type when applicable;
- should_offer_trial;
- should_handoff;
- support_override;
- confidence/uncertainty indicator.

The deterministic workflow validates proposed_next_action before acting.

## 8. State Machine
Primary stages:
NEW → DISCOVERY → NEED_QUALIFIED → COMMERCIAL_DISCUSSION → TRIAL_INTEREST → SCHEDULING → CONVERSION → SUBMITTED/BOOKED.

Side/override states:
SUPPORT, HUMAN_HANDOFF, NURTURE, OPTED_OUT, CLOSED_NOT_INTERESTED, RECOVERY_REQUIRED.

Transitions must be explicit and testable. A user can move backward by correction or changed intent without losing valid state.

## 9. Greenfield Development Environment
- Create workflow as inactive/staging.
- Use safe copied KB/config sheets where write risk exists.
- Use synthetic test users and unique test session IDs.
- Never point testing to production lead writes without an explicit isolated test route.
- Keep workflow JSON versioned in GitHub/Drive.

## 10. Test Strategy
Layer 1 — Contract tests
- taxonomy completeness;
- entity schema;
- normalization;
- state merge;
- source-gate mapping.

Layer 2 — Offline conversation regression
- current WU85 cases;
- all 62 intents;
- EN/AR/FR and code-switching;
- multi-turn state scenarios;
- ambiguity and correction.

Layer 3 — Runtime integration
- Google Sheets/config reads;
- Redis persistence;
- lead UPSERT;
- handoff;
- scheduling/live availability;
- booking confirmation;
- failure/retry behavior.

Layer 4 — E2E Sales journeys
- discovery to qualified lead;
- price objection to trial;
- teacher preference to scheduling;
- multiple children;
- not interested/opt-out;
- complaint/support override;
- human request;
- failed tool recovery.

Layer 5 — Red team / reliability
- unsupported claims;
- prompt injection;
- PII leakage;
- duplicate lead;
- false booking/success;
- stale pricing/availability;
- repeated confirmation;
- state corruption;
- multilingual inconsistency.

## 11. Release Strategy
No big-bang replacement.

1. Build inactive greenfield workflow.
2. Pass static and offline gates.
3. Pass isolated runtime tests.
4. Run shadow/controlled test traffic if feasible.
5. Run full E2E regression and red team.
6. Compare conversion logic and latency/cost against current production.
7. Owner release approval.
8. Canary cutover.
9. Observe telemetry and rollback immediately on blocking regression.
10. Lock/tag the approved greenfield release.

## 12. Source-of-Truth Priority for This Build
1. Engineering Constitution and 011 spec.
2. Locked owner/business directives.
3. SPM V2 taxonomy/entity/normalization/playbook/config sheets.
4. Current live integration contracts where runtime verification is required.
5. WU84–WU86 evidence.
6. Existing production workflow only as behavior/reference evidence.

## 13. First Implementation Milestone
WU87 must end with an empty-but-valid greenfield workflow skeleton containing only the architectural backbone, typed contracts, staging credentials placeholders/references, and test hooks. No production cutover and no broad business logic implementation in WU87.
