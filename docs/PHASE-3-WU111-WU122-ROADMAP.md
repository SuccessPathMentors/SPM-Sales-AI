# SPM Sales AI — Phase 3 Roadmap

Status: PLANNED / NOT STARTED
Phase boundary: Phase 2 continues through WU-110. Phase 3 starts at WU-111.

## Governance boundary

- WU-101 through WU-110 remain Phase 2.
- WU-107 through WU-110 are reserved for the existing Phase 2 roadmap and are not redefined by this document.
- Phase 3 begins only after WU-110 is completed/locked or otherwise formally closed according to project governance.
- This document is planning only. It does not authorize Production changes, Supabase cutover, data deletion, or migration execution.
- Every WU below requires its own Scope Freeze -> Contract -> Implementation -> STAGING/Shadow Validation -> Regression -> Owner Acceptance -> Lock cycle.

# Phase 3 Objective

Move the Sales AI platform from spreadsheet-centric operational storage toward a governed Supabase data platform, while introducing complete conversation recording, call-center-style QA review, response quality scoring, conversion intelligence, and a closed-loop learning system.

Phase 3 has three programs:

1. Data Platform Modernization — Excel/Google Sheets to Supabase
2. Conversation QA / CRM Intelligence
3. Conversion Analytics and Continuous Learning

---

# Program A — Data Platform Modernization

## WU-111 — Supabase Migration Discovery & Target Architecture

Objective:
Create the authoritative migration blueprint before moving any data.

Scope:
- inventory all current Excel/Google Sheets/Redis/n8n data stores used by Sales AI;
- identify source-of-truth per entity and field;
- identify data owners, PII, retention constraints, and update frequency;
- define DEV/STAGING/PROD Supabase environments;
- define migration sequence, rollback model, backup strategy, and zero-loss requirements;
- identify which spreadsheet functions remain operational reports versus system-of-record data.

Primary deliverables:
- source-system inventory;
- entity/data-flow map;
- migration dependency map;
- target architecture;
- migration risk register;
- rollback and recovery plan.

Lock gate:
No schema or data migration begins until every authoritative source and ownership rule is identified.

## WU-112 — Supabase Canonical Schema, Identity & Security Model

Objective:
Design the normalized Supabase/Postgres model that replaces spreadsheet storage safely.

Scope:
- canonical IDs and foreign keys;
- leads, parents, students, tutors, sessions, registration state, packages, actions, conversations, messages, QA records, outcomes, and audit events;
- timestamps/time zones and multilingual fields;
- Row Level Security (RLS);
- service roles versus staff/admin roles;
- PII classification and minimization;
- indexes, uniqueness, deduplication constraints, soft-delete/archive rules;
- auditability and schema versioning.

Primary deliverables:
- ERD/schema contract;
- table/column definitions;
- RLS/access matrix;
- data dictionary;
- key/ID strategy;
- migration mapping template.

Lock gate:
Schema must support current WU-101→110 behavior without losing lineage, identity, or audit data.

## WU-113 — Historical Spreadsheet Migration ETL & Data Quality Certification

Objective:
Load historical Excel/Google Sheets data into Supabase without changing live behavior.

Scope:
- extract and normalize source data;
- cleanse names, IDs, dates, currencies, nulls, duplicates, and malformed records;
- map legacy IDs to canonical Supabase IDs;
- historical import into non-production first;
- record-level reconciliation and source-to-target counts;
- exception/quarantine table for unresolved records;
- repeatable/idempotent migration scripts.

Primary deliverables:
- ETL/migration scripts;
- mapping tables;
- reconciliation report;
- exception register;
- migration evidence package.

Lock gate:
No cutover until critical tables reconcile to agreed tolerance with zero unexplained P0 data loss.

## WU-114 — Supabase Shadow Write / Dual-Write & Reconciliation

Objective:
Prove that new live events can be written to Supabase safely while the legacy spreadsheet path remains authoritative.

Scope:
- shadow or dual-write from n8n to Supabase;
- idempotency keys and retry behavior;
- write-order and failure handling;
- reconciliation jobs between legacy store and Supabase;
- duplicate prevention;
- latency and failure telemetry;
- rollback that disables Supabase writes without affecting customer conversations.

