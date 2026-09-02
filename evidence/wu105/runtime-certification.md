# WU-105 Runtime Golden Intent Certification Evidence

Status: IN_PROGRESS — CR-105-01 DEPLOYED / TEST-04 RETEST PENDING
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

**Retest status:** `PENDING OWNER SCREENSHOT` using the exact same fresh-session prompt.

## Running certification summary

- Customer-output tests attempted: `4`
- PASS: `3`
- Initial FAIL requiring repair: `1`
- CRs opened: `1` (`CR-105-01`)
- CR-105-01 CI/deployment/readback: `PASS`
- Pending: Test 04 exact customer-output retest

Owner screenshot evidence for Tests 01-04 supplied in chat on 2026-09-03.
