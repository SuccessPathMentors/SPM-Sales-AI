# 000 Master System Tasks

Status: Initial migration/task map
Date: 2026-08-19

## Phase 1 — Establish Spec-Driven Governance
- [x] T001 Create `09_Spec_Kit_SDD` in the existing AI Sales Bot Drive workspace.
- [x] T002 Create `.specify/memory` and `specs` structure.
- [x] T003 Create engineering constitution covering deterministic-first behavior, locked releases, data integrity, commercial truthfulness, live verification, privacy, multilingual parity, observability, testing, and traceability.
- [x] T004 Create master system specification for the existing production chatbot.
- [x] T005 Create master technical plan for introducing Spec Kit without rewriting locked production behavior.
- [x] T006 Add a requirements-quality checklist for master and future feature specs.
- [x] T007 Map existing release gates and QA evidence into Spec Kit release/convergence gates.

## Phase 2 — GitHub Repository Readiness
- [ ] T008 Create or identify the GitHub repository for `spm-ai-sales-bot`.
- [ ] T009 Initialize Spec Kit in the repository using the selected coding-agent integration.
- [ ] T010 Mirror `.specify/memory/constitution.md` and numbered `specs/` artifacts into GitHub Markdown.
- [ ] T011 Add `.gitignore`, `.env.example`, README, contribution/change-control notes, and secret-handling rules.
- [ ] T012 Import sanitized current workflow JSON snapshots into `workflows/`.
- [ ] T013 Import architecture, QA, project-state, and changelog controls that should be version-controlled.
- [ ] T014 Establish branch/PR naming tied to numbered feature specs.
- [ ] T015 Enable issue creation from Spec Kit tasks when useful and preserve requirement/task IDs in PR descriptions.

## Phase 3 — Reverse-Spec Existing Production Baseline
- [ ] T016 Verify the exact current published n8n workflow against the locked R1 snapshot.
- [ ] T017 Create a baseline behavior matrix for R1 lead submission.
- [ ] T018 Map current AI vs deterministic responsibilities by node/function.
- [ ] T019 Map persistence contracts for Sheets and Redis.
- [ ] T020 Map lead/student/parent canonical identifiers and shared fields.
- [ ] T021 Map volatile-data dependencies including teacher/slot availability and booking confirmation.
- [ ] T022 Map handoff, opt-out, nurture, and notification state transitions.
- [ ] T023 Map EN/AR parity obligations.

## Phase 4 — First Production Feature Under Spec Kit
Feature: `001-r2-error-handling`

- [x] T024 Run specification creation from the bounded R2 reliability objective.
- [x] T025 Run clarification and resolve material ambiguities before planning.
- [x] T026 Produce technical plan with exact affected n8n nodes/integrations.
- [x] T027 Create requirements checklist.
- [x] T028 Generate dependency-ordered implementation tasks.
- [x] T029 Run cross-artifact analysis and resolve critical conflicts.
- [x] T030 Implement the smallest safe candidate change.
- [ ] T031 Run focused runtime tests.
- [ ] T032 Run affected R1 regression tests.
- [ ] T033 Run convergence against spec/plan/tasks and add/fix any remaining gaps.
- [ ] T034 Update PROJECT_STATE and CHANGELOG.
- [ ] T035 Promote, verify, lock/tag, and archive obsolete candidate artifacts only after all gates pass.

## Phase 5 — Next High-Value Feature Specs
- [ ] T036 `002-deterministic-lead-submission`
- [ ] T037 `003-location-timezone-currency-integrity`
- [ ] T038 `004-parent-student-data-sync`
- [ ] T039 `005-live-scheduling-and-booking`
- [ ] T040 `006-human-handoff-hardening`
- [ ] T041 `007-optout-and-nurture`
- [ ] T042 `008-observability-and-telemetry`
- [ ] T043 `009-multilingual-parity`
- [ ] T044 `010-knowledge-governance`

## Definition of Done for Any Future Feature
A feature is complete only when its specification is approved and internally consistent; implementation maps to tasks; applicable runtime and regression tests pass; no critical checklist/analyze/converge gaps remain; secrets/PII are excluded from version control; production behavior matches the approved spec; project state/change log are updated; and the approved artifacts are traceable in GitHub and mirrored to Drive as required.
