# PROJECT_STATE.md

Last updated: 2026-08-21
Project: Success Path Mentors — AI Sales Chatbot / n8n Automation
Timezone: America/Toronto

## Release State
- R1 — Reliable Lead Submission: APPROVED AND LOCKED.
- Focused R1 regression tests: 10/10 PASS, owner confirmed.
- Active development strategy: Greenfield End-to-End Sales Agent rebuild.
- Active Spec Kit feature: `011-e2e-sales-agent-greenfield`.
- WU87 — Greenfield Architecture & Contracts: COMPLETE; static architecture PASS.
- WU88 — 62-Intent Classifier & Routing: IMPLEMENTATION COMPLETE; static/offline deterministic QA 37/37 PASS; semantic n8n runtime certification PENDING.
- WU89 — Entity Extraction & Normalization: PROTOTYPE COMPLETE; static safety 16/16 PASS; runtime certification PENDING.
- WU90 — Durable Sales State & Journey: PROTOTYPE COMPLETE; static safety 16/16 PASS; Redis/journey runtime certification PENDING.
- WU91 — Knowledge Retrieval & Source Gates: PROTOTYPE COMPLETE; static QA 19/19 PASS; runtime certification PENDING.
- WU92 — Consultative Sales Agent Core: PROTOTYPE COMPLETE; static QA 19/19 PASS; runtime certification PENDING.
- WU93 — Pricing / Offers / Objections: PROTOTYPE COMPLETE; static QA 17/17 PASS; runtime certification PENDING.
- WU94 — Trial / Scheduling Truth Layer: PROTOTYPE COMPLETE; static QA 21/21 PASS + contract tests 8/8 PASS; approved live adapter endpoint/credential NOT CONFIGURED; runtime certification PENDING.
- WU95 — Deterministic Lead Conversion: PROTOTYPE COMPLETE; static QA 29/29 PASS + contract regression 14/14 PASS; real lead-write/handoff adapters disabled or not configured; runtime certification PENDING.
- WU96 — Nurture / Follow-Up / Opt-Out / Support Overrides: PROTOTYPE COMPLETE; static QA 32/32 PASS + contract regression 15/15 PASS; external follow-up/CRM opt-out/handoff adapters NOT CONFIGURED; runtime certification PENDING.
- WU97 — Reliability / Privacy / Security: PROTOTYPE COMPLETE; static QA 54/54 PASS + contract regression 18/18 PASS; production writes remain disabled; runtime certification PENDING.
- WU98 — Multilingual / Conversation Regression: OFFLINE REGRESSION PACK COMPLETE; RT-033..RT-096 adds 64 new cases to authoritative RT-001..RT-032 for a 96-case target, 62/62 intent coverage, suite metadata QA 20/20 PASS + deterministic WU97 safety regression 44/44 PASS; actual n8n LLM semantic runtime NOT_RUN.
- WU99 — Full Runtime / E2E Certification: PREPARED, NOT RUN; 109-node WU97-equivalent testable SUT + 5-node harness + 96-case/106-invocation plan + evidence ledger + 15-case failure-injection matrix created. SUT/harness inactive; Execute-SUT node disabled and unbound until the imported SUT workflow ID is selected in n8n.
- WU100 — Canary Release / Production Certification: PREPARATION PACKAGE COMPLETE; canary plan, release-manifest template, rollback runbook, monitoring gates, production approval checklist, and preparation QA created. Preparation QA 12/12 PASS. ACTUAL CANARY/PRODUCTION RELEASE NOT_RUN and BLOCKED on WU99 runtime PASS + owner approval.
- First blocking certification gate remains actual WU88 semantic n8n runtime inside WU99; downstream runtime certification cannot pass before upstream PASS.
- Next action: execute WU99 in n8n. WU100 release execution remains blocked; only its planning/package layer is prepared.
- New implementation sequence runs WU87 through WU100.
- R1/R2/R2.5 remain protected reference/regression/rollback artifacts; do not patch their graph as the primary build path.
- Production cutover is NOT authorized.

