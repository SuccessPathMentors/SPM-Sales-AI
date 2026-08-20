# R2 — Reliability & Error Handling (Feature Spec) — UPDATED (classification)

Spec ID: R2-RELIABILITY-ERROR-HANDLING
Status: DRAFT — CLASSIFICATION PASS

This update classifies each requirement as Current / Proposed / Needs Validation to avoid codifying assumptions into the constitution.

Objective
- Define the reliability and error-handling requirements for background workflows and agent interactions and indicate which items are currently in place vs proposed changes.

Classification key
- Current: Implemented today and confirmed in the architecture.
- Proposed: Recommended change to be approved and implemented if accepted.
- Needs Validation: We suspect this is needed but must confirm implementation details, feasibility, and impact in the current runtime (n8n, Redis, Sheets, scheduler).

Requirements (classified)

1. n8n Workflows
   - Default retry policy (3 attempts, exponential backoff 1s/4s/16s): Proposed — choose after validating n8n's node-level retry configurability and external API rate limits. (Needs Validation: whether existing n8n workflows already set retries.)
   - On persistent failure: mark lead state = "error:integration": Proposed — needs review of canonical lead-state taxonomy in Google Sheets and CRM.

2. Agent Error Handling
   - Guarded execution wrapper and output validation: Current (Needs Validation) — agents perform some validation today, but the coverage and validation harness must be audited and documented.
   - Deterministic fallback that creates a human-handoff ticket on validation failure: Proposed — fallback behavior exists in spirit but requires a formalized ticket structure and QA acceptance.

3. Redis / State
   - Detect outages and write critical session snapshots to durable storage (temporary sheet or drive): Proposed / Needs Validation — the snapshot destination and data-loss risk need confirmation with operations and security.

4. Observability
   - Metrics: failed_tasks_per_minute, MTTR, fallback_trigger_count, handoff_lag: Proposed — we recommend these metrics be implemented; validate existing telemetry coverage.
   - Alerts: fire when fallback_trigger_count crosses threshold: Proposed — thresholds need to be calibrated against production baselines.

5. Testing & QA
   - Unit tests and integration tests simulating API failures: Current/Needs Validation — some automated tests exist; extent needs validation.
   - Manual QA plan for staged failure scenarios: Proposed — must be drafted in QA artifacts.

Rollout Plan (classification)
- Canary rollout (5% → 25% → 100%): Proposed — rollout percentages and windows to be validated against staging traffic patterns and canary tooling.
- Fallback rollback via feature flag: Current (if feature flags available) / Needs Validation — confirm feature flagging mechanism and its integration with runtime.

Acceptance Criteria
- Tests covering simulated failures: Needs Validation (confirm CI/integration harness).
- Manual staging validation and QA sign-off: Proposed — QA process must be documented and scheduled.
- Metrics and alerting configured: Proposed — requires instrumentation and production baseline.

Next validation steps
1. Owners to confirm which items are Current by pointing to implementation artifacts (n8n workflows, agent code, Redis configs, telemetry dashboards).
2. For Proposed items, produce change specs describing implementation approach and acceptance criteria.
3. After validation, move items from Proposed/Needs Validation to Current and update master spec accordingly.

