# WU89 — Entity Extraction & Normalization Static QA

Status: PASS — static architecture and safety validation complete; semantic n8n runtime still required.
Artifact: SPM_E2E_Sales_Agent_Greenfield_WU89_Entities_Normalization_2026-08-20.json
SHA-256: 704c3fa78525cb4ecdcf8dac1c36b0b0c971aa4cab0c3a040819bc79523b5cf2

## Implemented
- Read-only SPM_ENTITY_SCHEMA_V2 loader; exactly 47 ACTIVE entity definitions expected.
- Read-only SPM_NORMALIZATION_V2 loader; exactly 29 ACTIVE normalization rules expected.
- Explicit-current-message entity extraction only; prior sales state is context, not a source of unstated values.
- Raw message/value preservation.
- Controlled normalization for subject, grade, country, communication language, phone/email and selected structured values.
- Arabic safety: preserves negation and does not globally replace ة with ه.
- Code-switching preserved before extraction.
- Correction detection and latest explicit customer correction metadata.
- Multiple children represented as separate student_profiles; grades/subjects/goals are not merged.
- Country alone never generates timezone.
- PII/system/live-owned fields are marked for validation rather than trusted automatically.
- Telemetry guard identifies PII entity names without copying values.
- No production writes in WU89.

## Static QA
16/16 PASS:
- workflow inactive and has no top-level workflow ID/versionId;
- 35/35 unique node names and IDs;
- zero dangling connections;
- entity schema and normalization loaders present/read-only;
- entity extraction, deterministic normalizer and safety guard present;
- Arabic integrity, timezone, multi-student, PII and correction rules present;
- zero Google Sheets/Redis/CRM write operations.

## Runtime Boundary
Entity semantic extraction against live OpenAI + Sheets credentials has not been executed in n8n yet. Runtime fixtures for EN/AR/FR, code switching, correction and multiple children belong to later certification.

## Decision
WU89 static gate: PASS.
Production release: NOT AUTHORIZED.
Next unit: WU90 — Durable Sales State & Journey Engine.
