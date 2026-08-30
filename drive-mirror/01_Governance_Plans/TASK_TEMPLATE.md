# TASK_TEMPLATE.md — Bounded Work Session

Use one copy per meaningful task.

## Task ID
`R?-TASK-###`

## Task Name
[Short name]

## Phase
[R2 / R3 / Knowledge / Calendar / Payments / etc.]

## Single Objective
[One measurable result only]

## Completion Criteria
- [ ] implementation completed
- [ ] focused test passed
- [ ] regression risk checked
- [ ] evidence recorded
- [ ] `PROJECT_STATE.md` updated
- [ ] `CHANGELOG.md` updated

## Source of Truth
- `00_START_HERE/PROJECT_STATE.md`
- Current workflow: [exact filename]
- Relevant evidence: [file/execution ID]

## Context Budget
Target: 10K–30K.
Preferred maximum: 100K.

Escalate above 100K only if:
[document concrete dependency reason]

## Files / Nodes Allowed Initially
- [node/file 1]
- [node/file 2]
- [execution/range]

## Do Not Load Initially
- `08_Archive`
- old JSON versions
- full conversation history
- unrelated reports/modules

## Observed Behavior
[Exact current result/error]

## Expected Behavior
[Exact expected result]

## Latest Evidence
- Execution ID:
- Timestamp:
- Error/output:
- Sheet row/reference, if applicable:

## Dependency Expansion Log
Only fill this if more context is needed.

### Expansion 1
Reason:
Additional node/file:
Finding:

## Proposed Smallest Change
[Describe minimal safe modification]

## Test Plan
1. [test]
2. [test]
3. [regression check]

## Result
PASS / FAIL / PARTIAL

## Durable Findings
[Only information needed by future sessions]

## Next Action
[One exact next action]
