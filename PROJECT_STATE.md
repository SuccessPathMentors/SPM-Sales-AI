# PROJECT_STATE.md

This document records the repository state, active experiments, and what is considered canonical vs experimental.

Sourcing date: 2026-08-20

Branches
- main (or default): canonical production branch (protect before merge)
- add/openai-backend: experimental branch with a minimal Express backend prototype — EXPERIMENT
- spec/bootstrap: current branch with spec baseline — DRAFT, NOT APPROVED, DO NOT MERGE

Experiments
- add/openai-backend: Purpose: prototype a direct OpenAI backend. Status: experimental; not part of the master spec. Owner: TBD. Risks: could encourage unreviewed model usage and drift from deterministic R1 behavior.

CI / Tooling
- Spec Kit: Not yet initialized with upstream CLI. A spec-bootstrap scaffold exists in spec/bootstrap. The upstream GitHub Spec Kit CLI should be run locally or in CI once maintainers approve the baseline.

Next actions (engineering pass)
1. Replace scaffolding with full baseline (this commit). 2. Author project constitution and owner assignments. 3. Add QA/release gates and R2 feature spec (done here as first draft). 4. After QA and sign-off, run upstream Spec Kit CLI to initialize toolchain and add CI validations.
