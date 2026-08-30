# GitHub Linking Plan — SPM AI Sales Bot Spec Kit

Status: Ready for repository connection
Date: 2026-08-19

## Purpose
Use GitHub as the execution/version-control repository for Spec Kit artifacts, workflow JSON, architecture docs, tests, and implementation changes while keeping Google Drive as the business-accessible review and durable workspace.

## Recommended Repository
Repository name: `spm-ai-sales-bot`

Recommended root structure:
- `.specify/`
- `.specify/memory/constitution.md`
- `specs/`
- `workflows/`
- `automation/` or `src/`
- `knowledge/`
- `tests/`
- `docs/architecture/`
- `docs/qa/`
- `AGENTS.md`
- `PROJECT_STATE.md`
- `CHANGELOG.md`
- `.gitignore`
- `.env.example`

## Spec Kit Initialization
Initialize Spec Kit inside the repository using the chosen coding-agent integration. For a Codex CLI skills setup, the current Spec Kit documentation supports an initialization pattern equivalent to:

`specify init . --integration codex --integration-options="--skills"`

Then verify the installed CLI with:

`specify version`

## Production Workflow
For each material feature:
1. create numbered feature directory/branch;
2. run constitution check;
3. create/update spec;
4. clarify requirements;
5. create technical plan;
6. create requirements checklist;
7. generate tasks;
8. run cross-artifact analysis;
9. implement bounded changes;
10. run runtime and regression tests;
11. run convergence until no material gaps remain;
12. update PROJECT_STATE and CHANGELOG;
13. open PR with requirement/task/test references;
14. merge/tag only after release gate passes;
15. mirror approved artifacts/evidence to Drive when business review requires it.

## Drive ↔ GitHub Authority
Runtime truth remains governed by the project's source-of-truth priority. GitHub should become authoritative for versioned engineering artifacts once connected. Drive remains the accessible project-management and review mirror. Do not maintain conflicting independently edited copies of the same engineering file.

Recommended sync rule:
- GitHub: canonical Markdown/code/JSON/test history.
- Google Drive: review copy, business documents, evidence, and current-state links.
- PROJECT_STATE should link or identify the exact GitHub commit/tag and exact production workflow version after GitHub adoption.

## Security Rules Before First Push
- Remove API keys, access tokens, OAuth credentials, webhook secrets, Redis credentials, database credentials, and embedded service-account data.
- Inspect n8n workflow JSON for credentials or sensitive fixed values.
- Do not commit live customer PII.
- Use sanitized fixtures for tests.
- Add local environment files and credential exports to `.gitignore`.
- Store secrets in GitHub/n8n/environment secret stores, never in repo files.

## Traceability Rules
Every PR should identify:
- Feature spec ID
- Requirement IDs affected
- Task IDs completed
- Runtime/workflow files changed
- Test evidence
- Regression impact
- Rollback/recovery note when applicable
- Resulting production version/tag after release

## First GitHub Feature
After repository connection, begin with `001-r2-error-handling` rather than importing an uncontrolled batch of new changes. First commit the baseline governance/spec artifacts and sanitized locked workflow snapshots, then create the R2 feature branch/spec.
