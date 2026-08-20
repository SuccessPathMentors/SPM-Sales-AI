# Master System Specification — Draft

This file is the top-level system specification for SPM-Sales-AI. It should describe the system boundaries, major components, integration points, and high-level non-functional requirements.

## Overview
SPM-Sales-AI is an AI-enabled sales assistant platform composed of the following major components:

- openai-backend: Node/Express service that proxies prompts to OpenAI and enforces auth/rate-limiting.
- Frontend: Web UI for agents to interact with the assistant (TBD).
- n8n Workflows: Automation flows for lead handling, CRM sync, and notifications.
- Integrations: CRM, email gateway, analytics, and monitoring.

## System Boundaries
- The system processes customer data (leads, interactions) and uses OpenAI models for assistance. Data residency and privacy must be considered.

## Major Components
- API Gateway / Backend: Handles auth, routing, and business logic.
- AI Service (openai-backend): Responsible for safe prompt handling, rate limiting, and model selection.
- Orchestration (n8n): Runs workflows for background processing.
- Persistence: Database(s) for users, leads, and logs.
- Observability: Logging, metrics, and alerting for critical paths.

## Non-Functional Requirements (Draft)
- Security: Secrets must be stored in host environment variables or secrets manager; no API keys stored in repo.
- Availability: Critical API endpoints 99.9% uptime target.
- Privacy: Sensitive PII must be redacted or stored according to policy.
- Performance: Typical conversational responses within 2s median.

## Next Steps
- Flesh out component responsibilities with owners and acceptance criteria.
- Break down system spec into sub-specs per component (backend, n8n, frontend, infra, QA).
- Draft concrete cross-cutting concerns (auth, observability, CI/CD, testing strategy).

(Use this master spec as the authoritative top-level document and keep it in sync with the constitution and lower-level specs.)
