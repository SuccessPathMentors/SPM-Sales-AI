# Google Drive Folder-Level Migration Audit

Audit date: 2026-08-30
Drive root: `Success_Path_Mentors_AI_Sales_Chatbot`
Drive root ID: `1V7siTY6XYtE0RJXANlXnQmiJDS0vuUkf`
Target: `SuccessPathMentors/SPM-Sales-AI`

Status legend:
- `MIRRORED`: active text authority represented in GitHub.
- `PARTIAL`: active items remain.
- `EXTERNAL_RUNTIME`: intentionally remains outside GitHub as mutable runtime data.
- `PENDING_EXACT_TEXT_TRANSPORT`: file is readable/downloadable from Drive but the current GitHub connector has no direct local-file upload path; do not create a truncated substitute.
- `PENDING_TRANSPORT`: JSON/binary artifact requires exact provider transfer and identity/hash verification.
- `ARCHIVE_SECONDARY`: historical cold storage; not required to become hot engineering truth before cutover.

| Folder | Drive ID | Status | GitHub treatment / remaining work |
|---|---|---|---|
| `00_START_HERE` | `1cMOB0Yr0KeE_0bPhS362DkV6OnkzQldq` | PARTIAL | Start-here and file index mirrored. `PROJECT_STATE.md` (42,464 bytes, modified 2026-08-25) is `PENDING_EXACT_TEXT_TRANSPORT`; current reconciled state is `docs/STATE.yaml`. |
| `01_Governance_Plans` | `1TXqn7O5R35JAnncyP_gVDHEkZcEv8CeH` | MIRRORED | Project charter, current status, release phases/gates, token/context optimization, and task template mirrored. |
| `02_Current_Architecture` | `1Vz1zjzVvrqku24DIelHxi3c5hWmXrqZb` | PARTIAL | `SYSTEM_ARCHITECTURE.md` mirrored. `AI_Agent_System_Message_fixed.md` (~21 KB) remains `PENDING_EXACT_TEXT_TRANSPORT`. |
| `03_Workflows_Current` | `1CN2-wUUxPWle2aLVvkoD3cE2OXcCsmyZ` | PENDING_TRANSPORT | Locked/current R1/R2/refactor/handoff workflow JSON exports require exact transfer; no partial reconstruction allowed. |
| `04_AI_Knowledge_Sources` | `1wfeUvXa9wuTUVQqMZL9dWNNRgHS75iib` | MIRRORED + EXTERNAL_RUNTIME | Governance/reference docs mirrored. Live Google Sheets knowledge data remains an external mutable runtime source unless snapshot policy is separately approved. |
| `05_Testing_QA` | `1LyZI0Z685X65z4nsSoH76x8A2G9j7mz6` | PARTIAL | QA release gate and R1 lock record mirrored. Stage 10 XLSX template remains binary `PENDING_TRANSPORT` / external evidence exception. |
| `06_History_Decisions` | `13ObecLw1j0HGBSxhfvV5LMzotyaM1AP6` | PARTIAL | Decision and history logs mirrored. `CHANGELOG.md` (22,376 bytes) remains `PENDING_EXACT_TEXT_TRANSPORT`; no truncated copy will be created. |
| `07_Reports_Risks_Gaps` | `1OdLJKtclDCGuBZ2-PzKmqwuR4g3xAkdy` | MIRRORED | Risk/action report, workflow fix report, knowledge-gap audit, comprehensive audit, external automation reuse policy, and DB migration roadmap mirrored. |
| `08_Archive` | `191AtJ609-9wdulAmi0q4vmWuVbgWu9Rl` | ARCHIVE_SECONDARY | `drive-mirror/08_Archive/README.md` records cold-storage policy. Historical pasted transcripts and older workflow exports do not override current state/specs. |
| `09_Spec_Kit_SDD` | `104anjjAJ8PnNpF-jCteksm3ELmDvfKGD` | MOSTLY_MIRRORED | Constitution, quality gates, 000 master spec, 001 R2 feature, 011 greenfield core documents, WU87–WU98 QA core, WU99/WU100 release/evidence docs mirrored. Large candidate workflow/test JSONs remain exact-transport items. |

## Spec Kit subfolder audit
- `.specify`: Engineering Constitution mirrored.
- `quality`: requirements checklist, expanded draft, and release/convergence gates mirrored.
- `specs/000-master-system`: spec, plan, and tasks mirrored.
- `specs/001-r2-error-handling`: spec, clarify, plan, tasks, runtime-test-gate, analysis, runtime-export-analysis, and requirements checklist mirrored.
- `specs/011-e2e-sales-agent-greenfield`: spec, plan, work-units, tasks, contracts, release gate, WU87–WU98 core QA, WU99/WU100 runbooks/checklists/evidence templates mirrored; candidate workflow JSONs and large test plan/harness remain exact-transport items.

## Historical duplicate handling
When Drive contains multiple files with the same logical QA name, the latest/canonical file is stored at the normal checklist path. Alternate/older versions are preserved under `checklists/history/` with a Drive-ID suffix. Historical artifacts never override later evidence.

## Cutover blockers
1. Exact transport of production/locked workflow JSONs and required release candidates.
2. Exact text transport of `PROJECT_STATE.md`, `CHANGELOG.md`, and the large current system-prompt file, or an explicitly approved archive/reference exception for each.
3. n8n runtime inventory/current IDs and active/inactive state under `MIG-001`.
4. Verify RC3/final release artifact identity and SHA; any `RC4_2 FINAL FROZEN` reference remains unverified until the actual artifact is found.
5. PR review and explicit owner approval for GitHub source-of-truth cutover.
