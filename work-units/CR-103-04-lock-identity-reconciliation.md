# CR-103-04 — Reconcile locked WU-103 candidate identity

Status: APPROVED FOR AUDIT CORRECTION
Parent work unit: WU-103 — LOCKED
Issue: #30
Date: 2026-09-02

## Problem
`work-units/WU-103.lock.md` records the pre-correction candidate SHA-256:

`0d53579c9bc93a0a440b8f8c5e9e6545d3dd4b11399116eea57efee6b9fff746`

However, after the Publish Decisions JavaScript syntax correction and memory-safe candidate rebuild, the same inactive WU-103 STAGING workflow (`5COEoxXjk8AvuGBa`) was successfully updated and remote-read-back verified using the corrected candidate SHA-256:

`f39994bb9fd87c6046419de7ebfbe782d94b52c29fe047156a054ff0ab1c9e38`

The workflow file on `main` also locks `EXPECTED_SHA256` to `f39994bb9fd87c6046419de7ebfbe782d94b52c29fe047156a054ff0ab1c9e38`.

This leaves the authoritative lock record inconsistent with the deployed/verified locked artifact.

## Correction
Update only the WU-103 lock documentation so that:

- locked corrected STAGING candidate SHA-256 = `f39994bb9fd87c6046419de7ebfbe782d94b52c29fe047156a054ff0ab1c9e38`;
- pre-correction SHA `0d53579c9bc93a0a440b8f8c5e9e6545d3dd4b11399116eea57efee6b9fff746` remains recorded as superseded historical identity;
- n8n workflow ID remains `5COEoxXjk8AvuGBa`;
- workflow remains inactive / Manual Trigger / STAGING only;
- no ledger/shadow schema, gate, family adapter, Production boundary, or runtime behavior is changed.

## Evidence
- GitHub Issue #30 records the corrected-candidate deployment and remote read-back for Run #26 (`33440564532`) on commit `47e21c3b8911e87c672d24ff17c542ccd4b7bc9b`.
- That evidence records corrected candidate SHA `f39994bb9fd87c6046419de7ebfbe782d94b52c29fe047156a054ff0ab1c9e38`, 38 change fields, regression payload binding, minimum two regression cases, 31 nodes / 28 connection sources, inactive workflow, and same workflow ID `5COEoxXjk8AvuGBa`.
- `.github/workflows/wu103-staging.yml` on `main` uses the same corrected SHA as `EXPECTED_SHA256`.
- `work-units/WU-103.review.md` already treats the earliest ADD/v2 rows with empty regression-case IDs as historical pre-final-hardening fixtures and uses Runtime Test #6 as authoritative final gate evidence.

## Scope / safety
Documentation/audit correction only.

No changes to:
- n8n workflow content;
- Google Sheets data;
- canonical Production KB;
- Production workflow;
- WU-101/WU-102/WU-104 behavior.

## Approval basis
The Owner explicitly instructed ChatGPT to correct the identified WU-103 problems on 2026-09-02. This CR implements only the lock-identity reconciliation required by that instruction.