Primary deliverables:
- shadow-write workflow;
- reconciliation dashboard/report;
- failure-injection tests;
- parity evidence;
- rollback switch.

Lock gate:
Sustained shadow parity must pass before Supabase becomes authoritative.

## WU-115 — Supabase Read Cutover, System-of-Record Transition & Legacy Archive

Objective:
Move operational reads/writes to Supabase only after certified parity.

Scope:
- staged read cutover;
- controlled write cutover;
- regression across Sales AI workflows;
- backup and restore rehearsal;
- performance/load validation;
- spreadsheet freeze/archive strategy;
- documented emergency rollback;
- prohibit silent deletion of historical spreadsheet sources.

Primary deliverables:
- cutover runbook;
- production-readiness checklist;
- rollback rehearsal evidence;
- post-cutover reconciliation;
- legacy archive policy.

Lock gate:
Owner approval required before any Production source-of-truth switch.

---

# Program B — Conversation QA / CRM Intelligence

## WU-116 — Complete Conversation Event Capture & Transcript Ledger

Objective:
Record the complete chatbot interaction history as a structured CRM/QA ledger, not only the latest question.

Scope:
- persist every customer turn and assistant turn;
- conversation/session/thread IDs;
- turn sequence;
- timestamps and channel;
- language;
- customer intent and classifier confidence;
- response text;
- workflow/model/prompt/KB version identifiers;
- action requested versus action executed;
- latency and error/fallback flags;
- handoff/support/escalation markers;
- link to lead/customer/student only through governed identifiers;
- immutable/auditable event history where appropriate.

Privacy requirements:
- no passwords, secrets, API keys, or prohibited credentials in the ledger;
- PII minimization and retention rules;
- access control and audit logging.

Primary deliverables:
- conversation/message schema;
- event contract;
- n8n logging layer;
- turn reconstruction test;
- no-loss and ordering validation.

Lock gate:
A full multi-turn conversation must be reconstructable in correct order with workflow/version lineage.

## WU-117 — Response QA Taxonomy & Scoring Rubric

Objective:
Define exactly what a good or bad chatbot response means before automating scoring.

QA dimensions include:
- relevance to the inquiry;
- factual correctness / source grounding;
- hallucination risk;
- helpfulness;
- directness / to-the-point behavior;
- unnecessary extension or verbosity;
- completeness;
- clarity;
- tone and empathy where appropriate;
- policy/safety compliance;
- correct use of known context / no unnecessary re-ask;
- correct next step;
- action honesty;
- whether the response moves the conversation toward the customer's goal;
- whether the response increases, preserves, or decreases customer interest;
- conversion contribution;
- meaningless/non-value response;
- confusion introduced versus confusion resolved.

Primary deliverables:
- scorecard and definitions;
- 0–100 overall quality score model;
- severity levels (P0/P1/P2/P3);
- reason codes;
- annotated examples;
- pass/fail thresholds;
- human-review override rules.

Lock gate:
Two reviewers should be able to score the same example with acceptable agreement using the rubric.

## WU-118 — Automated Conversation QA Classification & Scoring Pipeline

Objective:
Automatically evaluate every conversation/response using the WU-117 rubric while retaining human review authority.

Scope:
- response-level QA scoring;
- conversation-level scoring;
- intent/response alignment;
- relevance and helpfulness scoring;
- hallucination/grounding detection;
- directness/verbosity classification;
- interest/conversion direction classification;
- confidence score and reason codes;
- rule-based checks plus LLM evaluator where appropriate;
- evaluator prompt/version tracking;
- sampling and calibration against human labels;
- fail-safe behavior when evaluator confidence is low.

Primary deliverables:
- QA scorer pipeline;
- evaluator contract;
- calibration dataset;
- accuracy/agreement report;
- scoring audit trail.

Lock gate:
Automated QA cannot silently overwrite human labels and must expose confidence/reason codes.

## WU-119 — QA Review Console / CRM Conversation Review Workflow

Objective:
Create the call-center-style quality review layer for staff and supervisors.

