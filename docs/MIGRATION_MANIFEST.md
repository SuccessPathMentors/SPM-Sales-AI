# Google Drive → GitHub Migration Manifest

Status: **IN PROGRESS — CUTOVER NOT YET APPROVED**
Audit date: 2026-08-30
Drive project root: `Success_Path_Mentors_AI_Sales_Chatbot`
Target repo: `SuccessPathMentors/SPM-Sales-AI`
Migration branch: `setup/agent-orchestration-v1`

## Authority model after sign-off
- GitHub: versioned engineering source of truth for specs, roadmaps, work units, gates, prompts, workflow JSON, tests, decisions, release evidence, and change history.
- n8n: runtime/deployment environment; not the version-control source of truth.
- Google Sheets: live operational/knowledge data where runtime mutability is required; GitHub stores governance/schema/version references and optionally approved snapshots, never credentials.
- Google Drive: archive/secondary reference after migration sign-off.

## Folder audit
See `docs/DRIVE_FOLDER_AUDIT.md` for the folder-by-folder migration matrix and exact Drive IDs.

## Mirrored authoritative text layers
### Governance / context
- `drive-mirror/AGENTS_DRIVE_2026-08-18.md`
- `drive-mirror/00_START_HERE/00_START_HERE.md`
- `drive-mirror/00_START_HERE/FILE_INDEX.md`
- all files in `drive-mirror/01_Governance_Plans/`
- `drive-mirror/02_Current_Architecture/SYSTEM_ARCHITECTURE.md`
- all governance/reference files in `drive-mirror/04_AI_Knowledge_Sources/`

### QA / decisions / reports
- `drive-mirror/05_Testing_QA/QA_TESTING_RELEASE_GATE.md`
- `drive-mirror/05_Testing_QA/R1_LOCK_RECORD_2026-08-17.md`
- `drive-mirror/06_History_Decisions/DECISION_LOG.md`
- `drive-mirror/06_History_Decisions/HISTORY_LOG.md`
- all six active reports/policies in `drive-mirror/07_Reports_Risks_Gaps/`
- `drive-mirror/08_Archive/README.md` cold-storage policy

### Master Spec Kit / engineering governance
- `drive-mirror/09_Spec_Kit_SDD/.specify/memory/constitution.md`
- `drive-mirror/09_Spec_Kit_SDD/GITHUB_LINKING.md`
- `drive-mirror/09_Spec_Kit_SDD/quality/requirements-checklist.md`
- `drive-mirror/09_Spec_Kit_SDD/quality/requirements-checklist-expanded-draft.md`
- `drive-mirror/09_Spec_Kit_SDD/quality/release-convergence-gates.md`
- `drive-mirror/09_Spec_Kit_SDD/specs/000-master-system/spec.md`
- `drive-mirror/09_Spec_Kit_SDD/specs/000-master-system/plan.md`
- `drive-mirror/09_Spec_Kit_SDD/specs/000-master-system/tasks.md`

### Feature 001 — R2 Error Handling
Mirrored:
- `spec.md`
- `clarify.md`
- `plan.md`
- `tasks.md`
- `runtime-test-gate.md`
- `analysis.md`
- `runtime-export-analysis-2026-08-20.md`
- `requirements-checklist.md`

### Feature 011 — Greenfield E2E Sales Agent
Core mirrored:
- `spec.md`
- `plan.md`
- `work-units.md`
- `tasks.md`
- `contracts.md`
- `wu88-analysis.md`
- `checklists/greenfield-release-gate.md`

Core WU87–WU98 QA/evidence mirrored:
- `checklists/wu87-static-qa.md`
- `checklists/wu88-classifier-qa.md`
- `checklists/wu89-entity-normalization-static-qa.md`
- `checklists/wu90-state-journey-static-qa.md`
- `checklists/wu91-knowledge-source-gates-qa.md`
- `checklists/wu92-sales-agent-core-qa.md`
- `checklists/wu93-commercial-objections-qa.md`
- `checklists/wu94-trial-scheduling-truth-layer-qa.md`
- `checklists/wu95-deterministic-lead-conversion-qa.md`
- `checklists/wu96-nurture-optout-support-qa.md`
- `checklists/wu97-reliability-privacy-security-qa.md`
- `checklists/SPM_WU98_Offline_Regression_Report_2026-08-21.md`
- `checklists/SPM_WU98_Offline_QA_2026-08-21.json`

WU99/WU100 release/evidence layer mirrored:
- `checklists/SPM_WU99_Runtime_Certification_Runbook_2026-08-21.md`
- `checklists/SPM_WU99_Preflight_QA_2026-08-21.json`
- `checklists/SPM_WU99_Runtime_Evidence_Ledger_96_2026-08-21.csv` — historical unexecuted template, preserved verbatim
- `checklists/SPM_WU99_Failure_Injection_Matrix_2026-08-21.csv` — historical unexecuted template, preserved verbatim
- `checklists/SPM_WU100_Production_Approval_Checklist_2026-08-21.md`
- `checklists/SPM_WU100_Rollback_Runbook_2026-08-21.md`
- `candidate/SPM_WU100_Canary_Release_Plan_2026-08-21.md`
- `candidate/SPM_WU100_RC3_Final_Targeted_Regression_Plan_2026-08-25.md`
- `candidate/SPM_WU100_Canary_Monitoring_Gates_2026-08-21.csv`
- `candidate/SPM_WU100_Preparation_QA_2026-08-21.json`
- `candidate/SPM_WU100_Release_Manifest_TEMPLATE_2026-08-21.json`

