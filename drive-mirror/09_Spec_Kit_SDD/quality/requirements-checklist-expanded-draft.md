# Requirements Quality Checklist — SPM AI Sales Bot

Status: Active governance checklist v1.0
Applies to: master specification and every numbered feature specification

## A. Problem and Outcome
- [ ] The problem is stated in business/user terms, not only as a technical change.
- [ ] The intended user or operational outcome is measurable or observable.
- [ ] The feature boundary is small enough to implement and test safely.
- [ ] Non-goals and excluded behavior are explicit.

## B. Requirements Completeness
- [ ] Every material behavior has a requirement ID or unambiguous requirement statement.
- [ ] Inputs, outputs, state changes, and persistence effects are defined.
- [ ] Validation and normalization rules are explicit for structured data.
- [ ] Source-of-truth rules are identified for data the feature reads or writes.
- [ ] Conflict-resolution and propagation rules are defined where shared fields exist.
- [ ] Volatile facts identify the required live source.
- [ ] Deterministic actions are separated from model-semantic responsibilities.

## C. Failure Behavior
- [ ] Expected failure modes are listed.
- [ ] The system cannot report success when the deterministic action failed.
- [ ] Retry, fallback, handoff, or stop behavior is defined where applicable.
- [ ] Partial-write and duplicate-action risks are addressed.
- [ ] Recovery or rollback expectations are stated for production-impacting changes.

## D. Commercial Truthfulness
- [ ] Prices, discounts, refunds, policies, teacher claims, availability, and booking status are source-backed.
- [ ] Unsupported commercial claims are explicitly prohibited.
- [ ] Live verification is required for volatile operational facts.
- [ ] Booking success requires successful scheduling plus a valid booking identifier.

## E. Data Integrity and Privacy
- [ ] Canonical IDs are defined for lead/session/parent/student entities touched by the feature.
- [ ] Minimum necessary data is collected and exposed.
- [ ] Secrets, credentials, tokens, and unnecessary PII are excluded from specs, fixtures, logs, and workflow exports.
- [ ] Idempotency requirements are defined for writes that may be retried or reconfirmed.
- [ ] Corrections update the intended record rather than create an unintended duplicate.

## F. Multilingual Parity
- [ ] English and Arabic execute the same business rules and safeguards.
- [ ] Any additional production language is tested for equivalent operational outcomes.
- [ ] Translation differences do not change policy, pricing logic, validation, or truth conditions.

## G. Acceptance Criteria
- [ ] Acceptance criteria are specific, observable, and testable.
- [ ] Positive-path acceptance criteria are included.
- [ ] Negative/failure-path acceptance criteria are included.
- [ ] Locked R1 behavior affected by the feature has explicit regression criteria.
- [ ] PASS/FAIL evidence can be captured without relying only on model narrative.

## H. Traceability
- [ ] Requirement → plan → task → implementation → test evidence → release/change record is traceable.
- [ ] Every workflow/code/config change maps to a requirement and task ID.
- [ ] GitHub issue/PR references can be attached when GitHub is the execution repository.
- [ ] Approved artifacts can be mirrored back to Google Drive.

## I. Constitution Gate
A specification is ready for planning only when all critical items above are resolved or explicitly marked not applicable with rationale. Material ambiguity blocks implementation.
