# Runtime Export Analysis — 2026-08-20

Status: Static review complete; main runtime identity owner-confirmed
Feature: 001-r2-error-handling / 002-deterministic-lead-submission convergence

## Uploaded Runtime Exports
- `Validated Human Handoff (1).json`
  - workflow ID: `swhmNa0Goo0uYm1k`
  - active: true
  - nodes: 10
  - current validation/conflict/upsert/success flow is intact.
  - current Google Sheets lookup/upsert operations do not yet contain the R2 retry/error-output hardening.
- `ChatBotMSE v2 - R2.5 Release Candidate Stable Efficient.json`
  - workflow ID: `vSc7cMIMFMEUdi7z`
  - active: false
  - nodes: 74
  - compared with R2 Token Optimized: +20 nodes / -5 nodes.
  - removed legacy/AI-mediated lead nodes include `Submit Validated Human Handoff`, `Save Qualified Lead`, `Create or Update Human Handoff`, and `Check Existing Lead`.
  - added deterministic registration/handoff nodes include `Deterministic Lead Registration Gateway`, `Build Deterministic Handoff Payload`, `Can Submit Handoff Deterministically?`, `Execute Validated Human Handoff Directly`, `Format Deterministic Handoff Result`, and lead-state save/restore nodes.
  - no `ai_tool` edge exists in the exported R2.5 graph.

## Deterministic Handoff Identity
`Execute Validated Human Handoff Directly` targets workflow ID `swhmNa0Goo0uYm1k`, cached as `Validated Human Handoff`.

This exactly matches the uploaded active handoff workflow ID.

Therefore, the R2.5 candidate is statically wired to the current handoff workflow rather than an AI tool call.

## Important Runtime Limitation
The uploaded handoff export proves that the handoff subworkflow is active.

The exported R2.5 file contains `active=false`, but the owner has explicitly confirmed that this exact R2.5 workflow is the main chatbot currently running in n8n. For runtime identity, the owner confirmation is authoritative over the export flag.

Do not modify the working production R2.5 or replace the active handoff until SAFE TEST runtime tests pass.

## SAFE TEST Candidate
A new test-only candidate was generated from the uploaded active handoff export, not from the older Drive baseline:

`Validated_Human_Handoff_R2_ERROR_HANDLING_SAFE_TEST_2026-08-20.json`

Safety controls:
- `active=false`.
- top-level workflow `id` removed.
- top-level `versionId` removed.
- existing uploaded handoff node IDs and behavior preserved.
- only the two in-scope Google Sheets nodes receive bounded retry and explicit error outputs.
- added `Return Lead Lookup Error` and `Return Lead Write Error`.
- success paths remain unchanged.

SAFE TEST SHA-256:
`0a6935331fddc9c9ee1a3ac1720bd884c61a0a9eefa6a2fcd408e7810359905c`

## Static QA
PASS:
- JSON valid.
- 12/12 node names unique.
- 12/12 node IDs unique.
- `active=false`.
- no top-level workflow ID/version ID.
- protected node semantics unchanged.
- lookup retry/error branch present.
- upsert retry/error branch present.
- original success routes preserved.
- basic plaintext secret scan clean.
- R2.5 main graph has no duplicate node names/IDs or dangling graph references.

## Exact Next Runtime Gate
1. Use the owner-confirmed R2.5 workflow as the current production main baseline.
2. Import the SAFE TEST handoff candidate as a separate inactive workflow.
3. Temporarily point a non-production copy of R2.5 to the imported SAFE TEST workflow.
4. Run R2-F01 through R2-F10, including lookup failure, write failure, transient recovery, duplicate prevention, validation failure, and success=false handling.
5. Run all permanent R1 regression cases 1–10.
6. Converge results against Spec Kit artifacts.
7. Promote only after every gate passes.

Release status: main identity RESOLVED; Feature 001 promotion remains BLOCKED pending SAFE TEST runtime evidence and R1 regression.
