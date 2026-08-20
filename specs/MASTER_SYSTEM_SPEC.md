# Master System Specification — SPM-Sales-AI (REPLACEMENT)

Status: DRAFT — NOT APPROVED

This master system spec describes the currently intended system baseline for SPM-Sales-AI. This document represents the canonical system boundaries and the components that are considered part of the approved system only after the spec is APPROVED.

Important notes
- The add/openai-backend Express experiment exists in the repository as an unapproved experiment and is intentionally NOT described here as an approved component.
- This spec reflects the working SPM design: n8n orchestration, deterministic agent routing, knowledge base, Google Sheets/data layer, Redis/state, lead capture, human handoff, scheduling/integrations, multilingual behavior, and locked R1 behavior.

1. System Overview
SPM-Sales-AI is an AI-assisted sales orchestration system intended to capture leads, qualify them, schedule follow-ups, and route conversations between AI agents and human operators.

2. High-level Components
- Orchestration (n8n): Responsible for event-driven workflows that connect webhooks, Google Sheets, CRM, email, and scheduling. n8n is the canonical orchestrator for external integrations and background flows.

- AI Agent Layer: A set of deterministic agents with an explicit routing policy. Agents are not monolithic: each agent has a role (lead-capture, qualification, multilingual-sales, scheduling, human-handoff) and operates against a defined knowledge base and state store.

- Routing & Decision Engine: Deterministic routing rules ensure predictable behavior for R1. Routing may call into a rule engine or deterministic policy service that maps inputs (lead attributes, intent detection, language) to agents or human-handoff.

- Knowledge Base (KB): Searchable, authenticated store (indexed content from docs, onboarding scripts, playbooks) used by agents for context. The KB includes curated prompts and allowed response patterns for R1.

- Canonical Data Layer (Google Sheets): Google Sheets acts as the canonical lead datastore for early-stage MVP. Source-of-truth data synchronization jobs (n8n) ensure sheets represent the latest approved lead state.

- Short-lived State Store (Redis): Holds transient conversation state, locks for human handoff, rate-limiting counters, and per-session metadata needed for deterministic routing.

- Human Handoff & Scheduling: Integrations with Calendly / scheduling provider and human operator queues. Handoff includes an audit trail, conversation transcript snapshot, and handoff triggers (explicit user request, confidence threshold, or rule match).

- Logging, Monitoring & Observability: Structured logs, metrics, and alerts for failed workflows, routing anomalies, and uptime issues. Sensitive data must be redacted in logs.

3. Architecture Boundaries
- External Systems: Google Sheets, CRM, OpenAI (or other model providers), calendar/scheduling, email gateways, and payment providers are external to the system and accessed via controlled integrations.
- In-Repo Experiments: Branches/feature directories like add/openai-backend are experiments and must be promoted via spec approval to become part of the canonical architecture.
- Data Residency: PII stored in Google Sheets or CRM must align with privacy rules; any sync to other persistence must be captured in a spec and approved.

4. Non-Functional Requirements (Initial Draft)
- Reliability: R1 must be deterministic for approved flows (i.e., behavioral invariants enforced by routing and templated responses).
- Observability: End-to-end traces for lead lifecycle events; errors surfaced to n8n runs and a monitoring dashboard.
- Privacy & Security: Secrets are injected via host provider secrets; no keys in repo.
- Performance: Define per-spec targets — R1 behavior is about determinism and safety over low-latency. Specific latency SLOs belong in the R2 reliability spec.

5. R1 Locked Behavior (must be preserved unless changed by an APPROVED spec)
- Deterministic routing rules for lead-capture and qualification flows.
- Template-driven responses for sensitive decisions (no open-ended generation in R1 without guardrails).
- Human handoff triggers and mandatory transcript capture for operator context.
- Language detection and deterministic selection of multilingual agent variants.

6. QA / Release Gates (overview)
- Each feature spec must include:
  - Acceptance criteria (functional and non-functional)
  - Automated tests (unit/integration where applicable)
  - Manual QA checklist items (hand-off flows, PII checks, multilingual spot-checks)
  - Rollout plan with canary percentage and rollback criteria
- No feature affecting R1 behavior can be released without a QA sign-off and staging validation run (see specs/R2-RELIABILITY.md for the R2 gate).

7. Ownership & Next Steps
- Break this master spec into component-level specs (n8n, agents, KB, data sync, human handoff) and assign owners.
- Draft concrete SLOs and test plans for R2 reliability.

8. Appendix
- Experiment inventory: add/openai-backend (branch) — EXPERIMENT, NOT APPROVED.
