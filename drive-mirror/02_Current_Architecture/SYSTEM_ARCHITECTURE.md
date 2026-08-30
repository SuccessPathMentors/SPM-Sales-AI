# Current System Architecture

Last updated: 2026-08-17.

## Runtime flow

1. Website sends chat input, session ID, locale, and page metadata to n8n.
2. Guard nodes protect greetings, confirmations, corrections, summaries, and contextual replies.
3. Intent/NLP extracts language, intent, entities, sales stage, and next action.
4. Redis manages short-lived conversation and sales state.
5. Domain routing loads relevant ACTIVE knowledge.
6. Retrieval normalizes, ranks, and aggregates verified context.
7. Decision logic selects knowledge, consultative sales, unanswered, or handoff behavior.
8. AI Agent composes the user-facing response under system constraints.
9. Unanswered questions are deduplicated and sent for review.
10. Validated confirmed handoffs write/update `LEADS_TEMPLATE` using the same session key.
11. Final response exposes only approved user-facing text.

## Ownership boundaries

| Component | Owns | Must not own |
|---|---|---|
| Website | UI, stable session identifier, transport | Facts or lead validation |
| Main workflow | Routing, context, decisions, dialogue state | Conflicting lead writers |
| Handoff workflow | Final validation and lead upsert | General conversation |
| Google Sheets | Approved knowledge and operational records | Secrets or runtime memory |
| Redis | Temporary conversation/sales state | Durable business truth |
| OpenAI model | Understanding and response wording | Invented facts or unverified success |

## Locked R1 invariant

A submission/update success response is valid only after the confirmed data is successfully written. Corrections use the same session record, and operational lead messages never enter unanswered-question logging.

## Next architecture work

R2 adds bounded retries, timeouts, idempotent error behavior, and safe multilingual failures. R1 behavior remains frozen and covered by permanent regression tests.
