# WU-105 Contract, Candidate + First STAGING Evidence

Status: PASS_RECONCILED / PASS_INACTIVE_STAGING_CREATE_READBACK / RUNTIME_MATRIX_PENDING
Issue: #60
PR: #61

## V1 Golden Intent manifest
Frozen count: 13 existing intents from the authoritative `SPM_V2_62_INTENTS` classifier taxonomy:
`subject_inquiry`, `pricing`, `package_comparison`, `price_objection`, `free_trial`, `trial_details`, `teacher_quality`, `availability`, `schedule_request`, `registration`, `ready_to_register`, `human_handoff`, `refund_policy`.

WU-105 does not add, remove, rename, or reclassify taxonomy entries.

## Formal upstream dependency reconciliation
WU-104 is formally LOCKED on `main` via `work-units/WU-104.lock.md` and Owner approval.

Exact inherited WU-104 identity:
- final CR: `CR-104-05`
- locked artifact source: Actions run `33663124381`, artifact `wu104-cr10405-evidence`
- locked WU-104 SHA-256: `32721cae2b09531d8f4860373c37911ace9e95b6818babdca880fa08ef1b7bc9`
- node count: `126`
- inactive WU-104 STAGING workflow: `Bt3PvOIbFzU0O9gk`

WU-105 consumes the exact locked artifact; it does not rebuild or infer WU-104 from an older intermediate candidate.

Inherited controls explicitly verified include:
- `Build WU104 Short Query Decision`
- `Apply WU104 Short Trial Inquiry Guard`
- `Persist WU104 Awaited Context Hint`
- `Persist WU104 Final Asked Field`
- `Apply WU104 Clarification Response Override`
- CR-104-04 signature `SPM_WU104_KNOWN_SLOT_RECONCILE_V1`
- CR-104-05 signature `SPM_WU104_SHORT_SEMANTIC_GUARD_V1`

## Reconciled deterministic WU-105 candidate
Candidate name: `[STAGING] SPM_WU105_GOLDEN_INTENTS_V1`
Candidate SHA-256: `f02ab822c37e8cad6b45f83934361bc2388e540070b2c38b15ce631f93f6171c`
Node count: `127`

Candidate delta remains intentionally narrow:
- preserves all 126 locked WU-104 nodes;
- preserves locked WU-104 controls/topology except the planned WU-105 response-prompt interposition;
- adds exactly one deterministic Code node: `Apply WU105 Golden Intent Prompt Overlay`;
- interposes only `Build WU96-Aware Sales Agent Prompt -> WU105 overlay -> Generate WU92 Sales Agent Response`;
- adds no LLM/classifier/agent node;
- adds no credential or external execution node;
- grants no business-action permission;
- remains inactive/non-production.

## Runtime matrix
`contracts/WU105_RUNTIME_MATRIX_V1.json` is bound to candidate SHA `f02ab822c37e8cad6b45f83934361bc2388e540070b2c38b15ce631f93f6171c`.

Coverage:
- 13 Golden Intents;
- 39 EN/AR/FR direct prompts;
- 104 planned runtime scenarios total;
- answer-first;
- no-reask trusted context;
- stale-context override;
- WU-104 compatibility;
- nearest confusion-pair behavior;
- source-unavailable / no-invention behavior.

## Reconciled CI / dry-run evidence
Representative validation proved:
- locked WU-104 SHA exact;
- WU-104 node count 126;
- WU-105 candidate SHA `f02ab822c37e8cad6b45f83934361bc2388e540070b2c38b15ce631f93f6171c`;
- WU-105 node count 127;
- all 126 WU-104 nodes preserved;
- CR-104-04/05 signatures inherited;
- exactly one deterministic overlay added;
- deployer `PASS_DRY_RUN` with operation `NONE`;
- `published_or_activated=false`;
- Production workflow `CMBMpxX5AqqK2UTn` protected.

Matrix-binding commit `2d257d64876dcb1fc8fb57d5cb47f53ca649ab4a` passed contract/staging/repository guards.

## First STAGING deployment attempt — safe pre-write failure
Run `33667092500` attempted an exact-name workflow LIST before any apply. The n8n API key returned HTTP 403 for LIST access.

Assessment:
- candidate/build/tests had already PASSed;
- failure occurred before `deploy_nonprod.py --mode apply`;
- apply/readback steps were skipped;
- no WU-105 n8n write occurred;
- retained only as fail-closed evidence.

## First successful WU-105 STAGING create/readback — PASS
Controlled create-only retry run: `33667744959`.

Deployment result:
- status: `PASS_APPLY`
- operation: `CREATE_INACTIVE_NONPROD`
- target workflow ID: `KXfalaYSCLdgmf4X`
- remote name: `[STAGING] SPM_WU105_GOLDEN_INTENTS_V1`
- remote versionId: `d3f02c13-c68c-4a34-bf6e-8de1ec700bd9`
- candidate SHA: `f02ab822c37e8cad6b45f83934361bc2388e540070b2c38b15ce631f93f6171c`
- node count: `127`
- `remote_active_after=false`
- `published_or_activated=false`
- Production workflow ID protected: `CMBMpxX5AqqK2UTn`

Remote readback result: `WU105_REMOTE_READBACK_PASS`.

Remote verifier confirmed:
- all final WU-104 nodes present;
- CR-104-04 signature true;
- CR-104-05 signature true;
- WU-105 overlay present;
- WU-102 unanswered queue operation remains `appendOrUpdate`;
- WU-102 matching key remains `queue_event_id`;
- Redis Chat Memory remains STAGING-isolated with `spm:staging:chat:` session prefix;
- workflow remains inactive.

Evidence artifact:
- name: `wu105-one-time-staging-deployment-evidence`
- artifact ID: `9861234029`
- ZIP SHA-256: `54528de4c68f0fbaab9f77c41128d88252da94ffa66a32d072d7ac9b1e633740`

## Superseded artifacts
Historical artifacts that MUST NOT be deployed:
- 115-node candidate SHA `1375a5045b0d30641dfac4885b7c833aa1188e025da41b6babd0227caa485838` built directly from Production;
- 125-node candidate SHA `43ac3b2be6ae51b99b16f4e3166e0c9e0e055ccbc0b67d48871346d594415eed` built on a pre-final WU-104 intermediate candidate.

## Current gate
Formal WU-104 reconciliation and first inactive WU-105 STAGING create/readback are complete.

**Next gate: runtime Golden Intent certification on STAGING workflow `KXfalaYSCLdgmf4X`.**

Runtime certification must prove representative answer-first/no-reask/current-intent/source-safety behavior, WU-104 compatibility, multilingual parity, confusion-pair separation, and protected non-Golden regressions before material review.

Production remains untouched.