Historical duplicate/revision QA files discovered in Drive are preserved under `checklists/history/` with Drive-ID suffixes instead of overwriting canonical files.

## GitHub-native control files
- `AGENTS.md`
- `docs/STATE.yaml`
- `docs/ROADMAP.md`
- `docs/N8N_DEPLOYMENT_POLICY.md`
- `docs/MIGRATION_MANIFEST.md`
- `docs/DRIVE_ARTIFACT_INVENTORY.md`
- `docs/DRIVE_FOLDER_AUDIT.md`
- `work-units/TEMPLATE.md`
- `change-requests/TEMPLATE.md`

## Reconciled current release interpretation
Newer dated Drive release evidence supersedes older PREPARED/NOT_RUN wording where statuses conflict. Historical files remain verbatim for audit, but do not override later evidence.

Current supported facts:
- WU99 runtime execution is recorded as complete at the later task/release layer: 96/96 runtime cases PASS; 106/106 invocations complete; 15/15 failure injection PASS; R1 protected outcomes 10/10 PASS; manual semantic review complete; EN/AR/FR parity accepted; zero P0/P1 and zero false-success regressions recorded in the later certification evidence.
- The original WU99 evidence ledger and failure-injection matrix found in Drive are pre-execution templates (`NOT_RUN`). No separate completed ledger file was located during this audit. Therefore the later task/release documents are the current evidence for aggregate completion, while exact per-execution identifiers remain a reconciliation item.
- RC3: lead/CRM adapter certification 6/6 PASS; clean RC3 generated; production static QA PASS; production Redis namespace `spm:prod:sales:*`; scheduling/booking, human-handoff live execution, payment, and external follow-up explicitly excluded from RC3 scope.
- Rollback drill: PASS, n8n execution ID 2276; rollback baseline SHA-256 `8450550bf2e33ee161a034deea4be0f0d6667959716e891166d0da6bb149dbd2`.
- Canary operational thresholds were owner-approved on 2026-08-25.
- Production cutover remains NO-GO because final targeted RC3 regression, final RC3 freeze/hash, and explicit owner approval to activate 5% canary are not yet evidenced as complete in the migrated source.

## Remaining migration classes
### PENDING_EXACT_TEXT_TRANSPORT
These files can be downloaded exactly from Drive, but the current GitHub connector accepts text content rather than a local file reference. Do not create truncated substitutes:
- `00_START_HERE/PROJECT_STATE.md` — Drive ID `1R7nQEZstCUdHtx3LmH01_O2oHNMpqtZR`, 42,464 bytes. Current operational state is already reconciled separately in `docs/STATE.yaml`; when mirrored, this Drive file must be labeled a dated historical snapshot.
- `06_History_Decisions/CHANGELOG.md` — Drive ID `1frxBHSbh2sk6qniuDyKXfh9o0Qpb5vBz`, 22,376 bytes.
- `02_Current_Architecture/AI_Agent_System_Message_fixed.md` — Drive ID `1K_r-0A-HTnya8dUyYiz6sQqi_QpP0hIz`, approximately 21 KB.

### PENDING_TRANSPORT — exact versioned runtime artifacts
- `03_Workflows_Current` R1/R2/refactor/handoff workflow JSONs.
- WU87–WU99 large Greenfield candidate workflow JSONs.
- WU99 runtime harness/test-plan JSONs where exact raw transfer is still required.
- WU98 red-team expansion JSON/CSV where not yet exact-mirrored.
- Stage 10 XLSX QA template/evidence unless approved as an external/binary evidence exception.

All workflow/binary artifacts must be transferred from provider exports and verified by checksum/version identity. Do not reconstruct from chat snippets or truncated connector output.

### PENDING_RUNTIME_IDENTITY — MIG-001
- Confirm current n8n workflow inventory: exact names, workflow IDs, and active/inactive state.
- Map GitHub artifacts to runtime workflows.
- Define and test one repeatable non-production GitHub → n8n staging/import path.
- Production auto-deploy remains disabled.

### PENDING_RELEASE_IDENTITY
- Verify exact RC3/final release workflow export and SHA before source-of-truth cutover.
- `SPM_E2E_Sales_Agent_RC4_2_FINAL_FROZEN_2026-08-26.json` was not found by exact Drive-name searches and remains `UNVERIFIED_REFERENCE` until the actual artifact is located.

### EXTERNAL_RUNTIME DECISION
The live Google Sheets knowledge/workbook data currently remains external mutable runtime truth. GitHub already contains its governance and schema/reference documents. Scheduled versioned snapshots are optional and require an explicit policy decision; they are not required to pretend the live sheet is static code.

## Archive rule
`08_Archive` is `ARCHIVE_SECONDARY`, not active engineering authority. Its pasted transcripts and older workflow exports remain in Drive cold storage and must never override `docs/STATE.yaml`, approved specs, locked decisions, or later release evidence. A separate cold-archive export is required only if Drive itself will later be retired/deleted.

## Numbering rule
The authoritative Drive `work-units.md` defines WU-101 through WU-110. GitHub/n8n migration/bootstrap work is `MIG-001` and must not consume WU-101.

## Cutover gate
Do **not** mark migration COMPLETE or switch engineering authority fully to GitHub until:
1. all active authoritative text artifacts are mirrored exactly or explicitly approved as historical/external exceptions;
2. required runtime/workflow artifacts are transferred exactly and identity/hash reconciled;
3. n8n runtime workflow IDs/state and staging deployment path are confirmed under MIG-001;
4. current release candidate identity/hash is verified;
5. no WU numbering/state conflict remains;
6. PR review passes;
7. owner explicitly approves GitHub source-of-truth cutover.
