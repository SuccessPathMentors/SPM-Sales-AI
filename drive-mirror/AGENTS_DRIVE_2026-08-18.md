# AGENTS.md — Project Context & Execution Policy

Last updated: 2026-08-18
Project: Success Path Mentors AI Sales Chatbot

## Mission
Work accurately while minimizing unnecessary context, token usage, latency, and repeated file reads.

The conversation is temporary working memory.
Google Drive project files are the durable source of truth.

## Mandatory Session Startup
Read only:
1. `00_START_HERE/PROJECT_STATE.md`
2. the current task file, if one exists
3. exact affected workflow nodes/files required for the task

Read `00_START_HERE/00_START_HERE.md` only when broader project orientation is needed.

Do NOT automatically read:
- the full previous conversation;
- every governance document;
- all workflow JSON versions;
- `08_Archive`;
- historical pasted transcripts;
- completed task evidence unrelated to the current objective.

## Source-of-Truth Priority
When information conflicts, use:
1. locked/current workflow artifact;
2. `PROJECT_STATE.md`;
3. current task specification;
4. release/QA evidence;
5. architecture documentation;
6. decision/change logs;
7. archive/history;
8. old conversation context.

Never downgrade a current decision based only on older history.

## Context Budget
### Hot Context — 10K–30K preferred
Normal debugging and implementation zone.

### Normal Working Context — <=100K preferred
Most sessions must remain in this range.

### Elevated Context — 100K–200K
Use only for genuine multi-component dependency analysis.

### High Context — >200K
Exceptional. Checkpoint first and consider a clean session.

Large context capacity is safety headroom, not a target.

## Retrieval Protocol
Always use:

Search → Read exact range/node → Work → Test → Update State

For large JSON:
- search node name/ID/error/field;
- inspect affected node;
- inspect direct upstream input;
- inspect direct downstream dependency only if needed;
- expand graph only when evidence requires it.

For logs:
- latest failed execution first;
- smallest useful output range;
- do not load repeated successful logs.

For docs:
- locate exact heading/section;
- avoid full-document reads when a bounded section answers the task.

## One Session = One Primary Objective
Examples:
- R2 retry/error handling;
- deterministic lead submission;
- FAQ retrieval;
- calendar booking;
- payments;
- authentication/SSO;
- validation;
- reporting.

If the objective changes materially:
1. checkpoint;
2. update state/changelog;
3. start a clean task/session.

## Change Discipline
For each implementation:
1. define one measurable outcome;
2. inspect only direct dependencies;
3. make the smallest safe change;
4. run a focused test;
5. preserve unrelated locked behavior;
6. record evidence;
7. update `PROJECT_STATE.md`;
8. update `CHANGELOG.md`;
9. archive obsolete working versions when appropriate.

## R1 Protection
R1 — Reliable Lead Submission is APPROVED AND LOCKED.
Do not modify locked R1 behavior unless:
- a regression is reproduced, or
- a new version/phase explicitly supersedes it.

## Compaction Safety
Before context becomes large, persist:
- exact workflow/version name;
- node IDs/names;
- schemas/mappings;
- approved decisions;
- test evidence;
- unresolved issue;
- next action.

Do not depend on compaction to preserve exact technical state.

## Deterministic-First Engineering
Do not use the model for operations that can be deterministic, including:
- IDs;
- validation;
- country/province/currency mappings;
- routing rules;
- sheet writes;
- fixed status transitions;
- direct success/failure responses.

Use AI where language understanding, ambiguity resolution, or generation is genuinely required.

## Tool Output Rule
Keep outputs bounded.
Do not paste complete unchanged JSON or large sheets into chat when node-level/range-level evidence is enough.
Summarize findings and retain only identifiers/evidence needed for the next action.

## Session Exit Gate
A session is not complete until `PROJECT_STATE.md` can answer:
- Where are we?
- What is locked?
- What changed?
- What passed/failed?
- What is still open?
- What exact task comes next?

A fresh session should resume without reading the previous conversation.
