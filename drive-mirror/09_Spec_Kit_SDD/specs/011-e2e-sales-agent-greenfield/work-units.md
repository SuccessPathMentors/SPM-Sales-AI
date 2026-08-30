# 011 Greenfield E2E Sales Agent — Working Units

WU84–WU86 remain historical integration/certification inputs. Greenfield implementation begins at WU87.

## WU87 — Greenfield Architecture & Contracts
Deliverables:
- new inactive n8n workflow with new identity;
- session envelope contract;
- classifier output contract;
- entity contract;
- durable sales_state contract;
- source-gate contract;
- Sales Agent output contract;
- deterministic action gateway skeleton;
- telemetry envelope;
- rollback/reference links.
Gate: static graph valid; no production writes; architecture review PASS.

## WU88 — 62-Intent Classifier & Routing
Implement the full SPM V2 62-intent classifier with confidence, optional secondary intent, ambiguity handling, and temporary legacy-route alias only where required.
Gate: all intents mapped; no irreversible action from low-confidence classification; offline classifier suite PASS.

## WU89 — Entity Extraction, Normalization & Multi-Student Model
Implement schema-based extraction and safe normalization for academic, location, scheduling, teacher preference, operational, and lead entities. Add separate child profiles.
Gate: correction precedence, Arabic normalization, code-switching, timezone prerequisites, and multi-child separation PASS.

## WU90 — Durable Sales State & Journey Engine
Implement non-destructive Redis state merge and explicit journey transitions: discovery, need, commercial, trial, scheduling, conversion plus support/nurture/opt-out/handoff/recovery overrides.
Gate: refresh/re-entry persistence, sticky opt-out, no repeated known-field questions, state transition tests PASS.

## WU91 — Knowledge Retrieval & Source Gates
Implement targeted ACTIVE-record retrieval and gate resolver for KB/config/live sources. Separate stable facts from volatile operational facts.
Gate: no whole-KB prompt loading; unsupported claims blocked; price/policy/teacher/scheduling source routing PASS.

## WU92 — Sales Agent Core
Build the primary consultative Sales Agent prompt/contract using the Sales Playbook. FAQ becomes supporting knowledge only.
Agent behavior: acknowledge, clarify, recommend, confirm interest, next step; answer first; one purposeful question; no pressure or unsupported promise.
Gate: sales-quality scenario review across discovery, pricing, trial, teacher, objection, and conversion PASS.

## WU93 — Pricing, Packages, Offers & Objections
Wire dynamic package retrieval, currency/business directives, authorized-offer checks, package comparison, price objections, and competitor/online/attention/teacher objections.
Gate: no hardcoded stale pricing where config is authoritative; no invented discounts; objection red-team PASS.

## WU94 — Trial, Availability, Scheduling & Booking
Implement live timezone-aware scheduling, teacher/slot availability, weekend/evening handling, trial progression, booking execution, and booking_id truth gate.
Gate: no availability/booking claim without live success; timezone and retry/failure tests PASS.

## WU95 — Deterministic Lead Conversion & CRM/Handoff
Implement validated lead collection, consent, final summary, deterministic UPSERT, correction, deduplication, human handoff, and downstream notification separation.
Gate: R1 protected lead outcomes 10/10 PASS plus new failure-injection tests.

## WU96 — Nurture, Follow-Up, Opt-Out & Support Overrides
Implement need-to-think/follow-up eligibility, sticky not-interested/opt-out, complaint/technical/login/update-contact flows, and support-over-sales precedence.
Gate: no promotional nurture after opt-out; support/handoff context tests PASS.

## WU97 — Reliability, Errors, Observability & Privacy
Implement retry policy, structured failures, recovery states, telemetry, PII minimization, prompt-injection resistance, secret hygiene, latency/cost capture, and dead-letter evidence.
Gate: no false success; security/static QA PASS; critical failure paths observable.

## WU98 — Multilingual & Conversation Regression
Run EN/AR/FR parity, dialect/code-switching, typo handling, multi-turn corrections, repeated questions, multiple children, and long-session state tests.
Gate: multilingual business outcome parity; no destructive Arabic normalization; regression target PASS.

## WU99 — Full Runtime / E2E Certification
Run classifier, Sheets, Redis, CRM/lead, handoff, scheduling/booking, notification, failure-injection, and complete sales journey runtime suites. Expand the existing runtime set into full E2E coverage, including red-team cases.
Gate: all blocking runtime tests PASS; no P0/P1; release evidence complete.

## WU100 — Canary Release, Production Certification & Lock
Create immutable release candidate; owner approval; canary cutover; monitor conversion, errors, latency, costs, lead integrity, opt-out, scheduling, and handoff; rollback on blocking regression; then tag/lock the approved release and archive obsolete candidates.
Gate: production certification approved and PROJECT_STATE/CHANGELOG/GitHub artifacts updated.

## Dependency Rule
Each WU is implemented only after its spec/plan/tasks/checklist dependencies pass. A later WU may be prototyped but cannot be certified while an upstream contract remains unresolved.

