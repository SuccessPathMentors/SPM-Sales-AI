# Google Drive → GitHub Migration Manifest

Status: **COMPLETE — GITHUB ENGINEERING SOURCE-OF-TRUTH CUTOVER APPROVED**  
Cutover date: 2026-08-30  
Repository: `SuccessPathMentors/SPM-Sales-AI`  
Cutover PR: #4  
Cutover merge commit: `561788510bea13d9a9fea85d5ce0841b846c8432`

## Authority model after cutover
- **GitHub `main`** — approved engineering source of truth for versioned specs, state, Working Units, workflow JSON, tests, decisions, release evidence, deployment policy and change history.
- **n8n** — runtime/deployment target. It is not the engineering version-control authority.
- **Google Drive** — archive/secondary historical reference. Historical files remain useful evidence but do not override GitHub current state.
- **Google Sheets** — live mutable operational/knowledge data where runtime mutability is required; GitHub stores governance/schema/version references, not credentials.

Cutover changes engineering authority only. It does **not** authorize n8n Production activation, production auto-deploy, or direct AI/GitHub → Production changes.

## Migration gates
| Gate | Result | Primary evidence |
|---|---|---|
| MIG-001 — runtime identity/dependencies | PASS / CLOSED | Issue #5; `docs/MIG-001_N8N_RUNTIME_INVENTORY.md` |
| MIG-002 — exact artifact transport | PASS / CLOSED | Issue #6; `docs/MIG-002_EXACT_TRANSPORT_MANIFEST_2026-08-30.csv` |
| MIG-003 — GitHub → n8n non-production deploy path | PASS / CLOSED | Issue #7; PR #9; `docs/MIG-003_N8N_NONPROD_DEPLOYMENT.md` |
| MIG-004 — historical evidence precedence | PASS / CLOSED | Issue #8; `docs/MIG-004_RELEASE_EVIDENCE_PRECEDENCE.md` |
| Cutover review | APPROVED / COMPLETE | PR #4; `docs/CUTOVER_REVIEW_2026-08-30.md` |

## Verified current Production runtime
- Workflow/export: `SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json`
- n8n workflow ID: `CMBMpxX5AqqK2UTn`
- Runtime evidence: successful execution `2539`
- Nodes: `114`
- Disabled nodes: `0`
- Native `Execute Workflow` nodes: `0`
- Exact GitHub artifact: `n8n/workflows/production/SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json`
- Bytes: `330119`
- SHA-256: `680496f2b68b13dd7105e72fd132a2066d70ec969e6e0675f138ebb1fb16fe39`
- Exact transport: **PASS**

Current Production scope remains explicitly bounded:
- Lead/CRM write adapter: enabled current scope
- Scheduling/booking execution: excluded
- Human handoff contract: present
- Human handoff live execution: disabled/not configured
- Payment execution: excluded
- External follow-up execution: excluded

The standalone historical `Validated_Human_Handoff_FIXED.json` remains preserved, but RC4.3.3 contains no native `Execute Workflow` dependency on it.

## Exact artifact migration
MIG-002 verified the Drive transport batch:
- artifacts: `30`
- total bytes: `3,273,938`
- exact matches: `30/30`
- mismatches: `0`
- JSON parsing: PASS for JSON artifacts
- Stage 10 XLSX structure: PASS
- preliminary secret-pattern scan: no obvious secret values detected

The exact transport includes historical `PROJECT_STATE.md`, `CHANGELOG.md`, legacy/reference workflows, QA material and retained WU87–WU99 artifacts. The WU99 Runtime-Testable SUT remains **TEST ONLY** and cannot be promoted directly to Production.

Detailed integrity references:
- `docs/ARTIFACT_INTEGRITY_REGISTER.yaml`
- `docs/MIG-002_EXACT_TRANSPORT_MANIFEST_2026-08-30.csv`

## Non-production deployment path
MIG-003 proved the reviewed GitHub → n8n DEV/STAGING path.

Evidence includes:
- API read-only smoke: PASS
- exact RC4.3.3 dry-run: PASS / zero writes
- side-effect-free STAGING create: PASS
- fail-closed missing-target test: PASS
- deterministic update of the same STAGING target: PASS

STAGING proof workflow:
- name: `[STAGING] MIG003_STAGING_CANARY`
- ID: `BIDVhNCRbj9dvH1t`
- active: `false`
- credentials: `0`
- external side-effect nodes: `0`

Long-term deployment automation:
- `.github/workflows/n8n-nonprod-deploy.yml`
- `scripts/n8n/deploy_nonprod.py`
- `n8n/deployment/nonprod-policy.json`

Safety invariants:
- DEV/STAGING only
- Production workflow ID `CMBMpxX5AqqK2UTn` hard-denied
- active/published targets refused
- exact SHA-256 required for apply
- implicit create refused
- no activate/publish/deactivate/delete endpoint in the deployer
- post-write GET + inactive validation required
- API key limited to workflow create/read/update

## Temporary bootstrap cleanup
The default-branch MIG-003 bootstrap was only a temporary mechanism for first live API validation. After explicit owner cutover approval:
- `.github/workflows/mig-003-bootstrap.yml` — removed from `main`
- `docs/MIG-003_BOOTSTRAP_NOTE.md` — removed from `main`

The reviewed generic non-production workflow is now the retained automation path.

## Historical release evidence precedence
Historical Drive snapshots, runbooks and ledgers remain immutable audit evidence. They are not rewritten to imitate later results.

Authority rules:
1. `docs/STATE.yaml` answers current engineering state.
2. verified current n8n runtime identity/exact export answers what is live now.
3. later dated verified evidence may supersede older preparation-state claims for current-state use.
4. older `NOT_RUN`, preparation-only or unknown-runtime statements remain valid historical checkpoints only.
5. unsupported chronology is not inferred.

Known later WU99 aggregate evidence records:
- 96/96 automated runtime PASS
- 106/106 invocations complete
- 15/15 failure injection PASS
- R1 protected regression 10/10 PASS
- manual semantic review complete
- EN/AR/FR parity accepted
- zero P0/P1 in later certification evidence

RC4.2 remains an `UNVERIFIED_HISTORICAL_REFERENCE` and cannot override independently verified RC4.3.3.

The fact that RC4.3.3 is live does not prove undocumented intermediate 5%/20%/50%/100% canary-stage history.

## Numbering and next phase
Migration work used `MIG-*` identifiers and does not consume Phase 2 WU numbers.

Authoritative Phase 2 backlog remains:
- WU-101 Conversation Analytics
- WU-102 Unanswered Question Queue
- WU-103 Knowledge Maintenance Loop
- WU-104 Short Query & Ambiguity UX
- WU-105 Golden Intents Optimization
- WU-106 Dialect & Language Coverage
- WU-107 Human Handoff Adapter
- WU-108 WhatsApp Staff Notification
- WU-109 Conversation Outcome KPIs
- WU-110 Optimization Regression Pack

Cutover completion makes WU-101 eligible for planning, but no Working Unit starts automatically without an explicit work decision.

## Production control after cutover
The approved path remains:

`GitHub → DEV/STAGING → validation/runtime tests → human approval → separate Production release process`

The following remain false/unauthorized:
- `production_auto_deploy`
- GitHub-driven Production activation
- direct AI → Production deployment

Future Production changes continue to require explicit owner/release approval.
