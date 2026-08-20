# OPERATIONS.md — Runtime operations & runbooks (DRAFT)

Status: DRAFT — FOR REVIEW

Purpose
- Provide operators and maintainers with runbooks for common failure modes, detection, mitigation, rollback, and post-incident tasks. This document is intentionally concise and references detailed runbooks per component when those are added.

Operational responsibilities
- Role-based owners (no personal contacts in this doc): Product Owner, Engineering Owner, QA Owner, On-call Operator. Assign named people in the PR when ready.

Monitoring & Health Checks
- Critical checks to run continuously:
  - n8n health and recent run errors.
  - Agent runtime health and response validation.
  - Redis availability and memory/eviction metrics.
  - Google Sheets API errors / quota usage.
  - Scheduler integration failures and 5xx rates.
  - Model provider errors (OpenAI or equivalent): rate limits, 5xx, and malformed responses.
- Suggested metrics (implement per monitoring stack): error_rate, median_response_time, fallback_trigger_count, handoff_queue_length, n8n_failed_runs.

Failure modes & runbooks (high-level)
1. n8n workflow failures
   - Detection: alert on increased node failures or workflow run failure counts.
   - Mitigation: restart failing workflow nodes; isolate the failing node by disabling it in n8n; re-run failed executions after root cause identified.
   - Recovery: re-run idempotent tasks; if non-idempotent, reconcile state with canonical Google Sheets.
   - Post-incident: capture run logs, time range, and affected lead IDs; create incident ticket.

2. Google Sheets API or quota errors
   - Detection: elevated 4xx/5xx or quota-exceeded logs for Sheets API calls.
   - Mitigation: throttle writes, pause non-critical sync jobs, and switch to a read-only degraded mode where possible.
   - Recovery: resume jobs after quota reset or increase quota; reconcile missed writes from n8n run logs.

3. Redis outage or performance degradation
   - Detection: connection errors, high latency, eviction warnings.
   - Mitigation: switch to local in-memory fallback for short period (if available) and persist session snapshots to durable storage (temporary sheet or file) for handoff continuity. NOTE: This fallback is a proposed stopgap and must be validated for data-loss risk.
   - Recovery: restore from backup or failover to replica; reconcile session context from durable snapshots.

4. Model provider (OpenAI) failures or unexpected outputs
   - Detection: service 5xx, malformed response, or validation failures against allowed schema.
   - Mitigation: trigger deterministic fallback: stop open-ended generation; create human-handoff ticket; mark lead state "awaiting-human".
   - Recovery: after provider recovers, replay safe retries only for idempotent tasks.

5. Scheduling integration failures
   - Detection: API errors when provisioning or reading calendar events.
   - Mitigation: present scheduling as "pending" to the user and route to human operator for manual scheduling.
   - Recovery: reconcile calendar events after integration restored.

Incident lifecycle
- Triage: On alert, operator creates incident ticket (document impact, scope, and initial mitigation).
- Escalation: If impact is service-level (affecting > X% leads or critical flows), escalate to Engineering Owner and Product Owner.
- Remediation: Implement mitigation, verify recovery, and run reconciliation.
- Postmortem: Produce a postmortem within 72 hours with root cause, timeline, and corrective actions.

Rollbacks & Release safety
- Feature flags: Use feature flags for any changes affecting R1; ensure quick toggle to disable features.
- Canary releases: Run targeted subsets of traffic through new code (percentages and windows to be validated per R2 acceptance criteria).
- Emergency rollback: The operator or Engineering Owner may revert deployments or flip feature flags immediately for critical failures.

Runbook artifacts to add next (action items)
- Detailed n8n node-level runbook with exact remediation steps.
- Redis failover and backup/restore procedure.
- Sheets reconciliation tool and how to run it.
- Human-handoff ticket template and required fields.

