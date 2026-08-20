# Project Constitution — SPM Sales AI (REPLACEMENT)

Status: DRAFT — NOT APPROVED — NOT MERGEABLE

This constitution is the authoritative governance and decision document for the SPM-Sales-AI project while we adopt Spec-Driven Development.

Maintainers and Owners
- Primary owner: SuccessPathMentors (org)
- Core engineering maintainers: @<list-to-be-filled-in-PR>
- Product owner: <name/email>
- QA owner: <name/email>

Purpose
- Deliver a reliable, safe, and explainable AI Sales Assistant for Success Path Mentors focused on lead capture, qualification, and scheduling. The constitution governs how specs are produced, reviewed, and approved.

Scope
- This constitution applies to all code, infra, workflows, and specs under SuccessPathMentors/SPM-Sales-AI. It covers:
  - Orchestration: n8n workflows and integrations
  - AI agents and routing (deterministic routing; R1 locked behavior)
  - Knowledge base and data layers (Google Sheets as the canonical lead store, indexed KB)
  - Short-lived state stores (Redis) and durable storage
  - Human handoff and scheduling integrations
  - Internationalization and multilingual sales behaviors
  - Diagnostics, QA, and release gates

Decision-making & Spec Lifecycle
- Spec statuses: DRAFT, REVIEW, APPROVED, DEPRECATED.
- All architecture, infra, and cross-cutting changes must be captured in a spec and reach APPROVED status before being considered master-system behavior.
- Small operational changes (docs, tests) may be merged by maintainers without full spec approval, but must reference the relevant spec.
- Major experiments (e.g., add/openai-backend) must be explicitly marked in PROJECT_STATE.md as EXPERIMENT and are NOT included in the master system spec until approved.

Review & Approval Process
- Spec authors create a spec under specs/ and open a PR from a feature branch to spec/bootstrap (or the main branch) referencing the spec file.
- At least one maintainer and one QA reviewer must approve.
- Acceptance criteria and rollout plan must be included in the spec.

Security & Data Policy
- Secrets are never stored in the repo. All credentials must use environment variables or provider secret stores.
- Customer/lead PII handling must be specified within the relevant feature spec and comply with applicable privacy rules.

Governance Cadence
- Weekly status notes are optional. No automated cadence is enforced here — governance cadence will be captured in the CONDUCT section when maintainers are named.

Change Control
- Any change that impacts the R1 locked behavior or data handling requires an APPROVED spec and a staged rollout with QA gates.

This constitution is intentionally prescriptive about the requirement to approve architecture before merging. The current branch spec/bootstrap remains DRAFT and NOT MERGEABLE until spec artifacts are APPROVED.