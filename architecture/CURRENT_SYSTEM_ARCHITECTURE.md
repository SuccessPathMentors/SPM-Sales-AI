# Current System Architecture — SPM-Sales-AI

Status: DRAFT — FOR ARCHITECTURE VALIDATION

This document records the current, *as-deployed/implemented* system architecture as the team understands it today. It intentionally avoids future assumptions about design choices or proposed SLOs. Each section includes a "Validation" line pointing to what must be confirmed (owner, location, or evidence).

Summary (current components)
- Orchestration: n8n is the canonical orchestrator for event-driven workflows, integrations, and background jobs (webhooks, Google Sheets sync, scheduling, CRM). Validation: confirm n8n instance URL, credentials, and workflow repository/location.

- AI Agent Layer: Deterministic agent routing is used to select role-based agents (lead-capture, qualification, multilingual sales, scheduling, human-handoff). Agents execute against curated playbooks / templates for R1 behavior. Validation: confirm agent runtime (serverless, hosted service, or external provider) and where playbooks are stored.

- Routing & Decision Engine: Deterministic routing rules/policy determine agent selection and handoff triggers. Validation: provide the current rule definitions (n8n flow, rule engine, or code repository path).

- Knowledge Base (KB): A curated, indexed KB supplies context and allowed response templates for agents. Validation: confirm KB technology (local docs, vector DB, embeddings, search index) and repo/location.

- Canonical Data Layer: Google Sheets is the present canonical lead store for MVP-era workflows. Validation: list the active sheets, access scopes, and the job/process that syncs writes.

- Short-lived State Store: Redis is used for transient session state, locks for human handoff, and per-session metadata. Validation: provide Redis instance details, persistence/backups, and how keys are namespaced.

- Human Handoff & Scheduling: Scheduling is integrated (Calendly or similar) and human operator queues capture transcripts and metadata for manual follow-up. Validation: confirm scheduler provider, integration method, and human-queue mechanism.

- Multilingual Support: Language detection and language-specific playbooks exist to support multilingual sales behavior in R1. Validation: list supported languages and where playbooks are authored.

- Observability: Logging and monitoring exist for n8n runs and critical flows; error reporting surfaces to an operator channel. Validation: list logging endpoints/agents, monitoring dashboards, and alert destinations.

- Experiments / Not-Canonical
- add/openai-backend (branch): Exists as an experimental Express prototype and is marked EXPERIMENT in PROJECT_STATE.md. It is NOT part of the canonical architecture until a spec promotes it. Validation: repository path and experiment owner.

What this document is NOT
- This is not a proposal. It documents current artifacts, runtime instances, and where to find evidence that each component exists.

Next steps for architecture validation
1. Owners must supply evidence for each "Validation" item above (links to n8n flows, KB storage, Redis instance, Google Sheets IDs, scheduler integration, and current agent runtime).
2. Once evidence is collected, update this document with concrete locations, instance URLs, and any constraints (e.g., auth scopes, IP allowlists).
3. Use this validated current-architecture doc as the baseline for the Master System Spec and for converting Proposed items in R2 into Current items.

