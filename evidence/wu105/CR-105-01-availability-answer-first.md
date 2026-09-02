# CR-105-01 — Availability Answer-First Safety Rewrite Repair

Status: IN_PROGRESS
WU: WU-105 — Golden Intents Optimization
Issue: #60
PR: #61

## Trigger
Owner-facing Runtime Test #4 used a fresh session with:

`Is Saturday available for a Grade 8 Math lesson?`

Observed customer output:

`We can proceed with that step, but it is only confirmed after the required system check or action succeeds.`

Result: **FAIL** for the WU-105 `availability` vs `schedule_request` confusion/answer-first gate.

## Why this is a WU-105 failure
The response is safe from a false booking claim, but it does not directly answer the availability question. WU-105 requires `availability` to state that live availability is not yet known and requires a live schedule check before confirmation.

## Root cause
The inherited locked `Validate + Guard WU92 Sales Agent Output` node contains the broad positive-success detector:

`/\b(booked|confirmed|saved|registered|refunded|discount approved|tutor assigned)\b/i`

A safe availability answer such as `...needs a live check before it can be confirmed` still contains the token `confirmed`. The inherited validator therefore sets `safety_rewrite_applied=true` and replaces the useful availability-specific wording with the generic safe action message.

The later locked WU-94 Scheduling Truth Guard preserves safety, but it cannot recover the lost availability-specific answer-first wording in this case.

## Constraint
WU-104 is LOCKED. CR-105-01 MUST NOT edit the inherited WU92/WU94/WU104 nodes or relax any live-truth/action gate.

## Proposed narrow repair
Add one WU-105 deterministic Code node after `Apply WU94 Scheduling Truth Guard` and before `Resolve WU95 Conversion Mode`:

`Apply WU105 Availability Answer-First Guard`

It may rewrite `answer_text` only when all are true:
- classified intent is `availability`;
- live availability is not verified;
- either inherited WU92 safety rewrite fired or WU94 rewrote an unverified booking/availability claim.

Safe replacement meaning:
- EN: `I need to check the live schedule before I can tell you whether your requested day or time has an open tutoring slot.`
- AR/FR equivalent meaning.

It MUST preserve:
- `proposed_action`;
- `action_requires_gateway`;
- `purposeful_question`;
- classifier intent;
- source truth;
- WU94 live scheduling truth;
- all action permissions;
- Production read-only status.

No new LLM, classifier, credential, external call, or business write is permitted.

## Expected candidate delta
- locked WU-104 nodes: 126 unchanged;
- existing WU-105 prompt overlay: retained;
- new deterministic availability guard: +1;
- expected WU-105 node count after CR-105-01: 128.

## Re-test gate
Repeat the exact fresh-session prompt after STAGING update:

`Is Saturday available for a Grade 8 Math lesson?`

PASS requires an availability-specific statement that a live schedule check is required, no false availability/booking claim, no Grade/Math re-ask, and at most one smallest scheduling qualifier.
