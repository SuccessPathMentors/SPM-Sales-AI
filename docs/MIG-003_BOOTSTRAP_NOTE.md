# MIG-003 Temporary Bootstrap Gate

Status: TEMPORARY / MANUAL DISPATCH ONLY

Purpose: allow a read-only API smoke test and zero-write dry-run from the default branch while the full MIG-003 implementation remains under PR review.

Workflow: `.github/workflows/mig-003-bootstrap.yml`

Safety:
- Uses GitHub Environment `n8n-staging` only.
- `api-smoke` performs a single GET against the known production workflow ID solely to verify API authentication/read scope; it performs no write.
- `dry-run` executes the MIG-003 deployer in zero-write mode against the exact RC4.3.3 artifact.
- No create/update/activate/publish operation exists in this temporary bootstrap workflow.
- The bootstrap workflow must be removed after MIG-003 is integrated and the normal non-production deployment workflow is available on the default branch.
