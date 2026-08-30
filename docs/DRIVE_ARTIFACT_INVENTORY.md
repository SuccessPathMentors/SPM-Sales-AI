# Drive Artifact Inventory — Migration Control

Status: ACTIVE MIGRATION INVENTORY
Audit date: 2026-08-30
Purpose: Track Drive-native engineering/release artifacts that must be mirrored or explicitly retained as external/archive references before GitHub source-of-truth cutover.

## Large/text transport exceptions
| Artifact | Drive ID | Size | Migration |
|---|---|---:|---|
| `PROJECT_STATE.md` | `1R7nQEZstCUdHtx3LmH01_O2oHNMpqtZR` | 42,464 B | PENDING_EXACT_TEXT_TRANSPORT — historical snapshot; current reconciled state is `docs/STATE.yaml` |
| `CHANGELOG.md` | `1frxBHSbh2sk6qniuDyKXfh9o0Qpb5vBz` | 22,376 B | PENDING_EXACT_TEXT_TRANSPORT |
| `AI_Agent_System_Message_fixed.md` | `1K_r-0A-HTnya8dUyYiz6sQqi_QpP0hIz` | ~21 KB | PENDING_EXACT_TEXT_TRANSPORT |
| `Success_Path_Mentors_Stage_10_Testing_TEMPLATE.xlsx` | `10VhfqZdNg9s6OtfjUCGBoVf_dTv5X0uT` | 18,768 B | PENDING_BINARY / external evidence exception candidate |

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
| Artifact | Drive ID | Migration |
|---|---|---|
| `wu87-static-qa.md` | `1Yi0_rZjAgQjm3DMp7HxurtXISnEPa0wApBUYTnQhozw` | MIRRORED |
| `wu88-classifier-qa.md` | `1RTSvSCYQwHE1ZMZ1h38hj8d-GP20ZfQ_fHn9B7fczAQ` | MIRRORED — canonical |
| `wu88-classifier-static-qa.md` | `1EH1TzpHk-40Viev-l5jmataADeZoaAtIOcmjQ-cyxXc` | MIRRORED under `checklists/history/` |
| alternate `wu88-classifier-qa.md` | `1GJqRI-SW3mz9w6CiYnL1IU7lSKANvSJvszxbKalEvDc` | MIRRORED under `checklists/history/` |
| `wu89-entity-normalization-static-qa.md` | `1X0gFKmEqCv_3nFBKMm5L-Xi0i8Q5OEE5_aFFJzdU1Gw` | MIRRORED |
| `wu90-state-journey-static-qa.md` | `1fsNdnbBVkN0S-7LSioBh6sJn87cpRIaSWPeFcn1rj2E` | MIRRORED |
| `wu91-knowledge-source-gates-qa.md` | `1rB3AVTdoOvkHjRLZdYw9hfE9LKY0V5zEitoa6RRQANA` | MIRRORED |
| `wu92-sales-agent-core-qa.md` | `1vEyjtobl0j12G4TZGRMn5KHvEv5c32_NScPPCLd9_yM` | MIRRORED |
| `wu93-commercial-objections-qa.md` | `1HZtO7bfKYQt_QBsoyzVT805-CZsCsVW5oyFzno1-bHs` | MIRRORED |
| `wu94-trial-scheduling-truth-layer-qa.md` | `1-ZX80Gxueh2hNpiCuoc6af6d_r_QG6S785LDHzzCwaI` | MIRRORED |
| `wu95-deterministic-lead-conversion-qa.md` | `1qnyucYlTfZVjnCQZ69IJi5G4tNCCJ_qEMiINtC9wMxc` | MIRRORED |
| `wu96-nurture-optout-support-qa.md` | `1RS1rDKmOW1OtC2PhO0qxkRZ2hgTIK8wT7UnF9GKT750` | MIRRORED |
| `wu97-reliability-privacy-security-qa.md` | `176uT41iHywIpKggDETZdkXUeuL-5ADNAFDXqfyPTHdc` | MIRRORED |
| `SPM_WU98_Offline_Regression_Report_2026-08-21.md` | `1N0qTBaYqUxg7IAByD2rIokvGrY7Ms23H` | MIRRORED |
| `SPM_WU98_Offline_QA_2026-08-21.json` | `1L2Ae-HC2-Q5lWxa15NozZohFI9Zjr7et` | MIRRORED |

