# 001 R2 Error Handling — Clarification Record

Status: Clarification complete for planning
Date: 2026-08-20

## Evidence Basis
- Locked baseline: ChatBotMSE_v2_R1_LOCKED_2026-08-17.json.
- Latest workflow checkpoint in 03_Workflows_Current: ChatBotMSE_v2_R2_TOKEN_OPTIMIZED_2026-08-18.json.
- Validated handoff subworkflow: Validated_Human_Handoff_FIXED.json.
- R1 permanent regression gate: 10/10 cases.

## Resolved Clarifications
C-001 — Published runtime identity: Google Drive exports cannot prove which n8n workflow is currently active because both main-workflow exports carry active=false. For this planning pass, R1 remains the locked behavioral baseline and the 2026-08-18 R2 token-optimized export is treated as the latest Drive checkpoint. Live n8n activation must be verified before promotion, not before static planning/candidate creation.

C-002 — Main graph delta: R1 and the R2 token-optimized checkpoint both contain 59 nodes and the same handoff graph. Only six nodes differ materially: AI Agent, Aggregate Knowledge Context, OpenAI Chat Model, OpenAI Chat Model1, Rank Relevant Knowledge, and Redis Chat Memory. No deterministic handoff/error-routing refactor exists in that R2 checkpoint.

C-003 — Current handoff invocation: Route Sales Decision sends the conversion branch to AI Agent. Submit Validated Human Handoff remains connected to AI Agent as ai_tool. The AI prompt instructs the model to call it exactly once after final confirmation and to claim success only when the tool returns success=true.

C-004 — Existing subworkflow safeguards: Validated Human Handoff contains deterministic payload validation, duplicate/session conflict checks, append-or-update by session_id, and explicit success/validation/conflict responses. However, Google Sheets lookup/write failures do not currently have structured error-return branches. Check Existing Lead Record has retryOnFail=false; Upsert Validated Human Handoff has no explicit retry/error branch.

C-005 — Scope boundary: Full removal of AI tool choice is deferred to 002-deterministic-lead-submission. The current main Redis sales_state does not persist the complete canonical handoff payload (for example parent_name, student_name, phone, email, preferred_language, last_summary, request_type). Moving the write into the deterministic main graph now would require a broader state-model redesign and would violate the smallest-safe-change rule.

C-006 — R2 implementation target: Harden the validated handoff subworkflow itself. Preserve the successful path exactly; add bounded retry and structured lookup/write failure returns. Main R1/R2 workflow routing remains unchanged in this feature.

C-007 — Retry policy: For Google Sheets lookup and append-or-update, allow one retry after the first failed attempt: maxTries=2 with a short wait. This is bounded and compatible with session_id-based append-or-update idempotency.

C-008 — Non-recoverable failure behavior: Return success=false with a stable failure status/error code. The existing AI rule remains authoritative: no success claim unless success=true. No internal stack trace, credential, sheet internals, or secret is exposed to the user.

C-009 — Notification failures: The validated handoff subworkflow does not contain notification nodes, so notification separation is not modified in this bounded feature.

## Planning Decision
Proceed with a candidate derived from Validated_Human_Handoff_FIXED.json only. Do not modify ChatBotMSE_v2_R1_LOCKED_2026-08-17.json. Do not change main AI routing in Feature 001.

## Promotion Blockers
- Verify the actual active/published n8n workflow and subworkflow IDs in the runtime environment.
- Run focused R2 runtime failure-injection tests.
- Re-run the complete permanent R1 10/10 regression set.
- Converge implementation against spec, plan, tasks, and evidence before release.
