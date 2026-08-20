# SECURITY.md — SPM-Sales-AI Security Baseline (DRAFT)

Status: DRAFT — FOR REVIEW

This document defines the current security posture requirements and baseline controls for the SPM-Sales-AI repository and runtime.

Principles
- Least privilege: Grant only the minimum permissions required for each service and person.
- Secrets out of repo: No API keys, credentials, or secrets are stored in the repository. Use host/CI/provider secret stores.
- Data minimization: Only collect and persist the fields required for business use; avoid storing unnecessary PII.
- Auditability: Changes to security-relevant configuration (secrets, IAM roles, key rotation) must be auditable and documented.

Repository rules
- No secrets checked in: Enforce pre-commit hooks and CI checks to prevent accidental commits of secrets.
- Branch protection: main (default) must be protected (require PR reviews, status checks) before merge. spec/bootstrap remains DRAFT and must not be merged until APPROVED.
- Experiments: Experimental branches (add/*) must be flagged in PROJECT_STATE.md and not be elevated to canonical status without a spec.

Secrets & API Keys
- Storage: Store secrets in GitHub Actions secrets, cloud provider secret manager (e.g., AWS Secrets Manager, GCP Secret Manager), or Vault.
- Rotation: Establish a rotation policy for long-lived keys (e.g., rotate at least every 90 days or per provider best practices).
- Access: Use short-lived tokens where possible (OAuth flows for Google Sheets; scoped service accounts for limited access).

PII & Transcripts
- PII classification: Define PII fields (name, email, phone, other identifiers). Only the canonical datastore (Google Sheets / CRM) may hold PII needed for business, and access should be restricted.
- Transcript handling: Conversation transcripts containing PII must be redacted before being logged to central logs. If full transcripts are required for handoff, store them in a protected store with strict access controls.
- Retention: Define retention windows for PII and transcripts; default to the minimum necessary retention for business and compliance.

Logs & Telemetry
- Redaction: Redact sensitive fields before emitting logs. Use schema-based redaction at the agent/router layer.
- Storage: Logs and traces should be stored in a centralized observability backend with RBAC controls.
- Access: Limit log access to operators and maintainers with justifiable need.

Network & Infrastructure
- Encrypt in transit: All external connections (APIs, model providers, calendars, Google services) must use TLS/HTTPS.
- Encrypt at rest: Use provider-managed encryption for any durable stores (cloud storage, DBs, Redis persistence if used).
- IP allow-lists / VPC: Prefer private network connectivity for critical systems when hosting in cloud; use VPCs and firewall rules for management endpoints.

Third-Party Integrations
- OAuth & scopes: For Google Sheets and calendar integrations, request the narrowest OAuth scopes required (e.g., sheets: read/write limited to specific sheet IDs when possible).
- Model provider keys: Treat model API keys as high-sensitivity secrets; do not embed keys in client-side code.

Access Control & Least Privilege
- Roles: Use role-based access (e.g., Product Owner, Engineering Owner, QA Owner, Operator). Map roles to minimal permissions for CI, deployment, and data access.
- MFA & SSO: Enforce MFA for all org accounts and use SSO for org membership where possible.

Incident Response & Disclosure
- Reporting: Security incidents must be reported to the owning team and logged in an incident tracker. Escalation paths should be defined in OPERATIONS.md.
- For data breaches: Follow legal requirements for disclosure and preserve evidence; notify affected parties per policy.

Validation & Audits
- Periodic review: Perform security reviews and access audits quarterly, or on major changes to integrations or data handling.

