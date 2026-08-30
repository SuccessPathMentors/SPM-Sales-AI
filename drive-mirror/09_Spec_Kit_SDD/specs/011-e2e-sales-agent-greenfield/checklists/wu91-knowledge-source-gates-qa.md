# WU91 — Knowledge Retrieval & Source Gates QA

Status: PROTOTYPE IMPLEMENTATION COMPLETE — STATIC QA PASS; runtime certification pending.
Candidate: SPM_E2E_Sales_Agent_Greenfield_WU91_Knowledge_Source_Gates_2026-08-20.json
SHA-256: 65b25c5f74ef6a2a139d973a157709ad47e171520b8022599bf4c9a1417df3d5

## Architecture
- Derived from canonical WU90 candidate.
- 52 nodes; names and IDs unique; zero dangling graph references.
- Candidate remains active=false with no top-level workflow id/versionId.
- Current production workflow is unchanged.

## Source-Gate Design
- Uses classification.source_gate as the authority for choosing a source family.
- Read-only source families: PACKAGES, POLICIES, SUBJECTS, SUBJECT_PATHWAYS, FAQ, SERVICES, LOCATIONS, FALLBACKS.
- Reads ACTIVE rows only from the safe V2 workbook.
- Retrieval is bounded to one authorized source family per request and compacts to a maximum of three evidence records.
- FAQ is supporting evidence, not the Sales Agent's primary role.
- PACKAGES is authoritative for price/package claims.
- POLICY_AND_LIVE_STATE may provide general policy context, but customer-specific outcomes remain live/team gated.
- VERIFIED_TEACHER_OR_POLICY may provide generic process context; tutor-specific credentials, availability, origin, or assignment are blocked without verified live/profile evidence.
- SCHEDULING_LIVE, PAYMENT_LIVE, CRM_VALIDATION, AUTHORIZED_OFFER_REQUIRED, and MARKET_PAYMENT_CONFIG do not become static claims when their required source is unavailable.

## Static QA
19/19 PASS:
- valid JSON / active=false / new identity safety;
- unique names and IDs;
- no dangling connections;
- zero production-write nodes;
- 8 read-only loaders target the safe V2 workbook;
- all loaders filter status=ACTIVE and use bounded retry/error output;
- max evidence records = 3;
- live/authorization/CRM gates remain blocked from static confirmation;
- teacher-specific claims remain blocked without verified evidence;
- WU92 Sales Agent remains separate from WU91 evidence generation.

## Runtime Gate
Not run. Certification requires n8n test execution after upstream WU88→WU90 runtime gates pass. Test source selection, no-match behavior, loader errors, evidence ranking, policy/live partial responses, and live-only blocking.
