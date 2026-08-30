# CHANGELOG.md — Project Change Log

## 2026-08-20 — Runtime Export Reconciliation / SAFE TEST Candidate
- Reviewed uploaded `Validated Human Handoff` runtime export: ID `swhmNa0Goo0uYm1k`, active=true.
- Reviewed uploaded `ChatBotMSE v2 - R2.5 Release Candidate Stable Efficient`: ID `vSc7cMIMFMEUdi7z`, active=false.
- Confirmed R2.5 already implements deterministic lead registration and direct handoff execution; final lead submission is no longer an AI tool edge in this candidate.
- Confirmed R2.5 direct execution targets `swhmNa0Goo0uYm1k`, matching the active uploaded handoff.
- Rebuilt Feature 001 error-handling test candidate from the active uploaded handoff so current node IDs and semantics are preserved.
- Removed top-level workflow ID/version ID from the SAFE TEST artifact and kept active=false to prevent accidental overwrite/activation.
- SAFE TEST static QA: PASS; SHA-256 `0a6935331fddc9c9ee1a3ac1720bd884c61a0a9eefa6a2fcd408e7810359905c`.
- Uploaded SAFE TEST artifact to the Feature 001 `candidate/` folder.
- Added `runtime-export-analysis-2026-08-20.md` to Feature 001.
- Release remains BLOCKED because the uploaded R2.5 main export is inactive and runtime test evidence has not been produced.

## 2026-08-20 — R2 Error Handling Spec Kit Candidate
- Created bounded feature `001-r2-error-handling` under Spec Kit.
- Completed clarification, technical plan, implementation tasks, runtime test gate, and static analysis.
- Compared R1 locked main workflow with the latest Drive R2 token-optimized checkpoint; final handoff remains AI-tool-mediated in both.
- Deferred full deterministic lead-submission decoupling to `002-deterministic-lead-submission` to avoid an unsafe broad state-model rewrite.
- Created `Validated_Human_Handoff_R2_ERROR_HANDLING_CANDIDATE_2026-08-20.json` from the validated handoff subworkflow only.
- Added bounded retry and explicit structured error outputs for lead lookup and append-or-update failures.
- Preserved R1 locked main workflow and protected validation/conflict/success paths.
- Static QA: PASS; Drive candidate readback matched the tested artifact.
- Candidate safety state corrected and verified as `active=false`; canonical candidate SHA-256 is `5678b2c27623d9927d28f4f54631620153d07fd057a003a6b35edc8ecc7de683`.
- Feature requirements checklist completed; master task map updated for T006/T007 and T024–T030.
- Runtime QA and R1 10/10 regression: NOT RUN; release remains BLOCKED until n8n runtime identity and execution tests are completed.

## 2026-08-18 — Context & Token Management Upgrade
- Added `AGENTS.md` as the project-wide execution/context policy.
- Added `PROJECT_STATE.md` as the compact session-resume source.
- Added bounded `TASK_TEMPLATE.md`.
- Expanded token/context optimization around Hot/Warm/Elevated/High operating zones.
- Set normal working target to <=100K active context for most tasks.
- Set Hot Context target to 10K–30K.
- Established context escalation instead of bulk historical loading.
- Established `Search → Read exact range → Work → Test → Update State`.
- Established one-primary-objective-per-session.
- Established checkpoint-before-large-context rule.
- Preserved R1 as APPROVED AND LOCKED.
- Next engineering phase remains R2 — Reliability and Error Handling.

## 2026-08-17 — R1 Release Lock
- R1 — Reliable Lead Submission approved and locked.
- Focused regression testing: 10/10 PASS, owner confirmed.
- Locked artifact: `ChatBotMSE_v2_R1_LOCKED_2026-08-17.json`.
- Lead write, correction, confirmation, and duplicate-prevention behavior validated.
- R2 designated as the next phase.

## Logging Standard Going Forward
Every meaningful change should record:
- date;
- task ID;
- artifact/version;
- exact change;
- test evidence;
- PASS/FAIL;
- rollback/lock status;
- next action.

