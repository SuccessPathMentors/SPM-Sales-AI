# Google Drive Folder-Level Migration Audit

Audit date: 2026-08-30
Drive root: `Success_Path_Mentors_AI_Sales_Chatbot`
Drive root ID: `1V7siTY6XYtE0RJXANlXnQmiJDS0vuUkf`
Target: `SuccessPathMentors/SPM-Sales-AI`

Status legend:
- `MIRRORED`: identified active engineering authority is represented in GitHub.
- `MIRRORED_EXACT`: provider-original file bytes were transported and identity verified.
- `MIRRORED_ACTIVE_HISTORY_SECONDARY`: active engineering set is represented; additional cold/history material may remain in Drive by policy.
- `EXTERNAL_RUNTIME`: intentionally outside GitHub because it is mutable runtime data.
- `ARCHIVE_SECONDARY`: historical cold storage; not hot engineering authority.

## Folder matrix

| Folder | Drive ID | Status | GitHub treatment / remaining work |
|---|---|---|---|
| `00_START_HERE` | `1cMOB0Yr0KeE_0bPhS362DkV6OnkzQldq` | MIRRORED_EXACT | Start-here/index were already mirrored; `PROJECT_STATE.md` is now exact-mirrored. It remains a historical snapshot; `docs/STATE.yaml` is current reconciled state authority. |
| `01_Governance_Plans` | `1TXqn7O5R35JAnncyP_gVDHEkZcEv8CeH` | MIRRORED | Project charter, current status, release phases/gates, token/context optimization, and task template mirrored. |
| `02_Current_Architecture` | `1Vz1zjzVvrqku24DIelHxi3c5hWmXrqZb` | MIRRORED_EXACT | `SYSTEM_ARCHITECTURE.md` mirrored; `AI_Agent_System_Message_fixed.md` now exact-mirrored. |
| `03_Workflows_Current` | `1CN2-wUUxPWle2aLVvkoD3cE2OXcCsmyZ` | MIRRORED_EXACT | R1 locked, R2 token-optimized, paused refactor, fixed reference, and validated handoff workflow exports transported byte-for-byte. Current production RC4.3.3 is versioned separately under `n8n/workflows/production/`. |
| `04_AI_Knowledge_Sources` | `1wfeUvXa9wuTUVQqMZL9dWNNRgHS75iib` | MIRRORED + EXTERNAL_RUNTIME | Governance/reference docs mirrored. Live Google Sheets knowledge data remains mutable runtime truth by design. |
| `05_Testing_QA` | `1LyZI0Z685X65z4nsSoH76x8A2G9j7mz6` | MIRRORED_EXACT | QA release gate and R1 lock record mirrored; Stage 10 XLSX template transported exactly and validated as an XLSX container. |
| `06_History_Decisions` | `13ObecLw1j0HGBSxhfvV5LMzotyaM1AP6` | MIRRORED_EXACT | Decision/history logs mirrored and `CHANGELOG.md` exact-mirrored. Historical records do not override current state. |
| `07_Reports_Risks_Gaps` | `1OdLJKtclDCGuBZ2-PzKmqwuR4g3xAkdy` | MIRRORED | Risk/action report, workflow fix report, knowledge-gap audit, comprehensive audit, external automation reuse policy, and DB migration roadmap mirrored. |
| `08_Archive` | `191AtJ609-9wdulAmi0q4vmWuVbgWu9Rl` | ARCHIVE_SECONDARY | Cold-storage policy recorded in GitHub. Historical transcripts/older exports are intentionally not loaded into normal engineering context and are not required for cutover unless Drive itself will be retired. |
| `09_Spec_Kit_SDD` | `104anjjAJ8PnNpF-jCteksm3ELmDvfKGD` | MIRRORED_ACTIVE_HISTORY_SECONDARY | Constitution, quality gates, 000 master spec, 001 R2 feature, 011 Greenfield core docs/QA/release evidence, and retained WU87–WU99 candidate/test artifacts are mirrored. Exact candidate/test transport is complete for the identified retention set; duplicate historical bytes are deduplicated by content while provenance is documented. |

## Exact-transport batch result
- Batch artifacts: `30`
- Batch bytes: `3,273,938`
- Exact Git blob matches: `30/30`
- Mismatches: `0`
- Staging upload commit: `5531c377208bd7d1cc5572533fa5760713bcefa0`
- Final placement commit: `86ec918bb75e919df67d167ae3e3e67c040c633c`
- Temporary `migration-incoming/` folder: removed after verification
- Detailed identity manifest: `docs/MIG-002_EXACT_TRANSPORT_MANIFEST_2026-08-30.csv`

## Current production artifact
Current live n8n production workflow is separately exact-mirrored:
- `n8n/workflows/production/SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json`
- workflow ID: `CMBMpxX5AqqK2UTn`
- SHA-256: `680496f2b68b13dd7105e72fd132a2066d70ec969e6e0675f138ebb1fb16fe39`
- exact transport: PASS

## Historical duplicate handling
When Drive contains multiple logical copies/revisions, canonical/latest items remain at normal paths and historical alternates remain secondary. The two discovered Drive copies of the same WU88 62-intent candidate were byte-identical, so one exact content object is retained with duplicate provenance documented. R1 locked and the paused refactor export are also byte-identical but both names are preserved because their historical roles differ.

## Remaining cutover gates — not MIG-002 transport blockers
1. Complete/update n8n runtime dependency inventory and close `MIG-001` from current RC4.3.3 evidence.
2. Reconcile current state/release documentation so stale RC3/RC4.2 historical references cannot override verified RC4.3.3 runtime truth.
3. Review migration PR and ensure branch history is integrated cleanly.
4. Owner explicitly approves GitHub engineering source-of-truth cutover.
5. If Drive will later be deleted entirely, perform a separate cold-archive export of `08_Archive`; this is not required for normal engineering cutover.
