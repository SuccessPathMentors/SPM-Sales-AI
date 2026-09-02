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
Authoritative corrected GitHub Actions run: `33650791726`
Conclusion: `success`
Head commit: `4bf1c3d18f1bf7d2fd6588a809659e2ce5da7133`

Validated:
- Golden manifest count and uniqueness.
- Every selected intent exists in the locked Production classifier definitions.
- Every declared confusion-pair neighbor exists in the same locked classifier definitions.
- Answer-first / one-question / no-reask / WU-104 authority rules are frozen.
- Source and deterministic action gates remain authoritative.
- No WU-105 business action permission is granted.
- RC4.3.3 Production artifact SHA-256 remains exactly `680496f2b68b13dd7105e72fd132a2066d70ec969e6e0675f138ebb1fb16fe39`.

## Required WU-104 inherited upstream
WU-105 is built on the current deterministic WU-104 candidate, never directly on Production.

- WU-104 upstream artifact: `n8n/generated/SPM_WU104_STAGING_SHORT_QUERY_CANDIDATE.json`
- WU-104 upstream SHA-256: `d0c2ad10c3455b435868a8b7d4c874d31d27ae35e64844d62713d1a5ba74e45f`
- WU-104 upstream node count: `124`
- Required inherited controls:
  - `Build WU104 Short Query Decision`
  - `Persist WU104 Awaited Context Hint`
  - `Apply WU104 Clarification Response Override`

The WU-105 builder hard-fails if this exact upstream SHA or these WU-104 controls are absent.

## Deterministic WU-105 STAGING candidate
Candidate name: `[STAGING] SPM_WU105_GOLDEN_INTENTS_V1`
Generated artifact: `n8n/generated/SPM_WU105_STAGING_GOLDEN_INTENTS_CANDIDATE.json`
Candidate SHA-256: `43ac3b2be6ae51b99b16f4e3166e0c9e0e055ccbc0b67d48871346d594415eed`
Node count: `125`
CI artifact ID: `9854666311`

Candidate delta is intentionally narrow:
- inherits all 124 current WU-104 nodes unchanged as parsed JSON;
- adds exactly one deterministic Code node: `Apply WU105 Golden Intent Prompt Overlay`;
- interposes only `Build WU96-Aware Sales Agent Prompt -> WU105 overlay -> Generate WU92 Sales Agent Response`;
- all unrelated WU-104 connections remain unchanged;
- no additional LLM/classifier model is introduced;
- no credentials or external execution node is added;
- candidate remains inactive and non-production.

## Superseded offline artifact
The earlier WU-105 candidate SHA `1375a5045b0d30641dfac4885b7c833aa1188e025da41b6babd0227caa485838` / 115 nodes was generated directly from Production before the dependency inheritance correction. It is superseded and MUST NOT be deployed or used as WU-105 certification evidence.

## Dependency / release gate
Do not certify WU-105 as complete until WU-104 is formally reconciled in GitHub. At the time of this evidence record:
- `work-units/WU-104.lock.md` does not exist on `main`;
- `evidence/wu104/runtime-matrix-coverage.md` still records `Status: IN_PROGRESS` and remaining live integration representatives.

The owner has performed additional manual WU-104 clarification-response checks, but WU-105 must not silently treat missing GitHub lock/evidence as completed runtime certification. Offline WU-105 implementation may continue; final STAGING runtime certification remains gated pending explicit WU-104 reconciliation or approved dependency waiver.

Production remains untouched.