Do not use this file as a verbose transcript. Keep only durable project changes.
## Greenfield End-to-End Sales Agent Reset
- Owner approved a greenfield rebuild of the end-to-end chatbot workflow.
- Current production R1/R2/R2.5 workflows remain reference/regression/rollback artifacts only.
- Created Spec Kit feature `011-e2e-sales-agent-greenfield`.
- Product identity changed from FAQ-centric bot to consultative AI Sales Agent with knowledge retrieval as supporting grounded capability.
- Adopted WU84–WU86 as design/certification inputs; new implementation starts at WU87.
- Added WU87–WU100 sequence covering architecture, 62-intent routing, entities, durable state, knowledge/source gates, Sales Agent core, pricing/objections, scheduling/booking, deterministic lead conversion, nurture/opt-out/support, reliability/security, multilingual regression, runtime certification, and canary production release.
- Added feature artifacts: `spec.md`, `plan.md`, `work-units.md`, `tasks.md`, and `checklists/greenfield-release-gate.md`.
- Updated the Master Spec with the greenfield implementation directive.
- Updated PROJECT_STATE so the next action is WU87-T01: create a brand-new inactive n8n workflow and build only the architectural backbone.
- Production cutover remains unauthorized.

## 2026-08-20 — WU87 Greenfield Architecture & Contracts
- Completed WU87 for `011-e2e-sales-agent-greenfield`.
- Created a brand-new n8n candidate from scratch rather than cloning the production graph: `SPM_E2E_Sales_Agent_Greenfield_WU87_Skeleton_2026-08-20.json`.
- Candidate is inactive and has no top-level workflow ID/version ID, preventing intentional identity reuse on import.
- Added canonical session envelope and explicit TEST_ONLY guard; non-test traffic stops before the architecture pipeline.
- Added disabled Redis GET architecture placeholder for WU90; no Redis writes or production credentials are required in WU87.
- Added contracts/stubs for durable sales state, 62-intent classifier output, entity normalization, journey/NBA, source gates, Sales Agent structured output, deterministic action gateway, and telemetry.
- Deterministic action gateway is NOOP in WU87; there are no lead/CRM/booking/handoff writes and no AI/LLM execution nodes.
- Static QA PASS: 14 nodes, all names/IDs unique, no dangling connections, 0 production writes.
- Candidate SHA-256: `c636cde504cf7945fe63664668e76862a4a21575b867979fc6e96c135ae14e95`.
- Added `contracts.md` and `checklists/wu87-static-qa.md`.
- Marked WU87-T01 through WU87-T14 complete in `tasks.md`.
- Next unit: WU88 — implement and test the 62-intent classifier and confidence/ambiguity routing.
- Production cutover remains unauthorized.



## 2026-08-20 — WU88 62-Intent Classifier Implementation
- Built `SPM_E2E_Sales_Agent_Greenfield_WU88_62Intent_Classifier_2026-08-20.json` from the WU87 greenfield skeleton.
- Replaced the classifier stub with a read-only ACTIVE `SPM_INTENTS_V2` catalog loader, semantic classifier LLM chain, tolerant validator, and direct/clarify/fallback confidence routing.
- Enforced catalog authority for required entities, source gate, risk tier, sales stage, and per-intent confidence threshold; model output cannot override those business-control fields.
- Added safe recovery for invalid model intent and invalid secondary intent.
- Preserved `irreversible_action_allowed=false`; no production writes/actions were introduced.
- Static/offline deterministic QA: 37/37 PASS.
- Verified 62/62 ACTIVE unique intents and 32/32 golden runtime fixtures consistent with taxonomy metadata.
- Candidate SHA-256: `ab69c029a84f3f9b16800d4a5c10b96f46836cf713541caa532849d5582e7a32`.
- Uploaded candidate to Feature 011 `candidate/`; added `wu88-analysis.md` and `checklists/wu88-classifier-qa.md`.
- WU88 semantic n8n runtime was not executed; WU88 certification remains pending.
- Production workflows remain unchanged and cutover is unauthorized.
- Next gate: import WU88 inactive and execute `SPM_RUNTIME_TESTS` semantic classifier cases.


