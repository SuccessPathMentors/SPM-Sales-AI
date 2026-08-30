# 000 Master System Specification — Success Path Mentors AI Sales Bot

Status: Baseline specification v1.0
Date: 2026-08-19
Owner: Success Path Mentors
Purpose: Define the production behavior of the AI sales system and provide the parent specification for future feature specs.

## 1. Product Goal
Provide a reliable multilingual AI sales assistant that answers approved tutoring questions, qualifies prospective families, captures valid lead information, supports free-trial and scheduling journeys, handles objections and follow-up, and safely transfers conversations to humans when automation should stop.

The system must increase sales efficiency without sacrificing truthfulness, data integrity, customer trust, or operational control.

## 2. Primary Users
- Prospective parents and students seeking tutoring information
- Returning leads continuing a sales conversation
- Operations staff receiving qualified leads and handoffs
- Sales/relationship staff reviewing lead state and conversation outcomes
- Administrators maintaining approved knowledge, mappings, workflow rules, and QA evidence

## 3. System Boundary
In scope:
- Website/chat entry point
- n8n orchestration
- AI language understanding and response generation
- Intent classification and routing
- Approved knowledge retrieval
- Lead qualification and data capture
- Student/parent relationship data
- Validation and normalization
- Free-trial journey
- Scheduling and booking integrations
- Conversation/session state
- Human handoff
- Nurture/opt-out behavior
- Google Sheets and Redis persistence
- Notifications/downstream automation
- Telemetry, QA, and release controls
- EN/AR production behavior

Out of scope for this master baseline unless separately specified:
- Full LMS delivery
- Tutor payroll/accounting
- Academic assessment engine
- Production website redesign
- Unapproved CRM replacement

## 4. Core Functional Requirements
### FR-001 Approved Knowledge Answers
The bot must answer questions using approved knowledge or authorized live data sources. It must distinguish stable knowledge from volatile operational data.

### FR-002 Intent Recognition
The system must classify or normalize user intent sufficiently to route the request to the correct business flow. Ambiguous requests may use AI interpretation, but final deterministic actions must follow explicit routing rules.

### FR-003 Commercial Truthfulness
Prices, packages, policies, teacher claims, availability, booking status, refunds, and exceptions must never be invented. Unsupported claims must be withheld or escalated.

### FR-004 Lead Qualification
The bot must collect only the fields required by the active qualification flow and preserve them in session state until the user confirms or corrects them.

### FR-005 Lead Validation
Email, phone, country/location, subject, grade, timezone, currency, and other structured fields must be validated or normalized according to their defined rule set before confirmed persistence.

### FR-006 Lead Persistence
A confirmed valid lead must be written successfully exactly once per intended lead/session identity. Duplicate confirmation must not create duplicate leads. Corrections must update the intended record.

### FR-007 Student/Parent Data Consistency
Shared attributes across linked student and parent records must use explicit canonical rules. Updates to canonical shared fields must propagate according to the approved synchronization policy.

### FR-008 Free Trial Journey
The bot must explain and initiate the free-trial process according to approved business rules. Trial availability or booking must not be claimed until applicable live checks succeed.

### FR-009 Scheduling
Volatile slot availability must come from the scheduling source. Timezone handling must be deterministic and location-aware. Booking confirmation requires successful scheduling plus a valid booking identifier.

### FR-010 Human Handoff
The bot must transfer to a human when required by policy, user request, unresolved ambiguity, failed automation, exception handling, or sales escalation. Relevant conversation and lead context must be preserved.

### FR-011 Opt-Out and Nurture State
Opt-out must remain sticky across the relevant session/contact scope. Automated nurture must not resume unless the approved re-entry rule is satisfied.

### FR-012 Multilingual Parity
English and Arabic must execute the same business logic and safeguards. Wording may differ appropriately, but policy, prices, validation, and operational outcomes must remain equivalent.

### FR-013 Failure Handling
Tool, write, lookup, validation, scheduling, or notification failures must be detected and represented accurately. The bot must not report success when the deterministic action failed.

### FR-014 Observability
Critical business actions must produce enough structured evidence to identify route, validation result, persistence result, scheduling result, handoff result, and failure category.

