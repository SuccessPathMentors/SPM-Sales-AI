# File Index and Source of Truth

Last updated: 2026-08-17.

## Current workflow artifacts

| Asset | Role | Authority |
|---|---|---|
| `ChatBotMSE_v2_R1_LOCKED_2026-08-17.json` | Locked R1 main-workflow snapshot | Approved R1 baseline; do not overwrite |
| `ChatBotMSE_v2_Refactor_Working_Copy_2_PAUSED_2026-08-17.json` | Latest main-workflow checkpoint inspected at pause | Diagnostic source; not approved for production |
| `ChatBotMSE_v2_FIXED.json` | Earlier corrected main workflow candidate | Superseded for diagnosis by the latest paused checkpoint; retain for comparison |
| `Validated_Human_Handoff_FIXED.json` | Validated lead upsert subworkflow candidate | Must be revalidated when R1 resumes |
| `AI_Agent_System_Message_fixed.md` | Current prompt candidate | Guidance only; cannot replace deterministic orchestration |
| `Success_Path_Mentors_Stage_10_Testing_TEMPLATE.xlsx` | QA template | Not release evidence until completed results are saved |
| `R1_LOCK_RECORD_2026-08-17.md` | R1 approval and acceptance record | Authoritative phase-lock record |

## Status and governance files

| File | Purpose |
|---|---|
| `00_START_HERE.md` | Exact pause/resume point |
| `CURRENT_STATUS_PROGRESS.md` | Completion, blocker, and next action |
| `RELEASE_PHASES_AND_GATES.md` | One-phase-at-a-time roadmap |
| `QA_TESTING_RELEASE_GATE.md` | R1 acceptance evidence |
| `WORKFLOW_FIX_REPORT.md` | Latest technical diagnosis |
| `LIVE_AI_KNOWLEDGE_SOURCE.md` | Live sheet pointer and KB checkpoint |
| `KNOWLEDGE_GAP_AUDIT_2026-08-17.md` | Historical audit plus approved changes |
| `DECISION_LOG.md` | Locked decisions |
| `HISTORY_LOG.md` | Chronological work record |

## Archive policy

- Never overwrite an approved export; save a versioned checkpoint.
- Move pasted code snapshots and superseded exports to `08_Archive` only after a replacement is verified.
- Keep credentials, API keys, Redis URLs, and secrets out of documentation.
