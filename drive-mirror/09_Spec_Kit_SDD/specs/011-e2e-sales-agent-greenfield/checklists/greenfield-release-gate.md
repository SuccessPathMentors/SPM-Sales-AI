# 011 Greenfield E2E Sales Agent — Release Gate

Release is blocked until every applicable gate passes.

## Gate A — Architecture
- [ ] New workflow has a new identity and is inactive.
- [ ] No production workflow overwritten.
- [ ] Semantic AI responsibilities and deterministic authority are explicitly separated.
- [ ] Contracts exist for classifier, entities, state, source gates, Sales Agent output, actions, and telemetry.

## Gate B — Taxonomy / State
- [ ] 62/62 detailed intents mapped.
- [ ] Confidence and ambiguity rules tested.
- [ ] Entity normalization passes EN/AR/FR/code-switch cases.
- [ ] Multi-student profiles remain separated.
- [ ] Durable state merge is non-destructive.
- [ ] Opt-out remains sticky.

## Gate C — Grounding / Sales Quality
- [ ] Stable facts use approved ACTIVE sources.
- [ ] Volatile facts use required live tools.
- [ ] Sales Agent acts consultatively rather than as an FAQ-only bot.
- [ ] No unsupported commercial/teacher/policy/availability claims.
- [ ] No invented discount, urgency, outcome, booking, or success.

## Gate D — Conversion
- [ ] PII collected only after explicit next-step acceptance/request.
- [ ] Lead fields validated before write.
- [ ] Confirmed lead write exactly once.
- [ ] Corrections update intended lead/session.
- [ ] Duplicate confirmation is idempotent.
- [ ] Handoff preserves known sales context.

## Gate E — Scheduling / Booking
- [ ] Timezone resolution deterministic.
- [ ] Availability comes from live scheduling.
- [ ] Booking confirmation requires tool success and booking_id.
- [ ] Retry/failure paths do not produce false availability or success.

## Gate F — Reliability / Security
- [ ] All critical failures classified and observable.
- [ ] Retry rules bounded and idempotent.
- [ ] No PII/secrets exposed in logs/prompts beyond approved minimum.
- [ ] Prompt-injection and unsupported-action tests pass.
- [ ] No P0/P1 open issue.

## Gate G — Regression
- [ ] WU85 baseline/offline regression preserved or explicitly superseded by stronger tests.
- [x] R1 protected lead outcomes 10/10 pass against the new system (final targeted rerun 2026-08-25; 10 automated PASS, 0 failures).
- [ ] 62-intent regression passes.
- [ ] Runtime Sheets and Redis tests pass.
- [ ] Full E2E sales journeys pass.
- [ ] EN/AR/FR parity passes.
- [ ] Red-team and failure-injection suite passes.

## Gate H — Production Cutover
- [ ] Immutable release candidate produced.
- [ ] Rollback path verified.
- [ ] Owner release approval recorded.
- [ ] Canary plan and monitoring thresholds defined.
- [ ] Canary passes without blocking regression.
- [ ] PROJECT_STATE, CHANGELOG, GitHub, and Drive mirror updated.
- [ ] Approved release locked/tagged.

Current status: WU99 runtime execution is complete: 96/96 automated runtime PASS, manual semantic remediation closed, failure injection 15/15 PASS, and final R1 protected regression 10/10 PASS. Final WU99 certification remains BLOCKED only on evidence consolidation/execution identifiers and any required owner acceptance of documented method deviations. Gate H / WU100 production cutover remains unauthorized.
