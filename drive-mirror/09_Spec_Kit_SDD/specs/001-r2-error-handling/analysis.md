# 001 R2 Error Handling — Static Analysis

Status: Static candidate QA PASS; runtime QA pending
Date: 2026-08-20

## Main Workflow Comparison
- R1 locked main workflow: 59 nodes, active=false in export.
- Latest Drive R2 token-optimized checkpoint: 59 nodes, active=false in export.
- Node names added/removed between R1 and R2 checkpoint: none.
- Materially changed nodes: AI Agent, Aggregate Knowledge Context, OpenAI Chat Model, OpenAI Chat Model1, Rank Relevant Knowledge, Redis Chat Memory.
- Handoff graph is unchanged: Route Sales Decision conversion output still reaches AI Agent; Submit Validated Human Handoff remains an ai_tool connected to AI Agent.

## Subworkflow Baseline
Validated_Human_Handoff_FIXED.json contains 10 nodes. Existing protected flow:
When Executed by Another Workflow → Validate Lead Payload → Is Lead Payload Valid? → Check Existing Lead Record → Assess Existing Lead → Is Lead Record Safe? → Upsert Validated Human Handoff → Return Handoff Success.

Validation failure and duplicate conflict already have explicit success=false terminal responses.

## Candidate Change
Candidate: Validated_Human_Handoff_R2_ERROR_HANDLING_CANDIDATE_2026-08-20.json.
Candidate node count: 12.
Candidate activation state: active=false (required before runtime validation).

Added nodes:
- Return Lead Lookup Error.
- Return Lead Write Error.

Modified nodes only:
- Check Existing Lead Record: retryOnFail=true, maxTries=2, waitBetweenTries=1000, onError=continueErrorOutput.
- Upsert Validated Human Handoff: retryOnFail=true, maxTries=2, waitBetweenTries=1000, onError=continueErrorOutput.

Success branches remain:
- Check Existing Lead Record → Assess Existing Lead.
- Upsert Validated Human Handoff → Return Handoff Success.

New error branches:
- Check Existing Lead Record error output → Return Lead Lookup Error.
- Upsert Validated Human Handoff error output → Return Lead Write Error.

## Static QA Result
PASS — JSON parses successfully.
PASS — 12/12 node names unique.
PASS — 12/12 node IDs unique.
PASS — both new error nodes present.
PASS — lookup and write retry/error settings match the approved plan.
PASS — protected nodes unchanged: Validate Lead Payload, Is Lead Payload Valid?, Return Lead Validation Error, Assess Existing Lead, Is Lead Record Safe?, Return Lead Conflict, Return Handoff Success, and workflow trigger.
PASS — original success connections preserved.
PASS — new error-output connections present.
PASS — basic secret scan found no newly introduced OpenAI key, bearer token, password assignment, or API-key assignment.
PASS — original validated handoff source was not overwritten.

Original source SHA-256: dbad9ec0591c4e4d8560226c29e59a0dc08935a33715aa90dc11d9d0cde914f8
Candidate SHA-256: 60d99424868f42db3e164aad424370636fcef2ea3c8639b141876a06735af75f
Drive readback of candidate matched the candidate SHA-256.

## Remaining Risk / Runtime Block
Static QA cannot prove Google Sheets retry behavior, n8n error-output execution, AI handling of success=false, or row-level idempotency under transient failures. These require actual n8n execution/failure injection before release.

The current Drive exports also do not prove which main workflow is active in n8n because export active=false is present on both inspected main files. Runtime identity verification remains mandatory.

## Convergence Status
Specification: aligned.
Clarification: aligned.
Technical plan: aligned.
Candidate implementation: aligned with bounded Feature 001 scope.
Static QA: PASS.
Runtime QA: NOT RUN.
R1 regression: NOT RE-RUN.
Release eligibility: BLOCKED pending runtime QA and R1 regression.
