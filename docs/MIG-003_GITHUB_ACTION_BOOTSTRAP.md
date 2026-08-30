# MIG-003 — GitHub Action Bootstrap Constraint

GitHub `workflow_dispatch` only receives manual dispatch events when the workflow file exists on the repository default branch.

Current state:
- MIG-003 implementation lives on `migration/mig-003-nonprod-deploy`.
- PR #9 targets the migration branch, not `main`.
- PR-triggered safety tests already run successfully without secrets.
- Therefore the `Run workflow` UI for the new manual deploy workflow must **not** be assumed available yet.

## Safe options for the first live STAGING API gate

### Preferred — narrow bootstrap PR to default branch
After review, create a narrowly scoped PR to `main` containing only the non-production deployment harness/policy and the exact artifact needed for the STAGING test. This does not declare full source-of-truth cutover. Once the workflow file exists on `main`, use `workflow_dispatch` and GitHub Environment `n8n-staging`.

### Interim — exact versioned script execution
Run the exact committed `scripts/n8n/deploy_nonprod.py` from the reviewed commit against STAGING using local environment variables. This can prove the API contract before the Action is present on the default branch, but GitHub Actions automation is not considered fully proven until a later `workflow_dispatch` run succeeds.

## Secret rule
Do not add n8n API keys to workflow files, commits, issues, PR comments, logs, or chat. Store them only in GitHub Environment secrets or a local ephemeral environment for the interim test.

## Production invariant
Neither option permits writes to production workflow ID `CMBMpxX5AqqK2UTn`. The deployer hard-denies that ID and refuses any active/published target.
