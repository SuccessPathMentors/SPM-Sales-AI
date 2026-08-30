# Future Database Migration Roadmap

## Direction

Use PostgreSQL/Supabase as the future durable database; optionally add `pgvector` for semantic retrieval. Keep n8n as orchestration. Google Sheets may remain an editorial review surface during transition.

## Candidate tables

- `knowledge_records`
- `knowledge_sources`
- `intent_catalog`
- `sales_nurture`
- `unanswered_questions`
- `leads`
- `lead_events`
- `conversation_sessions`
- `test_runs` and `test_results`
- `audit_log`

## Migration sequence

1. Define schema, IDs, constraints, RLS, backups, and retention.
2. Migrate a read-only, low-risk knowledge domain.
3. Dual-read Sheets and database; compare outputs.
4. Add editorial sync and conflict rules.
5. Move unanswered questions.
6. Move leads only after encryption, permissions, backups, and rollback pass.
7. Retire Sheets writes gradually; keep export/reporting access.

## Entry gate

Do not start the pilot until R1–R6 core gates are locked and current behavior has measurable QA evidence.
