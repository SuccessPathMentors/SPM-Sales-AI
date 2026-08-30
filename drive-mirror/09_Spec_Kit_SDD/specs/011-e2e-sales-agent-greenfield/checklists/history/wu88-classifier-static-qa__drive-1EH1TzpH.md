# WU88 — 62-Intent Classifier Static QA

Historical Drive artifact ID: `1EH1TzpHk-40Viev-l5jmataADeZoaAtIOcmjQ-cyxXc`
Status: PASS — static/offline validation complete; semantic n8n runtime still required.
Artifact: SPM_E2E_Sales_Agent_Greenfield_WU88_62Intent_Classifier_2026-08-20.json
SHA-256: ab69c029a84f3f9b16800d4a5c10b96f46836cf713541caa532849d5582e7a32

## Scope Implemented
- Read-only loader for SPM_INTENTS_V2 with status=ACTIVE.
- Runtime catalog validation requires exactly 62 unique ACTIVE intents.
- LLM performs semantic classification only; it cannot author source_gate, risk_tier, sales_stage, threshold, or required_entities.
- Workflow deterministically enriches classification from the authoritative catalog.
- Per-intent threshold is enforced; default threshold is 0.85.
- confidence < 0.60 routes to safe fallback.
- confidence below threshold or ambiguous=true routes to clarification.
- Invalid model intent is recovered safely to out_of_scope/fallback.
- Secondary intent is accepted only when it exists in the active catalog and differs from the primary intent.
- All irreversible actions remain disabled in WU88.

## Static QA Result
37/37 checks PASS.
- 62 ACTIVE intents and 62 unique IDs/names.
- All source gates present.
- Risk tiers restricted to A/B/C.
- EN/AR/FR enabled for all catalog intents.
- Workflow active=false; no top-level workflow ID/versionId.
- 24 unique node names and 24 unique node IDs.
- No dangling graph connections.
- Google Sheets catalog lookup is read-only with bounded retry.
- No production/irreversible write nodes.
- 62/62 deterministic catalog metadata mapping simulation PASS.
- Low-confidence, ambiguity, invalid-intent, invalid-secondary and model-metadata-injection guards PASS.
- Existing 32 runtime fixture definitions are taxonomy-consistent.

## Runtime Boundary
Not executed here: semantic classification against live OpenAI + Google Sheets credentials inside n8n. This belongs to the runtime gate and must be captured after import of the inactive candidate.

## Release Decision
WU88 static gate: PASS.
Production release: NOT AUTHORIZED.
Next build unit: WU89 — Entity Extraction, Normalization & Multi-Student Model.
