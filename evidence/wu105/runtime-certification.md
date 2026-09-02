# WU-105 Runtime Golden Intent Certification Evidence

Status: IN_PROGRESS — TEST-07 FAIL / CR-105-02 IN DIAGNOSIS
Workflow: `[STAGING] SPM_WU105_GOLDEN_INTENTS_V1`
Workflow ID: `KXfalaYSCLdgmf4X`
Current Candidate SHA-256: `e40610b13ec61a781acf44842b74955a88a11286e83baa7e121aee349cc9dcf0`
Current node count: `128`
Current remote versionId: `7a3a7285-9a46-4b9b-93e0-47538b637a99`
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

**Observed response:**
`We offer personalized one-to-one tutoring in Grade 8 Math, including Basics and Operations, Fractions and Rational Numbers, and Algebra and Equations, tailored to your son's level and goals. May I ask if there is a specific topic or challenge he wants to focus on?`

**Result:** `FAIL`

Assessment:
- Grade 8 and Math were recognized: PASS;
- no false booking/confirmation claim: PASS;
- explicit request to **start a free trial** was honored as conversion/intake intent: FAIL;
- response entered generic subject/learning-need discovery instead of the `free_trial` progression/intake path: FAIL;
- `trial_details` vs `free_trial` separation is therefore only passing in the informational direction, not yet in the explicit-action direction.

### Diagnosis
The locked classifier contract already defines explicit `start/request/arrange/book/receive a free trial` wording as `free_trial`, and WU95 already treats `free_trial` as a lead/conversion intent. If `free_trial` reaches WU95, the deterministic lead truth guard renders the smallest missing lead field instead of a generic subject answer.

The observed customer output therefore indicates that this explicit action meaning is being lost before the WU95 lead path (most likely semantic intent resolution/classifier output for the compound `free trial + Grade 8 + Math` message), rather than a WU95 intake rendering defect.

### Planned CR-105-02 boundary
A narrow deterministic semantic guard will be evaluated **after locked WU-104 short-trial handling and before WU89 classifier-context capture**. It may remap only an unmistakable explicit free-trial action phrase to the existing `free_trial` taxonomy intent, while preserving support/opt-out/complaint/human-handoff precedence and leaving `free trial?` / `How does the free trial work?` informational cases untouched.

Hard constraints:
- no new intent;
- no second LLM/classifier;
- no Production mutation;
- no booking/lead write authorization;
- WU-104 `free trial? -> trial_details` behavior remains authoritative;
- support/opt-out overrides remain authoritative;
- downstream WU95 consent/confirmation/write gates remain unchanged.

## Running certification summary

- Customer-output tests attempted: `7`
- Current passing customer-output cases: `6 / 7`
- Initial failures encountered: `2` (Test 04, Test 07)
- Repaired and retested: `1` (Test 04 via CR-105-01)
- Current blocking runtime defect: `Test 07 explicit free-trial action routing`
- Next action: implement and statically certify `CR-105-02`, deploy to inactive WU-105 STAGING only, then repeat the exact Test 07 prompt.

Owner screenshot evidence for Tests 01-07 supplied in chat on 2026-09-03.
