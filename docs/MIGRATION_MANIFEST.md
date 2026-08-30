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

## Mirrored now
### Governance / architecture / knowledge
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

### QA / decisions / risk
- `drive-mirror/05_Testing_QA/QA_TESTING_RELEASE_GATE.md`
- `drive-mirror/05_Testing_QA/R1_LOCK_RECORD_2026-08-17.md`
- `drive-mirror/06_History_Decisions/DECISION_LOG.md`
- `drive-mirror/06_History_Decisions/HISTORY_LOG.md`
- `drive-mirror/07_Reports_Risks_Gaps/RISKS_GAPS_ACTIONS.md`
- `drive-mirror/07_Reports_Risks_Gaps/DATABASE_MIGRATION_ROADMAP.md`

### 011 Greenfield Spec Kit
- `spec.md`
- `plan.md`
- `work-units.md`
- `tasks.md`
- `contracts.md`
- `checklists/greenfield-release-gate.md`
- `checklists/SPM_WU99_Runtime_Certification_Runbook_2026-08-21.md`
- `checklists/SPM_WU100_Production_Approval_Checklist_2026-08-21.md`
- `checklists/SPM_WU100_Rollback_Runbook_2026-08-21.md`
- `candidate/SPM_WU100_Canary_Release_Plan_2026-08-21.md`
- `candidate/SPM_WU100_RC3_Final_Targeted_Regression_Plan_2026-08-25.md`

## GitHub-native control files
- `AGENTS.md`
- `docs/STATE.yaml`
- `docs/ROADMAP.md`
- `docs/N8N_DEPLOYMENT_POLICY.md`
- `docs/DRIVE_ARTIFACT_INVENTORY.md`
- `work-units/TEMPLATE.md`
- `change-requests/TEMPLATE.md`

## Reconciled current release interpretation
Newer Drive release evidence supersedes older PREPARED/NOT_RUN wording where statuses conflict.

Current supported facts:
- WU99: 96/96 runtime cases PASS; 106/106 invocations complete; 15/15 failure injection PASS; R1 protected outcomes 10/10 PASS; manual semantic review complete; EN/AR/FR parity accepted; zero P0/P1 and zero false-success regressions recorded in certification evidence.
- RC3: lead/CRM adapter certification 6/6 PASS; clean RC3 generated; production static QA PASS; production Redis namespace `spm:prod:sales:*`; scheduling/booking, human-handoff live execution, payment, and external follow-up are explicitly excluded from RC3 scope.
- Rollback drill: PASS, n8n execution ID 2276; rollback baseline SHA-256 `8450550bf2e33ee161a034deea4be0f0d6667959716e891166d0da6bb149dbd2`.
- Canary operational thresholds were owner-approved on 2026-08-25.
- Production cutover remains NO-GO because final targeted RC3 regression, final RC3 freeze/hash, and explicit owner approval to activate 5% canary are not yet evidenced as complete in the migrated source.

Historical conflict rule: old documents such as the WU99 runbook and original rollback runbook are mirrored verbatim for audit history, but their old status statements do not override later dated release evidence.

## Still required before source-of-truth cutover
1. Exact `00_START_HERE/PROJECT_STATE.md` mirror, clearly tagged as a dated snapshot and reconciled against later release artifacts.
2. Remaining governance/current-prompt documents.
3. `06_History_Decisions/CHANGELOG.md` exact mirror.
4. Remaining risk/audit reports.
5. Remaining Spec Kit roots: `.specify`, `quality`, `000-master-system`, `001-r2-error-handling`, plus 011 `wu88-analysis` and remaining checklists.
6. Exact workflow JSON transport for locked/current R1/R2/R2.5 and WU87–WU100 artifacts.
7. WU99 evidence ledger, failure-injection matrix, regression packs and supporting JSON/CSV evidence.
8. QA workbook or a text/CSV equivalent that preserves evidence without losing information.
9. `08_Archive` inventory/cold-storage policy.
10. Verify exact release workflow export identity and hash for RC3 and any later frozen RC. The referenced `SPM_E2E_Sales_Agent_RC4_2_FINAL_FROZEN_2026-08-26.json` was not found by exact Drive-name searches during this audit and remains `UNVERIFIED_REFERENCE`.
11. MIG-001: confirm current n8n runtime workflow IDs and active/inactive states; define a repeatable non-production deployment/import path.
12. Decide whether Google Sheets remains live external runtime truth only or also receives scheduled versioned snapshots in GitHub.

## Large-artifact transport rule
Workflow JSONs and binary evidence must not be reconstructed from screenshots, chat excerpts, or truncated connector output. They must be transferred exactly from provider exports and reconciled by checksum/version identity. The available GitHub connector currently exposes text-file content writes but no generic binary/local-file upload action; therefore large exact artifacts remain `PENDING_TRANSPORT` rather than being partially recreated.

## Numbering rule
The authoritative Drive `work-units.md` defines WU-101 through WU-110. GitHub/n8n migration/bootstrap work is `MIG-001` and must not consume WU-101.

## Cutover gate
Do not mark migration COMPLETE or switch engineering authority fully to GitHub until every active authoritative Drive artifact has a GitHub counterpart or documented external-runtime exception, hashes/identities are reconciled, current project/release state is reconciled, PR review passes, and owner explicitly approves the GitHub source-of-truth cutover.
