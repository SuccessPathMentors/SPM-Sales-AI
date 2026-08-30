# WU95 — Deterministic Lead Conversion QA

Status: PROTOTYPE STATIC PASS — lead write/handoff runtime adapters NOT certified
Artifact: SPM_E2E_Sales_Agent_Greenfield_WU95_Deterministic_Lead_Conversion_2026-08-20.json
SHA-256: 0d52cb2cc8b54db920743a334d5977146f008931f9f4aae575456ea96fbed9bd

## Scope
WU95 adds the deterministic lead-conversion boundary on top of WU94. It builds a canonical lead payload from durable state, validates required registration/contact fields, requires explicit consent and final confirmation, performs a read-only existing-lead lookup by session_id, decides create/update/no-change/conflict deterministically, preserves an existing lead_id on correction, and blocks success until a real write tool reports verified success.

## Safety Architecture
- Current production workflow remains untouched.
- Greenfield workflow remains active=false and import-safe with no top-level workflow ID/version ID.
- Existing-lead lookup is READ ONLY against V2 LEADS_TEMPLATE.
- The future Google Sheets appendOrUpdate node exists only as a disabled + disconnected reference node.
- There are zero active Lead/CRM/Handoff external write nodes in WU95.
- Human handoff is an explicit deterministic contract; the Greenfield handoff adapter remains NOT_CONFIGURED.
- WU95 conversion/confirmation state is persisted only to the existing test Redis namespace spm:test:sales:*.

## Lead Validation Contract
Required before lead write eligibility: valid session_id, parent_name, student_name, phone, email, country, city, IANA/approved timezone, subject, grade, supported communication language, usable summary, explicit consent_to_contact, and final confirmation.

Names are not aggressively normalized. Spreadsheet formula injection is escaped. Arabic ta marbuta is not globally rewritten. Invalid/unconfirmed values cannot reach a write adapter.

## Idempotency / Correction / Dedupe
- Idempotency key: session_id.
- 0 matching rows → CREATE candidate.
- 1 matching row + changed data → UPDATE candidate using the existing lead_id and created_at.
- 1 matching row + identical data → NO_CHANGE; no duplicate is created.
- More than 1 matching row → BLOCKED_CONFLICT / MULTIPLE_LEADS_FOR_SESSION; no new row is created.
- Multi-student requests are currently blocked from lead write with MULTI_STUDENT_LEAD_KEY_REQUIRED because LEADS_TEMPLATE does not provide a safe per-student idempotency key. This prevents accidental child-profile merging.

## Success Truth Gate
A lead is successful only when all are true: tool_executed=true, success=true, lead_id is non-empty, and the verified operation is created or updated. The Sales Agent cannot claim successful registration/submission before that evidence exists.

## Static QA
Result: 29/29 PASS.
Graph: 92 nodes; unique names/IDs; zero dangling references; zero active Lead/CRM/Handoff writes.

## Contract Regression
Result: 14/14 PASS.
Coverage includes unconfirmed lead blocking, pending-confirmation + explicit yes, invalid phone/email, spreadsheet formula injection, multi-student safety block, duplicate conflict, correction preserving lead_id, no-change dedupe, new-session create plan, false-success blocking, verified-success rule, explicit handoff boundary, and sticky opt-out override.

## R1 Outcomes Preserved as Greenfield Acceptance Criteria
- Complete confirmed lead can progress to deterministic write.
- Corrected data updates the same session/lead.
- Invalid/unconfirmed data is not written.
- Duplicate confirmation does not create a duplicate lead.
- Success is reported only after write success.

## Blocking Integration Gap
WU95 does not activate the real appendOrUpdate or human-handoff execution while upstream runtime certification remains open. The disabled reference UPSERT targets V2 LEADS_TEMPLATE and matches by session_id, ready for later controlled test authorization.

## Release Decision
Prototype/static PASS only. Production cutover unauthorized. First certification gate remains WU88 semantic runtime; downstream certification proceeds in dependency order.

## Next Unit
WU96 — nurture, follow-up, sticky opt-out, and support-over-sales overrides. It must never re-enable promotion after opt-out without an approved opt-in path.