## 2026-08-20 — WU89 Entity Normalization + WU90 Durable State Prototypes
- Built WU89 on the canonical WU88 24-node classifier candidate.
- Added read-only ACTIVE entity-schema and normalization-rule loaders, explicit-message entity extraction, deterministic normalization, correction handling, separate multi-student profiles, Arabic integrity guards, timezone non-inference, and PII safety.
- WU89 static QA: 16/16 PASS; 35 unique nodes; zero dangling connections; zero production writes.
- WU89 artifact SHA-256: `704c3fa78525cb4ecdcf8dac1c36b0b0c971aa4cab0c3a040819bc79523b5cf2`.
- Built WU90 on WU89 with test-only Redis state load/save, non-destructive durable state merge, sticky opt-out, support/handoff/recovery overrides, next-best-action, missing-field and no-reask logic.
- WU90 Redis namespace is restricted to `spm:test:sales:*`; non-test traffic is blocked before Redis.
- WU90 static QA: 16/16 PASS; 40 unique nodes; zero dangling connections; only write is test-namespace Redis persistence.
- WU90 artifact SHA-256: `18a8487a50b53bf9638bcfdc251cc39a05f2989531a1de8e4c9e8df0ff484b77`.
- Added WU89 and WU90 static QA checklists.
- WU89/WU90 are prototypes/static PASS, not certified units; upstream WU88 semantic runtime remains the first blocking certification gate.
- Production workflows remain unchanged; production cutover remains unauthorized.


## 2026-08-20 — WU91–WU93 Knowledge, Sales Agent, and Commercial Prototypes
- Built WU91 Knowledge Retrieval & Source Gates on WU90.
- WU91 uses source_gate-driven read-only retrieval from one authorized source family per request, ACTIVE rows only, maximum three evidence records, with live/authorization/CRM claims blocked when their required source is unavailable.
- WU91 static QA: 19/19 PASS; 52 nodes; zero dangling references; zero production writes.
- WU91 SHA-256: `65b25c5f74ef6a2a139d973a157709ad47e171520b8022599bf4c9a1417df3d5`.
- Built WU92 Consultative Sales Agent Core on WU91.
- WU92 makes the AI a consultative Sales Agent rather than an FAQ bot; uses WU91 evidence, Sales Playbook, bounded intake questions, one-question/no-reask behavior, structured output, source-ref validation, false-success guard, opt-out, and handoff preservation.
- Isolated ACTIVE RESPONSE_RULES RULE-015/RULE-017 from the Sales Agent prompt because their fact-bearing currency/location logic conflicts with current PACKAGES/source-gate evidence. Source rows were not modified.
- WU92 static QA: 19/19 PASS; 62 nodes; zero dangling references; zero production writes.
- WU92 SHA-256: `8c9c1c5601b1bb0cde36f8dd5ed51ecbd22bc13648cf5dc299ebec722dbea2c6`.
- Built WU93 Commercial / Pricing / Objections Controls on WU92.
- WU93 adds deterministic package arithmetic, lowest-per-lesson comparison boundary, read-only SPM_CONFIG controls, approved OBJECTIONS guidance, authorization-required discount handling, competitor non-disparagement, and commercial claim guards.
- WU93 static QA: 17/17 PASS; 71 nodes; zero dangling references; zero production writes.
- WU93 SHA-256: `14a4ea707e469c45ed95598e900f8b7182459ac4d29939170e8c3547cfce9458`.
- WU91/WU92/WU93 are prototype/static PASS only. WU88 semantic runtime remains the first blocking certification gate.
- Production workflows remain unchanged; production cutover remains unauthorized.
- Next implementation unit: WU94 — trial, live availability, scheduling, and booking.


