# History Log

## Build history summary

- Connected website chat, OpenAI, n8n, Google Sheets, and Redis.
- Built multilingual grounded knowledge, intent/NLP, consultative sales, unanswered-question handling, and lead lifecycle.
- Completed iterative QA and refactor work.
- Created a phase-gated Drive workspace and documentation set.

## 2026-08-17 — Knowledge Issue 1 locked

- Approved Canada/USA currency rule using the same package numbers.
- Approved location resolution from explicit country or verified ACTIVE province/state/city mapping.
- Updated packages, response rules, sales flow, review notes, and source log.
- Verified exact live cells after write.

## 2026-08-17 — Knowledge Issue 2 locked

- Approved multilingual refund/service-recovery policy.
- Activated and aligned `POL-004`, `POL-008`, and `POL-012`.
- Verified status validation and wrapped long cells.
- Locked the related review note.

## 2026-08-17 — Latest workflow diagnosis and pause

- Inspected `ChatBotMSE v2 - Refactor Working Copy (2).json`.
- Confirmed valid JSON, 59 nodes, and inactive export.
- Confirmed final lead submission remains model-dependent through the AI Agent tool connection.
- Confirmed personal tool inputs use `$fromAI` rather than deterministic confirmed state.
- Identified the missing deterministic submit branch as the current P0 root cause.
- Made no live n8n or sheet changes during diagnosis.
- Saved a versioned paused checkpoint and updated project status files.
- Owner paused work and will resume at R1 deterministic lead submission.

## 2026-08-17 — R1 completed and locked

- Owner completed the complete R1 focused test set.
- Lead data was written successfully with no reported remaining issue.
- New lead, correction, consent, confirmation, and duplicate-protection behavior passed.
- Operational correction/summary messages remained outside unanswered-question logging.
- R1 was explicitly approved and locked by the owner.
- Saved immutable workflow snapshot `ChatBotMSE_v2_R1_LOCKED_2026-08-17.json`.
- Created `R1_LOCK_RECORD_2026-08-17.md`.
- Next phase is R2; it has not started.

## Required change-log fields going forward

Date/author; phase/issue; changed files/nodes; reason/risk; before/after; tests/execution IDs; rollback reference; approval status.
