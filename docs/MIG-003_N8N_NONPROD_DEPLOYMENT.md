# MIG-003 — GitHub → n8n Non-Production Deployment

Status: IMPLEMENTED / API SMOKE + DRY-RUN PASS / LIVE STAGING CANARY WRITE PENDING
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
- `n8n/workflows/staging/MIG003_STAGING_CANARY.json` — side-effect-free live API canary.
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
A verified production export may be used as *read-only validation input* during dry-run. It is **not** used for the first live write because it contains runtime credential references and business side-effect nodes.

The first live n8n write uses `MIG003_STAGING_CANARY.json`, which contains only a Manual Trigger and no credentials, webhook, Redis, Google Sheets, OpenAI, lead write, booking, payment, handoff, or external-follow-up action.

After the deployment mechanism is proven with the canary, any real STAGING copy of RC4.3.3 requires a separate environment-hardening step that replaces/isolates production runtime dependencies before runtime execution.

## Live validation evidence — 2026-08-30
### API smoke — PASS
GitHub Actions run `33326561623`:
- n8n API authentication: PASS
- workflow read permission: PASS
- protected production ID returned exactly: `CMBMpxX5AqqK2UTn`
- production active state observed: `true`
- write performed: `false`

### RC4.3.3 dry-run — PASS
GitHub Actions run `33326906101`:
- SHA-256: `680496f2b68b13dd7105e72fd132a2066d70ec969e6e0675f138ebb1fb16fe39` — PASS
- Nodes: 114 — PASS
- Connection source nodes: 112 — PASS
- Credential references detected: 26
- Proposed non-production name: `[STAGING] SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json`
- Source production ID recognized: `CMBMpxX5AqqK2UTn`
- Operation performed: `NONE`
- Published/activated: `false`
- Result: `PASS_DRY_RUN`
- Evidence artifact ID: `9736488268`
- Evidence artifact digest: `sha256:3dbe1d39e9dfaf2895b3d61994019cf648239e1d4049716332157f6a991146b0`

## GitHub Environment setup
`n8n-staging` is configured with environment-scoped secrets:
- `N8N_API_BASE_URL`
- `N8N_API_KEY`

The API key is intentionally limited to:
- `workflow:create`
- `workflow:read`
- `workflow:update`

It does **not** include workflow activate/deactivate/delete privileges.

After first canary creation, record the returned inactive STAGING ID as:
- `N8N_TARGET_WORKFLOW_ID`

## First STAGING write sequence
1. Run `MIG-003 nonprod bootstrap` with mode `create-canary`.
2. The action verifies exact canary SHA-256 `f49a1610a26974684b3469cd803f116e3c8ab1ffd45e66df0c4478c7df654bb9`.
3. The deployer creates a new workflow named `[STAGING] MIG003_STAGING_CANARY`.
4. It immediately GETs the returned ID and fails unless `active=false` and the `[STAGING]` prefix is preserved.
5. Record that ID as the `N8N_TARGET_WORKFLOW_ID` secret in the `n8n-staging` GitHub Environment.
6. Run mode `update-canary` to prove deterministic update of only that known inactive workflow.
7. Verify production ID `CMBMpxX5AqqK2UTn` remains untouched.

## Rollback / restore for non-production
For a STAGING canary or later approved STAGING artifact, the GitHub artifact and exact SHA are the desired version. A restore uses the same explicit inactive target ID. Production rollback is outside MIG-003 and remains governed by the production release/approval process.

## Remaining exit gate
MIG-003 can close only after:
- one controlled STAGING canary create passes;
- returned target ID is recorded;
- one deterministic update of that same inactive target passes;
- target is reverified inactive;
- execution evidence is attached to issue #7;
- PR #9 is reviewed/merged into the migration branch;
- no production workflow was modified or published.
