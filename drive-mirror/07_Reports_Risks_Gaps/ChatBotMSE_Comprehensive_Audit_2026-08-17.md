# ChatBotMSE — Comprehensive Workflow Audit

Date: 2026-08-17  
Source reviewed: `ChatBotMSE copy.json`  
Scope: architecture, routing, knowledge grounding, Intent/NLP, sales state, Redis memory, unanswered questions, lead handoff, reliability, security, performance, and maintainability.

## Executive conclusion

The workflow is functionally mature and its core architecture is sound. It includes multilingual conversation handling, structured intent classification, deterministic knowledge routing, lexical knowledge ranking, Redis-backed sales state, consultative sales logic, unanswered-question governance, and consent-based human handoff.

The next step should not be another large feature. The correct next step is a controlled hardening and refactoring release based on the tested workflow. Freeze the current workflow as the acceptance baseline, duplicate it, and implement the urgent fixes below in the duplicate.

Production readiness cannot be formally approved from the JSON alone because the completed Stage 10 results workbook was not included with this audit.

## Static-analysis summary

- Total nodes: 63
- Nodes reachable through the main execution graph: 52
- Code nodes: 18
- Total JavaScript in Code nodes: about 82,097 characters
- Largest Code node: `Determine Next Best Action` at about 26,739 characters / 1,255 lines
- Main execution graph: acyclic
- Disabled nodes: 1
- Structurally disconnected or unreachable operational nodes: 4
- Workflow groups: 0
- Workflow tags: 0
- The exported copy is inactive, as expected for a testing copy
- No error workflow is referenced in the exported workflow settings

## What is already strong

1. The chat trigger validates real message events before processing.
2. Greetings, thanks, and goodbyes bypass the costly AI/knowledge pipeline.
3. Intent classification uses a structured output parser and a controlled intent catalog.
4. The workflow validates intent names, confidence, language, entities, sales stage, and sentiment after the model responds.
5. Sales state is stored independently from chat memory in Redis.
6. Knowledge routing loads only the selected domain and ACTIVE language records.
7. Knowledge records are normalized, ranked, limited, and then supplied as bounded context.
8. Unknown questions follow a dedicated logging and deduplication path.
9. Prices are produced through deterministic code rather than free-form model generation.
10. Objection handling and short contextual answers preserve the sales journey.
11. OpenAI models use temperature 0, timeout, and retry settings.
12. The public chat trigger has an origin restriction for the website.

## Urgent findings — fix before the next production release

### P0-1 — Two AI-accessible lead-writing tools

`Save Qualified Lead` and `Create or Update Human Handoff` can both write to the lead sheet. Preventing duplicate or incomplete writes currently depends mainly on prompt instructions. `Save Qualified Lead` can append a row even when consent is NO and mandatory data is incomplete.

Action:

- Disable and then remove `Save Qualified Lead` after regression testing.
- Keep one authoritative upsert path only.
- Add a deterministic validation node before the write that verifies every mandatory field, valid email, explicit consent, confirmation, and session-level idempotency.
- Do not allow the language model to decide whether an invalid payload may be written.

### P0-2 — Incorrect field name in `Prepare AI Context`

The assignment name is `=knowledge_domain` instead of `knowledge_domain`. The AI Agent system message reads `$json.knowledge_domain`, so the selected domain may be unavailable to the prompt even when the context is otherwise correct.

Action:

- Rename `=knowledge_domain` to `knowledge_domain`.
- Store `knowledge_found` as Boolean, not String.
- Store `knowledge_count` as Number, not String.

### P0-3 — Pricing Redis state is inconsistent

`Save Pricing Sales State` uses the key expression `= {{ $json.sales_state_key }}` instead of the consistent `={{ $json.sales_state_key }}`. It also has no expiration, while the normal sales state expires after 30 days.

Action:

- Correct the key expression.
- Add the same 30-day TTL or adopt one documented retention policy for all sales-state writes.
- Add retry/error handling to Redis reads and writes.

### P0-4 — Error workflow is not attached in the export

The workflow settings do not contain an `errorWorkflow` reference, although a separate workflow-error alert was created previously.

Action:

- Attach the published error workflow in Workflow Settings.
- Trigger one controlled failure and confirm that the formatted alert arrives.

### P0-5 — Lead validation remains prompt-based

Email validation, required-field enforcement, explicit confirmation, and consent are written in the system prompt and tool description, but no deterministic validator guards the actual write.

Action:

Create a strict path:

`AI extracts lead payload → Validate Lead Payload → Check Existing Lead → Upsert Human Handoff → Confirm success`

Validation must reject malformed email, empty fields, UUIDs used as names, missing consent, and unconfirmed summaries.

## High-priority maintainability findings

### P1-1 — `Determine Next Best Action` is too large

