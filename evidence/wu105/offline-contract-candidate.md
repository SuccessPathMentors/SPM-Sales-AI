# WU-105 Offline Contract + Candidate Evidence

Status: PASS_OFFLINE / STAGING_RUNTIME_PENDING
Issue: #60
PR: #61

## V1 Golden Intent manifest
Frozen count: 13 existing intents from the locked `SPM_V2_62_INTENTS` classifier taxonomy.

1. `subject_inquiry`
2. `pricing`
3. `package_comparison`
4. `price_objection`
5. `free_trial`
6. `trial_details`
7. `teacher_quality`
8. `availability`
9. `schedule_request`
10. `registration`
11. `ready_to_register`
12. `human_handoff`
13. `refund_policy`

Selection is bounded to high business value, conversion entry, confusion risk, source/action risk, and support resolution. WU-105 does not change, add, remove, or rename any intent.

## Contract / baseline validation
GitHub Actions run: `33650276104`
Conclusion: `success`

Validated:
- Golden manifest count and uniqueness.
- Every selected intent exists in the locked Production classifier definitions.
- Every declared confusion-pair neighbor exists in the same locked classifier definitions.
- Answer-first / one-question / no-reask / WU-104 authority rules are frozen.
- Source and deterministic action gates remain authoritative.
- No WU-105 business action permission is granted.
- RC4.3.3 Production artifact SHA-256 remains exactly `680496f2b68b13dd7105e72fd132a2066d70ec969e6e0675f138ebb1fb16fe39`.

## Deterministic STAGING candidate
Candidate name: `[STAGING] SPM_WU105_GOLDEN_INTENTS_V1`
Generated artifact: `n8n/generated/SPM_WU105_STAGING_GOLDEN_INTENTS_CANDIDATE.json`
Candidate SHA-256: `1375a5045b0d30641dfac4885b7c833aa1188e025da41b6babd0227caa485838`
Node count: `115`
CI artifact ID: `9854466059`

Candidate delta is intentionally narrow:
- adds exactly one deterministic Code node: `Apply WU105 Golden Intent Prompt Overlay`;
- interposes only `Build WU96-Aware Sales Agent Prompt -> WU105 overlay -> Generate WU92 Sales Agent Response`;
- all pre-existing baseline nodes remain parsed-JSON equivalent;
- all unrelated connections remain unchanged;
- no additional LLM/classifier model is introduced;
- no credentials or external execution node is added;
- candidate remains inactive and non-production.

## Dependency / release gate
Do not deploy or certify WU-105 as complete until WU-104 is formally reconciled in GitHub. At the time of this evidence record:
- `work-units/WU-104.lock.md` does not exist on `main`;
- `evidence/wu104/runtime-matrix-coverage.md` still records `Status: IN_PROGRESS` and remaining live integration representatives.

The owner has performed additional manual WU-104 clarification-response checks outside the repository, but WU-105 must not silently treat missing GitHub lock/evidence as completed runtime certification. Offline WU-105 work may continue; STAGING runtime certification remains gated pending explicit WU-104 reconciliation or approved dependency waiver.

Production remains untouched.
