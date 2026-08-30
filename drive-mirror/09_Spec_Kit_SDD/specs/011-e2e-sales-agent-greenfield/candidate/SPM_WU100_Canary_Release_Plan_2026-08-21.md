# SPM WU100 — Canary Release Plan (OWNER THRESHOLDS APPROVED)

Date: 2026-08-25
Feature: `011-e2e-sales-agent-greenfield`
Release candidate: `SPM_E2E_Sales_Agent_RC3_CERTIFIED_LEAD_ADAPTER_2026-08-25`
Status: **THRESHOLDS APPROVED — production cutover remains BLOCKED pending final targeted RC3 regression, final freeze/hash, and explicit owner activation approval.**

## 1. Entry evidence completed
- WU99 authoritative runtime suite: 96/96 PASS.
- Planned runtime invocations: 106/106 completed.
- Failure injection: 15/15 PASS.
- 62-intent runtime coverage demonstrated.
- Manual semantic review complete for EN/AR/FR/mixed cases.
- R1 protected outcomes: 10/10 PASS.
- Lead/CRM adapter certification V3: 6/6 PASS.
- RC3 production static QA: PASS.
- Production Redis namespace configured as `spm:prod:sales:*`.
- Scheduling/booking execution: EXCLUDED.
- Human handoff execution: EXCLUDED.
- Payment execution: EXCLUDED.
- External follow-up execution: EXCLUDED.
- Runtime rollback drill: PASS, n8n execution ID 2276.
- Rollback baseline SHA-256: `8450550bf2e33ee161a034deea4be0f0d6667959716e891166d0da6bb149dbd2`.

## 2. Approved rollout stages
| Stage | Minimum successful conversations | Minimum observation |
|---|---:|---:|
| 5% | 20 | 24 hours |
| 20% | 50 | 24 hours |
| 50% | 100 | 24 hours |
| 100% | N/A | 48 hours close monitoring before WU100 closure |

Advancement requires BOTH the minimum conversation count and the minimum observation time.

## 3. Approved operational thresholds
- Maximum overall workflow/runtime execution error rate: **2% per stage**.
- p95 end-to-end chatbot response latency: **20 seconds maximum per stage**.
- OpenAI average cost ceiling: **US$0.05 per conversation**.
- OpenAI anomaly alert: any single conversation estimated above **US$0.10** requires review before promotion.
- Redis/state persistence failure rate: **0%**.
- Handoff failure threshold: **N/A — live handoff execution is excluded from this release**.
- Scheduling/booking execution count: **0**.
- Payment execution count: **0**.
- External follow-up execution count: **0**.
- P0/P1 open defects: **0**.

## 4. Hard-stop invariants — zero tolerance
Immediately pause/rollback if any one occurs:
- false lead-created or lead-updated success;
- duplicate confirmed lead;
- correction applied to the wrong lead/session;
- promotional follow-up after sticky opt-out;
- false availability/scheduled/booking confirmation;
- booking confirmation without verified tool success and `booking_id`;
- PII/secret exposure beyond approved minimum;
- production write caused by test/harness traffic;
- invented discount/offer or unauthorized irreversible action;
- cross-student merge/corruption;
- any Redis/state persistence failure;
- any excluded booking/handoff/payment/follow-up adapter execution;
- any P0/P1 issue.

## 5. Monitoring dimensions
Track per stage and by language:
- conversations/executions and successful conversations;
- runtime error rate;
- p95 response latency;
- Redis read/write failures;
- knowledge/source retrieval failures;
- lead create/update/no-change/conflict outcomes;
- duplicate lead count;
- false-success violations;
- PII/security violations;
- OpenAI estimated cost/conversation;
- EN/AR/FR parity exceptions.

## 6. Remaining release gates
1. Final targeted RC3 regression.
2. Final static check, freeze, and SHA-256.
3. Explicit owner approval to activate the 5% canary.
4. 5% canary PASS.
5. 20% canary PASS.
6. 50% canary PASS.
7. 100% promotion + 48-hour monitoring.
8. Lock/tag and update PROJECT_STATE / CHANGELOG / durable evidence.

Current production decision: **NO-GO until gates 1–3 are complete.**
