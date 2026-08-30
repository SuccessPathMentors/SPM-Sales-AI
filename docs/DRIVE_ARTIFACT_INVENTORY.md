# Drive Artifact Inventory — Migration Control

Status: ACTIVE MIGRATION INVENTORY
Audit date: 2026-08-30
Purpose: Track Drive-native engineering/release artifacts that must be mirrored or explicitly retained as external/archive references before GitHub source-of-truth cutover.

## 011 Greenfield core documents
| Artifact | Drive ID | Migration |
|---|---|---|
| `spec.md` | `1XyZ0duRi7TdenNGY1_zuyyXrcXVYz8x8ySsCA5J_qdA` | MIRRORED |
| `plan.md` | `1isrBRSJ08YqRDCaiHtS_kN1ikCTnJeFfVvRrfPMCg8A` | MIRRORED |
| `work-units.md` | `1uO-cCO28Pzi1euQ7rTVlwPks0w2d4pxbN_j2gRtmLSk` | MIRRORED |
| `tasks.md` | `1MtiLL9SC47XEs4Zq-eftETLWdRjg8ANV_ARn_LE9A1s` | MIRRORED |
| `contracts.md` | `1R-Fssb6VjDEKazwsEFIsYPAbyXWokVXlpo1El67utpY` | MIRRORED |
| `wu88-analysis.md` | `12_XjLs2RcFrDADC9wzcfdTHCdpIwNNaQp_WSkZMkQyE` | PENDING |

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
| `SPM_WU100_Release_Manifest_TEMPLATE_2026-08-21.json` | `1AjtFtWmt1uWmfeR_8q3QxQIEvS9aOdMv` | ~2.5 KB | PENDING |
| `SPM_WU100_Canary_Release_Plan_2026-08-21.md` | `1aGzxesZROle9btwHPkq8_BqG3HjQ3gO6` | ~3.7 KB | PENDING |
| `SPM_WU100_RC3_Final_Targeted_Regression_Plan_2026-08-25.md` | `1KEoAq4Uzk85rGlTQwF6P4Uiyyq4DLBLK` | ~2.6 KB | PENDING |

## WU99 / WU100 checklists and evidence
| Artifact | Drive ID | Migration |
|---|---|---|
| `SPM_WU99_Runtime_Certification_Runbook_2026-08-21.md` | `1DWptnSM-0wL7GAnJ2BJ5ldbIAWrmp31i` | PENDING |
| `SPM_WU99_Preflight_QA_2026-08-21.json` | `1pFZdMCPmpoKMsvonksUjLqB1MvYHB8Ne` | PENDING |
| `SPM_WU99_Runtime_Evidence_Ledger_96_2026-08-21.csv` | `11HFxZ7exOhjJHnmgMrenhiPzbEd_tLOT` | PENDING — RECONCILE WITH LATER EXECUTION EVIDENCE |
| `SPM_WU99_Failure_Injection_Matrix_2026-08-21.csv` | `1C4MgHOyEL3fzVEQtd7d1dkwZiP5LGh0d` | PENDING — RECONCILE WITH 15/15 RESULT |
| `SPM_WU100_Rollback_Runbook_2026-08-21.md` | `1zI6NHEPUjOBC0nkH4GDiRbGqN3F0emyG` | PENDING |
| `SPM_WU100_Canary_Monitoring_Gates_2026-08-21.csv` | `1RVQ-SJWSdjQqTNMqkOuMPzgG1VithdMT` | PENDING |
| `SPM_WU100_Preparation_QA_2026-08-21.json` | `1zYXVri42DhEQLa9ZwKXYIWeKzZPJTXlI` | PENDING |
| `SPM_WU100_Production_Approval_Checklist_2026-08-21.md` | `1cfE5Q6znBrzNRp-JPJ5QdtFrJZiDwceo` | PENDING |
| `greenfield-release-gate.md` | `1LrzuDkFaJgRa8ie2DAinC-PUMs7hFFpJRgBCx7AWJF4` | PENDING |

## Legacy/current workflow artifacts
| Artifact | Drive ID | Migration |
|---|---|---|
| `ChatBotMSE_v2_R1_LOCKED_2026-08-17.json` | `1UhOb7V7zLRa6ZXJrjMiDBZbJTH_LXIhe` | PENDING_TRANSPORT — LOCKED BASELINE |
| `ChatBotMSE_v2_R2_TOKEN_OPTIMIZED_2026-08-18.json` | `1Xb7KL-SxcZODbf7zlHrbtlIohdwqOzj1` | PENDING_TRANSPORT |
| `ChatBotMSE_v2_Refactor_Working_Copy_2_PAUSED_2026-08-17.json` | `18wFMuXpMFTA-ZRt8_88OljwrspuX0ej9` | PENDING_TRANSPORT — DIAGNOSTIC |
| `ChatBotMSE_v2_FIXED.json` | `11NTBtzeNYfcODGQ-w8uHCDCnw-Tq61LL` | PENDING_TRANSPORT — SUPERSEDED REFERENCE |
| `Validated_Human_Handoff_FIXED.json` | `1WNifl9kf8Lv9zTvgy6OcoMt8BcDc6W08` | PENDING_TRANSPORT |

## Cutover-critical unresolved artifact
`SPM_E2E_Sales_Agent_RC4_2_FINAL_FROZEN_2026-08-26.json` is referenced by later GitHub/bootstrap state but has not yet been verified in this migration audit against its exact Drive file identity and checksum. Treat as `UNVERIFIED_REFERENCE` until located and reconciled.

## Transfer policy
- Never recreate workflow JSON from screenshots, chat excerpts, or partial connector output.
- Copy the provider export exactly, then record hash/version identity.
- Do not commit secrets, tokens, API keys, private keys, credential payloads, or Redis connection strings.
- n8n credential *references/names/IDs* may appear in exported workflow metadata; actual secret material must remain in the runtime credential store.
- TEST-only WU99 SUT must never be promoted directly to production.
