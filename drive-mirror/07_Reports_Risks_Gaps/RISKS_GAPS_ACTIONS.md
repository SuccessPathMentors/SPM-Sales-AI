# Risks, Gaps, and Corrective Actions

| Priority | Risk/gap | Evidence | Required action | Gate |
|---|---|---|---|---|
| P0 | Completed QA evidence not stored in project folder | Available workbook is a template | Save completed evidence and execution IDs | R1 |
| P1 | Runtime reliability is not yet hardened | External services can fail intermittently | Add bounded retry, timeout, and safe failure paths | R2 |
| P1 | Lead submission remains coupled to AI tool selection in the locked export | Functional tests pass, but orchestration is less deterministic than a direct branch | Monitor in R2 and decouple during controlled R2/R3 work with full R1 regression | R2/R3 |
| P1 | Large decision node | `Determine Next Best Action` is about 36 KB | Split only after R1 lock | R3 |
| P1 | Repeated normalization/validation | Multiple Code nodes implement related logic | Centralize helpers and schemas | R3 |
| P1 | Knowledge duplicates/provenance gaps | Historical audit findings remain | Controlled cleanup after Issue 3 | R5 |
| P1 | Time-zone inconsistency | Sheet/project timezone mismatch | UTC storage, Toronto display | R2/R5 |
| P2 | Intent catalog loaded per message | Extra latency/tokens | Versioned cache | R4 |
| P2 | Google Sheets transactional limits | Concurrency/scaling risk | Controlled PostgreSQL/Supabase pilot | R7 |

## Resolved and locked in R1

- Lead submission successfully writes confirmed data.
- Same-session corrections update without duplication.
- Invalid/unconfirmed data is rejected.
- Success is not claimed before successful completion.
- Lead-management messages are protected from unanswered routing.

## Stop conditions

- Internal JSON/tool output reaches a customer.
- The chatbot claims lead submission without verified write.
- Personal data is written without consent.
- Academy fact is answered without ACTIVE verified knowledge.
- Any open P0 test fails.