## Current Source of Truth
- Greenfield feature: `09_Spec_Kit_SDD/specs/011-e2e-sales-agent-greenfield/`
- Greenfield contracts: `contracts.md`
- WU87 candidate: `candidate/SPM_E2E_Sales_Agent_Greenfield_WU87_Skeleton_2026-08-20.json`
- WU88 candidate: `candidate/SPM_E2E_Sales_Agent_Greenfield_WU88_62Intent_Classifier_2026-08-20.json`
- WU89 candidate: `candidate/SPM_E2E_Sales_Agent_Greenfield_WU89_Entities_Normalization_2026-08-20.json`
- WU90 candidate: `candidate/SPM_E2E_Sales_Agent_Greenfield_WU90_Durable_State_Journey_2026-08-20.json`
- WU91 candidate: `candidate/SPM_E2E_Sales_Agent_Greenfield_WU91_Knowledge_Source_Gates_2026-08-20.json`
- WU92 candidate: `candidate/SPM_E2E_Sales_Agent_Greenfield_WU92_Consultative_Sales_Agent_Core_2026-08-20.json`
- WU93 candidate: `candidate/SPM_E2E_Sales_Agent_Greenfield_WU93_Commercial_Objections_2026-08-20.json`
- WU94 candidate: `candidate/SPM_E2E_Sales_Agent_Greenfield_WU94_Trial_Scheduling_Truth_Layer_2026-08-20.json`
- WU95 candidate: `candidate/SPM_E2E_Sales_Agent_Greenfield_WU95_Deterministic_Lead_Conversion_2026-08-20.json`
- WU96 candidate: `candidate/SPM_E2E_Sales_Agent_Greenfield_WU96_Nurture_OptOut_Support_Overrides_2026-08-20.json`
- WU97 candidate: `candidate/SPM_E2E_Sales_Agent_Greenfield_WU97_Reliability_Privacy_Security_2026-08-21.json`
- WU98 expansion JSON: `candidate/SPM_WU98_Multilingual_RedTeam_Expansion_64_2026-08-21.json`
- WU98 expansion CSV: `candidate/SPM_WU98_Multilingual_RedTeam_Expansion_64_2026-08-21.csv`
- WU98 offline report: `checklists/SPM_WU98_Offline_Regression_Report_2026-08-21.md`
- WU98 offline QA: `checklists/SPM_WU98_Offline_QA_2026-08-21.json`
- WU99 testable SUT: `candidate/SPM_E2E_Sales_Agent_Greenfield_WU99_Runtime_Testable_2026-08-21.json`
- WU99 runtime harness: `candidate/SPM_WU99_Runtime_Certification_Harness_96_2026-08-21.json`
- WU99 runtime plan: `candidate/SPM_WU99_Runtime_Certification_Plan_96_2026-08-21.json`
- WU99 evidence ledger: `checklists/SPM_WU99_Runtime_Evidence_Ledger_96_2026-08-21.csv`
- WU99 failure injection matrix: `checklists/SPM_WU99_Failure_Injection_Matrix_2026-08-21.csv`
- WU99 runbook: `checklists/SPM_WU99_Runtime_Certification_Runbook_2026-08-21.md`
- WU99 preflight QA: `checklists/SPM_WU99_Preflight_QA_2026-08-21.json`
- WU100 canary plan: `candidate/SPM_WU100_Canary_Release_Plan_2026-08-21.md`
- WU100 release manifest template: `candidate/SPM_WU100_Release_Manifest_TEMPLATE_2026-08-21.json`
- WU100 rollback runbook: `checklists/SPM_WU100_Rollback_Runbook_2026-08-21.md`
- WU100 production approval checklist: `checklists/SPM_WU100_Production_Approval_Checklist_2026-08-21.md`
- WU100 canary monitoring gates: `checklists/SPM_WU100_Canary_Monitoring_Gates_2026-08-21.csv`
- WU100 preparation QA: `checklists/SPM_WU100_Preparation_QA_2026-08-21.json`
- WU97 QA: `checklists/wu97-reliability-privacy-security-qa.md`
- WU94 QA: `checklists/wu94-trial-scheduling-truth-layer-qa.md`
- WU95 QA: `checklists/wu95-deterministic-lead-conversion-qa.md`
- WU96 QA: `checklists/wu96-nurture-optout-support-qa.md`
- WU91 QA: `checklists/wu91-knowledge-source-gates-qa.md`
- WU92 QA: `checklists/wu92-sales-agent-core-qa.md`
- WU93 QA: `checklists/wu93-commercial-objections-qa.md`
- WU88 analysis: `wu88-analysis.md`
- WU88 QA: `checklists/wu88-classifier-qa.md`
- Greenfield task map: `tasks.md`
- Legacy locked workflow: `03_Workflows_Current/ChatBotMSE_v2_R1_LOCKED_2026-08-17.json`
- Human handoff workflow: `03_Workflows_Current/Validated_Human_Handoff_FIXED.json`
- Architecture: `02_Current_Architecture/SYSTEM_ARCHITECTURE.md`
- Current progress: `01_Governance_Plans/CURRENT_STATUS_PROGRESS.md`
- Release gates: `01_Governance_Plans/RELEASE_PHASES_AND_GATES.md`
- QA gate: `05_Testing_QA/QA_TESTING_RELEASE_GATE.md`
- R1 lock evidence: `05_Testing_QA/R1_LOCK_RECORD_2026-08-17.md`

## R1 Locked Behavior
- Complete confirmed lead writes successfully.
- Corrected data updates the same lead/session.
- Invalid or unconfirmed data is not written.
- Duplicate confirmation does not create duplicate leads.
- Operational lead messages do not enter unanswered-question logging.
- Success is reported only after the write succeeds.

## Current Greenfield Architecture Snapshot
Website Chat
→ Greenfield test/session guard
→ 62-intent classifier + confidence/ambiguity routing
→ entity extraction/normalization + multi-student separation
→ test-namespace Redis durable sales state + journey/NBA
→ WU91 source-gate resolver + bounded approved evidence
→ WU92 consultative Sales Agent
→ WU93 pricing/offer/objection controls
→ WU94 scheduling/booking truth layer
→ WU95 deterministic lead conversion contracts
→ WU96 nurture/opt-out/support overrides
→ deterministic action gateway (still NO PRODUCTION WRITES in current prototype)
→ telemetry / test response

Production workflow remains separate and unchanged.

## Known R2 Reliability Priority
The locked export exposes `Submit Validated Human Handoff` through the AI Agent tool connection.
Decoupling deterministic writes from model tool choice is a P1 R2/R3 reliability improvement.
Treat this as a planned refactor, not an R1 failure, unless regression evidence exists.

## Knowledge-Base State
- Issue 1 — Canada/USA pricing and location resolution: LOCKED.
- Issue 2 — refund/service-recovery policy: LOCKED.
- Next knowledge issue: review `PHR-004` in `ISLAMIC_PHRASES`.
- Do not change approved knowledge wording without explicit approval.

## Context Operating Budget

### Hot Context — preferred
Target: 10K–30K tokens.
Load only:
- this state file;
- current task;
- affected workflow nodes/sections;
- latest error/execution evidence.

### Normal Working Context
Preferred ceiling: ~100K tokens for most tasks.
Cross-system work may temporarily exceed this only when dependencies genuinely require it.

### Warm Context
30K–100K tokens:
- architecture constraints;
- direct dependencies;
- relevant validation/mapping rules;
- recent decisions for the current task.

### Cold Context
Do not load by default:
- `08_Archive`;
- old JSON versions;
- pasted historical transcripts;
- completed-task logs;
- unrelated reports;
- full previous conversations.

