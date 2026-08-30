# Google Drive → GitHub Migration Manifest

Status: **IN PROGRESS — MIG-002 PASS — CUTOVER NOT YET APPROVED**
Audit date: 2026-08-30
Drive project root: `Success_Path_Mentors_AI_Sales_Chatbot`
Target repo: `SuccessPathMentors/SPM-Sales-AI`
Current exact-artifact branch: `migration/rc4-3-3-exact-artifact`

## Authority model after sign-off
- **GitHub**: versioned engineering source of truth for specs, roadmaps, Working Units, gates, prompts, workflow JSON, tests, decisions, release evidence, and change history.
- **n8n**: runtime/deployment environment, not an independent version-control authority.
- **Google Sheets**: live mutable knowledge/operational data where runtime mutability is required; GitHub stores governance/schema/version references, not credentials.
- **Google Drive**: archive/secondary reference after cutover approval.

Cutover is **not** yet approved. Exact transport completion does not itself authorize production deployment or make GitHub the sole authority.

## Current production runtime identity — verified
The current live production workflow is no longer unknown:

- Workflow/export name: `SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json`
- n8n workflow ID: `CMBMpxX5AqqK2UTn`
- Published/live production evidence: verified from n8n plus successful execution `2539`
- Node count: `114`
- Disabled nodes: `0`
- Native `Execute Workflow` nodes: `0`
- Exact GitHub path: `n8n/workflows/production/SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json`
- Bytes: `330119`
- SHA-256: `680496f2b68b13dd7105e72fd132a2066d70ec969e6e0675f138ebb1fb16fe39`
- Git blob SHA-1: `58d1e9cc45085909dff91d7a9d07138486e72c76`
- Exact transport: **PASS**

Runtime scope observed in the exact export:
- Lead/CRM production write adapter: present
- Scheduling/booking execution: excluded
- Human handoff execution: disabled/not configured in RC4.3.3
- Payment execution: excluded
- External follow-up execution: excluded
- Redis production state namespace: production-scoped

The standalone historical `Validated_Human_Handoff_FIXED.json` is preserved as an exact Drive artifact, but current RC4.3.3 contains no native `Execute Workflow` call to it.

## MIG-002 — exact artifact transport
**Status: PASS**

### RC4.3.3 production artifact
Transported separately and exact-byte verified as described above.

### Drive exact-transport batch
- Artifact count: `30`
- Total bytes: `3,273,938`
- Pre-transport JSON parse: PASS for all JSON files
- Stage 10 XLSX structural validation: PASS
- Preliminary secret-pattern scan: PASS with no obvious secret values detected
- Staging upload commit: `5531c377208bd7d1cc5572533fa5760713bcefa0`
- Exact final placement commit: `86ec918bb75e919df67d167ae3e3e67c040c633c`
- Local-original Git blob SHA vs GitHub blob: `30/30 MATCH`
- Mismatches: `0`
- Temporary `migration-incoming/`: removed after verification
- Detailed manifest: `docs/MIG-002_EXACT_TRANSPORT_MANIFEST_2026-08-30.csv`
- Integrity control: `docs/ARTIFACT_INTEGRITY_REGISTER.yaml`

The batch completed exact transport for the previously pending:
- `PROJECT_STATE.md` historical snapshot
- `CHANGELOG.md`
- `AI_Agent_System_Message_fixed.md`
- Stage 10 XLSX QA template
- five identified `03_Workflows_Current` exports
- retained WU87–WU99 Greenfield candidate/test artifacts
- WU98 multilingual red-team JSON/CSV
- WU99 runtime SUT, harness, and certification plan

The WU99 Runtime-Testable SUT and harness remain **TEST ONLY** and are not production promotion candidates.

## Mirrored authoritative engineering layers
### Governance / context
- `drive-mirror/AGENTS_DRIVE_2026-08-18.md`
- `drive-mirror/00_START_HERE/`
- `drive-mirror/01_Governance_Plans/`
- `drive-mirror/02_Current_Architecture/`
- governance/reference material under `drive-mirror/04_AI_Knowledge_Sources/`

