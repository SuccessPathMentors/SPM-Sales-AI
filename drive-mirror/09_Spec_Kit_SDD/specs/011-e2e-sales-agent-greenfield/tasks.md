# 011 Greenfield E2E Sales Agent — Tasks

Status: WU99 RUNTIME EXECUTION COMPLETE — FINAL EVIDENCE CONSOLIDATION PENDING; WU100 canary/production release BLOCKED

## Governance / Reset
- [x] G001 Freeze current production workflows as legacy/reference; no new feature work is based on patching their graph.
- [x] G002 Create `011-e2e-sales-agent-greenfield` Spec Kit feature.
- [x] G003 Define Sales Agent—not FAQ bot—as the primary product identity.
- [x] G004 Adopt WU84–WU86 as design/evidence inputs and start new implementation at WU87.
- [x] G005 Define WU87–WU100 sequence.

## WU87 — Architecture & Contracts
- [x] WU87-T01 Create a brand-new inactive n8n workflow with a new workflow ID.
- [x] WU87-T02 Add Chat Trigger and canonical session envelope.
- [x] WU87-T03 Add Redis Load Sales State node/subflow.
- [x] WU87-T04 Define `sales_state` JSON contract and non-destructive merge function.
- [x] WU87-T05 Define 62-intent classifier output schema.
- [x] WU87-T06 Define entity extraction/normalization output schema.
- [x] WU87-T07 Define journey-stage / next-best-action contract.
- [x] WU87-T08 Define source/tool gate resolver contract.
- [x] WU87-T09 Define Sales Agent structured output contract.
- [x] WU87-T10 Add deterministic action gateway skeleton with no production writes.
- [x] WU87-T11 Add telemetry envelope and execution correlation fields.
- [x] WU87-T12 Add test-mode flag and synthetic-session safeguards.
- [x] WU87-T13 Export candidate JSON and run static graph QA.
- [x] WU87-T14 Record architecture evidence and update PROJECT_STATE/CHANGELOG.

## WU88–WU90 — Understanding & State
- [ ] WU88 Implementation complete; 62-intent classifier + confidence/ambiguity routing built. Static + contract/router QA 129/129 PASS; n8n semantic runtime certification pending.
- [ ] WU89 Prototype implementation complete: entity normalization, correction precedence, multi-student profiles; static safety 16/16 PASS. Certification remains pending after WU88 runtime.
- [ ] WU90 Prototype implementation complete: test-namespace Redis durable state + explicit journey/NBA engine; static safety 16/16 PASS. Redis runtime certification pending.

## WU91–WU93 — Knowledge + Sales Core
- [ ] WU91 Prototype implementation complete: targeted read-only knowledge retrieval + source gates; static QA 19/19 PASS. Runtime certification pending.
- [ ] WU92 Prototype implementation complete: consultative Sales Agent core + structured output and deterministic safety guards; static QA 19/19 PASS. Runtime certification pending.
- [ ] WU93 Prototype implementation complete: deterministic pricing/package comparison, offer authorization boundary, objection guidance, commercial guard; static QA 17/17 PASS. Runtime certification pending.

## WU94–WU96 — Conversion Operations
- [ ] WU94 Prototype implementation complete: admin-controlled trial/scheduling truth layer, timezone/availability/booking guards; static QA 21/21 PASS + contract tests 8/8 PASS. Approved live adapter endpoint/credential not configured; runtime certification pending.
- [ ] WU95 Prototype implementation complete: canonical lead payload, consent/final-confirmation gate, read-only dedupe lookup, deterministic create/update/no-change/conflict decision, correction preserves lead_id, disabled/disconnected UPSERT reference, handoff contract, false-success guard; static QA 29/29 PASS + contract regression 14/14 PASS. Real write/handoff runtime adapters remain uncertified.
- [ ] WU96 Prototype implementation complete: communication precedence, sticky opt-out, consent-gated follow-up, need_to_think no-auto-follow-up, support-over-sales/handoff contract, read-only SALES_NURTURE context, false-execution guard; static QA 32/32 PASS + contract regression 15/15 PASS. Runtime communication adapters remain uncertified.