## 2026-08-20 — WU94 Trial / Scheduling Truth Layer Prototype
- Built `SPM_E2E_Sales_Agent_Greenfield_WU94_Trial_Scheduling_Truth_Layer_2026-08-20.json` on the canonical WU93 candidate.
- Added trial/scheduling mode resolution, deterministic request prerequisites, admin-controlled lifecycle contract, safe scheduling-adapter result, Sales Agent scheduling context, and false-success truth guard.
- Current operating model is admin-controlled: `WAITING_FOR_ASSIGNMENT → TEACHER_ASSIGNED → SCHEDULED`; automatic teacher selection and automatic slot booking remain disabled.
- Availability claims require approved live scheduling evidence. Booking confirmation requires live tool success plus non-empty `booking_id`.
- Country alone is not used to infer timezone; approved city/region mapping or explicit IANA timezone is required.
- No approved live scheduling/LMS API endpoint, credential, or booking workflow identifier was found in current sources; WU94 therefore returns `NOT_CONFIGURED` rather than inventing an integration.
- Static QA: 21/21 PASS; deterministic scheduling contract tests: 8/8 PASS.
- WU94 graph: 76 nodes; zero dangling references; no new production Sheets/HTTP/Execute Workflow action nodes.
- WU94 SHA-256: `3f6263dbe38496ef29b237a8d834ac9da019e54aa3babebbd0a86e097adef22e`.
- WU94 Drive file ID: `1F_jrTDDgwz6t_IzJsgb3YAPvz2dKt6Yp`.
- Added `checklists/wu94-trial-scheduling-truth-layer-qa.md`.
- WU94 remains prototype/static PASS only. WU88 semantic runtime remains the first certification gate.
- Production workflows unchanged; cutover unauthorized.
- Next implementation unit: WU95 — deterministic lead conversion, consent, UPSERT, correction, dedupe, and handoff.

## 2026-08-20 — WU95 Deterministic Lead Conversion Prototype
- Built `SPM_E2E_Sales_Agent_Greenfield_WU95_Deterministic_Lead_Conversion_2026-08-20.json` on canonical WU94.
- Added canonical lead payload construction from durable state without re-asking known fields.
- Added deterministic validation for session, names, phone, email, country/city/timezone, subject/grade, preferred language, summary, explicit contact consent, and final confirmation.
- Added read-only `LEADS_TEMPLATE` lookup by `session_id` and deterministic create/update/no-change/conflict assessment.
- Existing lead corrections preserve the same `lead_id`/`created_at`; identical data is no-change; multiple same-session rows are blocked as conflict.
- Multi-student writes are blocked with `MULTI_STUDENT_LEAD_KEY_REQUIRED` until a safe per-student idempotency key exists.
- Added spreadsheet-formula injection protection and preserved Arabic semantic integrity; no unsafe global `ة→ه` rewrite.
- Added a precise V2 `appendOrUpdate` reference node matching by `session_id`, but it is disabled and disconnected in WU95.
- Added deterministic human-handoff contract with execution adapter NOT_CONFIGURED.
- Added false-success guard: lead success requires executed successful write + non-empty lead_id + verified created/updated operation.
- Added second test-only Redis persistence after conversion state updates.
- Static QA: 29/29 PASS; deterministic lead contract regression: 14/14 PASS.
- WU95 SHA-256: `0d52cb2cc8b54db920743a334d5977146f008931f9f4aae575456ea96fbed9bd`.
- WU95 Drive file ID: `1CWlgLs4cdU2L7JkKK7X8hP_CzIGwe7dL`.
- Added `checklists/wu95-deterministic-lead-conversion-qa.md`.
- Production workflows unchanged; production cutover unauthorized.
- Next implementation unit: WU96 — nurture/follow-up/sticky opt-out/support overrides.