## Mandatory Retrieval Protocol
1. Read `AGENTS.md`.
2. Read this file.
3. Define one measurable task.
4. Search for exact node/file/error names.
5. Read only relevant ranges or connected nodes.
6. Expand context only when evidence requires it.
7. Implement the smallest safe change.
8. Test.
9. Update state/change log.
10. Archive obsolete working versions.

Default pattern:
Search → Read exact range → Work → Test → Update state.

Never default to:
Read everything → reconstruct project history → work.

## Next Action
WU99 runtime-certification infrastructure and the WU100 release-preparation package are both ready, but actual n8n runtime is still NOT_RUN.

Required execution remains WU99 first:
1. Import `SPM_E2E_Sales_Agent_Greenfield_WU99_Runtime_Testable_2026-08-21.json` as a NEW inactive workflow.
2. Resolve only the test-copy Google Sheets, Redis, and OpenAI credentials.
3. Import `SPM_WU99_Runtime_Certification_Harness_96_2026-08-21.json` as a separate inactive workflow.
4. In the harness, select the newly imported WU99 SUT workflow in `Execute Greenfield SUT [CONFIGURE TARGET THEN ENABLE]`, then enable only that node.
5. Execute all 96 cases / 106 invocations and capture execution IDs/results.
6. Complete manual semantic review and the 15-case failure-injection matrix.
7. Re-run protected R1 lead outcomes after any runtime fix.
8. Only after WU99 PASS, create a CLEAN immutable production RC. Do NOT promote the WU99 Runtime-Testable SUT directly because it contains a TEST-only trigger.
9. Fill the WU100 Release Manifest, verify rollback, approve operational canary thresholds, record owner approval, then run canary.

WU100 package status: PREPARED ONLY. Proposed rollout profile is 5% → 20% → 50% → 100%, but observation duration, minimum conversations, latency/cost/error thresholds remain TBD pending owner/ops approval. Hard-stop invariants have zero tolerance.

Production cutover remains unauthorized. Certification/release PASS cannot be inferred from static artifacts.

WU94 integration gap remains: no approved live scheduling/LMS endpoint/credential is configured.

WU95 integration gap remains: real Lead/CRM write and Human Handoff execution are disabled/not configured in Greenfield certification.

WU96 integration gap remains: external follow-up, CRM opt-out persistence, and handoff execution are NOT_CONFIGURED.

## Session Exit Requirement
Before ending a technical session, update:
- current phase/task;
- latest working artifact;
- change made;
- test result/evidence;
- unresolved issue;
- exact next action.

A fresh session must be able to resume without reading the old conversation.

## 2026-08-20 R2 Spec Kit Checkpoint
- Current feature: `001-r2-error-handling`.
- Spec Kit lifecycle completed through static candidate analysis: spec → clarify → plan → tasks → candidate → static QA.
- Candidate artifact: `specs/001-r2-error-handling/candidate/Validated_Human_Handoff_R2_ERROR_HANDLING_CANDIDATE_2026-08-20.json`.
- Candidate is explicitly `active=false` before runtime validation; verified Drive SHA-256: `5678b2c27623d9927d28f4f54631620153d07fd057a003a6b35edc8ecc7de683`.
- Candidate scope is intentionally bounded to `Validated_Human_Handoff_FIXED.json`; the R1 locked main workflow was not modified.
- Added structured lookup/write failure outputs plus bounded retry on the two in-scope Google Sheets operations.
- Static QA: PASS. Candidate JSON valid; node names/IDs unique; protected validation/conflict/success paths preserved; Drive readback matched the tested candidate.
- Master Spec Kit task map now marks T006/T007 and T024–T030 complete.
- Full removal of final submission from AI tool choice is deferred to `002-deterministic-lead-submission`, because the current main sales state does not yet persist the complete canonical handoff payload.
- Runtime QA: NOT RUN. Drive exports do not prove which n8n workflow/subworkflow is actively published.
- Release status: BLOCKED pending runtime identity verification, focused R2 failure-injection tests, complete R1 10/10 regression, convergence, and release approval.

### Exact Next Action
1. Verify the active main workflow and validated-handoff subworkflow IDs in n8n.
2. Import/attach the R2 error-handling candidate as a non-production candidate.
3. Execute focused R2 runtime cases R2-F01 through R2-F10 and record execution evidence.
4. Re-run all permanent R1 regression cases 1–10.
5. Run convergence and promote only if every gate passes.

## 2026-08-20 Runtime Export Reconciliation
- Uploaded active handoff export verified: `Validated Human Handoff`, workflow ID `swhmNa0Goo0uYm1k`, `active=true`.
- Uploaded main candidate verified: `ChatBotMSE v2 - R2.5 Release Candidate Stable Efficient`, workflow ID `vSc7cMIMFMEUdi7z`, `active=false`.
- R2.5 contains a deterministic registration/handoff path and no `ai_tool` connection for final lead submission.
- `Execute Validated Human Handoff Directly` points to workflow ID `swhmNa0Goo0uYm1k`, matching the uploaded active handoff.
- Therefore, the previously deferred deterministic lead-submission architecture is already implemented statically in R2.5, but is not yet production-certified.
- A safer Feature 001 test candidate was rebuilt from the uploaded active handoff rather than the older baseline.
- SAFE TEST artifact: `specs/001-r2-error-handling/candidate/Validated_Human_Handoff_R2_ERROR_HANDLING_SAFE_TEST_2026-08-20.json`.
- SAFE TEST safety: `active=false`, no top-level workflow `id`, no top-level `versionId`; existing active-handoff node IDs/semantics preserved except the two intended retry/error-handling nodes.
- SAFE TEST SHA-256: `0a6935331fddc9c9ee1a3ac1720bd884c61a0a9eefa6a2fcd408e7810359905c`.
- Static QA: PASS.
- Runtime main identity is still unresolved because the uploaded R2.5 export is inactive.

