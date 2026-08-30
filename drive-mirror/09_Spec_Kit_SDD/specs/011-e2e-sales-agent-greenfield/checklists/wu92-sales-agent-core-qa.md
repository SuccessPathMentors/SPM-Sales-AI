# WU92 — Consultative Sales Agent Core QA

Status: PROTOTYPE IMPLEMENTATION COMPLETE — STATIC QA PASS; runtime certification pending.
Candidate: `SPM_E2E_Sales_Agent_Greenfield_WU92_Consultative_Sales_Agent_Core_2026-08-20.json`
SHA-256: `8c9c1c5601b1bb0cde36f8dd5ed51ecbd22bc13648cf5dc299ebec722dbea2c6`

## Product Behavior
- AI role is a consultative Sales Agent, not an FAQ bot.
- WU91 approved evidence is the factual boundary for stable claims.
- The Sales Playbook provides conversation objective/next-best-action structure.
- Intake questions are used only when one missing field genuinely advances the journey.
- The agent may propose an action but cannot execute or confirm irreversible business operations.

## Safety Controls
- Claims source refs are restricted to WU91 approved source refs.
- When `source_gate_decision.can_answer=false`, deterministic safe wording replaces unsupported factual output.
- Availability, booking, payment status, refund remedy, discount authorization, CRM write, and tutor assignment cannot be confirmed by the model.
- `POLICY_AND_LIVE_STATE` is limited to general-policy explanation before live/team verification.
- `VERIFIED_TEACHER_OR_POLICY` cannot invent a specific tutor's credentials, origin, gender availability, or schedule.
- Sticky opt-out is enforced; explicit human_handoff is preserved.
- One purposeful question maximum and no re-asking known state fields.

## Data-Governance Conflict Isolation
ACTIVE RESPONSE_RULES RULE-015 and RULE-017 contain fact-bearing location/currency logic that conflicts with the current PACKAGES/source-gate configuration. WU92 does not alter those rows, but excludes them from the model prompt so they cannot override WU91 approved factual evidence. This conflict should be reconciled in knowledge governance before production certification.

## Static QA
19/19 PASS:
- 62 nodes; all names/IDs unique; zero dangling references;
- active=false, no workflow identity reuse;
- no production write/execute-workflow/http action introduced;
- read-only Sales Playbook, RESPONSE_RULES, and INTAKE_QUESTIONS loaders;
- dedicated Sales Agent model and structured-output chain;
- claims_source_refs subset enforcement;
- false-success rewrite guard;
- opt-out and handoff enforcement;
- one-question policy;
- FAQ explicitly remains supporting knowledge rather than primary agent identity;
- deterministic action gateway remains NO WRITES.

## Runtime Gate
Not run. Certification requires upstream WU88→WU91 runtime gates, then multilingual sales scenarios covering grounded answer-first behavior, objection handling, missing-source behavior, source-ref correctness, opt-out, handoff, no-repeat state, and false-success protection.
