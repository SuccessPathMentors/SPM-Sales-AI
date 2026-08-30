# WU-101 Runtime Test #1 — Finding

Date: 2026-08-30
Environment: STAGING
Workflow: `[STAGING] SPM WU101 Conversation Analytics Candidate`
Workflow ID: `mMZVFxJIxE7a9SSW`

## Observed
- Customer-facing FAQ response rendered successfully for `What subjects do you offer?`.
- Execution reached `Build WU101 Conversation Analytics Event` successfully.
- Execution reached `Upsert WU101 Analytics [STAGING]`.
- Google Sheets node returned fail-open output with: `Invalid input for 'turn_index' [item 0]`.
- `WU101_ANALYTICS_STAGING` remained header-only; no analytics data row was persisted.
- No Production activation/deployment was involved.

## Classification
Material STAGING runtime finding, bounded to the analytics persistence layer.
Customer response behavior remained fail-open as designed.

## Required fix
Harden Google Sheets numeric-field handling in the deterministic WU-101 candidate and add regression coverage before repeating Runtime Test #1.
