# WU-105 Test 10 — Refund Policy / CR-105-03 Evidence

Status: `CR-105-03 DEPLOYED / EXACT CUSTOMER RETEST PENDING`

Workflow: `[STAGING] SPM_WU105_GOLDEN_INTENTS_V1`
Workflow ID: `KXfalaYSCLdgmf4X`
Production workflow: `CMBMpxX5AqqK2UTn` — untouched/protected

## Test 10 initial result

Prompt:
`What is your refund policy?`

Observed customer output:
`We can proceed with that step, but it is only confirmed after the required system check or action succeeds.`

Result: `FAIL`

Reason:
- the customer asked for general policy information;
- the answer did not explain the refund policy;
- the response was an action-gateway fallback and therefore violated WU-105 answer-first behavior;
- the policy inquiry was effectively confused with an executed/refund-action claim.

Owner screenshot evidence supplied in chat on 2026-09-03.

## Root cause diagnosis

Two read-only STAGING diagnosis runs were used; neither wrote to n8n.

The defect is in the existing node `Validate + Guard WU92 Sales Agent Output`, not primarily in the `refund_policy` classifier route. Its irreversible-action vocabulary includes:

`booked|confirmed|saved|registered|refunded|discount approved|tutor assigned`

When a legitimate source-backed refund-policy explanation contains vocabulary such as `refunded` (and potentially `confirmed`), the validator may interpret the informational policy statement as an executed irreversible action and replace the entire answer with the generic system-check fallback.

This is a false positive in policy prose. The protection itself remains important for real refund execution claims.

## CR-105-03 design

CR-105-03 does **not** modify or weaken the existing WU92 validator. It adds one narrow deterministic post-validator guard:

`Validate + Guard WU92 Sales Agent Output -> Apply WU105 Refund Policy Answer-First Guard -> Apply WU92 Sales Agent Policy Guard`

Guard schema: `SPM_WU105_REFUND_POLICY_ANSWER_FIRST_GUARD_V1`

Recovery is allowed only when all relevant conditions are met:
- current authoritative intent is `refund_policy`;
- customer wording is a general policy-information request;
- wording is not an explicit refund execution request;
- the existing source gate says the question can be answered;
- the upstream WU92 validator actually applied its safety rewrite;
- the original generated answer exists;
- unrelated executed-action claims are absent;
- customer-specific executed-refund claims are absent.

If safe recovery is permitted, execution-like vocabulary that causes the validator false positive is neutralized into policy wording while preserving the source-backed policy explanation.

Explicit requests such as `I want a refund`, `Please refund me`, or equivalent AR/FR wording retain the original action gateway. Source-unavailable cases remain fail-closed.

No new intent, LLM/classifier, credential, external call, or business-write permission is introduced.

## Static contract evidence

Actions run: `33694278816` — `PASS`

Input CR-105-02 candidate:
- SHA-256: `7fc201137671b1cd47f9fc6b4ec60a9b563b2bae7c0776952ec68e0988bfed1e`
- nodes: `129`

CR-105-03 final candidate:
- SHA-256: `aaaa139faa67815f4196fb9779232471c4c8b051a26f0ba0a3be4c56231d4653`
- nodes: `130`

Static tests PASS:
- exactly one deterministic post-validator Code guard added;
- general refund-policy information fixtures EN/AR/FR;
- explicit refund-action fixtures preserve original gateway;
- source-unavailable fail-closed behavior;
- no-action-permission invariants;
- false-positive validator vocabulary is sanitized without deleting refund-policy meaning.

Contract evidence artifact:
- `wu105-cr10503-candidate`
- artifact ID `9871183359`

## STAGING deployment and remote readback

Actions run: `33694457544` — `PASS`

Deployment result:
- operation: `UPDATE_INACTIVE_NONPROD`
- target: `KXfalaYSCLdgmf4X`
- candidate SHA-256: `aaaa139faa67815f4196fb9779232471c4c8b051a26f0ba0a3be4c56231d4653`
- node count: `130`
- remote versionId: `464aba28-b3b9-4cdf-9bb2-378039f19683`
- `active=false`
- `published_or_activated=false`
- Production ID checked/protected: `CMBMpxX5AqqK2UTn`

Remote result: `WU105_CR10503_REMOTE_PASS`

Readback verified:
- CR-105-01 present;
- CR-105-02 present;
- CR-105-03 present;
- CR-104-04 present;
- CR-104-05 present;
- WU-102 queue remains `appendOrUpdate` with `queue_event_id`;
- STAGING Redis Chat Memory remains `={{ 'spm:staging:chat:' + $json.sessionId }}`;
- workflow remains inactive.

Deployment evidence artifact:
- `wu105-cr10503-staging-update-evidence`
- artifact ID `9871247757`

Temporary diagnosis, contract, and deployment workflows were removed after evidence was captured.

## Exact runtime gate

Retest in a **fresh chat session** with exactly:

`What is your refund policy?`

Expected:
- answer the general refund policy first;
- do not return the generic system/action-confirmation fallback;
- do not claim a customer-specific refund has been issued or approved;
- do not invent eligibility, refund amount, timing, or promise;
- at most one follow-up question, only after the general policy answer if needed.

Test 10 remains `RETEST PENDING` until owner customer-output evidence is reviewed.
