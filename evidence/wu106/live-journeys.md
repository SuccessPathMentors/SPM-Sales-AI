# WU-106 — Owner-Observed Live Golden Journey Certification

Status: IN PROGRESS
Issue: #65
PR: #66
STAGING workflow: `vvHvidUHVxM5wTVT` (`[STAGING] SPM_WU106_END_TO_END_JOURNEYS_V1`)
Current candidate SHA-256: `2e219adbdd612106b782993cbcb2f94da6c0737b250264060b473f12f0fcc81f` (CR-106-03, 141 nodes)

## Evidence method
Owner executes the prescribed multi-turn prompts in n8n Test Chat and shares screenshots of customer-visible responses. Screenshots certify customer-visible behavior; internal state/lineage is covered separately by deterministic CI and remote readback.

## GJ-01 — Discovery → Pricing → Package Comparison
Result: PASS ✅
- Grade 8 + Math recognized and reused.
- Approved pricing and package comparison returned.
- No unnecessary Grade/Subject re-ask or unsolicited registration.

## GJ-02 — Discovery → Pricing → Price Objection → Explicit Free Trial
Result: PASS ✅
- Grade 10 + Physics preserved.
- Price objection handled without invented discount or pressure.
- Explicit trial request entered intake without false booking claim.

## GJ-03 — Trial Details → Explicit Trial Start → Registration Intake
Result: PASS ✅
- Trial-details inquiry remained informational.
- Explicit trial start entered intake.
- Registration continued without false trial/registration completion claim.

## GJ-04 — Registration → Availability → Schedule Request
Initial result: FAIL ❌
CR-106-01 live retest: FAIL ❌
Final result after CR-106-02: PASS ✅

Corrected live evidence:
- `Ahmed` bound to the awaited parent/guardian field and advanced to student name.
- `Omar` advanced to the phone field.
- `Is Saturday available?` interrupted stale registration intake and became the active availability objective.
- No re-ask of Grade 8/Math and no false availability/booking claim.

CR-106-02 root control:
- dedicated PII-free Redis key `spm:staging:regctrl:<session_id>`;
- registration control restored before classification when canonical continuation was absent;
- explicit current availability wording overrides stale registration clarification;
- canonical WU95 sales-state remains authoritative.

## GJ-05 — Availability → Requested Slot → Safe Alternative
Initial result: FAIL ❌
Final result after CR-106-03: PASS ✅

Owner-observed corrected sequence:
1. `My son is in Grade 8 and needs Math tutoring. Is Saturday at 6 PM Toronto time available?`
2. bot did not re-ask for timezone/city; it stated that live tutor availability must be checked to confirm the requested time;
3. `Please schedule Saturday at 6 PM.`
4. bot remained action-safe and did not falsely claim that the booking was completed;
5. `If 6 PM is not available, what other time could work?`
6. bot correctly treated the turn as an alternative-availability inquiry and replied that the live schedule must be checked for other available times while preserving the currently requested time as the preference unless the customer chooses another time.

Observed PASS evidence:
- `Toronto time` no longer caused a timezone/city re-ask;
- Saturday + 6 PM remained the requested scheduling preference;
- the explicit schedule request did not produce a false `booked` or `confirmed` claim;
- the alternative-slot question no longer fell into the generic action fallback;
- the response explicitly required a live schedule check before offering another slot;
- the system preserved the existing requested time instead of silently replacing it;
- no invented alternative slot was presented.

UX note — non-blocking:
- wording such as `Our team will coordinate suitable options for you` is broader than necessary and could be tightened later to avoid implying an automatic human follow-up. It did not claim booking, handoff, or action success and therefore is not a GJ-05 failure.

### CR-106-03 root remediation
Candidate: `2e219adbdd612106b782993cbcb2f94da6c0737b250264060b473f12f0fcc81f` (141 nodes).

Root controls:
- WU89 deterministic current-message scheduling normalization marker: `SPM_WU106_CR10603_SCHEDULING_NORMALIZATION_V1`;
- explicit `Toronto time`, `Mississauga time`, or `Milton time` maps to the explicitly supplied city plus `America/Toronto`; this is not country-based timezone inference;
- explicit scheduling day/time is normalized into `preferred_day` / `preferred_time` for the current request;
- new `Apply WU106 Alternative Slot Recovery [CR-106-03]` recognizes alternative-slot wording as `availability` without overwriting the existing requested preference;
- new `Apply WU106 Alternative Availability Response Guard [CR-106-03]` requires a live schedule check for alternatives and never invents a slot or claims a booking;
- human/support/opt-out precedence remains higher priority.

Offline/exact-lineage evidence:
- exact-lineage run `33770742954`: SUCCESS;
- executable result: `WU106_CR10603_GJ05_ROOT_FIX_EXECUTABLE_PASS`;
- 12-journey contract: PASS;
- 48-scenario deterministic matrix: PASS;
- permanent STAGING dry-run: PASS;
- Repository Guard: PASS.

STAGING deployment:
- update run `33770812500`: SUCCESS;
- operation: `UPDATE_INACTIVE_NONPROD`;
- candidate SHA: `2e219adbdd612106b782993cbcb2f94da6c0737b250264060b473f12f0fcc81f`;
- workflow remains `vvHvidUHVxM5wTVT`;
- remote versionId: `a353d744-8e37-4a8b-ada5-5c43bfc5e0fc`;
- remote node count: 141;
- `active=false`;
- remote readback: `WU106_CR10603_REMOTE_PASS`;
- Production write performed: false.

Certification scope: GJ-05 customer-visible behavior is now PASS after CR-106-03.

## Progress
- GJ-01: PASS
- GJ-02: PASS
- GJ-03: PASS
- GJ-04: PASS after CR-106-02
- GJ-05: PASS after CR-106-03
- GJ-06 → GJ-12: PENDING

Current certified owner-observed live journey score: `5 / 12 PASS`.