Older alternate QA documents discovered outside the canonical checklist set are retained for historical review or will be mirrored under `checklists/history/`; they must not override the canonical artifact or later dated release evidence.

## Greenfield candidate / release artifacts
| Artifact | Drive ID | Size | Migration |
|---|---|---:|---|
| `SPM_E2E_Sales_Agent_Greenfield_WU90_Durable_State_Journey_2026-08-20.json` | `12HSIY0QI1hEfc-BIrF3PgT-TolmQ7FUX` | ~73 KB | PENDING_TRANSPORT |
| `SPM_E2E_Sales_Agent_Greenfield_WU91_Knowledge_Source_Gates_2026-08-20.json` | `1QLZVacJRLYp51rOk3ZVJkqDQHMx2rFxu` | ~106 KB | PENDING_TRANSPORT |
| `SPM_E2E_Sales_Agent_Greenfield_WU92_Consultative_Sales_Agent_Core_2026-08-20.json` | `1VVcihcEgq0WYSPv2sWUV2FutIl_XFx_L` | ~126 KB | PENDING_TRANSPORT |
| `SPM_E2E_Sales_Agent_Greenfield_WU93_Commercial_Objections_2026-08-20.json` | `1SvjJvCAXZHu5cs30QGJ7Eg7bndXuEn1O` | ~143 KB | PENDING_TRANSPORT |
| `SPM_E2E_Sales_Agent_Greenfield_WU94_Trial_Scheduling_Truth_Layer_2026-08-20.json` | `1F_jrTDDgwz6t_IzJsgb3YAPvz2dKt6Yp` | ~156 KB | PENDING_TRANSPORT |
| `SPM_E2E_Sales_Agent_Greenfield_WU95_Deterministic_Lead_Conversion_2026-08-20.json` | `1CWlgLs4cdU2L7JkKK7X8hP_CzIGwe7dL` | ~199 KB | PENDING_TRANSPORT |
| `SPM_E2E_Sales_Agent_Greenfield_WU96_Nurture_OptOut_Support_Overrides_2026-08-20.json` | `19LK97ZBtwqgOR9431ELLmYbulA0XKQcj` | ~220 KB | PENDING_TRANSPORT |
| `SPM_E2E_Sales_Agent_Greenfield_WU97_Reliability_Privacy_Security_2026-08-21.json` | `1W6oT_XNGqL9YlUS85kKM7m424avdUYzW` | ~236 KB | PENDING_TRANSPORT |
| `SPM_WU98_Multilingual_RedTeam_Expansion_64_2026-08-21.json` | `1NRIcMLbpXNEDimWm0MzMn1TaVicIJb6W` | ~42 KB | PENDING_TRANSPORT |
| `SPM_WU98_Multilingual_RedTeam_Expansion_64_2026-08-21.csv` | `1jLddk-CAzqtTRzltvzoJeI9-MNaam6By` | ~17 KB | PENDING_TRANSPORT |
| `SPM_E2E_Sales_Agent_Greenfield_WU99_Runtime_Testable_2026-08-21.json` | `18fONdO3ZCs7z0QALTrfVftbz-VpKnTTH` | ~237 KB | PENDING_TRANSPORT — TEST ONLY |
| `SPM_WU99_Runtime_Certification_Harness_96_2026-08-21.json` | `1luSgx1Kod1kDGpXWuQM4Iq9u8lKUCyHY` | ~107 KB | PENDING_TRANSPORT |
| `SPM_WU99_Runtime_Certification_Plan_96_2026-08-21.json` | `1Bijgsn5VqvVXQW58J3YvEI3PJCXtGTur` | ~73 KB | PENDING_TRANSPORT |
| `SPM_WU100_Release_Manifest_TEMPLATE_2026-08-21.json` | `1AjtFtWmt1uWmfeR_8q3QxQIEvS9aOdMv` | ~2.5 KB | MIRRORED |
| `SPM_WU100_Canary_Release_Plan_2026-08-21.md` | `1aGzxesZROle9btwHPkq8_BqG3HjQ3gO6` | ~3.7 KB | MIRRORED |
| `SPM_WU100_RC3_Final_Targeted_Regression_Plan_2026-08-25.md` | `1KEoAq4Uzk85rGlTQwF6P4Uiyyq4DLBLK` | ~2.6 KB | MIRRORED |

