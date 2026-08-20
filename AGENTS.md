# AGENTS.md — Agent catalog and responsibilities

This file catalogs the agents and agent-like components used by SPM and documents the locked R1 behavior and how agents may be modified through the spec process.

Agent types and responsibilities

1. Lead-Capture Agent
- Purpose: Collect minimal lead information from webhooks, chat, or integrations.
- Inputs: Webhook payloads, form submissions, chat messages parsed by NLU.
- Outputs: Creates/updates a lead row in Google Sheets; emits an n8n event for downstream qualification.
- R1 rules: Use templated questions only, limited follow-ups (max 3 fields) to avoid open-ended generation.

2. Qualification Agent
- Purpose: Ask qualifying questions, score leads, and determine readiness for scheduling or human follow-up.
- Inputs: Lead record, conversation context, KB lookup.
- Outputs: Qualification score and tags written to Google Sheets; route decision to scheduling or human queue.
- R1 rules: Deterministic scoring policy; no freeform recommendations.

3. Multilingual Sales Agent(s)
- Purpose: Conduct sales conversations in supported languages using predefined playbooks.
- Inputs: Detected language, KB playbook for language, lead context.
- Outputs: Responses constrained to playbook templates, suggested next actions.
- R1 rules: Language detection + deterministic playbook selection. Fallback to human handoff when language not supported.

4. Scheduling Agent
- Purpose: Offer scheduling options (via Calendly or internal scheduler) and confirm appointments.
- Inputs: Availability window, lead preferences.
- Outputs: Calendar invites, lead status updates.
- R1 rules: Only propose available slots from the integrated scheduler; require explicit confirmation before creating events.

5. Human-Handoff Agent (Queue Manager)
- Purpose: Package conversation snapshots, push to human operator queue, track resolution.
- Inputs: Handoff trigger (rule or user request), conversation transcript, lead metadata.
- Outputs: Ticket or task for human, mark lead state in Google Sheets.
- R1 rules: Always capture transcript and metadata; do not remove required audit fields.

Agent modification and spec process
- Any change to an agent that could alter R1 behavior requires a feature spec with acceptance criteria and QA steps.
- Training data or prompt changes that broaden behavior must be reviewed by the owners and QA team before deployment.
