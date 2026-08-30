# WU88 — 62-Intent Classifier QA

Status: STATIC + CONTRACT REGRESSION PASS; n8n semantic runtime pending
Artifact: SPM_E2E_Sales_Agent_Greenfield_WU88_Classifier_2026-08-20.json
SHA-256: f0546157a17028ab0c41b1ac116d242f68e7ec231d1c31262213673f8b7c893b

## Source of Truth
- Google Sheet: Success_Path_Mentors_AI_KB_V2_SPM_2026-08-18
- Tab: SPM_INTENTS_V2
- Expected ACTIVE intent count: 62
- Classifier reads ACTIVE rows only.
- Catalog fields used by routing: intent_id, spm_intent_name, category, required_entities, legacy_route_intent, legacy_next_action, risk_tier, source_gate, sales_stage, min_confidence, languages.

## Implemented Graph
1. Load SPM V2 Intent Catalog [READ ONLY]
2. Build WU88 Classifier Context
3. Is 62-Intent Catalog Ready?
4. Classify Intent — SPM 62
5. OpenAI Classifier Model [WU88 TEST]
6. Validate + Enrich WU88 Classification
7. Build Safe Classifier Fallback
8. Apply Confidence + Ambiguity Guard

## Safety Rules
- Workflow remains active=false and contains no top-level workflow id/versionId.
- Non-test sessions are blocked before classifier execution.
- Intent catalog access is read-only.
- Classifier cannot write leads, bookings, CRM, handoff, Redis state, or Google Sheets rows.
- Model selects only an intent name and confidence/language/rationale. Business metadata is enriched deterministically from SPM_INTENTS_V2.
- Per-intent min_confidence is authoritative; default is 0.85.
- confidence >= threshold -> direct.
- 0.60 <= confidence < threshold -> clarify.
- confidence < 0.60, invalid intent, malformed output, or unavailable catalog -> fallback.
- Any non-direct route sets allow_irreversible_action=false.
- Secondary intent must also exist in the 62-intent catalog and cannot equal the primary intent.

## Static QA
PASS:
- JSON parses successfully.
- 21 nodes / 21 unique node names / 21 unique node IDs.
- 0 dangling connection sources.
- 0 dangling connection targets.
- All non-model nodes are main-reachable from Greenfield Chat Trigger.
- No production write node detected.
- Google Sheets node is read-only and filters status=ACTIVE.
- No plaintext API key, bearer token, or private key detected.

## Offline Contract / Router Regression
PASS 129/129.

Coverage:
- 62/62 valid intents map deterministically to their source_gate, risk_tier, sales_stage and required_entities metadata at high confidence.
- 62/62 low-confidence cases route to clarify and block irreversible action.
- Invalid intent routes to fallback.
- Below-floor confidence routes to fallback.
- Same primary/secondary intent is rejected as duplicate secondary.
- Valid distinct secondary intent is preserved.
- out_of_scope remains a valid catalog intent when selected with sufficient confidence.

## Important Limitation
The 129/129 suite validates classifier contracts, catalog mapping, threshold logic and safety routing. It does NOT prove semantic model accuracy on real messages. That requires importing this inactive candidate into n8n and executing the runtime message regression set against the configured OpenAI credential and Google Sheets credential.

## Runtime Gate Before WU88 Certification
- Load exactly 62 ACTIVE rows from SPM_INTENTS_V2.
- Run EN/AR/FR messages covering every intent family, typos, code-switching and multi-intent cases.
- Verify confusion pairs such as pricing vs price_objection, free_trial vs trial_details, availability vs schedule_request, teacher_quality vs teacher_quality_objection, registration vs ready_to_register, need_to_think vs not_interested, and human_handoff vs complaint/support.
- Verify low-confidence paths never permit irreversible action.
- Record actual_intent, confidence, route_decision and pass/fail evidence.

Release state: SAFE INACTIVE CANDIDATE. WU89 may be prototyped against this contract, but WU88 is not production-certified until runtime semantic regression passes.

## Post-QA Fix
Synthetic test-session detection was generalized from the WU87-only prefix to `wu<digits>_`, so WU88 and later synthetic sessions enter the test-only path without requiring a separate flag. The Drive candidate was updated in place and the SHA-256 above reflects the corrected artifact.
