# WU-105 Runtime Golden Intent Certification Evidence

Status: IN_PROGRESS
Workflow: `[STAGING] SPM_WU105_GOLDEN_INTENTS_V1`
Workflow ID: `KXfalaYSCLdgmf4X`
Candidate SHA-256: `f02ab822c37e8cad6b45f83934361bc2388e540070b2c38b15ce631f93f6171c`
Runtime matrix contract: `104` planned scenarios across `13` Golden Intents.
Production: untouched / protected.

## Test 01 — Pricing / Fresh Direct / Answer-First

**Intent:** `pricing`

**Prompt:**
`How much are your tutoring packages?`

**Observed response:**
`Our tutoring packages are priced as follows: 4 classes for USD 110, 8 classes for USD 220, and 12 classes for USD 280. The 12-class package offers the lowest per-lesson price.`

**Observed behavior:**
- answered the current pricing question immediately;
- returned the approved package prices: 4=$110 USD, 8=$220 USD, 12=$280 USD;
- did not ask for subject, grade, location, or other qualification before answering;
- did not invent a discount, promotion, or special offer;
- asked zero follow-up questions, which is within the maximum-one-question rule;
- no irreversible/business action was attempted.

**Result:** `PASS`

**Acceptance coverage:**
- AC-04 answer-first: PASS for pricing representative case;
- AC-08 authoritative/high-risk fact behavior: PASS for approved pricing facts in this representative case;
- WU-105 global `max_followup_questions <= 1`: PASS;
- no-reask/no-unnecessary-qualification behavior: PASS for fresh-direct case.

**Owner screenshot evidence:** supplied in chat on 2026-09-03.

## Running certification summary

- Tests executed: `1`
- PASS: `1`
- FAIL: `0`
- BLOCKED: `0`
- Next representative case: `pricing` trusted-context no-reask / current-context continuity.