### Revised Exact Next Action
1. Export or identify the actually ACTIVE main chatbot workflow in n8n.
2. Import the SAFE TEST handoff candidate as a new inactive workflow (do not replace `swhmNa0Goo0uYm1k`).
3. Point only a non-production copy of R2.5 to the newly imported SAFE TEST workflow.
4. Run R2-F01 through R2-F10 and capture execution evidence.
5. Re-run the permanent R1 10/10 regression set.
6. Converge Feature 001 and the already-present R2.5 deterministic submission path.
7. Promote only if every gate passes.

## Greenfield E2E Sales Agent Directive
- Owner direction: stop using the current end-to-end workflow as the construction base for the next generation.
- Build a new workflow from scratch under `09_Spec_Kit_SDD/specs/011-e2e-sales-agent-greenfield`.
- Product identity: AI Sales Agent, not FAQ bot. FAQ/KB is a supporting grounded knowledge service inside the sales journey.
- Mandatory design inputs: 62-intent SPM V2 taxonomy, entity/normalization schema, Sales Playbook, config/source gates, runtime tests, and WU84–WU86 evidence.
- WU84: integration/mapping input for the 62-intent model and deterministic controls.
- WU85: offline regression input; 23/23 baseline checks passed but runtime work remains historical evidence.
- WU86: certification/business-control input.
- New greenfield implementation sequence: WU87–WU100.
- Existing R1/R2/R2.5 workflows remain available only for regression outcomes, rollback, and integration reference.
- Current greenfield artifacts: `spec.md`, `plan.md`, `work-units.md`, `tasks.md`, and `checklists/greenfield-release-gate.md`.
- Production cutover is NOT authorized.

### Exact Next Action — WU87-T01
Create a completely new inactive n8n workflow. Do not clone the production node graph. Build only the WU87 architecture skeleton and contracts, then export it for static QA before implementing WU88 classifier behavior.

## 2026-08-20 WU87 Greenfield Architecture Completion
- Feature: `011-e2e-sales-agent-greenfield`.
- WU87 — Greenfield Architecture & Contracts: COMPLETE; static architecture gate PASS.
- New candidate: `candidate/SPM_E2E_Sales_Agent_Greenfield_WU87_Skeleton_2026-08-20.json`.
- Drive candidate file ID: `18jIsNNGPsAXkWcbcawy4f40WGn7mjFa4`.
- Candidate safety: `active=false`; top-level workflow `id`, `versionId`, and instance metadata are absent so import creates a new identity.
- Candidate SHA-256: `c636cde504cf7945fe63664668e76862a4a21575b867979fc6e96c135ae14e95`.
- Graph: 14 nodes; 14/14 unique names; 14/14 unique node IDs; 0 missing/dangling graph references.
- Production-write scan: 0 write nodes; 0 Execute Workflow nodes; 0 model/LLM nodes.
- Redis architecture placeholder: one GET node, disabled until WU90; no Redis write exists.
- Non-test traffic is blocked immediately by the WU87 test-mode guard.
- Added `contracts.md` defining session, durable sales state, classifier, entity, journey/NBA, source gate, Sales Agent output, deterministic action gateway, telemetry, and test-mode contracts.
- Added `checklists/wu87-static-qa.md`; result PASS.
- Updated `tasks.md`: WU87-T01 through WU87-T14 complete.
- Current production workflows remain unchanged and are still legacy/reference/regression/rollback only.
- Production cutover remains unauthorized.

### Exact Next Action — WU88
Implement the 62-intent classifier and routing on a new WU88 candidate derived from the WU87 greenfield skeleton. Use `SPM_INTENTS_V2` as the authoritative 62-intent catalog, enforce per-intent confidence/source-gate metadata, block irreversible actions on unresolved or low-confidence classification, and run offline/static classifier regression before any runtime promotion.



## 2026-08-20 WU88 62-Intent Classifier Implementation Checkpoint
- Feature: `011-e2e-sales-agent-greenfield`.
- WU88 implementation candidate: `candidate/SPM_E2E_Sales_Agent_Greenfield_WU88_62Intent_Classifier_2026-08-20.json`.
- Drive candidate file ID: `1qYNlqvqZ7k3NlTNbBSVBRLCrBIBa4HWB`.
- Candidate SHA-256: `ab69c029a84f3f9b16800d4a5c10b96f46836cf713541caa532849d5582e7a32`.
- Candidate safety: `active=false`; no top-level workflow `id` or `versionId`; test-mode guard retained; no production write/action nodes introduced.
- Graph: 24 nodes; 24/24 unique names; 24/24 unique IDs; 0 dangling graph references.
- Added read-only `SPM_INTENTS_V2` loader against the safe V2 workbook, ACTIVE rows only, with bounded retry.
- Added dedicated semantic classifier LLM chain and classifier model.
- Added tolerant JSON validation and deterministic catalog authority: `required_entities`, `source_gate`, `risk_tier`, `sales_stage`, and `min_confidence` are derived from `SPM_INTENTS_V2`, not trusted from model output.
- Added direct / clarify / fallback routing. Low-confidence or ambiguous classification cannot authorize irreversible action.
- Added explicit disambiguation guidance for pricing vs price objection, teacher quality question vs objection, trial request vs trial details, scheduling distinctions, conversion distinctions, nurture/stop, support, and payment cases.
- Static/offline deterministic QA: 37/37 PASS.
- Taxonomy gate: 62/62 unique ACTIVE intents; thresholds/source gates/risk tiers/languages valid.
- Golden fixture consistency: 32/32 `SPM_RUNTIME_TESTS` rows match the V2 taxonomy metadata for expected source gate and legacy route.
- Live semantic LLM accuracy was NOT executed in this environment and remains the blocking WU88 certification gate.
- Added `wu88-analysis.md` and `checklists/wu88-classifier-qa.md`.
- Updated `tasks.md`: WU88 implementation complete but certification checkbox remains open until n8n semantic runtime passes.
- Production workflow remains unchanged; production cutover remains unauthorized.

