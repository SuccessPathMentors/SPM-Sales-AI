# Spec Kit Requirements Quality Checklist — SPM AI Sales Bot

Use before planning and again before implementation.

## Requirement Quality
- [ ] Problem and user outcome are explicit.
- [ ] Scope and non-goals are explicit.
- [ ] Requirements describe what/why without prematurely locking implementation.
- [ ] Acceptance criteria are observable and testable.
- [ ] Failure behavior is defined.
- [ ] Ambiguous business terms are clarified.

## Business Truth and Safety
- [ ] Pricing/policy claims identify an approved source.
- [ ] Volatile facts identify a live source where required.
- [ ] Booking success requires scheduling success plus booking ID.
- [ ] Teacher qualification/language/gender/origin claims follow approved safeguards.
- [ ] No unsupported commercial claim can be emitted.

## Data Integrity
- [ ] Canonical IDs and source-of-truth fields are identified.
- [ ] Validation/normalization rules are explicit.
- [ ] Conflict-resolution and propagation rules are explicit.
- [ ] Idempotency/duplicate behavior is defined.
- [ ] Invalid/unconfirmed data cannot be treated as successfully confirmed data.

## Architecture
- [ ] Deterministic responsibilities are separated from AI responsibilities.
- [ ] Affected n8n nodes/integrations are identifiable during planning.
- [ ] Persistence/state implications are defined.
- [ ] Observability requirements are defined.
- [ ] Rollback/recovery behavior is known for production-impacting changes.

## UX and Language
- [ ] EN/AR business behavior remains equivalent.
- [ ] Human handoff conditions are explicit.
- [ ] User-facing failure messages do not misrepresent system state.
- [ ] Opt-out/nurture behavior is preserved where applicable.

## Security and Privacy
- [ ] Minimum necessary data is collected.
- [ ] No secrets are included in specs, workflow exports, fixtures, or GitHub commits.
- [ ] Test fixtures avoid unnecessary real PII.

## Testing and Release
- [ ] Focused functional tests are defined.
- [ ] Affected locked-behavior regression tests are defined.
- [ ] Static QA and runtime QA are distinguished.
- [ ] PASS/FAIL evidence is defined.
- [ ] PROJECT_STATE and CHANGELOG update requirements are included.
- [ ] Convergence against spec/plan/tasks is required before closure.