## WU99 / WU100 checklists and evidence
| Artifact | Drive ID | Migration |
|---|---|---|
| `SPM_WU99_Runtime_Certification_Runbook_2026-08-21.md` | `1DWptnSM-0wL7GAnJ2BJ5ldbIAWrmp31i` | MIRRORED |
| `SPM_WU99_Preflight_QA_2026-08-21.json` | `1pFZdMCPmpoKMsvonksUjLqB1MvYHB8Ne` | MIRRORED — historical pre-runtime state |
| `SPM_WU99_Runtime_Evidence_Ledger_96_2026-08-21.csv` | `11HFxZ7exOhjJHnmgMrenhiPzbEd_tLOT` | MIRRORED — historical NOT_RUN template; later aggregate completion comes from later release docs |
| `SPM_WU99_Failure_Injection_Matrix_2026-08-21.csv` | `1C4MgHOyEL3fzVEQtd7d1dkwZiP5LGh0d` | MIRRORED — historical NOT_RUN template; later docs report 15/15 PASS |
| `SPM_WU100_Rollback_Runbook_2026-08-21.md` | `1zI6NHEPUjOBC0nkH4GDiRbGqN3F0emyG` | MIRRORED — historical runbook wording retained |
| `SPM_WU100_Canary_Monitoring_Gates_2026-08-21.csv` | `1RVQ-SJWSdjQqTNMqkOuMPzgG1VithdMT` | MIRRORED — older TBD threshold template; later owner-approved plan supersedes thresholds |
| `SPM_WU100_Preparation_QA_2026-08-21.json` | `1zYXVri42DhEQLa9ZwKXYIWeKzZPJTXlI` | MIRRORED |
| `SPM_WU100_Production_Approval_Checklist_2026-08-21.md` | `1cfE5Q6znBrzNRp-JPJ5QdtFrJZiDwceo` | MIRRORED — updated 2026-08-25 |
| `greenfield-release-gate.md` | `1LrzuDkFaJgRa8ie2DAinC-PUMs7hFFpJRgBCx7AWJF4` | MIRRORED |

## Legacy/current workflow artifacts
| Artifact | Drive ID | Migration |
|---|---|---|
| `ChatBotMSE_v2_R1_LOCKED_2026-08-17.json` | `1UhOb7V7zLRa6ZXJrjMiDBZbJTH_LXIhe` | PENDING_TRANSPORT — LOCKED BASELINE |
| `ChatBotMSE_v2_R2_TOKEN_OPTIMIZED_2026-08-18.json` | `1Xb7KL-SxcZODbf7zlIohdwqOzj1` | PENDING_TRANSPORT |
| `ChatBotMSE_v2_Refactor_Working_Copy_2_PAUSED_2026-08-17.json` | `18wFMuXpMFTA-ZRt8_88OljwrspuX0ej9` | PENDING_TRANSPORT — DIAGNOSTIC |
| `ChatBotMSE_v2_FIXED.json` | `11NTBtzeNYfcODGQ-w8uHCDCnw-Tq61LL` | PENDING_TRANSPORT — SUPERSEDED REFERENCE |
| `Validated_Human_Handoff_FIXED.json` | `1WNifl9kf8Lv9zTvgy6OcoMt8BcDc6W08` | PENDING_TRANSPORT |

## Cutover-critical unresolved release artifact
`SPM_E2E_Sales_Agent_RC4_2_FINAL_FROZEN_2026-08-26.json` is referenced by later bootstrap/state material but was not found by exact Drive-name searches during this audit. Treat it as `UNVERIFIED_REFERENCE` until the actual artifact is located and its identity/hash is reconciled.

## Transfer policy
- Never recreate workflow JSON from screenshots, chat excerpts, or partial connector output.
- Copy the provider export exactly, then record hash/version identity.
- Do not commit secrets, tokens, API keys, private keys, credential payloads, or Redis connection strings.
- n8n credential references/names/IDs may appear in exported workflow metadata; actual secret material remains in the runtime credential store.
- TEST-only WU99 SUT must never be promoted directly to production.
- Historical templates are preserved, but later dated release evidence takes precedence for status reconciliation.
