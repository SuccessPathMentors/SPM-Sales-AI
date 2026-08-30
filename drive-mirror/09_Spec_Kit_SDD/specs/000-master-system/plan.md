# 000 Master System Technical Plan

Status: Initial architecture plan v1.0
Date: 2026-08-19

## 1. Objective
Introduce Spec-Driven Development around the existing SPM AI Sales Bot without replacing proven production components or reopening locked behavior.

## 2. Existing Technical Baseline
Current system:
Website Chat → n8n → AI Agent / deterministic routing → FAQ / Sales State / Lead Capture / Human Handoff → Google Sheets + Redis → notifications/downstream automation.

Existing durable project controls remain authoritative for runtime state, architecture, release evidence, and workflow artifacts. Spec Kit becomes the engineering lifecycle and traceability layer.

## 3. Target Engineering Architecture
### Governance layer
- `.specify/memory/constitution.md`
- `PROJECT_STATE.md`
- `AGENTS.md`
- release gates and change log

### Specification layer
- `specs/000-master-system/spec.md`
- numbered feature specifications under `specs/NNN-feature-name/`
- each production feature may include `spec.md`, `plan.md`, `tasks.md`, `checklists/`, data contracts, and test evidence references

### Runtime layer
- n8n workflows
- AI prompts/agent instructions
- deterministic validation/routing nodes
- Google Sheets persistence
- Redis/session state
- calendar/scheduling integrations
- notification and handoff integrations

### Quality layer
- requirement completeness checklist
- cross-artifact consistency analysis
- focused functional tests
- regression tests
- release evidence
- convergence review against implemented runtime

### Version-control layer
GitHub becomes the preferred execution/version-control repository for Markdown specs, workflow JSON exports, validation scripts, test fixtures, schemas, and documentation. Google Drive remains the business-accessible durable workspace and review mirror.

## 4. Repository Strategy
Recommended GitHub repository root:

`spm-ai-sales-bot/`
- `.specify/`
- `specs/`
- `workflows/`
- `src/` or `automation/` for deterministic scripts/config
- `knowledge/` for versioned approved schemas/exports, excluding secrets and unnecessary PII
- `tests/`
- `docs/architecture/`
- `docs/qa/`
- `AGENTS.md`
- `PROJECT_STATE.md`
- `CHANGELOG.md`
- `.gitignore`
- `.env.example`

## 5. Spec Kit Operating Flow
For production-impacting features use:
1. constitution check
2. specify
3. clarify
4. plan
5. checklist
6. tasks
7. analyze
8. implement
9. runtime/regression test
10. converge
11. release gate
12. update PROJECT_STATE and CHANGELOG
13. commit/PR/tag
14. mirror approved artifacts to Drive

## 6. Branch and Feature Naming
Use numbered feature directories and matching branches where practical:
- `001-r2-error-handling`
- `002-deterministic-lead-submission`
- `003-location-timezone-currency-integrity`
- `004-parent-student-data-sync`
- `005-live-scheduling-and-booking`

One feature spec should represent one bounded engineering outcome. Large efforts should be decomposed before implementation.

## 7. Data and Secret Handling
- Never commit credentials, OAuth tokens, API keys, webhook secrets, private URLs containing secrets, or live customer PII.
- Use environment variables/credential stores for runtime secrets.
- Store only sanitized fixtures in tests.
- Workflow JSON exports must be inspected for embedded credentials or sensitive values before commit.
- Approved knowledge can be versioned when it contains no restricted customer data.

## 8. n8n Development Strategy
- Production exports are versioned as immutable snapshots.
- Work on a candidate copy/branch.
- Prefer deterministic nodes/scripts for validation, mapping, persistence, status transitions, and idempotency.
- AI Agent responsibilities should be constrained to semantic tasks.
- Every workflow change maps to a requirement/task ID.
- Runtime evidence must verify critical paths before promotion.

## 9. Test Architecture
Minimum categories:
- Intent/routing tests
- Knowledge-answer truth tests
- Lead validation tests
- Lead idempotency tests
- Correction/update tests
- Location/timezone/currency integrity tests
- Scheduling/booking tests
- Human-handoff tests
- Opt-out/nurture tests
- EN/AR parity tests
- Failure-path tests
- R1 regression suite

Each feature plan must state which categories apply and define observable PASS/FAIL evidence.

## 10. Release Strategy
No direct production modification without an approved bounded spec for material changes. Candidate → static QA → runtime QA → regression gate → owner/engineering approval → production promotion → post-release verification → lock/tag.

## 11. Initial Migration Approach
Do not rewrite the current chatbot. Reverse-specify the current locked baseline, then introduce future changes through feature specs.

Phase A — establish constitution and master spec.
Phase B — create GitHub-ready repository structure.
Phase C — map existing WU/release controls to Spec Kit artifacts.
Phase D — start the next bounded reliability feature under Spec Kit.
Phase E — connect GitHub issues/PRs and Drive review mirror.

## 12. First Feature Recommendation
`001-r2-error-handling`

Goal: harden deterministic success/failure behavior around lead submission and operational errors without changing locked R1 outcomes.

This feature should begin by comparing the currently published workflow with the locked R1 artifact and defining a focused runtime test gate before implementation.
