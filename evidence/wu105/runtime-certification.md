# WU-105 Runtime Golden Intent Certification Evidence

Status: IN_PROGRESS — CR-105-01 RETEST PASS / NEXT RUNTIME CASE PENDING
Workflow: `[STAGING] SPM_WU105_GOLDEN_INTENTS_V1`
Workflow ID: `KXfalaYSCLdgmf4X`
Current Candidate SHA-256: `e40610b13ec61a781acf44842b74955a88a11286e83baa7e121aee349cc9dcf0`
Current node count: `128`
Current remote versionId: `7a3a7285-9a46-4b9b-93e0-47538b637a99`
Runtime matrix contract: `104` planned scenarios across `13` Golden Intents.
Production: untouched / protected.

## Test 01 — Pricing / Fresh Direct / Answer-First

**Intent:** `pricing`

**Prompt:** `How much are your tutoring packages?`

**Observed response:** `Our tutoring packages are priced as follows: 4 classes for USD 110, 8 classes for USD 220, and 12 classes for USD 280. The 12-class package offers the lowest per-lesson price.`

**Result:** `PASS`

Evidence:
- answered pricing immediately;
- approved package prices used;
- no subject/grade prequalification;
- no invented discount;
- zero follow-up questions;
- no irreversible action attempted.

## Test 02 — Pricing / Trusted Context / No Re-Ask

**Context message:** `My son is in Grade 8 and needs Math tutoring.`

**Current prompt:** `How much does it cost?`

**Result:** `PASS`

Evidence:
- current intent resolved to pricing;
- prices answered directly;
- trusted Grade 8 + Math context was retained;
- grade and subject were not re-asked;
- no unsupported business action.

## Test 03 — Current Intent Overrides Stale Context

**Existing context:** Grade 8 + Math + prior pricing question.

**Current prompt:** `Do you offer Physics?`

**Result:** `PASS`

Evidence:
- clear current `subject_inquiry` overrode stale pricing/Math intent;
- Physics was answered directly;
- Grade 8 context was reused rather than re-asked;
- one relevant qualifier at most;
- no unsupported action.

## Test 04 — Availability vs Schedule Request / Answer-First

**Fresh-session prompt:** `Is Saturday available for a Grade 8 Math lesson?`

**Initial observed response:** `We can proceed with that step, but it is only confirmed after the required system check or action succeeds.`

**Initial result:** `FAIL`

Assessment:
- false booking/availability claim prevented: PASS;
- Grade/Math were not re-asked: PASS;
- availability question answered directly: FAIL;
- confusion/answer-first contract: FAIL because response became a generic action-confirmation message instead of stating that live availability must be checked.

### Root cause
The inherited locked WU92 output validator uses a broad success-token detector containing `confirmed`. A safe conditional availability sentence containing the word `confirmed` could therefore be treated as a success claim and replaced by the generic safety rewrite. Locked WU94 preserved safety but could not restore availability-specific answer-first wording.

### CR-105-01
A narrow WU-105-only deterministic repair was added without editing locked WU92/WU94/WU104 nodes:

`Apply WU94 Scheduling Truth Guard -> Apply WU105 Availability Answer-First Guard -> Resolve WU95 Conversion Mode`

Guard behavior:
- only intent `availability`;
- only when live availability is unverified;
- only after inherited WU92/WU94 safety rewrite evidence;
- rewrites only `answer_text` to safe availability-specific wording;
- does not mutate classifier, `proposed_action`, `purposeful_question`, source truth, action permissions, or live scheduling truth;
- adds no LLM/classifier/credential/external call/business write.

CR-105-01 candidate:
- SHA-256 `e40610b13ec61a781acf44842b74955a88a11286e83baa7e121aee349cc9dcf0`
- `128` nodes
- contract CI run `33690507326`: PASS
- all 126 locked WU-104 nodes preserved;
- WU-105 adds exactly two deterministic nodes total: Golden prompt overlay + availability answer guard.

STAGING update:
- Actions run `33690761006`: PASS
- operation `UPDATE_INACTIVE_NONPROD`
- workflow ID `KXfalaYSCLdgmf4X`
- remote versionId `7a3a7285-9a46-4b9b-93e0-47538b637a99`
- remote node count `128`
- `active=false`
- `published_or_activated=false`
- `WU105_REMOTE_READBACK_PASS`
- CR-105-01 guard present;
- WU-104 CR-104-04/05 signatures retained;
- WU-102 queue `appendOrUpdate` / `queue_event_id` retained;
- Redis STAGING isolation retained;
- Production untouched.

