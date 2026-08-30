# 001 R2 Error Handling — Tasks

Status: Candidate implementation in progress
Date: 2026-08-20

## Specification and Analysis
- [x] R2-T001 Compare R1 locked main workflow with latest Drive main-workflow checkpoint.
- [x] R2-T002 Confirm the final handoff remains AI-tool-mediated in the main graph.
- [x] R2-T003 Inspect Validated_Human_Handoff_FIXED.json and map validation, duplicate, lookup, write, and success paths.
- [x] R2-T004 Resolve clarification scope and defer full deterministic submission to Feature 002.
- [x] R2-T005 Produce bounded technical plan.

## Candidate Implementation
- [x] R2-T006 Create a new versioned candidate from Validated_Human_Handoff_FIXED.json; never overwrite the source.
- [x] R2-T007 Enable bounded retry on Check Existing Lead Record: maxTries=2, waitBetweenTries=1000 ms.
- [x] R2-T008 Add explicit lookup error output and Return Lead Lookup Error with success=false/status=lookup_failed/error_code=LEAD_LOOKUP_FAILED.
- [x] R2-T009 Enable bounded retry on Upsert Validated Human Handoff: maxTries=2, waitBetweenTries=1000 ms.
- [x] R2-T010 Add explicit write error output and Return Lead Write Error with success=false/status=write_failed/error_code=LEAD_UPSERT_FAILED.
- [x] R2-T011 Preserve all existing validation, duplicate conflict, appendOrUpdate(session_id), and success outputs unchanged.
- [x] R2-T012 Keep the R1 locked main workflow and R2 token-optimized main checkpoint unchanged.

## Static QA
- [x] R2-T013 Validate candidate JSON syntax.
- [x] R2-T014 Verify unique node IDs and names.
- [x] R2-T015 Verify success paths are unchanged and both new error branches are connected.
- [x] R2-T016 Verify retry/error settings exist only on the two in-scope Google Sheets operations.
- [x] R2-T017 Scan candidate for newly introduced secrets/credentials/private tokens.
- [x] R2-T018 Produce analysis/static-QA evidence.

## Runtime QA — Blocked Until n8n Runtime Access
- [ ] R2-T019 Verify exact active main workflow and validated handoff subworkflow IDs in n8n.
- [ ] R2-T020 Import/attach the candidate without replacing the current working subworkflow.
- [ ] R2-T021 Run successful new-lead and same-session update cases.
- [ ] R2-T022 Force lookup failure and verify structured lookup_failed result with no success claim.
- [ ] R2-T023 Force write failure and verify structured write_failed result with no success claim.
- [ ] R2-T024 Test transient lookup retry recovery.
- [ ] R2-T025 Test transient write retry recovery and verify no duplicate row.
- [ ] R2-T026 Re-run validation and duplicate-conflict cases.
- [ ] R2-T027 Confirm no internal errors/secrets are exposed in user-facing output.

## Regression and Release
- [ ] R2-T028 Run all permanent R1 regression cases 1–10.
- [ ] R2-T029 Record execution IDs, timestamps, session IDs, expected/actual route, row references, and PASS/FAIL evidence.
- [ ] R2-T030 Run convergence review against spec.md, clarify.md, plan.md, tasks.md, and runtime evidence.
- [ ] R2-T031 Resolve all P0/P1 gaps.
- [ ] R2-T032 Update PROJECT_STATE.md and CHANGELOG.md.
- [ ] R2-T033 Promote only after owner/engineering release gate passes; otherwise retain current runtime and archive the failed candidate.

## Definition of Done
Feature 001 is complete only when the candidate has passed static QA, focused R2 runtime failure tests, all 10 locked R1 regressions, convergence, and release approval. Static QA alone is not production certification.
