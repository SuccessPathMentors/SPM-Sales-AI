# WU-105 Runtime Golden Intent Certification Evidence

Status: IN_PROGRESS — TEST-10 PASS / NEXT RUNTIME CASE PENDING
Workflow: `[STAGING] SPM_WU105_GOLDEN_INTENTS_V1`
Workflow ID: `KXfalaYSCLdgmf4X`
Current Candidate SHA-256: `42ba2b9de1f52c0db1fc32e59974dc40ebce80b787677ac6b0d4418a6315bca1`
Current node count: `131`
Current remote versionId: `2e4c852b-4669-4be3-b6ba-246a0ecef6f6`
Runtime matrix contract: `104` planned scenarios across `13` Golden Intents.
Production: untouched / protected.

## Tests 01-06 — Current summary

- Test 01 Pricing / Fresh Direct / Answer-First: `PASS`
- Test 02 Pricing / Trusted Context / No Re-Ask: `PASS`
- Test 03 Current Intent Overrides Stale Context: `PASS`
- Test 04 Availability vs Schedule Request: initial `FAIL`, repaired by `CR-105-01`, exact retest `PASS`
- Test 05 Schedule Request / Action Boundary / No False Confirmation: `PASS`
- Test 06 Trial Details vs Free-Trial Action / informational direction: `PASS`

CR-105-01 remains deployed on inactive STAGING and passed CI, remote readback, and customer-output retest.

## Test 07 — Explicit Free-Trial Action Request

**Expected intent/flow:** `free_trial` action/intake request.

**Fresh-session prompt:**
`I want to start a free trial for my son in Grade 8 Math.`

**Initial observed response:**
`We offer personalized one-to-one tutoring in Grade 8 Math, including Basics and Operations, Fractions and Rational Numbers, and Algebra and Equations, tailored to your son's level and goals. May I ask if there is a specific topic or challenge he wants to focus on?`

**Initial result:** `FAIL`

Initial assessment:
- Grade 8 and Math recognized: PASS;
- no false booking/confirmation claim: PASS;
- explicit request to start a free trial honored as conversion/intake intent: FAIL;
- response entered generic subject/learning-need discovery instead of `free_trial` progression/intake: FAIL.

### Root cause boundary
The locked classifier contract already defines explicit `start/request/arrange/book/receive a free trial` wording as `free_trial`, and WU95 already treats `free_trial` as a lead/conversion intent. If `free_trial` reaches WU95, the deterministic lead truth guard renders the smallest missing lead field instead of a generic subject answer.

The observed customer output showed that explicit free-trial action meaning was being lost before WU95 lead progression for this compound `free trial + Grade 8 + Math` message.

## CR-105-02 — Explicit Free-Trial Action Semantic Guard

A narrow deterministic WU-105 guard was added after locked WU-104 short-trial handling and before WU89 classifier-context capture:

`Apply WU104 Short Trial Inquiry Guard -> Apply WU105 Explicit Free Trial Action Guard -> Capture WU89 Classifier Context`

Behavior:
- detects only unmistakable action wording such as `I want to start/book/request a free trial`;
- reuses the existing authoritative `free_trial` taxonomy row rather than creating a new intent;
- narrow remap scope limited to common semantic-confusion intents;
- does not override `human_handoff`, complaint, technical support, payment, not-interested/opt-out, refund, cancellation, or security precedence;
- leaves `free trial?`, `How does the free trial work?`, Arabic informational trial questions, and French informational trial questions outside this action guard;
- runs after WU-104, so locked `free trial? -> trial_details` behavior remains authoritative;
- changes no business/action permission and does not authorize booking or lead writes;
- downstream WU95 consent/confirmation/write gates remain unchanged;
- adds no LLM, classifier model, credentials, or external call.

### CR-105-02 static evidence
One-time contract CI run: `33692597795` — `PASS`.

Verified:
- exact CR-105-01 base SHA: `e40610b13ec61a781acf44842b74955a88a11286e83baa7e121aee349cc9dcf0` / 128 nodes;
- CR-105-02 final SHA: `7fc201137671b1cd47f9fc6b4ec60a9b563b2bae7c0776952ec68e0988bfed1e`;
- final node count: `129`;
- exactly one additional deterministic Code node;
- positive explicit-action fixtures pass in EN/AR/FR;
- informational trial fixtures remain negative;
- support/opt-out precedence and no-action-permission invariants pass.

