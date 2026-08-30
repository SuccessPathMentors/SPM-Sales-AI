# WU98 — Multilingual & Conversation Regression / Red-Team Expansion

Status: OFFLINE / STATIC REGRESSION PACK PASS — n8n semantic runtime NOT RUN  
Date: 2026-08-21  
System under test: `SPM_E2E_Sales_Agent_Greenfield_WU97_Reliability_Privacy_Security_2026-08-21.json`  
WU97 SHA-256: `9946d7de5cbcfd15feb1dcb91a5f97aec9c5ab9900794e855e5f20de092d93dc`

## Scope
WU98 expands the existing authoritative `SPM_RUNTIME_TESTS` set from RT-001..RT-032 with RT-033..RT-096.

- Existing authoritative cases: 32
- New WU98 expansion cases: 64
- Combined runtime target: 96 cases
- Combined intent coverage: 62/62 SPM V2 intents
- Expansion language distribution: EN 23, AR 21, FR 17, mixed/code-switch 3
- Expansion critical cases: 55/64

## WU98 Expansion Coverage
The expansion covers:
- all 34 intents not represented in RT-001..RT-032;
- EN/AR/FR business-outcome parity for pricing, booking truth, opt-out, and human handoff;
- Arabic dialect ambiguity;
- English/French/Arabic code-switching and typo recovery;
- multi-turn corrections for subject, grade, email, and phone;
- no-reask behavior;
- separate multi-student profiles and child-specific correction;
- long-session sticky opt-out plus support override;
- prompt-injection attempts involving booking, discount fabrication, PII extraction, and false CRM success.

## Static Suite Metadata QA
Result: 20/20 PASS.

Checks include contiguous unique IDs, valid 62-intent membership, populated source gates, 62/62 combined taxonomy coverage, language thresholds, parity-group consistency, critical-case volume, and required red-team categories.

## WU97 Deterministic Guard Regression
Result: 44/44 PASS.

Verified offline/static:
- workflow remains inactive;
- 108/108 unique node names and IDs;
- zero dangling main graph references;
- input-length and control-character safety;
- telemetry removal/redaction for session IDs, tokens, email, and phone;
- sticky opt-out;
- support-over-sales precedence;
- consent-gated follow-up;
- `need_to_think` no-auto-follow-up;
- fail-closed behavior for lead lookup, state-save, and input-security failures;
- booking and availability false-success guards;
- lead success truth gate and duplicate conflict handling;
- disabled/disconnected lead UPSERT reference;
- test-only Redis namespace;
- no unsafe global Arabic `ة→ه` normalization;
- no active production Execute Workflow / HTTP action path.

## Important Limit
WU98 does **not** certify semantic LLM behavior. The 96 cases have not been executed through the actual n8n OpenAI classifier/entity/Sales-Agent nodes. `runtime_status` remains `NOT_RUN`.

Therefore:
- WU98 design-time regression pack: PASS.
- WU98 semantic conversation runtime: PENDING.
- Production cutover: UNAUTHORIZED.

## Runtime Acceptance for WU99
For each of the 96 cases capture at minimum:
`test_id`, `actual_intent`, `secondary_intent`, `confidence`, `language`, `entities`, `source_gate`, `answer_text`, `proposed_action`, `runtime_health`, `pii_redacted`, `tool_execution_evidence`, `PASS/FAIL`.

Critical failures that block release include:
- false booking/availability/lead success;
- invented discount or unsupported teacher claim;
- lost sticky opt-out;
- support receiving sales pressure;
- PII leakage in telemetry/output;
- destructive Arabic normalization;
- merged child profiles;
- irreversible action after low-confidence/fail-closed state.

## Files
- Expansion JSON SHA-256: `25c2e96703580a60c4ee4a09c5aabac11a7bb1a795350673c02dd32737501b90`
- Expansion CSV SHA-256: `c802cad113f619dd96bcf40d610b5f0d1102a85fbe19cbfda88c9b606c051b4f`
