# Release and Convergence Gates — SPM AI Sales Bot

Status: Active governance mapping v1.0
Purpose: map existing release/QA controls into the Spec Kit lifecycle without reopening locked production behavior.

## Gate 0 — Constitution Check
Entry: bounded feature objective exists.

PASS when:
- the feature does not silently violate a locked baseline;
- deterministic-first, truthfulness, privacy, parity, and observability principles are addressed;
- no material requirement is knowingly ambiguous.

Output: constitution-check result recorded in the feature spec/plan.

## Gate 1 — Specification Ready
PASS when:
- problem, users/outcome, scope, non-goals, requirements, failure behavior, and acceptance criteria are complete;
- volatile facts and authoritative sources are identified;
- affected locked behavior and required regression coverage are named.

Output: approved `spec.md`.

## Gate 2 — Plan Ready
PASS when:
- exact affected workflow nodes, integrations, data contracts, and state transitions are identified;
- AI vs deterministic responsibilities are explicit;
- security/privacy and rollback implications are known;
- applicable test categories and observable evidence are defined.

Output: approved `plan.md`.

## Gate 3 — Checklist + Tasks Ready
PASS when:
- requirements-quality checklist has no unresolved critical item;
- implementation tasks are dependency ordered and map to requirements;
- no task authorizes an unrelated broad rewrite.

Output: checklist + `tasks.md`.

## Gate 4 — Cross-Artifact Analysis
PASS when:
- spec, plan, tasks, constitution, architecture, and locked baseline contain no unresolved critical conflict;
- missing coverage and contradictory source-of-truth rules are resolved before implementation.

Output: analysis result with issues resolved or explicitly blocked.

## Gate 5 — Candidate Implementation
Rules:
- never modify the locked R1 artifact directly;
- work on a candidate copy/branch;
- implement the smallest safe change;
- every changed workflow/code/config artifact maps to requirement/task IDs.

PASS when static validation succeeds and no secret/PII exposure is introduced.

## Gate 6 — Focused Runtime QA
PASS when the feature acceptance criteria succeed in live/runtime testing with observable evidence.

Evidence should include, where applicable:
- execution ID;
- timestamp;
- route/intent;
- validation result;
- write/scheduling/handoff result;
- row or booking reference;
- expected vs actual outcome.

Static QA alone cannot pass this gate.

## Gate 7 — Regression Gate
PASS when all affected locked behavior continues to pass.

For R1 this includes at minimum:
- confirmed valid lead writes successfully;
- corrected data updates the same lead/session;
- invalid or unconfirmed data does not write as confirmed;
- duplicate confirmation does not create duplicates;
- operational lead messages do not pollute unanswered-question logging;
- success is reported only after the write succeeds.

## Gate 8 — Convergence Review
Compare implemented runtime against:
constitution → spec → plan → checklist → tasks → test evidence.

PASS when:
- implemented behavior matches approved requirements;
- no material task is incomplete;
- no undocumented runtime behavior was introduced;
- remaining gaps are either fixed or explicitly deferred outside the feature boundary.

## Gate 9 — Release Approval
PASS when:
- focused runtime QA passes;
- regression gate passes;
- rollback/recovery path is known;
- owner/engineering approval is recorded;
- production candidate is identifiable and reproducible.

## Gate 10 — Post-Release Lock and Evidence
After promotion:
- verify production behavior;
- update `PROJECT_STATE.md` and `CHANGELOG.md`;
- record release/test evidence;
- lock/tag the approved artifact;
- archive obsolete candidates without deleting historical evidence;
- mirror approved spec artifacts to Drive and GitHub as required.

## Current Application
R1 Reliable Lead Submission remains APPROVED AND LOCKED. The next production feature must enter at Gate 0 and must not modify R1 until its own Spec Kit gates authorize a candidate change.