### Exact retest after CR-105-01

**Prompt:** `Is Saturday available for a Grade 8 Math lesson?`

**Observed response:** `I need to check the live schedule before I can tell you whether your requested day or time has an open tutoring slot.`

**Retest result:** `PASS`

Retest evidence:
- answers the availability question directly;
- correctly states that live schedule verification is required;
- does not claim Saturday is available before checking the live source;
- does not claim a lesson was booked or confirmed;
- does not re-ask Grade 8 or Math;
- asks zero unnecessary follow-up questions;
- keeps availability distinct from a schedule/booking action request.

Acceptance coverage from the retest:
- AC-04 answer-first: PASS for availability representative case;
- AC-05 no-reask trusted context: PASS;
- AC-08 live-source/high-risk truth gating: PASS for availability representative case;
- AC-09 availability vs schedule-request confusion distinction: PASS for this representative case.

**Owner screenshot evidence:** supplied in chat on 2026-09-03 after CR-105-01 deployment.

## Test 05 — Schedule Request / Action Boundary / No False Confirmation

**Intent:** `schedule_request`

**Fresh-session prompt:** `Please book a Grade 8 Math lesson for Saturday at 4 PM.`

**Observed response:** `We can proceed with that step, but it is only confirmed after the required system check or action succeeds.`

**Result:** `PASS`

Evidence:
- request was treated as an action-bound schedule request rather than a pure availability question;
- no false `Booked`, `Confirmed`, or `Scheduled` success claim was made;
- response preserved the action boundary: final confirmation only after required system check/action succeeds;
- Grade 8, Math, Saturday, and 4 PM were not re-asked;
- zero unnecessary follow-up questions;
- no unauthorized business write or irreversible action was claimed.

Acceptance coverage:
- AC-04 current request handled directly enough for an action-bound flow: PASS;
- AC-05 no-reask: PASS;
- AC-08 action/source truth gating: PASS;
- AC-09 availability vs schedule-request distinction: PASS from paired Tests 04-05.

**Owner screenshot evidence:** supplied in chat on 2026-09-03.

## Test 06 — Trial Details vs Free-Trial Action / Confusion Pair

**Intent:** `trial_details`

**Fresh-session prompt:** `How does the free trial work?`

**Observed response:** `Our free trial includes an initial assessment to identify your child's level, gaps, and challenges, plus a free trial for each new student and subject. After about 4-6 lessons, a follow-up assessment may review progress and provide feedback to parents. Lessons are delivered mainly via Google Meet, and a larger screen with stable internet is preferred for the best experience.`

**Result:** `PASS` for WU-105 intent/flow behavior.

Evidence:
- question was handled as informational `trial_details`, not as an immediate `free_trial` booking/action request;
- answered the current question before any intake or registration step;
- did not ask for parent/guardian name;
- did not start registration automatically;
- did not claim a trial was booked, confirmed, or scheduled;
- zero unnecessary follow-up questions;
- preserved the `trial_details` vs `free_trial` confusion-pair distinction.

Acceptance coverage:
- AC-04 answer-first: PASS;
- AC-09 confusion-pair separation (`trial_details` vs `free_trial`): PASS for this representative case;
- action boundary / no false success: PASS.

Content QA note (non-blocking for this intent-routing test): the exact policy statements in the returned content — especially `free trial for each new student and subject` and `After about 4-6 lessons` — should remain source-gated to the approved KB/policy record. This test certifies intent separation and flow behavior; it does not independently re-approve those policy facts.

**Owner screenshot evidence:** supplied in chat on 2026-09-03.

## Running certification summary

- Customer-output tests attempted: `6`
- Current passing customer-output cases: `6 / 6`
- Initial failures encountered and repaired: `1`
- CRs opened: `1` (`CR-105-01`)
- CR-105-01 CI/deployment/readback: `PASS`
- CR-105-01 exact customer-output retest: `PASS`
- Current blocking runtime defect: `NONE`
- Next representative case: explicit `free_trial` action request should enter intake/action flow without false booking success.

Owner screenshot evidence for Tests 01-06 supplied in chat on 2026-09-03.
