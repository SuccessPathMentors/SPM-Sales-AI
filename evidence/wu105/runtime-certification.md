# WU-105 Runtime Golden Intent Certification Evidence

Status: IN_PROGRESS — CR-105-02 DEPLOYED / TEST-07 RETEST PENDING
Workflow: `[STAGING] SPM_WU105_GOLDEN_INTENTS_V1`
Workflow ID: `KXfalaYSCLdgmf4X`
Current Candidate SHA-256: `7fc201137671b1cd47f9fc6b4ec60a9b563b2bae7c0776952ec68e0988bfed1e`
Current node count: `129`
Current remote versionId: `6e1b8a71-a9e2-4bf5-8f09-a26c991a10ac`
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

Assessment:
- Grade 8 and Math were recognized: PASS;
- no false booking/confirmation claim: PASS;
- explicit request to **start a free trial** was honored as conversion/intake intent: FAIL;
- response entered generic subject/learning-need discovery instead of the `free_trial` progression/intake path: FAIL.

### Root cause boundary
The locked classifier contract already defines explicit `start/request/arrange/book/receive a free trial` wording as `free_trial`, and WU95 already treats `free_trial` as a lead/conversion intent. If `free_trial` reaches WU95, the deterministic lead truth guard renders the smallest missing lead field instead of a generic subject answer.

The observed customer output therefore showed that the explicit free-trial action meaning was being lost before WU95 lead progression for this compound `free trial + Grade 8 + Math` message.

## CR-105-02 — Explicit Free-Trial Action Semantic Guard

A narrow deterministic WU-105 guard was added **after locked WU-104 short-trial handling and before WU89 classifier-context capture**:

`Apply WU104 Short Trial Inquiry Guard -> Apply WU105 Explicit Free Trial Action Guard -> Capture WU89 Classifier Context`

Behavior:
- detects only unmistakable action wording such as `I want to start/book/request a free trial`;
- reuses the existing authoritative `free_trial` taxonomy row rather than creating a new intent;
- narrow remap scope is limited to common semantic-confusion intents;
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

The one-time deployment workflow was removed after successful update.

**Exact retest status:** `PENDING OWNER SCREENSHOT` using the same fresh-session prompt:
`I want to start a free trial for my son in Grade 8 Math.`

## Running certification summary

- Customer-output tests attempted: `7`
- Passing before Test 07 retest: `6 / 7`
- Initial failures encountered: `2` (Test 04, Test 07)
- Repaired and retested: `1` (Test 04 via CR-105-01)
- CR-105-02 static/deployment/readback: `PASS`
- Current blocking runtime gate: exact Test 07 customer-output retest
- Next action after PASS: continue Golden Intent runtime certification.

Owner screenshot evidence for Tests 01-07 supplied in chat on 2026-09-03.