The node has about 1,255 lines and handles intent priority, pricing discovery, student discovery, objections, trial flow, enrollment, handoff, lead summaries, repeat prevention, multilingual questions, and Redis-state mutation.

Action: split it into smaller deterministic components:

1. `Resolve Effective Intent`
2. `Build Discovery Decision`
3. `Build Objection Decision`
4. `Build Conversion Decision`
5. `Prevent Repeated Question`
6. `Finalize Sales State`

Each component should have one responsibility and its own test cases.

### P1-2 — Repeated normalization utilities

`clean`, `normalize`, and `unique` are recreated across many Code nodes. Arabic normalization also differs between nodes.

Action:

- Normalize message, language, and identifiers once near the trigger.
- Carry canonical fields through the workflow.
- Use the same canonical normalizer for knowledge matching and unanswered-question deduplication.

### P1-3 — Dead and unreachable nodes

The following nodes are not part of the effective execution:

- `Classify Knowledge Result`
- `Aggregate FAQ Context`
- `Select FAQ Fields`
- `Return Sales Discovery Question`

Action:

- Archive them in the baseline export if historical reference is needed.
- Remove them from the refactored workflow after regression testing.

### P1-4 — Redundant route-marker nodes and unused state fields

`Mark Pricing Route` and `Mark Student Support Route` create `intent_route`, but no downstream node reads it. `lead_saved` is initialized and preserved but never set to true. `price_request_count` is collected but not used in a decision. Several `should_*` fields are diagnostic only.

Action:

- Remove unused fields or connect them to explicit behavior/analytics.
- Connect intent-switch branches directly to the next required node when marker nodes have no purpose.

### P1-5 — System prompt is repetitive and partly stale

The AI Agent prompt is about 17,500 characters and repeats FAQ-grounding rules in several sections. It also lists knowledge tools that are not connected to the current AI Agent.

Action:

- Consolidate grounding into one section.
- Remove references to unavailable/legacy tools.
- Keep only response behavior, grounding contract, handoff contract, and security rules that the agent still owns.
- Move deterministic rules into Code/IF nodes.

## Knowledge and unanswered-question findings

### P1-6 — Weak unanswered-question deduplication key

The unanswered path lowercases and compresses spaces, but it does not consistently normalize Arabic letters, punctuation, or diacritics. Similar questions may create separate records.

Action:

- Create `question_key = language + '|' + canonical_normalized_question`.
- Use `question_key` for lookup and update.
- Apply the same normalizer used by the knowledge ranker.

### P1-7 — Update does not use language in its match

The check uses normalized question plus language, while the update matches only `normalized_question`.

Action:

- Match on a unique composite `question_key`.
- Add a uniqueness constraint after migration to a database.

### P1-8 — Duplicate ACTIVE knowledge silently uses the later row

`Normalize Knowledge Records` silently lets the later duplicate win. This hides governance defects.

Action:

- Add a scheduled knowledge-quality workflow that flags duplicate ACTIVE keys, missing answers, unsupported languages, and stale review dates.
- Do not silently resolve conflicting approved answers.

### P1-9 — Knowledge retrieval is lexical, not semantic

The ranking algorithm is a good lightweight first stage, but synonym-heavy or paraphrased questions can miss even when the answer exists.

Action:

- Keep lexical ranking as a fast layer.
- Add hybrid semantic retrieval with embeddings when moving to Supabase/pgvector.
- Record the selected `record_id` in internal analytics for every answered question.

### P1-10 — Some claims are hardcoded outside the knowledge base

For example, the verified pricing builder hardcodes the online one-to-one service statement. This can drift from approved business content.

Action:

- Move business claims into an ACTIVE approved knowledge or nurture record.
- Keep code responsible only for formatting and deterministic calculations.

## Reliability, performance, and security findings

### P1-11 — Missing retries and local error paths

Most Google Sheets and Redis nodes have no retry or node-level error route. A transient dependency error can end the chat.

Action:

- Configure limited retries with backoff for safe reads.
- Use idempotent retry protection for writes.
- Route persistent dependency errors to a multilingual safe response and the central error workflow.

### P1-12 — Intent catalog is loaded for every non-conversational message

The complete ACTIVE catalog is read and serialized into the classification prompt every time. Knowledge rows are also read from Sheets on demand.

Action:

- Cache intent catalog and stable knowledge metadata in Redis for a short TTL.
- Invalidate cache when approved knowledge is synchronized.
- Avoid loading the same packages twice in one request path.

### P1-13 — Token and latency cost

Most non-conversational requests can involve an intent-model call and an answer-model call. The large prompts, intent catalog, up to 30 chat-memory messages, and knowledge context increase tokens and latency.

Action:

- Reduce the AI Agent system prompt.
- Lower memory context from 30 messages after confirming a safe summary mechanism.
- Pass only the top 3–5 verified knowledge records.
- Add maximum response length and token telemetry.