### Workflows / QA / decisions / reports
- exact historical/current Drive workflow exports under `drive-mirror/03_Workflows_Current/`
- QA/release gate and Stage 10 template under `drive-mirror/05_Testing_QA/`
- decision/history logs and exact `CHANGELOG.md` under `drive-mirror/06_History_Decisions/`
- active reports/policies under `drive-mirror/07_Reports_Risks_Gaps/`
- cold-storage policy under `drive-mirror/08_Archive/README.md`

### Spec Kit / SDD
Mirrored engineering governance includes:
- constitution
- quality checklists and release-convergence gates
- 000 master spec/plan/tasks
- 001 R2 error-handling spec/clarify/plan/tasks/runtime gate/analysis
- 011 Greenfield spec/plan/work-units/tasks/contracts
- WU87–WU98 QA/evidence
- WU99/WU100 runbooks/checklists/evidence templates
- retained WU87–WU99 candidate/test artifacts exact-mirrored under `candidate/`

Historical duplicate/revision files do not overwrite canonical material. Duplicate exact bytes may be deduplicated by content while provenance is retained.

## Reconciled release interpretation
Historical RC3/WU100 documents remain audit evidence and must not be rewritten to pretend later events occurred inside those old files.

Current runtime evidence supersedes stale statements that the active main workflow is unknown or that RC3 is necessarily the present runtime. The current live runtime is verified RC4.3.3.

Known later WU99 execution evidence still records:
- 96/96 automated runtime PASS
- 106/106 invocations complete
- 15/15 failure injection PASS
- protected R1 regression 10/10 PASS
- manual semantic review complete
- EN/AR/FR parity accepted
- zero P0/P1 reported in the later certification layer

Historical `NOT_RUN` ledgers/templates remain verbatim as historical evidence; they are not rewritten to fabricate individual execution records.

### RC4.2 historical reference
`SPM_E2E_Sales_Agent_RC4_2_FINAL_FROZEN_2026-08-26.json` remains an `UNVERIFIED_HISTORICAL_REFERENCE` because exact Drive-name/hash searches did not locate the underlying artifact. It must not override the independently verified RC4.3.3 current runtime/export identity.

## External runtime decision
Live Google Sheets knowledge/workbook data remains external mutable runtime truth. GitHub contains governance/schema/reference material. Scheduled snapshots are optional policy work, not a prerequisite to pretend live data is static code.

## Archive rule
`08_Archive` remains `ARCHIVE_SECONDARY`. Historical transcripts/older exports do not override `docs/STATE.yaml`, approved specs, locked decisions, or verified current runtime evidence. A separate cold-archive export is required only if Drive itself will later be retired/deleted.

## Numbering rule
Authoritative Phase 2 Working Units remain:
- WU-101 Conversation Analytics
- WU-102 Unanswered Question Queue
- WU-103 Knowledge Maintenance Loop
- WU-104 Short Query & Ambiguity UX
- WU-105 Golden Intents Optimization
- WU-106 Dialect & Language Coverage
- WU-107 Human Handoff Adapter
- WU-108 WhatsApp Staff Notification
- WU-109 Conversation Outcome KPIs
- WU-110 Optimization Regression Pack

Migration/bootstrap work uses `MIG-*` identifiers and must not consume WU-101.

## Remaining migration gates
MIG-002 transport is no longer a blocker. Before GitHub source-of-truth cutover:
1. finish/close `MIG-001` by reconciling the current RC4.3.3 runtime/dependency inventory in durable GitHub state;
2. reconcile stale current-state/release fields in `docs/STATE.yaml` against verified RC4.3.3 evidence;
3. prepare and validate a **non-production-only** GitHub → n8n path under `MIG-003`;
4. review the migration PR/branches and integrate without losing exact artifact history;
5. confirm no unresolved state/numbering conflict remains;
6. owner explicitly approves GitHub engineering source-of-truth cutover.

Production auto-deploy remains disabled. No AI-driven production activation is authorized by this migration manifest.