## WU97–WU100 — Certification
- [ ] WU97 Prototype implementation complete: input security before external calls, bounded model/read retries, lead-lookup fail-closed branch, unified reliability policy/error taxonomy, runtime health, fail-closed privacy/security guard, Telemetry V2 PII/session redaction; static QA 54/54 PASS + contract regression 18/18 PASS. Runtime certification pending.
- [ ] WU98 Offline regression pack complete: authoritative RT-001..RT-032 retained + RT-033..RT-096 expansion (64 new / 96 combined), 62/62 intent coverage, EN/AR/FR/mixed parity and red-team coverage; suite metadata QA 20/20 PASS + WU97 deterministic safety regression 44/44 PASS. Actual n8n LLM semantic/conversation runtime remains NOT_RUN and therefore WU98 certification remains pending.
- [ ] WU99 Runtime certification execution COMPLETE / FINAL EVIDENCE CONSOLIDATION PENDING: authoritative 96-case runtime suite completed 96/96 automated PASS with manual semantic remediation closed; 15/15 failure-injection PASS (FI-003/FI-007/FI-008 behavioral method deviations documented); final protected R1 regression rerun 10/10 automated PASS with 0 failures. Runtime-testable SUT remains TEST-only and must not be promoted directly. Final WU99 release status remains blocked until evidence ledger/execution identifiers are complete and owner acceptance of documented method deviations is recorded if required.
- [ ] WU100 Release-preparation package complete: canary plan, release-manifest template, rollback runbook, monitoring gates, production approval checklist, and preparation QA 12/12 PASS. Proposed canary profile 5%→20%→50%→100% is NOT owner-approved; operational latency/cost/error/volume/duration thresholds remain TBD. Actual clean immutable RC, rollback drill, owner approval, canary execution, production cutover, and lock/tag remain BLOCKED pending WU99 runtime PASS.

## Permanent Gates
- [x] 62/62 intent contract coverage (static mapping/guard contract).
- [ ] All irreversible actions deterministic and source-gated.
- [x] R1 lead-protection behaviors retained as regression outcomes (final targeted rerun 10/10 PASS).
- [ ] No false lead/booking/scheduling success.
- [ ] Sticky opt-out.
- [ ] Human handoff context preserved.
- [ ] EN/AR/FR parity for business logic.
- [ ] No P0/P1 before production cutover.

## Immediate Stop Point
Do not edit the current production workflow. WU99 runtime execution, semantic review, 15/15 failure injection, and final R1 protected regression are complete. Final certification remains BLOCKED only on evidence consolidation/execution identifiers and any required owner acceptance of documented behavioral method deviations. WU100 planning/package preparation is also complete, but release execution is BLOCKED. Import the 109-node WU99 Runtime-Testable SUT as a new inactive workflow, import the 5-node harness, bind the new SUT workflow ID, and run all 96 cases / 106 invocations plus the 15-case failure-injection matrix. Do NOT promote the WU99 testable SUT directly because it contains a TEST-only trigger. After WU99 PASS, generate a clean immutable production RC, remove all test-only paths, verify rollback, approve thresholds, record owner approval, then run canary. Production cutover remains unauthorized.

## Release 2 / Phase 2 Tasks — Approved Backlog, Deferred
Do not start these tasks until Release 1 is completed through WU-100, final workflow is frozen/certified, SHA recorded, and explicit production approval is complete.

- [ ] WU-101 Conversation Analytics — capture real customer intent/confidence/fallback/outcome signals safely.
- [ ] WU-102 Unanswered Question Queue — log no-match, low-confidence, ambiguous, repeated, misunderstood, unsupported, poor-feedback, and human-request cases.
- [ ] WU-103 Knowledge Maintenance Loop — review → approve → KB update → version → regression → publish → measure.
- [ ] WU-104 Short Query & Ambiguity UX — answer-first for clear short queries; 2–4 clarification options for ambiguous short queries.
- [ ] WU-105 Golden Intents Optimization — prioritize top 15–20 recurring commercial intents with stronger answers and regression coverage.
- [ ] WU-106 Dialect & Language Coverage — expand real Arabic dialect, EN/FR, spelling, code-switching, and short-query coverage using the 26k corpus plus real traffic.
- [ ] WU-107 Human Handoff Adapter — deterministic handoff record and success only after tool evidence.
- [ ] WU-108 WhatsApp Staff Notification — notify staff only after approved handoff execution succeeds.
- [ ] WU-109 Conversation Outcome KPIs — dashboard for answered %, clarification %, unanswered %, handoff %, top intents, top gaps, and lead conversion by intent.
- [ ] WU-110 Optimization Regression Pack — turn every approved real-world gap/fix into permanent regression tests.

Phase 2 priority rule: optimize from real customer traffic first. The key question is not “how many synthetic questions do we have?” but “what did real customers ask, where did the system fail or hesitate, and what should be approved and tested next?”
