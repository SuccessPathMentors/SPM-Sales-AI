# Main Branch Protection Policy

Status: PROPOSED — HARD-001
Effective target: immediately after GitHub source-of-truth cutover
Repository: `SuccessPathMentors/SPM-Sales-AI`
Protected branch: `main`

## Purpose
`main` is the approved engineering source of truth. Routine engineering changes must therefore enter through reviewed, testable pull requests rather than direct pushes.

## Required rules
1. Require a pull request before merging to `main`.
2. Require at least one approving review for material engineering changes.
3. Require review conversations/threads to be resolved before merge.
4. Require applicable CI/status checks to pass before merge.
5. Block force pushes to `main`.
6. Block deletion of `main`.
7. Do not use direct pushes to `main` for routine work.
8. Apply protection to administrators by default; emergency bypass must be deliberate and exceptional.

## CI expectation
The repository's long-term n8n automation is `.github/workflows/n8n-nonprod-deploy.yml`. Production auto-deploy is not authorized. Branch protection must not be interpreted as approval for direct GitHub → n8n Production deployment.

## Production invariant
GitHub branch protection governs source control only.

It does not change the existing production controls:
- `production_auto_deploy: false`;
- GitHub-driven production activation remains unauthorized;
- direct AI → Production remains prohibited;
- Production changes require their own release/human approval gate.

## Working-unit workflow
Normal change path:

`Issue/WU → feature branch → implementation → tests → PR → review → merge to main`

No Working Unit may self-approve or self-lock.

## Verification
HARD-001 is complete only when GitHub reports protection/rules enforcement on `main`. This document alone does not satisfy the gate.
