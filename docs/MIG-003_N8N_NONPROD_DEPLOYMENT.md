# MIG-003 — GitHub → n8n Non-Production Deployment

Status: IMPLEMENTED / LIVE API TEST PENDING
Issue: #7
Branch: `migration/mig-003-nonprod-deploy`

## Objective
Create a repeatable, fail-closed path from a versioned GitHub workflow artifact to an **inactive DEV/STAGING n8n workflow**. MIG-003 must never publish, activate, update, or overwrite the verified production workflow.

## Protected production identity
The current production workflow is immutable for MIG-003:

- Name: `SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json`
- n8n workflow ID: `CMBMpxX5AqqK2UTn`
- SHA-256: `680496f2b68b13dd7105e72fd132a2066d70ec969e6e0675f138ebb1fb16fe39`
- Policy: `DENY_ALL_MIG_003_WRITES`

The ID is hard-coded in the deployer deny-list and duplicated in `n8n/deployment/nonprod-policy.json`; unit tests require both to match.

## Files
- `.github/workflows/n8n-nonprod-deploy.yml` — manual deployment workflow + PR safety tests.
- `scripts/n8n/deploy_nonprod.py` — stdlib-only deployment client and safety gate.
- `scripts/n8n/test_deploy_nonprod.py` — unit tests for hard-stop behavior.
- `n8n/deployment/nonprod-policy.json` — machine-readable policy.
- `deployment-result.json` — generated evidence file, uploaded as a GitHub Actions artifact.

## n8n Public API contract used
The implementation uses the n8n Public API with `X-N8N-API-KEY` and an API base URL ending in `/api/v1`.

Allowed calls:
- `GET /workflows/{id}` — verify target identity/state.
- `POST /workflows` — only when a one-time create is explicitly requested.
- `PUT /workflows/{id}?publishIfActive=false` — update an already-known inactive DEV/STAGING workflow.

Forbidden calls:
- publish / activate
- unpublish / deactivate
- delete
- any write to a published/active workflow
- any write to protected production ID `CMBMpxX5AqqK2UTn`

The deployer deliberately reduces workflow exports to the writable Public API fields rather than sending a raw GET/export object back to n8n. Server-managed fields such as `id`, `active`, `createdAt`, `updatedAt`, `versionId`, `tags`, and other read-only metadata are not submitted.

## Safety gates
An apply operation stops unless all applicable conditions pass:

1. Environment is exactly `dev` or `staging`.
2. Artifact is valid UTF-8 JSON.
3. Required workflow fields exist: `name`, `nodes`, `connections`, `settings`.
4. Node names and non-empty node IDs are unique.
5. Connections do not reference unknown nodes.
6. Artifact SHA-256 exactly matches the supplied expected checksum.
7. `SPM_DEPLOY_CONFIRM=SPM_NONPROD_ONLY` is present.
8. API base URL is HTTPS and ends with `/api/v1`.
9. Target ID is not on the protected production deny-list.
10. Existing target is `active=false`.
11. Existing target name begins with `[DEV] ` or `[STAGING] ` as appropriate.
12. If there is no target ID, creation is refused unless `--allow-create` was explicitly supplied.
13. After create/update, the workflow is fetched again and re-checked as inactive non-production.
14. The script contains no publish/activate/deactivate API call.

## Source artifact behavior
A verified production export may be used as the *source bytes* for a STAGING copy. The source workflow ID does not become the destination ID. The write payload:

- strips server-managed fields;
- prefixes the workflow name with `[DEV]` or `[STAGING]`;
- forces `availableInMCP=false` if present as true;
- does not include secret values;
- retains n8n credential references, which must resolve in the target runtime before runtime certification.

## Local dry-run evidence — 2026-08-30
The deployer was executed in `dry-run` mode against the exact RC4.3.3 artifact:

- SHA-256: `680496f2b68b13dd7105e72fd132a2066d70ec969e6e0675f138ebb1fb16fe39` — PASS
- Nodes: 114 — PASS
- Connection source nodes: 112 — PASS
- Credential references detected: 26
- Proposed non-production name: `[STAGING] SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json`
- Source production ID recognized: `CMBMpxX5AqqK2UTn`
- Operation performed: `NONE`
- Published/activated: `false`
- Result: `PASS_DRY_RUN`

This proves local artifact validation and safety transformation. It does **not** prove n8n API connectivity; that is the remaining MIG-003 live gate.

## GitHub Environment setup
Create two GitHub Environments:

- `n8n-dev`
- `n8n-staging`

For each environment, configure secrets directly in GitHub. Never paste them into issues, workflow files, commits, or chat transcripts.

Required for `apply`:
- `N8N_API_BASE_URL` — for n8n Cloud: `https://<instance>.app.n8n.cloud/api/v1`
- `N8N_API_KEY` — API key scoped to the minimum required workflow permissions where supported.

Optional after the first deliberate creation:
- `N8N_TARGET_WORKFLOW_ID` — exact inactive DEV/STAGING workflow ID. Once configured, future applies update only this explicit target.

Recommended API-key scopes where granular scopes are available:
- `workflow:create` only if first creation is required
- `workflow:read`
- `workflow:update`

Do **not** grant `workflow:activate` for MIG-003.

## First STAGING sequence
1. Configure GitHub Environment `n8n-staging` with `N8N_API_BASE_URL` and `N8N_API_KEY`.
2. Run `n8n non-production deploy` manually with:
   - environment: `staging`
   - artifact: RC4.3.3 GitHub artifact
   - expected SHA: the recorded RC4.3.3 SHA
   - mode: `dry-run`
   - allow_create: `false`
3. Confirm the Action result is `PASS_DRY_RUN`.
4. Run again with mode `apply`, `allow_create=true` for the one-time creation.
5. Confirm the created workflow name starts `[STAGING]` and remains inactive/unpublished.
6. Record the returned target workflow ID as the `N8N_TARGET_WORKFLOW_ID` secret in `n8n-staging`.
7. Future runs use `apply`, `allow_create=false`; they can only update that known inactive STAGING workflow.
8. Perform runtime regression manually/in staging; do not promote automatically to production.

## Rollback / restore for non-production
Before an update, the GitHub artifact itself remains the immutable desired version. If a STAGING change is bad:

1. Select the previously accepted GitHub workflow artifact and exact SHA.
2. Run the same Action in `dry-run` mode.
3. Run `apply` against the same inactive `N8N_TARGET_WORKFLOW_ID`.
4. Re-run STAGING regression.

Production rollback is outside MIG-003 and remains governed by the production release/approval process.

## Remaining exit gate
MIG-003 can close only after:
- GitHub Environment secrets are configured without exposing them;
- Action safety tests pass in GitHub;
- one GitHub Action dry-run passes;
- one controlled STAGING create or update passes through the n8n API;
- returned target ID is recorded;
- target is reverified inactive;
- execution evidence is attached to issue #7;
- no production workflow was modified or published.
