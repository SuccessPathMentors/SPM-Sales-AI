# WU96 — Nurture / Opt-Out / Support Overrides QA

Status: PROTOTYPE STATIC PASS — runtime communication adapters NOT configured
Artifact: SPM_E2E_Sales_Agent_Greenfield_WU96_Nurture_OptOut_Support_Overrides_2026-08-20.json
SHA-256: 086fab4218b3aefcbfb571c6f334cd6a134162a8db836f795d7107454d00731e

## Scope
WU96 adds deterministic communication precedence after WU95: nurture/follow-up eligibility, sticky opt-out, and support-over-sales behavior.

## Precedence
1. Current support intent is served first even if the customer is already opted out.
2. Opt-out remains sticky and blocks promotional sales/nurture after support handling.
3. `not_interested` immediately sets opt_out=true.
4. `follow_up` requires explicit/valid consent_to_contact and no opt-out.
5. `need_to_think` never creates an automatic follow-up.
6. Normal sales continues only when no higher-priority communication override applies.

## Support Intents
human_handoff, complaint, technical_issue, account_login, update_contact_info, payment_problem, change_teacher.

All support modes suppress sales CTA, do not restart qualification, preserve known state, and create only a deterministic pending handoff contract. The human-handoff adapter remains NOT_CONFIGURED in this prototype.

## Nurture Controls
- SALES_NURTURE is read-only and ACTIVE-filtered.
- No automatic nurture scheduling is enabled.
- External follow-up is never claimed as scheduled without deterministic tool evidence.
- Sticky opt-out is not automatically cleared; explicit approved opt-in logic is deferred to a future certified control.

## Static QA
Result: 32/32 PASS.
- JSON valid, active=false, no top-level workflow identity.
- 100 nodes, unique names/IDs, zero dangling references.
- WU96 resolver/switch/context/guard nodes present.
- SALES_NURTURE source is read-only and ACTIVE-filtered.
- No new production Sheets/HTTP/Execute Workflow write nodes.
- Existing WU95 lead UPSERT remains disabled/disconnected reference only.
- Gateway remains NOOP_WU96 for irreversible actions.

## Contract Regression
Result: 15/15 PASS.
Covered: not_interested, sticky opt-out blocking follow-up, support overriding opt-out for the current request, complaint, technical issue, login, contact update, payment problem, tutor change, need_to_think no auto follow-up, follow_up with/without consent, normal sales flow, and sticky opt-out blocking later sales.

## Release Decision
Prototype/static PASS only. Runtime certification remains dependency-gated from WU88 forward. Production cutover is unauthorized.

## Next Unit
WU97 — reliability, retries, observability, privacy, and security controls across the full Greenfield stack. WU97 should harden failure handling without enabling production writes.
