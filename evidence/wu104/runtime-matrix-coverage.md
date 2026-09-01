# WU-104 Runtime Matrix Coverage

Status: IN_PROGRESS
Issue: #48

## Canonical STAGING identity
- n8n workflow ID: `Bt3PvOIbFzU0O9gk`
- name: `[STAGING] SPM WU104 Short Query + Ambiguity UX Candidate`
- active: `false`
- locked candidate SHA-256: `af403c1f57bbf7a2532a6dc262f4d6de70bf473359f22c07ccfc5f72695dda88`
- node count: 123
- WU-104 nodes: `Build WU104 Short Query Decision`, `Apply WU104 Clarification Response Override`

## Completed live runtime representatives
1. Fresh short semantic `price?` -> direct authorized pricing response; no clarification. PASS.
2. Fresh bare subject fragment `Math` -> exactly one concise clarification; no invented action. PASS.

## Deterministic executable coverage already in CI
`scripts/wu104/test_core.py` covers:
- clear short EN/AR/FR semantic requests remain direct;
- fresh bare subject requires clarification;
- awaiting subject + `Math` -> deterministic binding;
- fresh grade clarifies; awaiting grade binds;
- fresh day/time clarifies; awaited scheduling day/time binds;
- awaited city/location binds;
- fresh yes/no is unsafe; locked registration confirmation guard permits contextual binding without granting irreversible permission;
- unknown awaiting field is rejected from fuzzy binding;
- explicit `price?` overrides stale awaited grade;
- current correction overrides prior slot context;
- support intent overrides stale commercial context;
- long-form direct intent remains direct;
- classifier ambiguity/below-threshold remains observable and safe;
- clarification attempts 1 and 2 are one-question turns; third unresolved same-key turn produces safe fallback/human-help and resets loop;
- language change does not create an unlimited new ambiguity key;
- direct resolution resets clarification state;
- EN/AR/FR clarification text parity.

## Remaining material live runtime representatives
To avoid redundant manual testing, final live certification should prove only the integration points not fully demonstrated by pure core tests:
1. Context-bound fragment through persisted n8n state: establish exactly one awaited subject, then `Math` must not repeat the fresh-session ambiguity question.
2. Current-message precedence through persisted stale state: while a different field is awaited, send a clear semantic request (`price?`) or correction; current meaning must win.
3. Clarification loop persistence across actual Redis-backed turns: unresolved same ambiguity reaches attempt cap and does not ask a third repeated question.
4. One non-English live ambiguity/context representative (AR or FR) to confirm customer-facing language override integration.

Production workflow and locked WU101/WU102/WU103 workflow IDs remain denied and untouched.