## Release 2 / Phase 2 Backlog — Deferred Until Release 1 (WU-100) Is Certified and Locked

Status: APPROVED BACKLOG — DO NOT IMPLEMENT IN RELEASE 1.
Principle: Release 1 must be frozen, certified, hashed, approved, and cut over before any WU-101+ work begins. No random production edits. Each Phase 2 gap follows Spec Kit: Requirement → Work Unit → Tests → Evidence → Approval → Lock.

### WU-101 — Conversation Analytics
Goal: Capture the real customer conversation signals needed for optimization.
Scope: intent, secondary intent, confidence, language, session outcome, source gate, fallback use, clarification use, human-request signal, lead-conversion outcome, and safe telemetry.
Acceptance direction: analytics must not expose secrets or unnecessary PII and must not change current customer-facing behavior.

### WU-102 — Unanswered Question Queue
Goal: Capture questions the system could not answer confidently or completely.
Trigger candidates: no KB match, low confidence, ambiguous intent, fallback used, repeated question, customer says they did not understand, human requested, unsupported/out-of-scope question, poor-answer feedback.
Minimum queue fields: timestamp, session_id, raw_question or safely redacted question, language/dialect hint, predicted intent, confidence, KB-match status, fallback flag, human-request flag, repeat flag, resolution status, approved-answer status, added-to-KB status.

### WU-103 — Knowledge Maintenance Loop
Goal: Convert real customer gaps into approved, versioned KB improvements.
Loop: Real traffic → detect gap → unanswered queue → human review → approve/edit answer → map to intent/source → add/update KB → regression test → publish → measure again.
No answer becomes production knowledge without review/approval and regression evidence.

### WU-104 — Short Query & Ambiguity UX
Goal: Handle short messages such as “price?”, “teachers?”, “curriculum?”, “duration?” without forcing long conversations.
Rules: clear short intent → answer first, then ask one useful question. Ambiguous short intent → do not guess; offer 2–4 concise clarification options/buttons. Unsupported/low-confidence → safe fallback + log gap + offer human assistance when appropriate.

### WU-105 — Golden Intents Optimization
Goal: Prioritize the 15–20 highest-value commercial intents instead of optimizing all 62 equally.
Initial candidates: pricing, lesson duration, packages, free trial, curriculum, subjects, grade coverage, teacher quality, teacher experience, teacher language, teacher gender, homework, assessment, progress tracking, sibling discount, service area/location, online class process, scheduling, registration, human handoff.
Each Golden Intent should have approved answers, representative real-user variations, dialect/language coverage, and stronger regression coverage.

### WU-106 — Dialect & Language Coverage
Goal: Improve recognition of real Arabic dialects and natural EN/FR variations without expanding prompts blindly.
Coverage candidates: Levantine, Egyptian, Gulf, Maghrebi, MSA, English, French; short forms, spelling variation, code-switching, and common colloquial phrases.
The 26k-question corpus is treated as a variation/coverage corpus, not a payload to send in every model request.

### WU-107 — Human Handoff Adapter
Goal: Add real, deterministic human-handoff execution.
Requirements: detect handoff intent, preserve session context, collect only minimum required contact/context, create a handoff record, return success only after tool evidence, and never falsely claim handoff completion.

### WU-108 — WhatsApp Staff Notification
Goal: Notify the operations/customer-service team when an approved human handoff succeeds.
Notification should include only required operational context such as reason, language, latest customer need, safe contact reference, and session/reference ID. Do not claim notification success unless the WhatsApp/API tool succeeds.

### WU-109 — Conversation Outcome KPIs
Goal: Create management visibility into real chatbot performance.
Target KPIs: total conversations, answered-without-clarification %, clarification %, fallback/unanswered %, human-handoff %, top intents, top unanswered topics, lead-conversion rate by intent, repeat-question rate, registration completion, and degraded-response rate.
Optimization priority must be driven primarily by real customer traffic and failures, not by synthetic question volume alone.

### WU-110 — Optimization Regression Pack
Goal: Turn newly discovered real-world gaps into permanent regression coverage.
Every approved KB/routing/UX improvement should create one or more regression cases before release. Test EN/AR/FR and representative dialect/short-query variants where relevant.

### Phase 2 Design Principles
1. The 62 intents remain the routing/taxonomy layer: they describe what the customer wants, not the final answer.
2. The 26k question corpus is used for language/variation coverage, retrieval evaluation, and testing; it is not injected wholesale into each prompt.
3. Answer the customer’s actual question first, then advance the sales journey naturally with at most one purposeful next question.
4. Never hide a simple answer behind a long sales pitch.
5. Use real traffic to drive maintenance: what customers ask, what was unanswered, what was ambiguous, what repeated, and what required human help.
6. Human handoff is a deterministic execution feature and must remain excluded from Release 1 until WU-107/WU-108 are implemented and certified.
7. Every Phase 2 change must follow the Spec Kit lifecycle and produce test/evidence before lock.

Recommended Phase 2 execution order: WU-101 → WU-102 → WU-103 → WU-104 → WU-105 → WU-106 → WU-107 → WU-108 → WU-109 → WU-110.