### P1-14 — Public endpoint protection

CORS is useful but is not authentication or abuse prevention.

Action:

- Add rate limiting at the website/proxy layer.
- Add bot/abuse protection and payload-size limits.
- Reject excessively long messages before model calls.
- Never log raw personal data in analytics or error emails.

### P1-15 — Retention policy mismatch

Chat memory expires after one day, while sales state expires after 30 days, and the pricing-state write currently has no TTL.

Action:

- Define one documented retention policy for chat history, sales discovery, and lead PII.
- Add a user/session deletion mechanism.
- Store only the minimum information required.

### P1-16 — Time-zone inconsistency

Some timestamps are explicitly created in `America/Toronto`; others use the instance default via `$now.toISO()`.

Action:

- Store all system timestamps in UTC ISO format.
- Store the customer time zone separately.
- Convert only for display and scheduling.

### P1-17 — Final response fallback is Arabic-only

`Finalize Chat Response` uses an Arabic fallback even for English and French requests.

Action:

- Make the technical fallback multilingual using the resolved language.
- Route conversational responses through the same final response normalizer to ensure one response contract.

## Recommended post–Stage 10 roadmap

### Stage 11 — Freeze, harden, and refactor

Deliverables:

- Export and archive the tested baseline.
- Create `ChatBotMSE v2 - Refactor`.
- Apply all P0 fixes.
- Remove dead nodes and stale prompt sections.
- Split `Determine Next Best Action`.
- Standardize response and state contracts.

Exit criteria:

- All P0 Stage 10 cases pass.
- No duplicate lead writers.
- Error workflow test succeeds.
- No unreachable production nodes.

### Stage 12 — Deterministic lead and handoff engine

Deliverables:

- Dedicated `lead_state` in Redis.
- Structured lead payload.
- Programmatic email, phone, name, consent, and confirmation validation.
- One idempotent lead upsert path.
- Update/correction flow and deletion request flow.

Exit criteria:

- Invalid or incomplete payloads can never reach Google Sheets.
- Duplicate submission is impossible for the same request key.
- Corrections update the same record.

### Stage 13 — Observability, security, and operations

Deliverables:

- Attach error workflow.
- Add health checks and dependency alerts.
- Add anonymized analytics: execution ID, hashed session ID, intent, domain, route, answer source IDs, unanswered flag, handoff result, latency, and model usage.
- Add rate limiting and payload limits.
- Create a production dashboard and incident runbook.

Exit criteria:

- Every failure has an error ID and alert.
- Every answer can be traced internally to its approved record.
- No raw PII appears in analytics logs.

### Stage 14 — Automated regression and evaluation

Deliverables:

- Convert the Stage 10 cases into an automated evaluation dataset.
- Run regression tests after every workflow revision.
- Add multilingual paraphrase, injection, timeout, duplicate, and concurrency cases.
- Establish a release gate: at least 95% pass, zero P0 failures, zero blocked cases.

### Stage 15 — Knowledge platform upgrade

Deliverables:

- Knowledge quality checks and approval lifecycle.
- Canonical unique keys and version history.
- Redis caching.
- Supabase/Postgres migration when Sheets becomes a concurrency or scale limitation.
- Hybrid lexical plus vector retrieval using pgvector.

### Stage 16 — Booking automation

Deliverables:

- Verified available-slot retrieval.
- Google Calendar booking after explicit confirmation.
- Time-zone-safe scheduling and duplicate-booking protection.
- Booking confirmation and staff notification.

### Stage 17 — Multichannel expansion

Deliverables:

- WhatsApp integration using the same intent, knowledge, sales, and lead services.
- Channel-independent session and identity mapping.
- Consistent consent and handoff behavior across website and WhatsApp.

### Stage 18 — Voice experience

Deliverables:

- ElevenLabs speech output and, if required, speech input.
- Realtime interruption/turn handling.
- Voice-specific latency, consent, fallback, and transcript policy.

### Stage 19 — Sales and conversion optimization

Deliverables:

- Funnel reporting: question → qualified interest → trial request → booked trial → paid enrollment.
- Objection conversion analysis.
- A/B-tested nurture messages without changing verified academy facts.
- CRM/Supabase integration and team ownership workflows.

## Immediate implementation order

1. Freeze the tested workflow and do not refactor the production copy directly.
2. Upload the completed Stage 10 results workbook for a formal release decision.
3. Create the v2 refactor copy.
4. Fix `Prepare AI Context` and `Save Pricing Sales State`.
5. remove the duplicate lead-write tool and add deterministic lead validation.
6. Attach and test the error workflow.
7. Remove dead nodes and simplify the system prompt.
8. Split `Determine Next Best Action`.
9. Run targeted P0 regression tests, then the full Stage 10 suite.
10. Publish v2 only after the release gate passes.