## 2026-08-20 — WU96 Nurture / Follow-Up / Sticky Opt-Out / Support Overrides Prototype
- Built `SPM_E2E_Sales_Agent_Greenfield_WU96_Nurture_OptOut_Support_Overrides_2026-08-20.json` on canonical WU95.
- Added deterministic communication mode resolution for normal sales, nurture, stop/opt-out, and support.
- Added sticky opt-out behavior: `not_interested` sets opt_out; an existing opt-out blocks future promotional nurture/sales and cannot be cleared automatically.
- Added support-over-sales precedence for human handoff, complaint, technical issue, account login, contact update, payment problem, and tutor-change requests.
- Added consent-gated follow-up: `follow_up` is eligible only with valid contact consent and no opt-out; `need_to_think` never schedules follow-up automatically.
- Added read-only ACTIVE `SALES_NURTURE` context and deterministic post-model communication truth guard.
- Added false-execution protection for external follow-up, CRM opt-out persistence, and human handoff; all remain NOT_CONFIGURED in this prototype.
- No new production write nodes. Existing WU95 Lead UPSERT remains disabled/disconnected; Redis persistence remains test namespace only.
- Static QA: 32/32 PASS; communication contract regression: 15/15 PASS.
- WU96 SHA-256: `086fab4218b3aefcbfb571c6f334cd6a134162a8db836f795d7107454d00731e`.
- WU96 Drive file ID: `19LK97ZBtwqgOR9431ELLmYbulA0XKQcj`.
- Added `checklists/wu96-nurture-optout-support-qa.md`.
- Production workflows unchanged; production cutover unauthorized.
- Next implementation unit: WU97 — reliability, retries, observability, privacy, and security controls.


## 2026-08-21 — WU97 Reliability / Privacy / Security Prototype
- Built `SPM_E2E_Sales_Agent_Greenfield_WU97_Reliability_Privacy_Security_2026-08-21.json` on canonical WU96.
- Added input security before all external processing, blocking oversized/excess-control-character messages safely.
- Added bounded retries to model chains and missing Lead read retry/error handling; no unbounded retry loops.
- Added explicit Lead lookup failure branch that blocks UPSERT instead of treating a failed lookup as a new lead.
- Added unified reliability policy/error taxonomy, runtime health aggregation, and fail-closed behavior for unhealthy dependencies/state persistence failures.
- Added privacy/security guard that preserves sticky opt-out and blocks irreversible actions during fail-closed recovery.
- Upgraded telemetry to PII-redacted `SPM_TELEMETRY_V2`: correlation ID only, no raw session/message, email/phone scrubbing, error codes only, and no secret/token fields.
- Existing Lead UPSERT remains disabled/disconnected; no production Sheets/HTTP/ExecuteWorkflow writes were enabled; Redis remains test namespace only.
- Static QA: 54/54 PASS; reliability/security contract regression: 18/18 PASS.
- WU97 graph: 108 nodes; zero dangling references.
- WU97 SHA-256: `9946d7de5cbcfd15feb1dcb91a5f97aec9c5ab9900794e855e5f20de092d93dc`.
- WU97 Drive file ID: `1W6oT_XNGqL9YlUS85kKM7m424avdUYzW`.
- Added `checklists/wu97-reliability-privacy-security-qa.md`.
- Production workflow unchanged; cutover unauthorized.
- Next implementation unit: WU98 — multilingual/conversation regression and red-team expansion.


