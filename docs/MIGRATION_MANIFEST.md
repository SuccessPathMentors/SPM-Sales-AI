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
### Governance and context
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

### QA / lock evidence
- `drive-mirror/05_Testing_QA/QA_TESTING_RELEASE_GATE.md`
- `drive-mirror/05_Testing_QA/R1_LOCK_RECORD_2026-08-17.md`

### Decisions / history
- `drive-mirror/06_History_Decisions/DECISION_LOG.md`
- `drive-mirror/06_History_Decisions/HISTORY_LOG.md`

### Risks / future architecture
- `drive-mirror/07_Reports_Risks_Gaps/RISKS_GAPS_ACTIONS.md`
- `drive-mirror/07_Reports_Risks_Gaps/DATABASE_MIGRATION_ROADMAP.md`

### Greenfield Spec Kit
- `drive-mirror/09_Spec_Kit_SDD/specs/011-e2e-sales-agent-greenfield/work-units.md`
- `drive-mirror/09_Spec_Kit_SDD/specs/011-e2e-sales-agent-greenfield/tasks.md`
- The mirrored Work Units preserve the authoritative WU-101 → WU-110 Phase 2 backlog.

## New GitHub-native governance
- `AGENTS.md`
- `docs/STATE.yaml`
- `docs/ROADMAP.md`
- `docs/N8N_DEPLOYMENT_POLICY.md`
- `work-units/TEMPLATE.md`
- `change-requests/TEMPLATE.md`

## Reconciliation discovery — 2026-08-30
The newer Drive `011/.../tasks.md` is more recent than the older `PROJECT_STATE.md` snapshot and changes the runtime-certification interpretation:
- WU99 runtime execution is recorded as COMPLETE at the task-map level.
- Automated runtime: 96/96 PASS.
- Failure injection: 15/15 PASS, with FI-003/FI-007/FI-008 behavioral method deviations documented.
- Final protected R1 regression rerun: 10/10 PASS.
- Manual semantic remediation: closed.
- Final WU99 certification is still not fully releasable because evidence ledger/execution identifiers and any required owner acceptance of method deviations remain unresolved.
- WU100 package preparation is complete but canary/production execution remains blocked and unauthorized.

`docs/STATE.yaml` was corrected to reflect this newer evidence and to mark the repository authority as `MIGRATION_IN_PROGRESS`, not prematurely as final GitHub source of truth.

## Authoritative items still requiring exact mirror/verification before source-of-truth cutover
1. Latest `00_START_HERE/PROJECT_STATE.md` exact copy, retained as historical/current snapshot but reconciled against newer 2026-08-26 task/release evidence.
2. Remaining `01_Governance_Plans` document(s) and current architecture prompt file.
3. `05_Testing_QA` binary QA workbook or a GitHub-native text/CSV evidence representation.
4. `06_History_Decisions/CHANGELOG.md` exact mirror.
5. Remaining `07_Reports_Risks_Gaps`: workflow fix report, knowledge-gap audit, comprehensive audit, external automation reuse policy.
6. Full `09_Spec_Kit_SDD`: `.specify`, quality, 000-master-system, 001-r2-error-handling, and remaining 011 greenfield spec/plan/contracts/wu88-analysis/checklists/candidates.
7. Current/locked n8n workflow JSON artifacts, including R1/R2/R2.5 and Greenfield WU87–WU100 candidates/harnesses.
8. Runtime evidence ledgers, failure-injection matrices, regression packs and related CSV/JSON evidence needed to substantiate WU99/WU100 gates.
9. `08_Archive`: inventory and cold-storage policy; archive must not override current locked decisions.
10. Locate and verify the latest frozen RC referenced by later project evidence (`SPM_E2E_Sales_Agent_RC4_2_FINAL_FROZEN_2026-08-26.json`) before release-source cutover. Do not treat its identity/SHA as authoritative until verified against Drive/runtime evidence.
11. Confirm current n8n runtime workflow IDs and active/inactive state under MIG-001.
12. Confirm whether live Google Sheets knowledge data remains external runtime truth only or receives scheduled versioned snapshots in GitHub.

## Large-artifact transport rule
Workflow JSONs and binary evidence are migration-critical, but must not be reconstructed from chat snippets. They must be transferred exactly from the provider export and verified by hash/version identity. If a connector path cannot safely transfer a large artifact in one operation, record it as PENDING_TRANSPORT rather than creating a partial file.

## Critical numbering correction
The Drive `work-units.md` defines WU-101 as Conversation Analytics through WU-110 as Optimization Regression Pack. Therefore the GitHub/n8n bootstrap issue is `MIG-001`, not WU-101.

## Cutover gate
Do not mark migration COMPLETE or switch engineering authority fully to GitHub until:
- every active authoritative Drive file has a GitHub counterpart or an explicitly documented external-runtime exception;
- checksums/version identity are recorded for workflow/release artifacts;
- latest project state is reconciled;
- no WU ID conflicts remain;
- WU99 evidence status is reconciled from primary artifacts rather than inferred from old state files;
- PR review passes;
- owner approves GitHub source-of-truth cutover.