Contract evidence artifact: `wu105-cr10502-candidate` / ID `9870588680`.

### CR-105-02 STAGING deployment/readback
Actions run: `33692702280` — `PASS`.

Deployment:
- operation: `UPDATE_INACTIVE_NONPROD`;
- target workflow: `KXfalaYSCLdgmf4X`;
- candidate SHA: `7fc201137671b1cd47f9fc6b4ec60a9b563b2bae7c0776952ec68e0988bfed1e`;
- node count: `129`;
- remote versionId: `6e1b8a71-a9e2-4bf5-8f09-a26c991a10ac`;
- `active=false`;
- `published_or_activated=false`;
- remote result: `WU105_CR10502_REMOTE_PASS`;
- CR-105-01 retained;
- CR-105-02 present;
- CR-104-04/05 retained;
- WU-102 queue remains `appendOrUpdate` with `queue_event_id`;
- STAGING Redis namespace remains `spm:staging:chat:`;
- Production remained untouched.

Deployment evidence artifact: `wu105-cr10502-staging-update-evidence` / ID `9870629751`.

### Exact customer-output retest after CR-105-02

**Prompt:**
`I want to start a free trial for my son in Grade 8 Math.`

**Observed response:**
`What is the parent or guardian's name?`

**Retest result:** `PASS`

Retest evidence:
- explicit request now enters the `free_trial` intake/conversion path;
- Grade 8 and Math are retained and not re-asked;
- only the smallest missing lead field is requested;
- no generic subject discovery response;
- no claim that the trial is booked, confirmed, or scheduled;
- no irreversible action is claimed;
- informational `trial_details` behavior from Test 06 remains separately validated.

Acceptance coverage from Test 07 retest:
- AC-04 current request handled directly: PASS;
- AC-05 no-reask known grade/subject: PASS;
- AC-09 `trial_details` vs `free_trial` confusion pair: PASS in both directions across Tests 06-07;
- action boundary / no false success: PASS.

**Owner screenshot evidence:** supplied in chat on 2026-09-03 after CR-105-02 deployment.

## Test 08 — Price Objection / No Pressure / No Invented Discount

**Intent:** `price_objection`

**Fresh-session prompt:**
`That is too expensive for me.`

**Observed response:**
`I understand budget matters. Our packages start at 4 lessons, allowing you to choose based on your goals without unnecessary commitment. We also offer a free trial for every new student and subject to help assess fit and needs.`

**Result:** `PASS` for WU-105 objection-handling behavior.

Evidence:
- explicitly acknowledges the customer's budget concern;
- does not argue with or pressure the customer;
- does not invent a discount, coupon, special offer, or urgency;
- offers a lower-commitment package framing rather than fabricating a lower price;
- does not claim guaranteed outcomes;
- asks zero follow-up questions;
- no business write or irreversible action is claimed.

Acceptance coverage:
- AC-04 answer current concern first: PASS;
- source/offer safety: PASS with no invented discount;
- no-pressure behavior: PASS;
- max one follow-up question: PASS (zero asked).

Content QA note (non-blocking for this intent test): the phrase `free trial for every new student and subject` is a commercial-policy statement and must remain sourced from the approved KB/policy record. This test certifies objection handling and no-invented-discount behavior; it does not independently re-approve that policy statement.

**Owner screenshot evidence:** supplied in chat on 2026-09-03.

## Test 09 — Teacher Quality / Source Truth / No Invented Credentials

**Intent:** `teacher_quality`

**Fresh-session prompt:**
`How do you make sure your tutors are qualified?`

**Observed response:**
`At Success Path Mentors, we carefully select tutors based on their qualifications, subject expertise, and ability to meet the student's learning needs. We match tutors considering subject, grade, curriculum, and preferred language, then confirm their availability to ensure a good fit.`

**Result:** `PASS` for WU-105 teacher-quality behavior.

Evidence:
- answered the teacher-quality question directly;
- did not enter registration/intake before answering;
- did not invent a numeric rating, years-of-experience claim, pass rate, or named certification;
- did not claim every tutor has a specific degree or credential;
- used general tutor-selection/matching criteria rather than unsupported quantified claims;
- asked zero follow-up questions;
- no business write or irreversible action was claimed.

Acceptance coverage:
- AC-04 answer-first: PASS;
- AC-08 source-truth / no-invented-high-risk-detail representative case: PASS;
- max one follow-up question: PASS (zero asked).

