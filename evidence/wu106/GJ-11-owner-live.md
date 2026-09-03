# WU-106 — GJ-11 Owner Live Certification

Status: PASS ✅
Journey: GJ-11 — Long Conversation to Stale-Context Override
STAGING workflow: `vvHvidUHVxM5wTVT`
Candidate: CR-106-03 / `2e219adbdd612106b782993cbcb2f94da6c0737b250264060b473f12f0fcc81f` / 141 nodes

## Owner-observed sequence
1. `My son is in Grade 8 and needs Math tutoring.`
2. `How much does it cost?`
3. `That is too expensive for me.`
4. `How does the free trial work?`
5. `Actually, I want to ask about Grade 10 Physics tutoring now.`

## PASS evidence
- the final clear current message became the active objective immediately;
- Grade 10 + Physics replaced the stale Grade 8 + Math student/subject context for the current turn;
- the bot did not force the user back into the old pricing objection;
- the bot did not remain stuck in the free-trial flow;
- the bot did not re-ask Grade or Subject because both were explicitly supplied in the current message;
- no unsolicited trial start or registration action was initiated;
- the old Grade 8 Math context did not appear in the final response.

## QA observations — non-blocking for GJ-11
- The final response included `aligned with Ontario's standards` even though Ontario was not explicitly supplied in this test session. This should be reviewed during final grounding/quality review to ensure curriculum/location claims are source-backed and not inferred from stale or unrelated context.
- The follow-up question about preferred teaching language was not required to prove GJ-11 and may be more information than necessary for this turn. It is a UX/directness observation, not a stale-context failure.

## Certification scope
Customer-visible stale-context override behavior PASS. The two QA observations above remain open for final material/grounding review and do not change the GJ-11 journey verdict.

## Progress after this test
- GJ-01: PASS
- GJ-02: PASS
- GJ-03: PASS
- GJ-04: PASS after CR-106-02
- GJ-05: PASS after CR-106-03
- GJ-06: PASS
- GJ-07: PASS
- GJ-08: PASS
- GJ-09: PASS
- GJ-10: PASS
- GJ-11: PASS
- GJ-12: PENDING

Current owner-observed live journey score: `11 / 12 PASS`.
