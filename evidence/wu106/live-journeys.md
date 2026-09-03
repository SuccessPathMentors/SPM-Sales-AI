# WU-106 — Owner-Observed Live Golden Journey Certification

Status: IN PROGRESS
Issue: #65
PR: #66
STAGING workflow: `vvHvidUHVxM5wTVT` (`[STAGING] SPM_WU106_END_TO_END_JOURNEYS_V1`)
Current candidate SHA-256: `50dbf22e2496e3c1b0ce7c9ff37edab752dbf6b69ddc62f80026942b31146014` (CR-106-02, 139 nodes)

## Evidence method
Owner executes the exact prescribed multi-turn prompts in n8n Test Chat and shares screenshots of customer-visible responses. These screenshots certify customer-visible journey behavior. They do not, by themselves, expose or certify internal `sales_state`; internal state/lineage is covered separately by deterministic contracts and CI.

## GJ-01 — Discovery → Pricing → Package Comparison
Result: PASS ✅

Observed sequence:
1. `My son is in Grade 8 and needs Math tutoring.`
2. `How much does it cost?`
3. `What is the difference between your tutoring packages?`

Observed PASS evidence:
- initial response recognized Grade 8 + Math;
- pricing response returned the approved package structure;
- package-comparison response compared 4 / 8 / 12 lesson packages and per-lesson economics;
- no re-ask of Grade or Subject;
- no unsolicited registration/action claim;
- no invented discount or package guarantee.

## GJ-02 — Discovery → Pricing → Price Objection → Explicit Free Trial
Result: PASS ✅

Observed PASS evidence:
- Grade 10 + Physics + daughter context preserved;
- approved package prices returned;
- price objection handled without invented discount or pressure;
- explicit free-trial request transitioned into intake;
- no false trial booking/confirmation claim.

## GJ-03 — Trial Details → Explicit Trial Start → Registration Intake
Result: PASS ✅

Observed PASS evidence:
- Grade 8 + Math preserved;
- trial-details question remained informational;
- explicit trial-start request entered intake;
- registration request remained in intake;
- no false trial/registration completion claim.

## GJ-04 — Registration → Availability → Schedule Request
Initial result: FAIL ❌
CR-106-01 live retest: FAIL ❌
Current status: RETEST PENDING after CR-106-02 root-cause deployment

Observed failure sequence:
1. `I want to register my son for Grade 8 Math tutoring.`
2. bot requested parent/guardian name
3. `Ahmed`
4. bot incorrectly returned `Could you tell me what you mean by that?`
5. `Is Saturday available?`
6. bot again incorrectly returned clarification
7. final schedule-request response remained action-safe but the journey had already failed upstream.

### Why CR-106-01 was insufficient
CR-106-01 could recover the short registration value only when the canonical registration continuation state (`registration_active` / `awaiting_field`) was already present in the next-turn payload. Live testing showed that this precondition was not reliable. Its availability override was also still coupled to classifier/clarification conditions rather than being fully current-message deterministic.

### CR-106-02 root-cause remediation
Candidate: `50dbf22e2496e3c1b0ce7c9ff37edab752dbf6b69ddc62f80026942b31146014` (139 nodes).

Root controls:
- dedicated PII-free STAGING Redis control key: `spm:staging:regctrl:<session_id>`;
- control key stores only registration control metadata, never customer field values or raw messages;
- control metadata is loaded and merged before classifier/catalog processing when canonical registration continuation is missing;
- active canonical `sales_state` remains authoritative when present;
- awaited registration values such as `Ahmed` bind deterministically even if the classifier is strongly wrong;
- explicit availability wording such as `Is Saturday available?` gets current-message deterministic priority over stale registration/clarification context;
- human/support/opt-out precedence is preserved;
- a PII-free registration-control snapshot is redundantly persisted after final WU95/WU104 registration state is known;
- canonical WU95 sales-state persistence remains unchanged and authoritative.

Offline exact-lineage certification:
- run `33766888766`: SUCCESS;
- executable result: `WU106_CR10602_ROOT_CAUSE_EXECUTABLE_PASS`;
- multi-turn simulation: PASS;
- 12 Golden Journey manifest: PASS;
- Journey State Contract: PASS;
- 48-scenario matrix: PASS.

STAGING deployment:
- run `33767318872`: SUCCESS;
- operation: `UPDATE_INACTIVE_NONPROD`;
- workflow remains `vvHvidUHVxM5wTVT`;
- remote versionId: `1734f210-1fc3-4a90-96ca-de09edde4c23`;
- remote node count: 139;
- active=false;
- remote readback: `WU106_CR10602_REMOTE_PASS`;
- registration-control Redis namespace isolation: PASS;
- canonical Redis credential reuse: PASS;
- WU102 queue idempotency and chat-memory isolation: PASS;
- Production write performed: false.

GJ-04 remains FAIL/RETEST PENDING until owner-visible Test Chat proves the corrected journey. No prior PASS journey is reopened by this change.

## Progress
- GJ-01: PASS
- GJ-02: PASS
- GJ-03: PASS
- GJ-04: RETEST PENDING after CR-106-02
- GJ-05 → GJ-12: PENDING

Current certified owner-observed live journey score: `3 / 12 PASS`.
