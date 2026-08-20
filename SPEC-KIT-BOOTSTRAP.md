# SPEC-KIT-BOOTSTRAP.md — Updated notes

We have not run the upstream GitHub Spec Kit CLI. The repository now contains a policy and spec baseline that must be reviewed and approved before running the toolchain.

Recommended procedure to initialize upstream Spec Kit CLI (run locally or on CI after approval):

1. Install the official Spec Kit CLI per the GitHub Spec Kit docs (link: https://github.com/github/spec-kit). Use the version pinned by maintainers.
2. From repository root run: `spec-kit init` (or the official CLI's bootstrap command) to generate any required tool scaffolding.
3. Run validation: `spec-kit validate` (or the equivalent) as part of CI to ensure specs meet organizational requirements.
4. Add a GitHub Actions workflow for spec validation to run on PRs targeting the default branch.

Do NOT run the CLI until maintainers confirm the specs in spec/bootstrap are approved for generation. Running the CLI prematurely may add tool-specific files that assume the spec is final.
