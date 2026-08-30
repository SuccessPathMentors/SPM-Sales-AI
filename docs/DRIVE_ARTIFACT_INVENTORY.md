# Drive Artifact Inventory — Migration Control

Status: ACTIVE MIGRATION INVENTORY — MIG-002 EXACT TRANSPORT COMPLETE
Audit date: 2026-08-30
Purpose: Track Drive-native engineering/release artifacts mirrored into GitHub and distinguish current runtime authority from historical/archive evidence.

## Exact transport summary

The MIG-002 batch transported **30 provider-original artifacts / 3,273,938 bytes**. All 30 matched the locally computed Git blob SHA-1 and byte length after GitHub upload. Final placement commit: `86ec918bb75e919df67d167ae3e3e67c040c633c`. Detailed SHA-256 and Git blob identities are recorded in `docs/MIG-002_EXACT_TRANSPORT_MANIFEST_2026-08-30.csv`.

The current live n8n production export was transported separately and is also exact-verified:
- `n8n/workflows/production/SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json`
- n8n workflow ID `CMBMpxX5AqqK2UTn`
- 330,119 bytes
- SHA-256 `680496f2b68b13dd7105e72fd132a2066d70ec969e6e0675f138ebb1fb16fe39`
- Git blob `58d1e9cc45085909dff91d7a9d07138486e72c76`
- status: `MIRRORED_EXACT_CURRENT_PRODUCTION_EVIDENCE`

## Large/text artifacts
| Artifact | Drive ID | Size | Migration |
|---|---|---:|---|
| `PROJECT_STATE.md` | `1R7nQEZstCUdHtx3LmH01_O2oHNMpqtZR` | 42,464 B | `MIRRORED_EXACT` at `drive-mirror/00_START_HERE/PROJECT_STATE.md`; historical snapshot only; current state is `docs/STATE.yaml` |
| `CHANGELOG.md` | `1frxBHSbh2sk6qniuDyKXfh9o0Qpb5vBz` | 22,376 B | `MIRRORED_EXACT` at `drive-mirror/06_History_Decisions/CHANGELOG.md` |
| `AI_Agent_System_Message_fixed.md` | `1K_r-0A-HTnya8dUyYiz6sQqi_QpP0hIz` | 21,315 B | `MIRRORED_EXACT` at `drive-mirror/02_Current_Architecture/AI_Agent_System_Message_fixed.md` |
| `Success_Path_Mentors_Stage_10_Testing_TEMPLATE.xlsx` | `10VhfqZdNg9s6OtfjUCGBoVf_dTv5X0uT` | 18,768 B | `MIRRORED_EXACT`; XLSX structure validated |

## 011 Greenfield core documents
| Artifact | Drive ID | Migration |
|---|---|---|
| `spec.md` | `1XyZ0duRi7TdenNGY1_zuyyXrcXVYz8x8ySsCA5J_qdA` | MIRRORED |
| `plan.md` | `1isrBRSJ08YqRDCaiHtS_kN1ikCTnJeFfVvRrfPMCg8A` | MIRRORED |
| `work-units.md` | `1uO-cCO28Pzi1euQ7rTVlwPks0w2d4pxbN_j2gRtmLSk` | MIRRORED |
| `tasks.md` | `1MtiLL9SC47XEs4Zq-eftETLWdRjg8ANV_ARn_LE9A1s` | MIRRORED |
| `contracts.md` | `1R-Fssb6VjDEKazwsEFIsYPAbyXWokVXlpo1El67utpY` | MIRRORED |
| `wu88-analysis.md` | `12_XjLs2RcFrDADC9wzcfdTHCdpIwNNaQp_WSkZMkQyE` | MIRRORED |

## WU87–WU98 QA / evidence
Canonical QA/evidence remains mirrored under `drive-mirror/09_Spec_Kit_SDD/specs/011-e2e-sales-agent-greenfield/checklists/`:
- WU87 static QA
- WU88 classifier QA plus historical alternates under `checklists/history/`
- WU89–WU97 static/contract QA
- WU98 offline regression report and offline QA JSON

Historical duplicates never override canonical or later dated release evidence.

## Greenfield candidate / runtime-test artifacts
All identified retained candidate/runtime artifacts below are now `MIRRORED_EXACT` under `drive-mirror/09_Spec_Kit_SDD/specs/011-e2e-sales-agent-greenfield/candidate/`:

