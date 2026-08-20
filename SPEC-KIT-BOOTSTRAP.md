# Spec Kit Bootstrap for SPM-Sales-AI

This branch contains a lightweight bootstrap of the GitHub Spec Kit (Spec-Driven Development) structure for the SPM-Sales-AI repository.

Purpose
- Provide a starting structure to author the project constitution and the master system specification.
- Make it easy to adopt the upstream Spec Kit tooling without placing tool-specific binaries or dependencies in the repo.

What I added
- .speckit/config.yml — minimal config pointing at the specs directory
- specs/CONSTITUTION.md — project constitution template (draft)
- specs/MASTER_SYSTEM_SPEC.md — master system specification template (draft)
- SPEC-KIT-BOOTSTRAP.md — instructions for installing and using GitHub Spec Kit locally and next steps

Notes
- I did not run upstream tooling (the repo is only modified with scaffolding files). To complete initialization you can follow the steps in SPEC-KIT-BOOTSTRAP.md to run the Spec Kit CLI or GitHub-hosted workflow locally.
- Per your request, this is on a new branch spec/bootstrap and I have not opened a PR.
