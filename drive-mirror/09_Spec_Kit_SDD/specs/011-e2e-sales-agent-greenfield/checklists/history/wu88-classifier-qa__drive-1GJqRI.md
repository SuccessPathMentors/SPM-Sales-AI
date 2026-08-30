# WU88 Classifier QA Gate

Historical Drive artifact ID: `1GJqRI-SW3mz9w6CiYnL1IU7lSKANvSJvszxbKalEvDc`
Candidate SHA-256: ab69c029a84f3f9b16800d4a5c10b96f46836cf713541caa532849d5582e7a32
Status: STATIC/OFFLINE PASS; LIVE SEMANTIC RUNTIME PENDING

## Passed — 37/37
- 62 ACTIVE intents present.
- 62 unique intent names and IDs.
- Every min_confidence is within 0..1.
- Every intent has a source_gate.
- All risk tiers are A/B/C.
- All 62 intents support en|ar|fr.
- Workflow active=false; no top-level id/versionId.
- 24 node names unique; 24 node IDs unique.
- No dangling connections.
- Catalog loader points to the safe V2 workbook and SPM_INTENTS_V2 sheet.
- ACTIVE-only filter present.
- Catalog read has bounded retry.
- Required semantic disambiguation rules are present in the classifier prompt.
- source_gate/risk_tier/sales_stage/threshold/required_entities are catalog-authoritative after model output.
- Invalid model intent is recovered to safe fallback.
- Invalid secondary intent is removed.
- Confidence routing implements direct / clarify / fallback.
- irreversible_action_allowed remains false.
- No Google Sheets writes, CRM writes, booking execution, handoff execution, HTTP action execution, or production write nodes are present.
- 62/62 synthetic valid-intent mappings preserve authoritative metadata.
- confidence 0.70 => clarify.
- confidence 0.50 => fallback.
- ambiguous=true at high confidence => clarify.
- invented intent => fallback/out_of_scope.
- model-supplied fake source gate cannot override PACKAGES_LIVE_CONFIG for pricing.
- 32/32 SPM_RUNTIME_TESTS fixtures are internally consistent with SPM_INTENTS_V2 expected source gate and legacy route metadata.

## Not Yet Executed
Semantic classifier accuracy has NOT been executed inside n8n. The 32 SPM_RUNTIME_TESTS rows remain the live runtime gate. This checklist must not be interpreted as production certification.

## Runtime Acceptance
- Import as inactive separate workflow.
- Use synthetic/test sessions only.
- Execute all classifier fixtures, with priority on critical=YES cases.
- Capture actual_intent, confidence, classifier_route, and result.
- Low-confidence/ambiguous cases must never authorize irreversible action.
- Any P0/P1 semantic-routing failure blocks WU88 certification.
