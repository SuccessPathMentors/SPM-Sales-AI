# AI Knowledge and Source Governance

## Live file

https://docs.google.com/spreadsheets/d/1owA8YtiPkmcA50vi39TQX-IvBhHLzXjoTeBX_5zjCU0/edit

## Current governance state

- Issue 1 pricing/location rule: **LOCKED**.
- Issue 2 refund/service-recovery policy: **LOCKED**.
- Issue 3 Islamic phrase `PHR-004`: **OPEN — no write authorized**.

## Answering rules

- Academy facts require an explicit ACTIVE approved record.
- Match language and applicable country/currency.
- Do not infer absence from missing information.
- Unknown business questions use the unanswered workflow.
- Greetings, confirmations, corrections, lead summaries, and contextual entity replies are operational/conversational and must not be logged as knowledge gaps.

## Data quality rules

- Stable unique ID.
- Approved status and language.
- Source/provenance, reviewer, and review date for material claims.
- No duplicate ACTIVE answer for the same normalized question and language.
- Price/policy changes require focused regression tests.
- Every approved change is recorded in `SOURCE_LOG`, history, decision log, and QA evidence.

## Approval sequence

Ask one owner question → draft Arabic/English/French rows → show exact target cells and test questions → obtain explicit approval → write → read back → test → lock.

## Resume point

Begin with `PHR-004` only. Do not move to FAQ duplicate cleanup or multilingual expansion until Issue 3 is decided and locked.