### Exact Next Action — WU88 Runtime Certification
1. Import the WU88 JSON as a new separate inactive workflow in n8n; do not replace production.
2. Confirm the Google Sheets and OpenAI credential references resolve.
3. Execute the `SPM_RUNTIME_TESTS` classifier cases using test/synthetic sessions only.
4. Capture `actual_intent`, confidence, `classifier_route`, and result for each case.
5. Fix any blocking semantic mismatch; require critical cases to pass before WU88 certification.
6. After WU88 runtime PASS, start WU89 entity extraction/normalization certification.


## 2026-08-20 WU89–WU90 Greenfield Prototype Checkpoint
- Feature: `011-e2e-sales-agent-greenfield`.
- WU89 prototype built from the canonical WU88 24-node classifier candidate, not from the older alternate draft.
- WU89 artifact: `candidate/SPM_E2E_Sales_Agent_Greenfield_WU89_Entities_Normalization_2026-08-20.json`.
- WU89 Drive file ID: `1G6yax_umfZNI7sqgjK4jUxbLUb2Qrdvf`.
- WU89 SHA-256: `704c3fa78525cb4ecdcf8dac1c36b0b0c971aa4cab0c3a040819bc79523b5cf2`.
- WU89 graph: 35 nodes; 35/35 unique names and IDs; zero dangling connections; zero production write nodes.
- WU89 reads `SPM_ENTITY_SCHEMA_V2` and `SPM_NORMALIZATION_V2` as ACTIVE read-only sources.
- WU89 enforces explicit-current-message extraction, raw preservation, safe normalization, Arabic semantic integrity, correction metadata, separate multi-student profiles, timezone non-inference from country, and PII validation/telemetry controls.
- WU89 static safety QA: 16/16 PASS. Semantic entity runtime remains uncertified.
- WU90 prototype built on the canonical WU89 artifact.
- WU90 artifact: `candidate/SPM_E2E_Sales_Agent_Greenfield_WU90_Durable_State_Journey_2026-08-20.json`.
- WU90 Drive file ID: `12HSIY0QI1hEfc-BIrF3PgT-TolmQ7FUX`.
- WU90 SHA-256: `18a8487a50b53bf9638bcfdc251cc39a05f2989531a1de8e4c9e8df0ff484b77`.
- WU90 graph: 40 nodes; 40/40 unique names and IDs; zero dangling connections.
- Redis is enabled only behind the Greenfield test-session guard and uses `spm:test:sales:*`; non-test sessions are blocked before Redis.
- WU90 implements non-destructive durable state merge, separate student-profile merge, sticky opt-out, support/handoff/recovery overrides, explicit journey stage, next-best-action, and missing-field/no-reask logic.
- Redis load/save use bounded retry and explicit safe fallback/failure context.
- Only write in WU90 is test-namespace Redis state persistence; there are still no Lead/CRM/booking/payment/handoff/production Sheets writes.
- WU90 static safety QA: 16/16 PASS. Redis persistence runtime remains uncertified.
- Added `checklists/wu89-entity-normalization-static-qa.md` and `checklists/wu90-state-journey-static-qa.md`.
- Production workflows remain untouched and production cutover remains unauthorized.

### Certification Dependency / Next Actions
1. WU88 semantic classifier runtime in n8n remains the first blocking certification gate.
2. After WU88 runtime PASS, certify WU89 entity extraction/normalization runtime.
3. After WU89 runtime PASS, certify WU90 Redis persistence and journey transitions.
4. WU91 — Knowledge Retrieval & Source Gates may be prototyped in parallel on the inactive Greenfield branch, but cannot be certified while upstream runtime gates remain open.


## 2026-08-20 WU91–WU93 Greenfield Prototype Checkpoint
- Feature: `011-e2e-sales-agent-greenfield`.
- WU91 artifact: `candidate/SPM_E2E_Sales_Agent_Greenfield_WU91_Knowledge_Source_Gates_2026-08-20.json`.
- WU91 Drive file ID: `1QLZVacJRLYp51rOk3ZVJkqDQHMx2rFxu`.
- WU91 SHA-256: `65b25c5f74ef6a2a139d973a157709ad47e171520b8022599bf4c9a1417df3d5`.
- WU91 graph: 52 nodes; unique names/IDs; zero dangling references; zero production write/action nodes.
- WU91 routes source claims by authoritative `source_gate` and uses one read-only source family per request: PACKAGES, POLICIES, SUBJECTS, SUBJECT_PATHWAYS, FAQ, SERVICES, LOCATIONS, or FALLBACKS.
- WU91 reads ACTIVE rows only from the safe V2 workbook, compacts to a maximum of three evidence records, and blocks unsupported live/authorization/CRM claims.
- WU91 static QA: 19/19 PASS. Runtime certification pending.
- WU92 artifact: `candidate/SPM_E2E_Sales_Agent_Greenfield_WU92_Consultative_Sales_Agent_Core_2026-08-20.json`.
- WU92 Drive file ID: `1VVcihcEgq0WYSPv2sWUV2FutIl_XFx_L`.
- WU92 SHA-256: `8c9c1c5601b1bb0cde36f8dd5ed51ecbd22bc13648cf5dc299ebec722dbea2c6`.
- WU92 graph: 62 nodes; unique names/IDs; zero dangling references; zero production writes.
- WU92 implements the primary consultative Sales Agent using WU91 evidence, Sales Playbook, bounded intake guidance, structured JSON output, deterministic source-ref validation, false-success protection, sticky opt-out, and human-handoff preservation.
- Data-governance conflict isolated: ACTIVE `RESPONSE_RULES` RULE-015/RULE-017 contain legacy fact-bearing currency/location logic conflicting with current PACKAGES/source-gate evidence. They are not changed, but are excluded from the Sales Agent prompt pending knowledge-governance reconciliation.
- WU92 static QA: 19/19 PASS. Runtime certification pending.
- WU93 artifact: `candidate/SPM_E2E_Sales_Agent_Greenfield_WU93_Commercial_Objections_2026-08-20.json`.
- WU93 Drive file ID: `1SvjJvCAXZHu5cs30QGJ7Eg7bndXuEn1O`.
- WU93 SHA-256: `14a4ea707e469c45ed95598e900f8b7182459ac4d29939170e8c3547cfce9458`.
- WU93 graph: 71 nodes; unique names/IDs; zero dangling references; zero production write/action nodes.
- WU93 adds deterministic package arithmetic, lowest-per-lesson comparison boundary, SPM_CONFIG read-only control context, approved OBJECTIONS guidance, authorized-offer boundary for discounts, competitor non-disparagement, and a commercial safety guard.
- WU93 static QA: 17/17 PASS. Runtime certification pending.
- Added checklists: `wu91-knowledge-source-gates-qa.md`, `wu92-sales-agent-core-qa.md`, and `wu93-commercial-objections-qa.md`.
- Production workflows remain unchanged; production cutover remains unauthorized.

