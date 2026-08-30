# Google Drive → GitHub Migration Manifest

Status: **IN PROGRESS — MIG-001/002/003 PASS — MIG-004 RECONCILED — CUTOVER NOT YET APPROVED**
Audit date: 2026-08-30
Drive project root: `Success_Path_Mentors_AI_Sales_Chatbot`
Target repo: `SuccessPathMentors/SPM-Sales-AI`
Current exact-artifact branch: `migration/rc4-3-3-exact-artifact`

## Authority model after sign-off
- **GitHub**: versioned engineering source of truth for specs, roadmaps, Working Units, gates, prompts, workflow JSON, tests, decisions, release evidence, and change history.
- **n8n**: runtime/deployment environment, not an independent version-control authority.
- **Google Sheets**: live mutable knowledge/operational data where runtime mutability is required; GitHub stores governance/schema/version references, not credentials.
- **Google Drive**: archive/secondary reference after cutover approval.

Cutover is **not** yet approved. Exact transport completion and non-production deployment automation do not themselves authorize production deployment or make GitHub the sole approved authority.

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

## MIG-001 — runtime identity reconciliation
**Status: PASS / CLOSED**

Durable current runtime state is recorded in `docs/STATE.yaml` and `docs/MIG-001_N8N_RUNTIME_INVENTORY.md`. RC4.3.3 is the verified current production workflow. Current adapter inclusion/exclusion is recorded explicitly and historical standalone workflows do not become current dependencies without revalidation.

## MIG-002 — exact artifact transport
**Status: PASS / CLOSED**

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

## MIG-003 — GitHub → n8n non-production path
**Status: PASS / CLOSED**

Implementation PR #9 was reviewed and merged to the migration branch with merge commit `7b10a4490e2668d254bef56355e7f96b4a05171f`.

Verified gates:
- read-only n8n API smoke PASS;
- exact RC4.3.3 dry-run PASS with zero writes;
- protected production workflow ID hard-denied;
- side-effect-free `[STAGING] MIG003_STAGING_CANARY` created inactive with ID `BIDVhNCRbj9dvH1t`;
- missing-target update attempt failed closed as designed;
- deterministic update of the same configured STAGING target passed;
- API key excludes activation/deactivation/delete permissions;
- no publish/activate path exists in the deployer.

Production auto-deploy remains disabled. MIG-003 proves only a controlled DEV/STAGING path.

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

## MIG-004 — historical release evidence precedence
**Status: RECONCILED**

Control document: `docs/MIG-004_RELEASE_EVIDENCE_PRECEDENCE.md`.

Historical RC3/WU99/WU100 documents remain audit evidence and must not be rewritten to pretend later events occurred inside those old files.

Precedence rule:
1. verified current runtime identity/exact runtime export answers what is live now;
2. later dated verified release/certification evidence supersedes older preparation-state claims for current-state use;
3. older `NOT_RUN`, preparation-only, or unknown-runtime files remain immutable historical snapshots;
4. when chronology is unsupported, state must remain `RECONCILIATION_REQUIRED` rather than inferred.

`drive-mirror/00_START_HERE/PROJECT_STATE.md` is explicitly classified in `docs/ARTIFACT_INTEGRITY_REGISTER.yaml` as `HISTORICAL_SNAPSHOT_ONLY`; current-state authority is `docs/STATE.yaml`.

Known later WU99 execution evidence records:
- 96/96 automated runtime PASS
- 106/106 invocations complete
- 15/15 failure injection PASS
- protected R1 regression 10/10 PASS
- manual semantic review complete
- EN/AR/FR parity accepted
- zero P0/P1 reported in the later certification layer

`SPM_WU100_Production_Approval_Checklist_2026-08-21.md`, updated 2026-08-25, records later WU99 results, Lead/CRM adapter certification, clean RC3/static QA, rollback drill execution `2276`, and approved canary operational thresholds. Its still-unchecked release/canary items remain historical facts at that checkpoint and are not silently filled in.

Historical `NOT_RUN` ledgers/templates/runbooks remain verbatim as historical evidence; they are not rewritten to fabricate individual execution records.

### RC4.2 historical reference
`SPM_E2E_Sales_Agent_RC4_2_FINAL_FROZEN_2026-08-26.json` remains an `UNVERIFIED_HISTORICAL_REFERENCE` because exact Drive-name/hash searches did not locate the underlying artifact. It must not override the independently verified RC4.3.3 current runtime/export identity.

### Non-inference rule
The fact that RC4.3.3 is live does not prove undocumented 5%/20%/50%/100% canary-stage execution history. Missing intermediate release evidence remains missing.

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

## Remaining migration / cutover gates
MIG-001, MIG-002, and MIG-003 are PASS/CLOSED. MIG-004 evidence precedence is reconciled. Before GitHub becomes the sole approved engineering source of truth:
1. close MIG-004 after final acceptance check;
2. review and integrate the remaining migration PR/branch chain without losing exact artifact history;
3. confirm no unresolved source-authority, release-state, or WU-numbering conflict remains;
4. confirm production auto-deploy remains disabled and the STAGING path remains the only automated n8n write path;
5. owner explicitly approves GitHub engineering source-of-truth cutover.

Production auto-deploy remains disabled. No AI-driven production activation is authorized by this migration manifest.
