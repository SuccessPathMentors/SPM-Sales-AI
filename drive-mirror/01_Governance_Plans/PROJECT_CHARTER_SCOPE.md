# Project Charter, Scope, and Success Criteria

## Product goal

Deliver a stable Arabic/English/French website assistant for Success Path Mentors that answers only from verified knowledge, remembers the conversation, performs consultative sales discovery, captures qualified leads with consent, and continuously records unanswered questions for review.

## Core scope — required before expansion

1. Stable website chat transport and session persistence.
2. Verified knowledge retrieval from ACTIVE records.
3. Intent/entity understanding and deterministic routing.
4. Consultative sales flow with controlled pricing behavior.
5. Redis-backed conversation and sales state.
6. Unanswered-question logging, deduplication, notification, approval, and sync.
7. Validated lead capture and reliable upsert into `LEADS_TEMPLATE`.
8. Error handling, monitoring, security, retention, and release evidence.

## Explicitly deferred

- Voice agents and ElevenLabs production integration.
- Broad CRM replacement or multiple sales-platform integrations.
- Unbounded new intents, campaigns, channels, or languages.
- Full Supabase/Postgres migration before the core release is locked.
- Autonomous copying of third-party sales content.

## Success criteria

| Area | Minimum acceptance |
|---|---|
| Knowledge | 100% of academy claims grounded in ACTIVE approved records |
| Language | Correct response language in Arabic, English, and French |
| Memory | Same session survives refresh; private visitor isolation remains correct |
| Routing | Known, unanswered, conversational, sales, and handoff paths are deterministic |
| Leads | New lead writes once; update changes same row; missing/invalid data is rejected |
| Consent | No write without clear consent and final confirmation |
| Unanswered | Unknown business question logs once and returns approved fallback |
| Reliability | 0 P0 defects, 0 blocked tests, >=95% test pass rate |
| Observability | Every failed execution produces a useful alert without exposing secrets |
| Cost | No unnecessary model or sheet calls; responses stay concise |

## Non-negotiable limits

- One active implementation phase at a time.
- No feature expansion while a P0/P1 defect is open.
- No production claim without execution evidence.
- No third-party content copied without ownership, license, privacy, and accuracy review.

