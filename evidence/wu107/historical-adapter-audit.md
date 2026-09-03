# WU-107 — Historical Human Handoff Adapter Audit

Status: AUDITED — DO NOT RECONNECT DIRECTLY
Source: `drive-mirror/03_Workflows_Current/Validated_Human_Handoff_FIXED.json`
Historical workflow name: `Validated Human Handoff`
Historical versionId: `4c774d85-54cc-4ace-b2aa-7b09a03fb3f6`
Historical exported active flag: `true`

## Executive decision
The historical adapter must **not** be reconnected directly to the locked WU-106 conversation workflow.

Useful validation/sanitization ideas may be reused, but WU-107 requires a new bounded handoff-queue execution layer with explicit `REQUESTED / QUEUED / ACCEPTED / FAILED / CANCELLED` truth states, provider evidence, pseudonymous session identity, idempotency, and retry/failure controls.

WU-108 remains responsible for staff WhatsApp notification. WU-107 must not treat a queue record or CRM/Sheets write as proof that a human received the case.

## What the historical workflow actually does
The workflow is invoked through `When Executed by Another Workflow` and expects a large payload including:
- raw `session_id`;
- parent and student full names;
- phone and email;
- country, city, timezone;
- subject and grade;
- preferred language;
- consent and final confirmation;
- last summary;
- request type and confirmation phrase.

It validates and sanitizes these fields, including spreadsheet-formula injection protection, then checks/updates a lead record in the Google Sheet workbook `Success_Path_Mentors_-_AI_Knowledge_Base_UPDATED`, sheet `LEADS_TEMPLATE`.

The final write node is `Upsert Validated Human Handoff`, using `appendOrUpdate` with `session_id` as the matching column.

After the Google Sheets upsert, `Return Handoff Success` returns `success: true` and customer-facing messages equivalent to:
- `Your request was recorded successfully and sent to the Success Path Mentors team.`
- or the corresponding update wording.

No downstream staff notification or human-acceptance node exists in the historical workflow.

## Positive controls worth reusing conceptually
1. Strong field validation functions.
2. Phone/email/timezone validation.
3. Spreadsheet formula-injection protection.
4. Explicit consent/final-confirmation checks for workflows that actually require contact authorization.
5. Read-before-write conflict handling.
6. EN/AR/FR validation/result messages.

These are reference patterns only; they do not make the historical workflow suitable as WU-107 V1 execution truth.

## Blocking gaps against the WU-107 contract

### 1. Queue receipt is conflated with team receipt
A successful Google Sheets upsert is rendered as `sent to the team`. The workflow has no evidence that a staff member or notification channel received, opened, or accepted the request.

WU-107 requires:
- durable queue write => at most `QUEUED`;
- human acceptance => `ACCEPTED` only with authoritative acceptance evidence.

### 2. CRM lead storage is conflated with handoff queue storage
The adapter writes to `LEADS_TEMPLATE`, while the WU-107 contract requires a dedicated handoff execution record. Lead/CRM truth and handoff execution truth must remain distinct.

### 3. Excessive default PII collection
The historical adapter requires parent name, student name, phone, email, country, city, timezone, subject, grade, and last summary before submission.

WU-107 requires minimum necessary operational context. An explicit request such as `I want to speak with a person` must not require a full registration form merely to create a support queue record.

### 4. Raw session identity
The historical adapter uses and persists raw `session_id`. WU-107 should reuse the existing WU-101/WU-102 pseudonymous conversation key (`sales_state.analytics.session_key`) for queue identity where possible.

### 5. No explicit idempotency key
The historical `appendOrUpdate` matches on `session_id`, which gives limited dedupe behavior but is not an explicit logical handoff idempotency contract. It cannot safely express multiple logical handoff cycles or deterministic retry semantics.

### 6. No bounded retry semantics
The Google Sheets nodes have no WU-107 retry-class contract distinguishing transient from permanent failure. WU-107 requires bounded retry/fail-closed execution truth.

### 7. No explicit truth-state machine
The historical workflow does not represent `REQUESTED`, `QUEUED`, `ACCEPTED`, `FAILED`, or `CANCELLED` as distinct execution states.

### 8. Full confirmation requirement is too broad for support queue creation
The workflow requires `consent_to_contact`, `confirmed`, and a final confirmation phrase for every request. Contact consent remains important when a callback/contact action is required, but it must not prevent preservation/queuing of a technical-support or complaint request that does not yet require exposing contact data.

### 9. Historical active flag
The exported workflow has `active: true`. The current production workflow does not call it. WU-107 must not reconnect or mutate this historical workflow directly; any implementation begins as a new isolated inactive STAGING path.

## WU-107 target adapter decision
Use a new provider-neutral queue contract backed initially by the already-certified STAGING Redis dependency.

### STAGING queue identity
- namespace: `spm:staging:handoff:`
- session identity: existing pseudonymous `sales_state.analytics.session_key`
- raw chat session ID is not persisted in the WU-107 queue record.

### Queue truth
A successful durable Redis queue write may produce `QUEUED` because tool evidence proves the request was durably accepted into the WU-107 queue.

It does **not** prove `ACCEPTED` by a human.

### WU-108 boundary
WU-108 will consume approved WU-107 queue records and implement staff WhatsApp notification. Notification success and human acceptance remain separate future evidence states.

## Reusable historical elements
Only bounded utility concepts may be ported after review:
- clean/canonical text helpers;
- contact validation if/when callback data is legitimately needed;
- formula-injection protection for any future spreadsheet sink;
- conflict-safe write principles.

The original workflow itself is not a WU-107 deployment artifact.

## Audit verdict
`HISTORICAL_ADAPTER_DIRECT_REUSE = BLOCKED`

`VALIDATION_PATTERN_REUSE = ALLOWED_WITH_REVIEW`

`WU107_NEW_ISOLATED_STAGING_QUEUE = REQUIRED`
