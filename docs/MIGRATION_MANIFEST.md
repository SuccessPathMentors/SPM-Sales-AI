# Google Drive → GitHub Migration Manifest

Status: IN PROGRESS — GitHub is not yet declared the sole source of truth.
Audit date: 2026-08-30
Drive project root: `Success_Path_Mentors_AI_Sales_Chatbot`
Target repo: `SuccessPathMentors/SPM-Sales-AI`
Migration branch: `setup/agent-orchestration-v1`

## Authority model after sign-off
- GitHub: versioned engineering source of truth for specs, roadmaps, work units, gates, prompts, workflow JSON, tests, decisions, release evidence, and change history.
- n8n: runtime/deployment environment; not the version-control source of truth.
- Google Sheets: live operational/knowledge data where runtime mutability is required; GitHub stores governance/schema/version references, not credentials.
- Google Drive: archive/secondary reference after migration sign-off.

## Migrated / mirrored now
- `drive-mirror/AGENTS_DRIVE_2026-08-18.md`
- `drive-mirror/00_START_HERE/00_START_HERE.md`
- `drive-mirror/00_START_HERE/FILE_INDEX.md`
- `drive-mirror/01_Governance_Plans/PROJECT_CHARTER_SCOPE.md`
- `drive-mirror/01_Governance_Plans/CURRENT_STATUS_PROGRESS.md`
- `drive-mirror/01_Governance_Plans/RELEASE_PHASES_AND_GATES.md`
- `drive-mirror/01_Governance_Plans/TOKEN_COST_OPTIMIZATION.md`
- `drive-mirror/01_Governance_Plans/TASK_TEMPLATE.md`
- `drive-mirror/02_Current_Architecture/SYSTEM_ARCHITECTURE.md`
- `drive-mirror/04_AI_Knowledge_Sources/AI_KNOWLEDGE_GOVERNANCE.md`
- `drive-mirror/04_AI_Knowledge_Sources/LIVE_AI_KNOWLEDGE_SOURCE.md`
- `drive-mirror/09_Spec_Kit_SDD/specs/011-e2e-sales-agent-greenfield/work-units.md` including authoritative WU-101 → WU-110 Phase 2 backlog.

## New GitHub-native governance
- `AGENTS.md`
- `docs/STATE.yaml`
- `docs/ROADMAP.md`
- `docs/N8N_DEPLOYMENT_POLICY.md`
- `work-units/TEMPLATE.md`
- `change-requests/TEMPLATE.md`

## Authoritative items still requiring exact mirror/verification before source-of-truth cutover
1. Latest `00_START_HERE/PROJECT_STATE.md` exact copy and reconciliation with later WU100/pre-canary evidence.
2. Remaining `01_Governance_Plans` and current architecture prompt file.
3. `05_Testing_QA` gates, lock evidence, and QA workbook.
4. `06_History_Decisions` CHANGELOG, DECISION_LOG, HISTORY_LOG.
5. `07_Reports_Risks_Gaps` reports and roadmaps.
6. Full `09_Spec_Kit_SDD`: `.specify`, quality, 000-master-system, 001-r2-error-handling, 011 greenfield spec/plan/tasks/contracts/checklists/candidates.
7. Current/locked n8n workflow JSON artifacts, including R1/R2/R2.5 and Greenfield WU87–WU100 candidates/harnesses.
8. Binary QA/test artifacts (XLSX/CSV where not already text-addressable in GitHub).
9. `08_Archive`: inventory and cold-storage policy; archive must not override current locked decisions.
10. Locate and verify the latest frozen RC referenced by later project evidence (`SPM_E2E_Sales_Agent_RC4_2_FINAL_FROZEN_2026-08-26.json`) before release-source cutover.
11. Confirm whether live Google Sheets knowledge data should remain external runtime truth or receive scheduled versioned snapshots in GitHub.

## Critical numbering correction
The Drive `work-units.md` defines WU-101 as Conversation Analytics through WU-110 as Optimization Regression Pack. Therefore the GitHub/n8n bootstrap issue is `MIG-001`, not WU-101.

## Cutover gate
Do not mark migration COMPLETE or switch engineering authority fully to GitHub until:
- every active authoritative Drive file has a GitHub counterpart or an explicitly documented external-runtime exception;
- checksums/version identity are recorded for workflow/release artifacts;
- latest project state is reconciled;
- no WU ID conflicts remain;
- PR review passes;
- owner approves GitHub source-of-truth cutover.