Capabilities:
- conversation replay in chronological order;
- customer and assistant turns shown together;
- intent and response classification;
- QA score by dimension;
- filters by date, language, intent, model/workflow version, staff owner, lead stage, and score;
- flag hallucination / irrelevant / too verbose / unhelpful responses;
- reviewer comments;
- manual score override with reason;
- assign remediation owner;
- create follow-up or engineering/KB issue;
- audit trail of reviewer changes.

Primary deliverables:
- reviewer workflow/UI specification;
- queue logic;
- review status lifecycle;
- audit model;
- role/access matrix.

Lock gate:
Reviewer can locate, replay, score, annotate, and close a conversation without editing original transcript history.

## WU-120 — QA Analytics, Management Dashboard & Trend Detection

Objective:
Turn conversation QA data into operational intelligence.

Metrics include:
- overall response quality;
- relevance rate;
- helpfulness rate;
- hallucination rate;
- directness/verbosity distribution;
- no-reask performance;
- fallback/clarification rate;
- handoff rate;
- QA score by intent/language/channel;
- QA score by workflow/model/prompt/KB version;
- recurring failure themes;
- response quality trends over time;
- top/bottom performing intents and journeys.

Primary deliverables:
- KPI definitions;
- dashboard/report specification;
- trend/alert thresholds;
- drill-down from KPI to individual conversation evidence.

Lock gate:
Every aggregate KPI must be traceable back to source conversations and scoring records.

---

# Program C — Conversion Analytics & Continuous Learning

## WU-121 — Conversation-to-Conversion Attribution & Interest Progression

Objective:
Measure whether chatbot responses actually move leads toward business outcomes rather than only sounding good.

Scope:
- define funnel events: inquiry -> qualified -> trial interest -> trial scheduled -> registered -> package/payment or other approved business outcome;
- conversation-level conversion stage;
- response-level interest direction: increased / neutral / decreased / unknown;
- objection recovery effectiveness;
- next-step acceptance;
- dropout after specific intents or responses;
- time-to-conversion;
- attribution rules that distinguish correlation from stronger evidence;
- avoid claiming causal impact without valid experiment or design.

Primary deliverables:
- conversion-event contract;
- funnel definitions;
- interest-direction taxonomy;
- attribution model;
- outcome dashboard/report;
- journey-level conversion metrics.

Lock gate:
No response is labeled causally responsible for conversion without explicit evidence/experimental basis.

## WU-122 — Closed-Loop Learning, Remediation & Regression Generation

Objective:
Use real conversation evidence to improve the chatbot continuously under governance.

Scope:
- identify recurring low-quality patterns;
- cluster failure reasons;
- generate candidate KB/prompt/routing improvements;
- convert production/staging failures into deterministic regression cases;
- maintain approved training/evaluation datasets;
- prevent raw customer PII from entering training/evaluation artifacts without approved handling;
- measure before/after QA and conversion impact;
- require CR + test + owner approval before behavior changes;
- retain rollback and version lineage.

Primary deliverables:
- learning-loop workflow;
- failure-to-test-case pipeline;
- remediation backlog;
- regression generation rules;
- before/after impact report;
- governance/approval gates.

Lock gate:
No automatically generated learning recommendation may directly modify Production behavior without the standard CR/QA/Owner Lock process.

---

# Phase 3 Dependency Order

Recommended sequence:

WU-111 -> WU-112 -> WU-113 -> WU-114 -> WU-115

Then, using Supabase as the governed analytical/operational foundation:

WU-116 -> WU-117 -> WU-118 -> WU-119 -> WU-120 -> WU-121 -> WU-122

Some design work for WU-116/WU-117 may begin before final WU-115 cutover, but Production conversation logging should use the approved Phase 3 data/security architecture.

# Phase 3 Success Definition

Phase 3 is successful when:

1. operational Sales AI data has a governed Supabase system of record with validated migration and rollback;
2. every chatbot conversation can be reconstructed turn by turn;
3. every assistant response can be reviewed and scored across relevance, correctness, helpfulness, directness, hallucination, context use, and conversion direction;
4. supervisors have a CRM/call-center-style QA review workflow;
5. management can see quality and conversion trends and drill down to evidence;
6. real conversation failures automatically feed a governed remediation/regression backlog;
7. no Production behavior changes bypass CR, QA, regression, and owner approval.
