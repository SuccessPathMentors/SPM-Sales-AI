# 001 R2 Error Handling — Success Path Mentors AI Sales Bot

Status: Draft specification v0.1
Parent: 000 Master System Specification
Governance: Engineering Constitution v1.0

## 1. Problem
R1 Reliable Lead Submission is approved and locked, but the current architecture still exposes an important validated submission/handoff operation through the AI Agent tool path. The production system must preserve R1 outcomes while reducing the risk that deterministic writes, tool failures, or operational failures depend on model tool choice or are incorrectly represented to the user as successful.

## 2. Goal
Harden deterministic success/failure behavior around lead submission, validated human handoff, and related operational errors without changing the locked R1 business outcomes.

## 3. User and Operational Outcomes
- A valid confirmed lead continues to be recorded exactly once.
- A failed deterministic action is never described as successful.
- A transient or permanent operational failure produces a controlled recovery, retry, or handoff outcome.
- Operations can diagnose the failure from structured evidence.
- Existing R1 behavior remains unchanged unless an approved requirement in this feature explicitly supersedes it.

## 4. In Scope
- Error handling around validated lead/handoff submission paths.
- Success/failure gating after deterministic writes.
- Tool/subworkflow failure detection.
- Controlled retry or fallback rules where safe.
- User-facing failure-state truthfulness.
- Structured failure categories and evidence.
- Regression protection for affected R1 behavior.

## 5. Out of Scope
- Pricing/package changes.
- Knowledge-base wording changes.
- New scheduling or booking functionality.
- Parent/student data synchronization redesign.
- New CRM replacement.
- Broad n8n workflow rewrite.
- Changes to the locked R1 lead fields or confirmation rules unless required by an approved defect fix.

## 6. Functional Requirements
### R2-FR-001 Deterministic Success Source
A successful lead/handoff submission must be based on the deterministic write result, not solely on model intent, model narrative, or tool-selection assumptions.

### R2-FR-002 No False Success
If a write, lookup, validation, subworkflow call, or required downstream action fails, the bot must not claim that the affected action succeeded.

### R2-FR-003 Failure Classification
Operational failures must be categorized sufficiently to distinguish at minimum validation failure, write failure, duplicate/idempotency outcome, subworkflow/tool failure, notification-only failure, and unknown/unhandled failure.

### R2-FR-004 Preserve R1 Idempotency
Repeated confirmation or retry must not create duplicate lead records. Corrections must continue to update the intended lead/session according to the locked R1 behavior.

### R2-FR-005 Safe Recovery
For each failure category the plan must define one of: safe retry, deterministic fallback, human handoff, user retry request, or terminal stop. Retry behavior must not create duplicate writes.

### R2-FR-006 Handoff Context Preservation
If an operational failure requires human handoff, the handoff must preserve the relevant lead/session/conversation context already captured.

### R2-FR-007 Observability
Critical execution paths must emit structured evidence sufficient to identify route, validation result, write result, failure category, retry/fallback result, and final user-visible outcome.

### R2-FR-008 Notification Separation
A post-write notification failure must not retroactively convert a successful persisted lead into a failed lead write. The system must distinguish primary business-action success from secondary notification failure.

### R2-FR-009 Locked R1 Regression Protection
The feature must preserve all locked R1 outcomes unless a reproduced regression and approved requirement explicitly authorize a change.

## 7. Acceptance Criteria
1. Confirmed valid lead submission still succeeds and writes exactly once.
2. Repeated confirmation does not create a duplicate record.
3. Corrected lead data updates the intended lead/session.
4. Invalid or unconfirmed data is not persisted as confirmed data.
5. A forced write failure does not produce a success message.
6. A forced subworkflow/tool failure is observable and produces the defined recovery/handoff behavior.
7. A post-write notification failure is recorded separately from write success.
8. Operational lead messages remain outside unanswered-question logging.
9. Success is reported only after the required deterministic business action succeeds.
10. Focused runtime tests and all affected R1 regression tests pass before release.

## 8. Required Runtime Evidence
Where applicable, test evidence must capture:
- execution ID;
- timestamp;
- session/lead test identifier;
- route or intent;
- validation result;
- write/subworkflow result;
- failure category;
- retry/fallback/handoff result;
- row/reference identifier when a write succeeds;
- expected outcome vs actual outcome.

## 9. Clarification Questions Before Planning
The following must be resolved from the currently published workflow and locked R1 artifacts before implementation:
- Which exact published workflow version is active now?
- Which node/subworkflow currently owns the authoritative lead/handoff write?
- Which success message path depends on tool choice or model output today?
- Are any retries already configured at node, subworkflow, or platform level?
- Which downstream notifications are business-critical versus secondary?
- What user-facing behavior is required after a non-recoverable write failure?
- Which failure categories already exist in logs or execution data?

## 10. Dependencies
- Current published n8n workflow export.
- `ChatBotMSE_v2_R1_LOCKED_2026-08-17.json` locked baseline.
- Validated human handoff workflow/subworkflow.
- Current architecture and release-gate documents.
- R1 regression evidence and test cases.

## 11. Constitution Check
This feature is aligned with specification-before-implementation, preserve-locked-behavior, deterministic-first engineering, no-false-success, observability, smallest-safe-change, privacy, and test-gated release principles.

Implementation is blocked until the clarification questions are resolved and a technical plan identifies the exact affected nodes and test gate.
