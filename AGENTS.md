# SPM Sales AI — Agent Operating Rules

## Mission
Deliver bounded, testable changes to the Sales AI Agent without reopening approved work, silently expanding scope, or changing production directly.

## Required startup sequence
1. Read `docs/STATE.yaml`.
2. Read the assigned Working Unit only.
3. Read only the locked dependencies and exact n8n workflow artifacts needed for that unit.
4. Do not reconstruct the project from chat history.

## State rules
- `LOCKED` artifacts are read-only.
- `FROZEN` release candidates are read-only.
- A downstream agent may consume a locked artifact but may never rewrite it.
- If a locked dependency must change, create a Change Request and stop the affected work.
- An agent may move its own work only to `READY_FOR_REVIEW`; it may not self-approve or self-lock.

## Historical evidence precedence
- `docs/STATE.yaml` is the reconciled current-state authority during migration.
- Files under `drive-mirror/**` that are snapshots, old runbooks, ledgers, preparation checklists, or archived exports are historical audit evidence unless a current control document explicitly promotes them.
- Never use an older `NOT_RUN`, preparation-only, or unknown-runtime statement to override later dated verified evidence.
- Never rewrite historical evidence to make it agree with a later event. Preserve the old artifact and record supersession only in current control documents.
- Current runtime identity claims require verified runtime evidence and/or an exact verified runtime export.
- If chronology or evidence precedence is unclear, set `RECONCILIATION_REQUIRED` instead of guessing.
- Apply `docs/MIG-004_RELEASE_EVIDENCE_PRECEDENCE.md` when historical release records conflict.

## Scope rules
- Implement only the assigned Working Unit.
- Do not add speculative features, refactors, abstractions, or redesigns.
- Do not modify unrelated workflows or nodes.
- Prefer the smallest safe change that satisfies the acceptance criteria.

## n8n rules
- GitHub is the source of truth for versioned workflow JSON, prompts, contracts, tests, and state.
- n8n is the runtime/deployment target.
- Never deploy an AI-generated change directly to production.
- Deploy first to a non-production/staging workflow.
- Production activation requires an explicit approval gate.
- Never edit a frozen JSON in place. Create a new release candidate/version.

## Review rules
Review only for material findings:
- requirement violation;
- functional bug;
- data-integrity problem;
- security/privacy risk;
- critical missing edge case;
- unsafe n8n side effect;
- false success or hallucinated business action.

Do not generate style-only or speculative redesign feedback.

## Loop control
- Maximum automated implementation/review repair cycles: 2.
- After a second material failure, set the WU to `BLOCKED` and request human/architect intervention.

## Completion contract
A Working Unit can be locked only when its required gates pass: implementation evidence, acceptance criteria, tests, review, and any required runtime evidence.

## Agent result format
Return a compact result:

```text
WU: WU-XXX
STATUS: READY_FOR_REVIEW | BLOCKED
FILES_CHANGED: ...
TESTS: ...
ACCEPTANCE: ...
COMMIT: ...
BLOCKERS: ...
CHANGE_REQUEST: none | CR-XXX
```