### Certification / Next Actions
1. Run WU88 semantic classifier runtime first.
2. Then certify WU89 entity extraction, WU90 Redis/journey, WU91 source retrieval, WU92 Sales Agent, and WU93 commercial controls in dependency order.
3. Greenfield implementation may continue with WU94 on the inactive/test-only branch, but WU94 cannot be certified until upstream gates pass.
4. WU94 must not confirm availability or booking without live scheduling success; booking confirmation must require a valid `booking_id`.


## 2026-08-20 WU94 Trial / Scheduling Truth Layer Prototype Checkpoint
- Feature: `011-e2e-sales-agent-greenfield`.
- WU94 artifact: `candidate/SPM_E2E_Sales_Agent_Greenfield_WU94_Trial_Scheduling_Truth_Layer_2026-08-20.json`.
- WU94 Drive file ID: `1F_jrTDDgwz6t_IzJsgb3YAPvz2dKt6Yp`.
- WU94 SHA-256: `3f6263dbe38496ef29b237a8d834ac9da019e54aa3babebbd0a86e097adef22e`.
- WU94 graph: 76 nodes; unique names/IDs; zero dangling references.
- Added scheduling-mode resolution for free trial, availability, timezone, scheduling, booking confirmation, and secondary scheduling intent.
- Added deterministic scheduling contract with admin-controlled lifecycle: `WAITING_FOR_ASSIGNMENT → TEACHER_ASSIGNED → SCHEDULED`.
- Automatic teacher selection and automatic slot booking remain disabled.
- Added explicit rule: availability is never confirmed without approved live scheduling evidence.
- Added explicit rule: booking is never confirmed without tool `success=true` plus non-empty `booking_id`.
- Added explicit rule: country alone never resolves timezone; approved city/region mapping or explicit IANA timezone is required.
- Because no approved scheduling/LMS endpoint or credential is present, the safe adapter result remains `NOT_CONFIGURED`; WU94 does not invent an endpoint.
- Static QA: 21/21 PASS. Deterministic WU94 contract tests: 8/8 PASS, including RT-019, RT-020, RT-021, RT-027, and RT-032 behaviors.
- Added `checklists/wu94-trial-scheduling-truth-layer-qa.md`.
- WU94 is prototype/static PASS only; runtime certification remains blocked by WU88-first dependency order and by the missing approved live scheduling adapter.
- Production workflows remain unchanged; production cutover remains unauthorized.

### Next Implementation Unit — WU95
Build deterministic lead conversion, consent, UPSERT/correction/dedupe, and handoff using the Greenfield state. Preserve the R1 outcomes: no write before validation/confirmation, correction updates the same lead/session, duplicate confirmation does not create duplicates, and success is stated only after the write succeeds. Trial/scheduling status must not be promoted to `SCHEDULED` by WU95 unless WU94 live scheduling evidence exists.

## 2026-08-20 WU95 Deterministic Lead Conversion Prototype Checkpoint
- Feature: `011-e2e-sales-agent-greenfield`.
- WU95 artifact: `candidate/SPM_E2E_Sales_Agent_Greenfield_WU95_Deterministic_Lead_Conversion_2026-08-20.json`.
- WU95 Drive file ID: `1CWlgLs4cdU2L7JkKK7X8hP_CzIGwe7dL`.
- WU95 SHA-256: `0d52cb2cc8b54db920743a334d5977146f008931f9f4aae575456ea96fbed9bd`.
- WU95 graph: 92 nodes; unique names/IDs; zero dangling references.
- Added deterministic conversion-mode resolution, canonical lead payload construction, explicit consent/final-confirmation gate, read-only existing-lead lookup by `session_id`, and deterministic `create / update / no_change / conflict` assessment.
- Correction preserves the existing `lead_id` and `created_at`; repeated identical data produces `no_change`; more than one matching session row produces `MULTIPLE_LEADS_FOR_SESSION` and no new lead.
- Current `LEADS_TEMPLATE` lacks a safe per-student idempotency key for more than one child in the same session. WU95 therefore blocks multi-student lead write with `MULTI_STUDENT_LEAD_KEY_REQUIRED` rather than merging children.
- Spreadsheet formula injection is escaped; names are not aggressively normalized; the unsafe Arabic `ة→ه` rewrite is not used.
- Real Google Sheets `appendOrUpdate` exists only as `Upsert WU95 Lead [DISABLED REFERENCE ONLY]`: disabled, disconnected, V2 `LEADS_TEMPLATE`, matching by `session_id`.
- Human handoff is an explicit deterministic contract but its Greenfield execution adapter remains `NOT_CONFIGURED`.
- WU95 post-conversion state is persisted only to the test Redis namespace `spm:test:sales:*`.
- Lead success may be reported only when `tool_executed=true`, `success=true`, a non-empty `lead_id` exists, and operation is verified as created/updated.
- Static QA: 29/29 PASS. Deterministic lead contract regression: 14/14 PASS.
- R1 protected outcomes remain acceptance criteria: no write before validation/confirmation; correction updates same lead/session; invalid/unconfirmed data not written; duplicate confirmation does not create duplicate lead; success only after write success.
- Added `checklists/wu95-deterministic-lead-conversion-qa.md`.
- WU95 remains prototype/static PASS only. First certification gate remains WU88 semantic runtime.
- Production workflow unchanged; production cutover unauthorized.

