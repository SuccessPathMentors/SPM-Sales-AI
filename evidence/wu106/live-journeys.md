# WU-106 — Owner-Observed Live Golden Journey Certification

Status: IN PROGRESS
Issue: #65
PR: #66
STAGING workflow: `vvHvidUHVxM5wTVT` (`[STAGING] SPM_WU106_END_TO_END_JOURNEYS_V1`)
Current candidate SHA-256: `5db680c1e2b51d35408f78077ef4bb098da542bdf5e071125532948ad6783e2e` (CR-106-01, 133 nodes)

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

Certification scope: customer-visible behavior PASS. Internal state trace not visible in screenshot and therefore not claimed from this evidence alone.

## GJ-02 — Discovery → Pricing → Price Objection → Explicit Free Trial
Result: PASS ✅

Observed sequence:
1. `My daughter is in Grade 10 and needs Physics tutoring.`
2. `How much does it cost?`
3. `That is too expensive for me.`
4. `Can we try a free trial?`

Observed PASS evidence:
- initial response recognized Grade 10 + Physics and daughter context;
- pricing response returned the approved package prices;
- price-objection response acknowledged budget concerns without inventing a discount or applying pressure;
- explicit free-trial request transitioned into intake by asking for the parent/guardian name;
- no re-ask of Grade 10 or Physics;
- no claim that the free trial was already booked or confirmed;
- no unauthorized registration/action completion claim.

Certification scope: customer-visible behavior PASS. Internal state trace not visible in screenshot and therefore not claimed from this evidence alone.

## GJ-03 — Trial Details → Explicit Trial Start → Registration Intake
Result: PASS ✅

Observed sequence:
1. `My son is in Grade 8 and needs Math tutoring.`
2. `How does the free trial work?`
3. `Okay, I want to start the free trial.`
4. `I want to register him for tutoring.`

Observed PASS evidence:
- initial response recognized Grade 8 + Math;
- trial-details question was answered informationally and did not begin registration intake;
- explicit trial-start request transitioned into intake and asked for the parent/guardian name;
- registration request stayed in intake and continued requesting the same still-missing parent/guardian name;
- asking for parent/guardian name again was not an unnecessary re-ask because the owner had not supplied that field;
- no re-ask of Grade 8 or Math;
- no claim that the trial was booked or that registration was completed/confirmed.

Certification scope: customer-visible behavior PASS. Internal state trace not visible in screenshot and therefore not claimed from this evidence alone.

## GJ-04 — Registration → Availability → Schedule Request
Initial result: FAIL ❌
Current status: RETEST PENDING after CR-106-01

Initial observed sequence:
1. `I want to register my son for Grade 8 Math tutoring.`
2. bot requested parent/guardian name
3. `Ahmed`
4. `Is Saturday available?`
5. `Please schedule it for Saturday at 6 PM.`

Initial failure evidence:
- `Ahmed` was not bound to the active registration `parent_name` awaiting field; customer received `Could you tell me what you mean by that?`;
- `Is Saturday available?` was also trapped in clarification instead of becoming the current availability objective;
- final schedule-request response remained action-safe and did not falsely claim booking success, but the journey had already failed upstream.

Root cause:
- WU-104 deterministic short-query binding covered grade/subject/location/day/time/confirmation semantics but not registration fields such as `parent_name`;
- WU89/WU95 already had contextual awaited-field extraction, but WU-104 clarification could stop the short value before it reached that downstream binding;
- active registration clarification could also dominate an explicit availability question when classifier confidence was weak.

CR-106-01 remediation:
- exact baseline SHA: `134b2d861d6c5060ca52d8fd838b2cdd7d5d88ffa74855e3de1665e302afda67` (132 nodes);
- remediated SHA: `5db680c1e2b51d35408f78077ef4bb098da542bdf5e071125532948ad6783e2e` (133 nodes);
- added deterministic node: `Apply WU106 Journey Transition Recovery [CR-106-01]`;
- topology: `Build WU104 Short Query Decision → CR-106-01 → Apply WU104 Short Trial Inquiry Guard`;
- executable contract PASS for `Ahmed` awaiting `parent_name`, unsafe-free-text fail-closed behavior, explicit Saturday availability override, human-handoff precedence, schedule-request distinction, and preservation of the locked WU-104 short-trial guard;
- offline exact-lineage run `33703265792`: SUCCESS;
- STAGING update run `33703545755`: SUCCESS;
- target remained `vvHvidUHVxM5wTVT`; operation `UPDATE_INACTIVE_NONPROD`;
- remote versionId: `b5605311-da47-48e3-8e6a-c2cb123c75e3`;
- remote node count: 133; active=false;
- remote readback: `WU106_CR10601_REMOTE_PASS`;
- Production write performed: false.

GJ-04 is not PASS until the owner repeats the exact live journey from a New Session and customer-visible responses satisfy the contract.

## Progress
- GJ-01: PASS
- GJ-02: PASS
- GJ-03: PASS
- GJ-04: RETEST PENDING after CR-106-01
- GJ-05 → GJ-12: PENDING

Current certified owner-observed live journey score: `3 / 12 PASS`.