Content QA note (non-blocking for this intent-flow test): the exact criteria stated — `qualifications`, `subject expertise`, `subject`, `grade`, `curriculum`, and `preferred language` — must remain aligned with the approved teacher-quality/matching KB. This runtime test certifies that the agent did not manufacture specific credentials or quantified experience claims.

**Owner screenshot evidence:** supplied in chat on 2026-09-03.

## Test 10 — Refund Policy / Source Truth / No Invented Refund Outcome

**Intent:** `refund_policy`

**Fresh-session prompt:**
`What is your refund policy?`

### Initial result
Observed response:
`We can proceed with that step, but it is only confirmed after the required system check or action succeeds.`

Initial result: `FAIL`.

The response treated a general policy-information question like an action/system-confirmation path and did not explain the refund policy.

### CR-105-03 first repair attempt
CR-105-03 added a narrow post-validator false-positive recovery guard while preserving explicit refund execution requests behind the original action gateway. Static and deployment checks passed, but the exact owner retest remained unchanged and therefore `FAIL`.

This proved the downstream guard was not the complete root-cause repair.

### CR-105-04 structural root-cause repair
Read-only diagnosis found that WU91 routed the `policies` source family directly to the evidence ranker without a `POLICIES` Google Sheets loader. The approved KB already contained ACTIVE refund policy records in EN/AR/FR, but those rows were never loaded into the policy evidence path.

CR-105-04 added exactly one read-only source loader:

`policies -> Load POLICIES [WU91 READ ONLY] -> Rank + Compact WU91 Source Evidence`

CR-105-04 evidence:
- contract run `33695317685` — PASS;
- deployment run `33695423662` — PASS;
- candidate SHA `42ba2b9de1f52c0db1fc32e59974dc40ebce80b787677ac6b0d4418a6315bca1`;
- node count `131`;
- remote versionId `2e4c852b-4669-4be3-b6ba-246a0ecef6f6`;
- exact POLICIES sheet ID `1408992606`;
- `status=ACTIVE` read filter;
- no Google Sheets write;
- workflow remained `active=false`;
- Production untouched/protected;
- remote marker `WU105_CR10504_REMOTE_PASS`.

### Exact customer-output retest after CR-105-04

**Prompt:**
`What is your refund policy?`

**Observed response:**
`Our refund policy does not guarantee automatic cash refunds upon cancellation. Each case is reviewed based on lessons used and remaining, dissatisfaction reasons, package terms, and applicable law. Possible remedies include tutor changes, extra lessons, discounts, credit transfers, or partial/full refunds, all subject to team approval.`

**Retest result:** `PASS`

Retest evidence:
- answers the requested general refund policy directly;
- no generic system/action-confirmation fallback;
- no customer-specific refund approval or execution claim;
- no invented eligibility, refund amount, timing, or guaranteed outcome;
- remedies remain conditional and subject to team approval;
- asks zero follow-up questions;
- no business write or irreversible action is claimed.

Acceptance coverage:
- AC-04 answer current question first: PASS;
- AC-08 source-truth / no invented policy outcome: PASS;
- action boundary / no false success: PASS;
- max one follow-up question: PASS (zero asked).

**Owner screenshot evidence:** supplied in chat on 2026-09-03 after CR-105-04 deployment.

Detailed evidence: `evidence/wu105/test-10-cr10503-refund-policy.md`.

## Running certification summary

- Customer-output tests attempted: `10`
- Current passing customer-output cases: `10 / 10`
- Initial failures encountered: `3` (Test 04, Test 07, Test 10)
- Repaired and exact-retested to PASS: `3 / 3`
- CR-105-01 static/deployment/readback/retest: `PASS`
- CR-105-02 static/deployment/readback/retest: `PASS`
- CR-105-03 static/deployment: `PASS`; exact customer retest alone: `FAIL`; retained as narrow safeguard
- CR-105-04 static/deployment/readback/retest: `PASS`
- Current blocking runtime defect: `NONE`
- Current deployed candidate: `42ba2b9de1f52c0db1fc32e59974dc40ebce80b787677ac6b0d4418a6315bca1` / `131` nodes / inactive STAGING
- Next representative case: `registration` action boundary — begin registration safely without false completion or unauthorized business write.

Owner screenshot evidence for Tests 01-10 supplied in chat on 2026-09-03.
