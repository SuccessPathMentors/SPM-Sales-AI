# Success Path Mentors AI Sales Chatbot — Start Here

Last updated: 2026-08-18 (America/Toronto)

## Release Checkpoint
- Project state: **R1 APPROVED AND LOCKED**.
- Completed phase: **R1 — Reliable Lead Submission**.
- Focused R1 regression tests: **10/10 PASS, owner confirmed**.
- Next phase: **R2 — Reliability and Error Handling (READY / NOT STARTED)**.
- Locked workflow: `03_Workflows_Current/ChatBotMSE_v2_R1_LOCKED_2026-08-17.json`.

## Default Restart Path — Token Optimized
For normal sessions, read only:

1. `PROJECT_STATE.md`
2. root `AGENTS.md`
3. current task created from `01_Governance_Plans/TASK_TEMPLATE.md`
4. exact affected workflow node/file/evidence

Do **not** read the full documentation list below by default.

## Expand Context Only When Needed
Use additional files based on the task:

- Architecture issue → `02_Current_Architecture/SYSTEM_ARCHITECTURE.md`
- Release planning → `01_Governance_Plans/RELEASE_PHASES_AND_GATES.md`
- Token/cost issue → `01_Governance_Plans/TOKEN_COST_OPTIMIZATION.md`
- QA/release evidence → `05_Testing_QA/`
- Decision/history question → `06_History_Decisions/`
- Risk/gap analysis → `07_Reports_Risks_Gaps/`
- Old version/regression investigation → `08_Archive/`

## Exact Engineering Restart Point
Resume with **R2 only**. Do not reopen R1 unless a regression is reproduced.

First R2 work should be one bounded reliability task:
1. export the currently published n8n workflow;
2. identify one external dependency/error path;
3. define focused pass/fail criteria;
4. implement the smallest safe change;
5. test and record evidence;
6. update `PROJECT_STATE.md` and `CHANGELOG.md`;
7. lock/checkpoint before moving to the next task.

## R1 Locked Behavior
- Complete confirmed leads write successfully.
- Corrected data updates the same lead/session.
- Invalid/unconfirmed data does not write.
- Duplicate confirmation does not create duplicate leads.
- Operational lead messages stay outside unanswered-question logging.
- Success is shown only after the write succeeds.

## Knowledge Checkpoint
- Issue 1 — Canada/USA pricing and location resolution: LOCKED.
- Issue 2 — refund/service-recovery policy: LOCKED.
- Next knowledge issue: review `PHR-004` in `ISLAMIC_PHRASES`.
- Do not change approved knowledge wording without explicit approval.

## Full Reference Set — On Demand Only
These files remain authoritative but should not all be loaded at session start:
- `CURRENT_STATUS_PROGRESS.md`
- `WORKFLOW_FIX_REPORT.md`
- `RELEASE_PHASES_AND_GATES.md`
- `QA_TESTING_RELEASE_GATE.md`
- `RISKS_GAPS_ACTIONS.md`
- `DECISION_LOG.md`
- `HISTORY_LOG.md`

## Authoritative Assets
- Live AI knowledge base: Google Sheets source already documented in project governance.
- n8n workspace: Success Path Mentors n8n workspace.
- Public website: Success Path Mentors website.

## Working Rule
Define → retrieve minimally → implement → test → record evidence → approve → lock.

Context rule:
**Search → Read exact range → Work → Test → Update State.**