### Next Implementation Unit — WU96
Build nurture/follow-up/opt-out/support overrides on WU95. Sticky opt-out must override all promotional follow-up. Follow-up may be proposed only when eligible and consent/state allows it. Support, complaint, technical issue, account/login, payment problem, and explicit human handoff must suppress sales pressure and preserve the known conversation state.



## 2026-08-20 WU96 Nurture / Opt-Out / Support Overrides Prototype Checkpoint
- Feature: `011-e2e-sales-agent-greenfield`.
- WU96 artifact: `candidate/SPM_E2E_Sales_Agent_Greenfield_WU96_Nurture_OptOut_Support_Overrides_2026-08-20.json`.
- WU96 Drive file ID: `19LK97ZBtwqgOR9431ELLmYbulA0XKQcj`.
- WU96 SHA-256: `086fab4218b3aefcbfb571c6f334cd6a134162a8db836f795d7107454d00731e`.
- WU96 graph: 100 nodes; unique names/IDs; zero dangling references.
- Added deterministic communication precedence: current support intent is served before sales; sticky opt-out blocks promotional nurture; `not_interested` sets opt_out immediately; nurture runs only when no higher-priority override applies.
- Added read-only ACTIVE `SALES_NURTURE` retrieval for nurture context.
- `follow_up` requires valid `consent_to_contact` and no opt-out; `need_to_think` never creates automatic follow-up.
- Support intents (`human_handoff`, `complaint`, `technical_issue`, `account_login`, `update_contact_info`, `payment_problem`, `change_teacher`) suppress sales CTA and preserve known state.
- Current support may be served even when already opted out, but opt-out remains sticky after support handling.
- External follow-up, CRM opt-out persistence, and human-handoff execution are NOT_CONFIGURED; WU96 never reports these actions as executed.
- No new production write nodes were added. Existing WU95 `appendOrUpdate` remains disabled/disconnected reference only; Redis remains test namespace only.
- Static QA: 32/32 PASS. Deterministic communication contract regression: 15/15 PASS.
- Added `checklists/wu96-nurture-optout-support-qa.md`.
- WU96 remains prototype/static PASS only. First certification gate remains WU88 semantic runtime.
- Production workflow unchanged; production cutover unauthorized.

### Next Implementation Unit — WU97
Harden the complete Greenfield stack with bounded retries, structured error taxonomy, safe fallback behavior, correlation IDs, PII-redacted telemetry, security/privacy controls, and deterministic failure truth. Do not enable production writes during WU97.


## 2026-08-21 WU97 Reliability / Privacy / Security Prototype Checkpoint
- Feature: `011-e2e-sales-agent-greenfield`.
- WU97 artifact: `candidate/SPM_E2E_Sales_Agent_Greenfield_WU97_Reliability_Privacy_Security_2026-08-21.json`.
- WU97 Drive file ID: `1W6oT_XNGqL9YlUS85kKM7m424avdUYzW`.
- WU97 SHA-256: `9946d7de5cbcfd15feb1dcb91a5f97aec9c5ab9900794e855e5f20de092d93dc`.
- WU97 graph: 108 nodes; unique names/IDs; zero dangling references.
- Added input security guard before Redis/Sheets/model calls; >8,000 characters or excessive control characters are blocked before external processing.
- Added bounded model retries and bounded read retries; business-validation failures are never retried, and irreversible write retries require idempotency.
- Added explicit fail-closed lead lookup error branch (`LEAD_LOOKUP_FAILED`, `can_upsert=false`).
- Added unified reliability policy and error taxonomy plus runtime health aggregation.
- Added fail-closed privacy/security guard; unhealthy dependencies cannot authorize irreversible actions.
- Telemetry upgraded to `SPM_TELEMETRY_V2`: correlation-only observability, no raw session ID/message, email/phone scrubbing, error/warning codes only, no secret/token fields.
- Sticky opt-out remains preserved under degraded/recovery paths.
- Existing WU95 Lead UPSERT remains disabled/disconnected; no active production Sheets/HTTP/ExecuteWorkflow writes were introduced; Redis stays test namespace only.
- Static QA: 54/54 PASS. Reliability/security contract regression: 18/18 PASS.
- Added `checklists/wu97-reliability-privacy-security-qa.md`.
- WU97 remains prototype/static PASS only. First runtime certification gate remains WU88 semantic classifier runtime.
- Production workflow unchanged; production cutover unauthorized.

### Next Implementation Unit — WU98
Run multilingual/conversation regression and red-team expansion against the WU97 Greenfield candidate. Include EN/AR/FR and code-switching, ambiguity, prompt-injection attempts, malformed/oversized input, PII leakage attempts, pricing/source-gate conflicts, false booking/lead claims, sticky opt-out/support precedence, multi-student integrity, and fail-closed recovery behavior.