| Artifact | Drive ID | Size | Migration |
|---|---|---:|---|
| `SPM_E2E_Sales_Agent_Greenfield_WU87_Skeleton_2026-08-20.json` | `18jIsNNGPsAXkWcbcawy4f40WGn7mjFa4` | 18,913 B | MIRRORED_EXACT |
| `SPM_E2E_Sales_Agent_Greenfield_WU88_62Intent_Classifier_2026-08-20.json` | canonical retained copy; duplicate Drive copies byte-identical | 36,595 B | MIRRORED_EXACT |
| `SPM_E2E_Sales_Agent_Greenfield_WU88_Classifier_2026-08-20.json` | `1FNRkyVZ0l8dg9G2d-vw31iH4dGopOmR2` | 33,172 B | MIRRORED_EXACT |
| `SPM_E2E_Sales_Agent_Greenfield_WU89_Entities_2026-08-20.json` | `1Jgv1aPq66_Dxq5HNpaJww3goFhXNhuWx` | 56,109 B | MIRRORED_EXACT |
| `SPM_E2E_Sales_Agent_Greenfield_WU89_Entities_Normalization_2026-08-20.json` | `1G6yax_umfZNI7sqgjK4jUxbLUb2Qrdvf` | 60,659 B | MIRRORED_EXACT |
| `SPM_E2E_Sales_Agent_Greenfield_WU90_State_Journey_2026-08-20.json` | `1xcyh__04InbTQspnGaYG2X8eSHXYyFzU` | 66,532 B | MIRRORED_EXACT |
| `SPM_E2E_Sales_Agent_Greenfield_WU90_Durable_State_Journey_2026-08-20.json` | `12HSIY0QI1hEfc-BIrF3PgT-TolmQ7FUX` | 73,222 B | MIRRORED_EXACT |
| `SPM_E2E_Sales_Agent_Greenfield_WU91_Source_Gates_2026-08-20.json` | `1l8ntvnLO5nbLRxZk4YqKZKFkTC84Jo_H` | 81,411 B | MIRRORED_EXACT |
| `SPM_E2E_Sales_Agent_Greenfield_WU91_Knowledge_Source_Gates_2026-08-20.json` | `1QLZVacJRLYp51rOk3ZVJkqDQHMx2rFxu` | 106,407 B | MIRRORED_EXACT |
| `SPM_E2E_Sales_Agent_Greenfield_WU92_Sales_Agent_Core_2026-08-20.json` | `1-CEjsNDHsBz5SuQbh4NXg5AwPsLJI8HA` | 103,529 B | MIRRORED_EXACT |
| `SPM_E2E_Sales_Agent_Greenfield_WU92_Consultative_Sales_Agent_Core_2026-08-20.json` | `1VVcihcEgq0WYSPv2sWUV2FutIl_XFx_L` | 126,274 B | MIRRORED_EXACT |
| `SPM_E2E_Sales_Agent_Greenfield_WU93_Commercial_Objections_2026-08-20.json` | `1SvjJvCAXZHu5cs30QGJ7Eg7bndXuEn1O` | 142,822 B | MIRRORED_EXACT |
| `SPM_E2E_Sales_Agent_Greenfield_WU94_Trial_Scheduling_Truth_Layer_2026-08-20.json` | `1F_jrTDDgwz6t_IzJsgb3YAPvz2dKt6Yp` | 155,758 B | MIRRORED_EXACT |
| `SPM_E2E_Sales_Agent_Greenfield_WU95_Deterministic_Lead_Conversion_2026-08-20.json` | `1CWlgLs4cdU2L7JkKK7X8hP_CzIGwe7dL` | 199,434 B | MIRRORED_EXACT |
| `SPM_E2E_Sales_Agent_Greenfield_WU96_Nurture_OptOut_Support_Overrides_2026-08-20.json` | `19LK97ZBtwqgOR9431ELLmYbulA0XKQcj` | 220,277 B | MIRRORED_EXACT |
| `SPM_E2E_Sales_Agent_Greenfield_WU97_Reliability_Privacy_Security_2026-08-21.json` | `1W6oT_XNGqL9YlUS85kKM7m424avdUYzW` | 235,801 B | MIRRORED_EXACT |
| `SPM_WU98_Multilingual_RedTeam_Expansion_64_2026-08-21.json` | `1NRIcMLbpXNEDimWm0MzMn1TaVicIJb6W` | 42,226 B | MIRRORED_EXACT |
| `SPM_WU98_Multilingual_RedTeam_Expansion_64_2026-08-21.csv` | `1jLddk-CAzqtTRzltvzoJeI9-MNaam6By` | 16,916 B | MIRRORED_EXACT |
| `SPM_E2E_Sales_Agent_Greenfield_WU99_Runtime_Testable_2026-08-21.json` | `18fONdO3ZCs7z0QALTrfVftbz-VpKnTTH` | 236,748 B | MIRRORED_EXACT — TEST ONLY |
| `SPM_WU99_Runtime_Certification_Harness_96_2026-08-21.json` | `1luSgx1Kod1kDGpXWuQM4Iq9u8lKUCyHY` | 106,626 B | MIRRORED_EXACT — TEST ONLY |
| `SPM_WU99_Runtime_Certification_Plan_96_2026-08-21.json` | `1Bijgsn5VqvVXQW58J3YvEI3PJCXtGTur` | 73,121 B | MIRRORED_EXACT |

