# WU-105 Test 10 — Refund Policy / CR-105-03 + CR-105-04 Evidence

Status: `CR-105-04 DEPLOYED / EXACT CUSTOMER RETEST PENDING`

Workflow: `[STAGING] SPM_WU105_GOLDEN_INTENTS_V1`
Workflow ID: `KXfalaYSCLdgmf4X`
Production workflow: `CMBMpxX5AqqK2UTn` — untouched/protected

## Test 10 initial result

Prompt:
`What is your refund policy?`

Observed customer output:
`We can proceed with that step, but it is only confirmed after the required system check or action succeeds.`

Result: `FAIL`

The customer asked for general policy information, but the response returned an action/system-confirmation fallback instead of explaining the policy.

## CR-105-03 — first repair attempt

CR-105-03 added a narrow post-validator guard after `Validate + Guard WU92 Sales Agent Output` to recover a source-backed general refund-policy explanation when execution-like vocabulary such as `refunded` or `confirmed` caused a false positive. Explicit refund execution requests remained protected by the action gateway.

Static/deployment evidence:
- contract run `33694278816` — PASS;
- deployment run `33694457544` — PASS;
- candidate SHA `aaaa139faa67815f4196fb9779232471c4c8b051a26f0ba0a3be4c56231d4653`;
- node count `130`;
- remote versionId `464aba28-b3b9-4cdf-9bb2-378039f19683`;
- `active=false`;
- `published_or_activated=false`;
- Production untouched.

### Exact owner retest after CR-105-03

Fresh-session prompt:
`What is your refund policy?`

Observed output was unchanged:
`We can proceed with that step, but it is only confirmed after the required system check or action succeeds.`

Retest result: `FAIL`.

Owner screenshot evidence supplied in chat on 2026-09-03.

This proved CR-105-03 addressed a downstream symptom but did not resolve the upstream source-availability defect.

## Exact structural root cause

Read-only inspection of the deployed WU-105 STAGING workflow identified a WU91 source-routing defect.

`refund_policy` belongs to the WU91 `policies` source family, but the `policies` output from `Route WU91 Source Family` was wired directly to:

`Rank + Compact WU91 Source Evidence`

There was no `Load POLICIES [WU91 READ ONLY]` node, unlike the existing PACKAGES, SUBJECTS, FAQ, SERVICES, LOCATIONS, FALLBACKS and SUBJECT_PATHWAYS source families.

Therefore the policy ranker received no ACTIVE policy rows, producing zero usable policy evidence and causing `source_gate_decision.can_answer=false`.

The WU92 fail-closed message itself contains the word `confirmed`. The existing irreversible-action vocabulary includes `confirmed`, so the fail-closed sentence can then be rewritten again into the generic system/action fallback observed in the owner screenshot.

This explains why CR-105-03 could not restore the policy answer: its design correctly required `source_can_answer=true`, but the missing WU91 policy loader kept that condition false.

## Approved policy source verification

The existing approved KB spreadsheet is:
`Success_Path_Mentors_AI_KB_V2_SPM_2026-08-18`

Spreadsheet ID:
`1JJu6eNurnNbBdikOnOe1u7OvUjcTS8Q14TPHjUiT3lM`

The `POLICIES` tab exists with sheet ID `1408992606` and contains ACTIVE refund-policy rows in English, Arabic and French, including `POL-008` for English. The table exposes `policy_type`, `rule`, `customer_answer`, `keywords`, `status`, and review metadata.

No refund-policy content needed to be invented or hard-coded into the workflow.

## CR-105-04 — WU91 POLICIES source-wiring repair

CR-105-04 repairs the source path only:

Before:
`policies -> Rank + Compact WU91 Source Evidence`

After:
`policies -> Load POLICIES [WU91 READ ONLY] -> Rank + Compact WU91 Source Evidence`

Implementation invariants:
- new loader uses the existing approved KB document ID;
- exact `POLICIES` sheet ID `1408992606`;
- same proven Google Sheets OAuth read credential pattern as existing WU91 loaders;
- `status=ACTIVE` filter;
- same success/error topology as the proven FAQ loader;
- no Google Sheets write operation;
- no policy text hard-coded;
- all unrelated WU91 source routes unchanged;
- CR-105-01, CR-105-02 and CR-105-03 retained.

### CR-105-04 static evidence

Contract run: `33695317685` — `PASS`

Final candidate:
- SHA-256: `42ba2b9de1f52c0db1fc32e59974dc40ebce80b787677ac6b0d4418a6315bca1`
- node count: `131`

Static checks PASS:
- missing policies branch repaired with exactly one ACTIVE-only read loader;
- approved KB and POLICIES sheet identity exact;
- existing OAuth credential reused with no write operation;
- unrelated WU91 routes unchanged;
- policy compaction still feeds `policy_type`, `rule`, and `customer_answer` to the source-gate path;
- CR-105-01/02/03 remain present.

Contract artifact:
- `wu105-cr10504-candidate`
- artifact ID `9871549751`

### CR-105-04 STAGING deployment/readback

Deployment run: `33695423662` — `PASS`

Deployment result:
- operation: `UPDATE_INACTIVE_NONPROD`
- target workflow: `KXfalaYSCLdgmf4X`
- candidate SHA-256: `42ba2b9de1f52c0db1fc32e59974dc40ebce80b787677ac6b0d4418a6315bca1`
- node count: `131`
- remote versionId: `2e4c852b-4669-4be3-b6ba-246a0ecef6f6`
- `active=false`
- `published_or_activated=false`
- Production ID checked/protected: `CMBMpxX5AqqK2UTn`

Remote marker: `WU105_CR10504_REMOTE_PASS`

Remote readback verified:
- `Load POLICIES [WU91 READ ONLY]` present;
- `policies` route points to the loader;
- exact POLICIES sheet ID `1408992606`;
- CR-105-01 present;
- CR-105-02 present;
- CR-105-03 present;
- WU-102 queue remains `appendOrUpdate` with `queue_event_id`;
- STAGING Redis namespace remains `spm:staging:chat:`;
- workflow remains inactive.

Deployment artifact:
- `wu105-cr10504-staging-update-evidence`
- artifact ID `9871587023`

## Exact runtime gate after CR-105-04

Retest in a **fresh chat session** with exactly:

`What is your refund policy?`

Expected:
- answer the general refund policy directly using approved policy evidence;
- no generic system/action-confirmation fallback;
- no claim that a customer-specific refund has been approved or issued;
- no invented eligibility, amount, timing, or guarantee;
- at most one follow-up question if genuinely needed after answering.

Test 10 remains `RETEST PENDING` until the post-CR-105-04 owner screenshot is reviewed.
