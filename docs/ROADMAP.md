# SPM Sales AI — Automated Delivery Roadmap

## Objective
Use GitHub as the control plane and source of truth, with n8n as the runtime. Each Working Unit moves through a controlled state machine, may be delegated to isolated workers when safe, and is locked after its required gates pass.

## Delivery spine

```text
Requirement
  ↓
Clarify only if needed
  ↓
Plan + acceptance criteria
  ↓
One material critique
  ↓
Freeze scope / contracts
  ↓
Create Working Unit + dependencies
  ↓
Orchestrator finds eligible work
  ↓
Delegate independent work in parallel
  ↓
Implement on isolated branch/worktree
  ↓
Static tests / contract tests
  ↓
Deploy to n8n staging/test
  ↓
Runtime / conversation regression
  ↓
One code/workflow review
  ↓
Fix material findings (max 2 cycles)
  ↓
Approval gate when required
  ↓
Merge / release
  ↓
LOCK Working Unit
  ↓
Recalculate dependency graph
```

## Current migration lane — MUST complete before deployment automation

```text
MIG-001 Runtime Identity Reconciliation
        ↓
MIG-002 Exact Artifact Transport + SHA Verification
        ↓
MIG-003 GitHub → n8n Non-Production Deployment Automation
        ↓
Staging Import / Dry Run
        ↓
Runtime Evidence
        ↓
Human Approval Gate
        ↓
Production Promotion (separate release action only)
```

### MIG-001 — IN PROGRESS / BLOCKING
GitHub issue #5. Identify the actually active n8n main workflow and reverify the validated-handoff identity. Record workflow IDs, active state, environment, dependencies, artifact path/hash, and credential references without secret values. WU99 SUT/harness must be imported only as new inactive TEST workflows.

### MIG-002 — IN PROGRESS
GitHub issue #6. Transfer remaining raw Drive artifacts exactly, secret-scan them, verify SHA-256 before and after GitHub commit, and keep historical state artifacts explicitly non-authoritative for current release state.

### MIG-003 — BLOCKED BY MIG-001 + MIG-002
GitHub issue #7. Add the repeatable GitHub-controlled non-production import/update path to n8n only after runtime identity and exact artifact inputs are reconciled. Initial automation must not activate production.

### MIG-004 — RECONCILIATION CONTROL
GitHub issue #8. Preserve historical WU99/WU100 NOT_RUN snapshots as audit evidence while preventing them from overriding later reconciled release evidence in `docs/STATE.yaml`.

## Locking policy
A downstream agent may read a locked artifact but must not edit it. If a locked dependency needs change, create a Change Request, version the affected artifact, rerun impacted tests, and relock the new version.

## Baseline position
- WU-01 → WU-84: protected historical predecessors.
- WU-87 → WU-98: greenfield implementation/static/offline baseline exists.
- WU-99: full semantic runtime/E2E certification evidence gate; historical preparation snapshots and later execution evidence must be chronology-reconciled.
- WU-100: release/canary control layer; production activation remains a separate approval gate.
- New planned feature work begins at WU-101 unless explicitly mapped to unresolved certification/canary work.

## GitHub lifecycle
`BACKLOG → READY → IN_PROGRESS → REVIEW → TESTING → APPROVAL → DONE/LOCKED`

Use `BLOCKED` as a side state. Do not reopen a locked predecessor silently.

## n8n lifecycle
`GitHub artifact → identity check → staging/test import/deploy → smoke test → regression → runtime evidence → approval → production promotion`

Production is not a working canvas. Any production-bound change must exist first as a versioned GitHub artifact and pass the applicable gates.

## Parallel delegation rule
Parallel work is allowed only if:
1. dependencies are already locked/baselined;
2. workers do not own the same workflow nodes/files;
3. shared request/response/state contracts are frozen;
4. integration is performed after worker results converge.

## Minimal artifacts per Working Unit
- Working Unit specification;
- acceptance criteria;
- affected systems/workflow/nodes;
- dependency list;
- implementation commit/PR;
- static and runtime evidence as applicable;
- final lock/version reference.

## Stop conditions
Stop automation and set `BLOCKED` when:
- runtime workflow identity or environment is ambiguous;
- a locked business rule must change;
- production credentials/actions would be enabled without approval;
- runtime evidence required for certification is unavailable;
- a worker exceeds two material repair cycles;
- two parallel tasks would modify the same ownership boundary;
- a test detects false lead/booking/payment/handoff success, PII leakage, corrupted state, or other hard-stop invariant;
- the WU99 TEST-only SUT is proposed for direct production promotion.