WU100 release/canary plans, QA, checklists, monitoring gates, and release-manifest template were already mirrored before the exact-transport batch.

## Legacy/current workflow artifacts
All five identified Drive workflows are now exact-mirrored under `drive-mirror/03_Workflows_Current/`:

| Artifact | Drive ID | Migration |
|---|---|---|
| `ChatBotMSE_v2_R1_LOCKED_2026-08-17.json` | `1UhOb7V7zLRa6ZXJrjMiDBZbJTH_LXIhe` | MIRRORED_EXACT — LOCKED HISTORICAL BASELINE |
| `ChatBotMSE_v2_R2_TOKEN_OPTIMIZED_2026-08-18.json` | `1Xb7KL-SxcZODbf7zlHrbtlIohdwqOzj1` | MIRRORED_EXACT — HISTORICAL |
| `ChatBotMSE_v2_Refactor_Working_Copy_2_PAUSED_2026-08-17.json` | `18wFMuXpMFTA-ZRt8_88OljwrspuX0ej9` | MIRRORED_EXACT — DIAGNOSTIC/HISTORICAL |
| `ChatBotMSE_v2_FIXED.json` | `11NTBtzeNYfcODGQ-w8uHCDCnw-Tq61LL` | MIRRORED_EXACT — SUPERSEDED REFERENCE |
| `Validated_Human_Handoff_FIXED.json` | `1WNifl9kf8Lv9zTvgy6OcoMt8BcDc6W08` | MIRRORED_EXACT — STANDALONE HISTORICAL HANDOFF WORKFLOW |

Note: R1 locked and the paused refactor export are byte-identical in Drive despite their different historical labels; both filenames are retained because their roles differ.

## WU99 / WU100 evidence documents
The existing historical runbooks, preflight QA, runtime evidence ledger template, failure-injection template, WU100 approval checklist, rollback runbook, monitoring gates, preparation QA, and greenfield release gate remain mirrored verbatim. Historical `NOT_RUN` templates must not be rewritten to fabricate later execution results; later dated release/runtime evidence governs current status.

## Current release identity vs unresolved historical reference
The current production runtime identity is now independently verified as **RC4.3.3**, workflow ID `CMBMpxX5AqqK2UTn`, and its exact export is versioned in GitHub.

`SPM_E2E_Sales_Agent_RC4_2_FINAL_FROZEN_2026-08-26.json` remains an `UNVERIFIED_HISTORICAL_REFERENCE`: exact Drive searches did not locate that named artifact. It must not override or block the separately verified RC4.3.3 current runtime identity.

## Transfer / safety policy
- Never recreate workflow JSON from screenshots, chat excerpts, or partial connector output.
- Provider exports are copied exactly and identity verified before becoming evidence.
- Do not commit tokens, API keys, private keys, credential payloads, passwords, or Redis connection strings.
- Credential references/names/IDs in workflow metadata are allowed; secret values remain in the runtime credential store.
- WU99 Runtime-Testable SUT and harness are TEST ONLY and cannot be promoted directly to production.
- Historical templates/evidence are preserved; later dated current-state evidence takes precedence for status reconciliation.
