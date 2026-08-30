# n8n Deployment Policy

## Source of truth
GitHub owns versioned workflow JSON, prompts, contracts, tests, state, and release evidence. n8n is the execution/runtime environment.

## Environments
Use at minimum:
- Development/Staging: AI-generated or human-authored changes may be imported/deployed here.
- Production: protected. No direct agent editing.

## Deployment flow

```text
Working Unit READY
→ isolated branch/worktree
→ update versioned n8n workflow artifact
→ validate JSON/graph/contracts
→ PR
→ staging deployment/import
→ smoke test
→ focused regression
→ broader regression when impact warrants it
→ review
→ approval
→ merge/release
→ production promotion
→ lock/version evidence
```

## Workflow identity rules
- New test candidates must be inactive by default.
- Do not reuse a production workflow identity for disposable test copies.
- Frozen release candidates are immutable.
- A code/configuration change to a frozen candidate creates a new release candidate and triggers targeted regression again.

## Runtime evidence
For AI conversation changes, static JSON validation alone is insufficient. Capture the applicable runtime evidence, including intent/routing result, structured entities/state, answer, proposed action, actual tool/action evidence, and PASS/FAIL.

## Hard-stop examples
Do not promote when any of these occur:
- false lead/CRM success;
- false booking/availability/scheduling success;
- invented pricing/discount/refund/payment claim;
- opt-out violation;
- cross-student state merge;
- raw PII/secrets in telemetry;
- unsafe production write;
- critical runtime regression.

## n8n integration modes
Preferred order:
1. Native n8n source-control/environments when available.
2. Controlled n8n API deployment from CI/automation.
3. Manual staging import as an interim path, still with GitHub as the source of truth.

Credentials and secrets must remain in n8n/secret storage and must not be committed to GitHub workflow artifacts.