## 2026-08-21 WU98 Multilingual / Conversation Regression Pack
- System under test remains `candidate/SPM_E2E_Sales_Agent_Greenfield_WU97_Reliability_Privacy_Security_2026-08-21.json`; WU98 does not change the execution graph.
- Authoritative base suite `SPM_RUNTIME_TESTS` RT-001..RT-032 remains unchanged and `NOT_RUN`.
- Added RT-033..RT-096 as a 64-case expansion in `candidate/SPM_WU98_Multilingual_RedTeam_Expansion_64_2026-08-21.json` and CSV companion.
- Combined runtime target: 96 cases with 62/62 SPM V2 intent coverage.
- Expansion language mix: EN 23, AR 21, FR 17, mixed/code-switch 3.
- Added four EN/AR/FR parity triplets for pricing truth, booking truth, sticky opt-out and human handoff.
- Added missing-intent coverage, dialect ambiguity, typo/code-switching, multi-turn corrections, no-reask, multi-student separation/correction, long-session state, and prompt-injection/PII cases.
- Offline suite metadata QA: 20/20 PASS.
- Deterministic WU97 safety/static regression: 44/44 PASS.
- WU98 semantic n8n conversation runtime: NOT_RUN; no LLM semantic accuracy is certified.
- Expansion JSON SHA-256: `25c2e96703580a60c4ee4a09c5aabac11a7bb1a795350673c02dd32737501b90`.
- Expansion CSV SHA-256: `c802cad113f619dd96bcf40d610b5f0d1102a85fbe19cbfda88c9b606c051b4f`.
- Offline report SHA-256: `be276bb1e68d5181058a846143756d44f7a083f4fbb713a7707176047188e690`.
- Offline QA JSON SHA-256: `5734ee2b42e9e0f530bfc1b2847ba115c3585cef6483f06be9510f6b48ad55b9`.
- Production workflow unchanged; production cutover unauthorized.
- Next unit: WU99 full runtime/E2E certification, beginning with WU88 semantic classifier runtime.

## 2026-08-21 WU99 Runtime Certification Preparation Checkpoint
- Created testable SUT `candidate/SPM_E2E_Sales_Agent_Greenfield_WU99_Runtime_Testable_2026-08-21.json`.
- Testable SUT is semantically WU97 plus one TEST-only `Execute Workflow Trigger`; graph = 109 nodes; active=false; no top-level workflow identity reuse.
- SUT SHA-256: `a74b6443151eca02d3cc0b28126be96344a68326a389f6ac2951f54bcce0c6fc`.
- Created `candidate/SPM_WU99_Runtime_Certification_Harness_96_2026-08-21.json`; graph = 5 nodes; active=false.
- Harness Execute-SUT node is deliberately disabled and has no workflow ID until the imported SUT ID exists in n8n.
- Harness SHA-256: `965ae82f03cd8e3f7cfbf0bcd12ac859cf5618373c25590b861e02858f6f06ab`.
- Runtime plan includes 96 final test cases and 106 total invocations because selected correction/long-session cases include prerequisite turns.
- Coverage: 62/62 intents; 77 critical cases.
- Added 96-row runtime evidence ledger and 15-case failure-injection matrix.
- Preflight static QA PASS: unique names/IDs, zero dangling references, SUT test trigger present, harness target intentionally unconfigured.
- Existing Lead UPSERT remains disabled/disconnected; only test-namespace Redis state writes remain active in the SUT.
- Actual n8n runtime execution: NOT_RUN.
- WU99 certification status: BLOCKED_NOT_RUN.
- Production cutover remains unauthorized.
- WU100 remains blocked until real WU99 runtime evidence and release approval exist.
## 2026-08-21 WU100 Canary / Production Release Preparation Checkpoint
- Prepared WU100 release package without authorizing or executing production cutover.
- Canary plan: `candidate/SPM_WU100_Canary_Release_Plan_2026-08-21.md`; Drive ID `1aGzxesZROle9btwHPkq8_BqG3HjQ3gO6`; SHA-256 `bb946c71a45c372cb00fe2d10f3d79bdec87d5641e203e5f75942ac414361d1e`.
- Release manifest template: `candidate/SPM_WU100_Release_Manifest_TEMPLATE_2026-08-21.json`; Drive ID `1AjtFtWmt1uWmfeR_8q3QxQIEvS9aOdMv`; SHA-256 `f13df27b339422a8389b33c64ab285b4f6eae66beddfc9ecb58eb5ece6607b6d`.
- Rollback runbook: `checklists/SPM_WU100_Rollback_Runbook_2026-08-21.md`; Drive ID `1zI6NHEPUjOBC0nkH4GDiRbGqN3F0emyG`; SHA-256 `3d6d2e582a1ea6470433091044b8e138f15cce488a0d2ef137b279d3109c47ed`.
- Production approval checklist: Drive ID `1cfE5Q6znBrzNRp-JPJ5QdtFrJZiDwceo`; SHA-256 `78f33393ba5c8b8f5962d4d779e5dccde654f3d718b85091775f5f910fd47e76`.
- Canary monitoring gates: Drive ID `1RVQ-SJWSdjQqTNMqkOuMPzgG1VithdMT`; SHA-256 `6387801f34a4558b5363551a9be9f7a9990de58827d9ff75521f0565745e11c9`.
- Preparation QA: 12/12 PASS; Drive ID `1zYXVri42DhEQLa9ZwKXYIWeKzZPJTXlI`; SHA-256 `2711d966828f37f37eac58eb3438b7089fc8d04d2cff1409265c23172f1f8288`.
- WU99 Runtime-Testable SUT is explicitly prohibited from direct production promotion because it contains a TEST-only Execute Workflow Trigger.
- Final immutable production RC remains unset/null until WU99 runtime PASS. It must be a clean export with test trigger/harness removed and test Redis namespace removed/replaced through approved production configuration.
- Proposed canary stages: 5% → 20% → 50% → 100%; this rollout profile is PROPOSED_NOT_APPROVED.
- Hard-stop zero-tolerance invariants include P0/P1, false lead/booking/scheduling success, duplicate confirmed lead, wrong-session correction, opt-out promotional violation, PII/secret leak, test traffic causing production writes, unauthorized offers/actions, and cross-student corruption.
- Operational thresholds for overall error rate, p95 latency, cost/token budget, minimum stage volume/duration, handoff failure, and state persistence failure remain TBD; they were not invented as approved values.
- Rollback drill: NOT_RUN. Owner approval: NOT_RECORDED. Canary: NOT_RUN. Production release: BLOCKED.

