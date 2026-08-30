# MIG-001 — n8n Runtime Identity Inventory

Status: OPEN / BLOCKING
GitHub issue: #5
Purpose: Resolve exact n8n runtime identities before any GitHub-driven import, update, runtime certification, or production activation.

## Authority rule
GitHub artifacts describe the intended workflow. n8n runtime identity must be evidenced from n8n itself. An exported JSON with `active=false` does not prove the currently active production workflow identity.

## Known evidence
| Role | Workflow | n8n ID | Active state evidence | Status |
|---|---|---|---|---|
| Validated handoff | `Validated Human Handoff` | `swhmNa0Goo0uYm1k` | previously verified `active=true` from runtime export evidence | REVERIFY IN MIG-001 |
| R2.5 main candidate/reference | `ChatBotMSE v2 - R2.5 Release Candidate Stable Efficient` | `vSc7cMIMFMEUdi7z` | verified export `active=false` | NOT PROOF OF ACTIVE MAIN |
| WU99 Runtime-Testable SUT | Greenfield WU99 test SUT | TBD after import | must remain inactive when imported | TEST ONLY |
| WU99 Harness | Runtime Certification Harness 96 | TBD after import | must remain inactive when imported | TEST ONLY |
| Current active main chatbot | UNKNOWN | UNKNOWN | must be read/exported from n8n | BLOCKING |

## Runtime record schema
For each relevant workflow record capture:

```yaml
workflow_name: ""
workflow_id: ""
environment: test|staging|production
active: false
role: production|test|harness|reference|rollback
n8n_updated_at: ""
github_artifact: ""
artifact_sha256: ""
credential_references: []   # names/IDs only; no secret values
execute_workflow_outbound: []
execute_workflow_inbound: []
evidence_source: ""
verified_at: ""
verified_by: ""
```

## Safe WU99 import sequence
1. Identify/export the actually ACTIVE main chatbot workflow in n8n. Do not infer from Drive or GitHub.
2. Reverify `Validated Human Handoff` identity/state and its callers.
3. Import `SPM_E2E_Sales_Agent_Greenfield_WU99_Runtime_Testable_2026-08-21.json` as a NEW workflow and keep it inactive.
4. Verify the imported SUT is the expected 109-node testable artifact and contains the TEST-only Execute Workflow Trigger.
5. Resolve only TEST credential references for Google Sheets, Redis, and OpenAI.
6. Import `SPM_WU99_Runtime_Certification_Harness_96_2026-08-21.json` as a NEW inactive workflow.
7. Bind only `Execute Greenfield SUT [CONFIGURE TARGET THEN ENABLE]` to the newly imported WU99 SUT ID, then enable only that node for test execution.
8. Do not overwrite or activate production workflows during MIG-001.

## WU99 immutable input identities
- Runtime-Testable SUT expected SHA-256: `a74b6443151eca02d3cc0b28126be96344a68326a389f6ac2951f54bcce0c6fc`.
- Runtime harness expected SHA-256: `965ae82f03cd8e3f7cfbf0bcd12ac859cf5618373c25590b861e02858f6f06ab`.
- Runtime plan expected SHA-256: `d1d03341603d8a3dfbbe6861a120d8ed13d15395f066c8b7eb6c592acdad7ad3`.

## Hard-stop rules
- Ambiguous active main workflow identity → STOP.
- Ambiguous environment → STOP.
- Import would overwrite an existing production workflow → STOP.
- Target SUT ID in harness does not match newly imported TEST SUT → STOP.
- Secret material appears in any GitHub artifact/log → STOP and remove before proceeding.
- WU99 test SUT is proposed for direct production promotion → STOP.

## Exit gate
MIG-001 may close only when the runtime inventory is complete, the active main identity is evidenced, WU99 SUT/harness identities are captured after safe import, dependency links are recorded, and `docs/STATE.yaml` plus the migration manifest are updated from evidence rather than inference.
