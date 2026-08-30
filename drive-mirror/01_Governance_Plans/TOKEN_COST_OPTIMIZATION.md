# Token, Context, Cost, and Latency Optimization

Last updated: 2026-08-18

## Objective
Keep most project work below ~100K active context while preserving reliability.
Large context capacity is emergency headroom, not a target to fill.

## Operating Zones

### HOT — 10K–30K preferred
Use for normal implementation/debugging.
Load:
- `AGENTS.md`;
- `00_START_HERE/PROJECT_STATE.md`;
- current task;
- affected nodes/sections;
- latest execution/error evidence.

### WARM — 30K–100K
Use when direct dependencies are required.
Add only:
- relevant architecture;
- schemas/mappings;
- connected workflow components;
- recent decisions affecting the task.

### ELEVATED — 100K–200K
Use only for genuine multi-module analysis.
Before entering this zone:
- confirm why smaller retrieval is insufficient;
- persist current findings;
- avoid unrelated historical material.

### HIGH — >200K
Exceptional only.
Before continuing:
- checkpoint project state;
- summarize durable findings into files;
- consider starting a clean task/session;
- retrieve old history selectively instead of carrying it wholesale.

## Mandatory Loading Strategy
Search → Read exact section → Work → Test → Update state.

Do not:
- read all project files at session start;
- read `08_Archive` unless investigating history/regression;
- load all workflow JSON versions;
- replay entire conversation history;
- repeatedly reload unchanged large files;
- paste complete JSON into chat when node-level evidence is enough.

## Large Workflow Rule
For JSON/n8n workflows:
1. search node name/ID/error first;
2. inspect the affected node;
3. inspect direct upstream input;
4. inspect direct downstream dependency if needed;
5. expand only when the dependency graph requires it.

The locked R1 JSON is the baseline. Old workflow copies are cold storage.

## AI Runtime Optimization
1. Route first; load only the required knowledge domain.
2. Keep stable system instructions concise and versioned.
3. Pass top-ranked verified knowledge records, not entire sheets.
4. Store structured sales/session state in Redis rather than replaying full history.
5. Cache stable/versioned lookup data where appropriate.
6. Use deterministic logic for validation, IDs, currency, routing, sheet writes, and other deterministic operations.
7. Do not invoke the AI Agent for direct deterministic success/failure responses.
8. Bound retries and tool outputs.
9. Preserve critical IDs, mappings, decisions, and test evidence in project files before compaction.

## Session Discipline
One session = one primary objective.

Examples:
- R2 retry/error handling;
- lead submission reliability;
- FAQ retrieval;
- calendar booking;
- payments;
- SSO;
- validation;
- reporting.

When the objective materially changes, checkpoint and begin a clean task/session.

## Measurement
Track where available:
- input tokens;
- output tokens;
- number of model calls;
- tool calls;
- Google Sheets calls;
- Redis calls;
- retries/errors;
- total latency and p95;
- cost per successful lead;
- cost per resolved question.

## Guardrails
Token savings must not weaken:
- grounding;
- validation;
- consent;
- data integrity;
- QA evidence;
- release gates.

Optimize after a passing behavioral baseline exists.

## Context Escalation
Level 1: current task + relevant node/range.
Level 2: direct dependencies.
Level 3: architecture/state/related decisions.
Level 4: archive or historical conversation.

Never begin at Level 4.