## 2026-08-21 — WU98 Multilingual / Conversation Regression Pack
- Completed WU98 design-time/offline regression expansion without changing the WU97 execution graph.
- Retained authoritative `SPM_RUNTIME_TESTS` RT-001..RT-032 and added RT-033..RT-096 as 64 new test cases.
- Combined runtime target is 96 cases covering all 62/62 SPM V2 intents.
- Expansion coverage includes EN/AR/FR parity, code-switching, Arabic dialect ambiguity, typos, multi-turn corrections, no-reask, multiple children, long-session sticky opt-out/support state, prompt injection, PII leakage attempts, booking truth, discount authorization, and CRM false-success prevention.
- Suite metadata QA: 20/20 PASS.
- Deterministic WU97 safety/static regression: 44/44 PASS.
- Actual n8n LLM semantic/conversation runtime was NOT_RUN; WU98 certification therefore remains pending.
- Expansion JSON SHA-256: `25c2e96703580a60c4ee4a09c5aabac11a7bb1a795350673c02dd32737501b90`.
- Expansion CSV SHA-256: `c802cad113f619dd96bcf40d610b5f0d1102a85fbe19cbfda88c9b606c051b4f`.
- Offline report SHA-256: `be276bb1e68d5181058a846143756d44f7a083f4fbb713a7707176047188e690`.
- Offline QA SHA-256: `5734ee2b42e9e0f530bfc1b2847ba115c3585cef6483f06be9510f6b48ad55b9`.
- Production workflow unchanged; production cutover unauthorized.
- Next unit: WU99 full runtime/E2E certification, starting with the blocking WU88 semantic classifier runtime and then proceeding in dependency order.

## 2026-08-21 — WU99 Runtime Certification Preparation
- Prepared WU99 runtime certification infrastructure; actual n8n runtime was NOT_RUN.
- Created `SPM_E2E_Sales_Agent_Greenfield_WU99_Runtime_Testable_2026-08-21.json` from canonical WU97 with one additional TEST-only Execute Workflow Trigger.
- Testable SUT: 109 nodes, active=false, zero dangling references, no production write enabled; SHA-256 `a74b6443151eca02d3cc0b28126be96344a68326a389f6ac2951f54bcce0c6fc`.
- Created `SPM_WU99_Runtime_Certification_Harness_96_2026-08-21.json`: 5 nodes, active=false; Execute-SUT node is deliberately disabled/unbound until the imported SUT workflow ID is selected; SHA-256 `965ae82f03cd8e3f7cfbf0bcd12ac859cf5618373c25590b861e02858f6f06ab`.
- Created 96-case runtime plan with 106 invocations to support multi-turn correction/long-session prerequisites; coverage remains 62/62 intents.
- Added a 96-row runtime evidence ledger and 15-case failure-injection matrix.
- Added WU99 runtime runbook and preflight QA; preflight static QA PASS.
- WU99 remains BLOCKED_NOT_RUN because no n8n execution connector is available in this environment and no actual execution evidence exists.
- WU100 canary release is blocked until WU99 runtime + manual semantic review + failure injection pass with zero blocking defects and release approval.
- Production cutover remains unauthorized.
## 2026-08-21 — WU100 Canary / Production Release Preparation
- Prepared WU100 release package; actual canary and production cutover remain NOT_RUN and unauthorized.
- Added `SPM_WU100_Canary_Release_Plan_2026-08-21.md` and `SPM_WU100_Release_Manifest_TEMPLATE_2026-08-21.json` to Feature 011 candidate artifacts.
- Added rollback runbook, production approval checklist, canary monitoring gates, and WU100 preparation QA to checklists.
- WU100 preparation QA: 12/12 PASS.
- Explicitly prohibited direct promotion of the WU99 Runtime-Testable SUT because it contains a TEST-only Execute Workflow Trigger.
- Final immutable production RC remains unset until WU99 runtime PASS and must be a clean export with test-only trigger/harness removed and production configuration reviewed.
- Defined zero-tolerance hard stops for P0/P1, false lead/booking success, duplicate lead, wrong correction, opt-out violation, PII/secret leak, test traffic production writes, unauthorized actions, and cross-student corruption.
- Proposed canary traffic progression 5% → 20% → 50% → 100%; proposal is not owner-approved. Operational latency/cost/error/volume/duration thresholds remain TBD rather than invented.
- Rollback target remains the last approved/locked baseline (R1 unless explicitly superseded later); rollback drill is NOT_RUN.
- WU99 runtime, manual semantic review, failure injection, owner approval, clean RC creation, rollback verification, and canary PASS remain mandatory blockers.
- Production cutover remains unauthorized.