### FR-015 Regression Protection
Locked behaviors must remain unchanged unless an approved spec explicitly supersedes them. Each production change must include focused regression coverage for affected locked behavior.

## 5. Existing Locked Baseline
R1 Reliable Lead Submission is an approved locked baseline. Its protected outcomes include:
- Complete confirmed lead writes successfully
- Corrected data updates the same lead/session
- Invalid or unconfirmed data is not written as confirmed
- Duplicate confirmation does not create duplicate leads
- Operational lead messages do not pollute unanswered-question logging
- Success is reported only after the write succeeds

## 6. Quality Attributes
### Reliability
Deterministic business operations must have explicit success/failure handling. Silent failure is unacceptable for lead creation, scheduling, handoff, and state transitions.

### Maintainability
Features must be decomposed into bounded specs and tasks. Business rules must be centralized where practical rather than duplicated across prompts/nodes.

### Traceability
Every material production change must link requirement → plan → task → implementation → test evidence → release/change record.

### Security and Privacy
Secrets must never be committed to version control. Only minimum necessary customer data should be captured and surfaced. Test fixtures must avoid unnecessary real personal information.

### Performance
Conversation flows should avoid unnecessary model calls and large-context retrieval. Deterministic preprocessing/routing should be used where it reduces latency and cost without reducing correctness.

### Recoverability
For production-impacting changes, rollback or recovery behavior must be known before release.

## 7. Data Domains Requiring Canonical Rules
- Lead ID/session ID
- Parent ID/student ID
- Name
- Email
- Phone
- Country
- Province/state
- City
- Time zone
- Currency
- Grade
- Subject
- Status
- Teacher preference
- Teacher assignment
- Scheduling identifiers
- Booking ID
- Opt-out state
- Handoff state

Each feature that writes or changes these fields must name the source of truth, validation rule, conflict rule, and propagation behavior.

## 8. Acceptance Criteria for the Master System
The system is considered aligned with this specification when:
1. Locked R1 behavior continues to pass regression tests.
2. Commercial claims are source-backed or live-verified where required.
3. Invalid/unconfirmed data cannot be represented as successfully committed confirmed data.
4. Duplicate lead confirmation is idempotent.
5. Booking success cannot occur without scheduling success and booking ID.
6. Human handoff retains the required lead/conversation context.
7. Opt-out remains sticky.
8. EN/AR business behavior is equivalent.
9. Critical deterministic failures are observable and do not masquerade as success.
10. New production work is introduced through a feature spec, plan, tasks, analysis, tests, and release evidence.

## 9. Feature Decomposition Roadmap
Future work should be specified as smaller numbered features under `specs/`, for example:
- 001-r2-error-handling
- 002-deterministic-lead-submission
- 003-location-timezone-currency-integrity
- 004-parent-student-data-sync
- 005-live-scheduling-and-booking
- 006-human-handoff-hardening
- 007-optout-and-nurture
- 008-observability-and-telemetry
- 009-multilingual-parity
- 010-knowledge-governance

Each feature runs through its own Spec Kit lifecycle and must reference this master specification and the engineering constitution.

## 10. Greenfield End-to-End Implementation Directive
The implementation strategy is now greenfield for the next-generation end-to-end workflow.

`011-e2e-sales-agent-greenfield` is the active workflow-construction feature. The existing production workflow and prior R1/R2/R2.5 candidates remain reference, regression, and rollback artifacts; they are not the node-graph template for the new build.

The AI component is defined as a consultative Sales Agent. FAQ/knowledge retrieval is a supporting grounded-data capability rather than the primary product role.

The detailed SPM V2 62-intent taxonomy, entity/normalization contracts, Sales Playbook, configuration controls, and WU84–WU86 evidence are mandatory design inputs. New implementation work begins at WU87 and proceeds through WU100 as defined by `011-e2e-sales-agent-greenfield/work-units.md`.

Features 001–010 remain valid requirement/reference modules and may supply acceptance criteria or reusable subflow requirements, but they no longer define the primary sequential construction path for the new workflow.
