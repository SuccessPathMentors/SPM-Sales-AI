# Success Path Mentors — R1 Workflow Closure Report

Last updated: 2026-08-17.

## File inspected

`ChatBotMSE v2 - Refactor Working Copy (2).json`

- Valid JSON.
- 59 nodes.
- Exported `active=false`.
- `Save Qualified Lead` disabled.

## Historical P0 root cause

The decision layer can correctly produce `action_type=submit_validated_handoff` and `lead_confirmation_accepted=true`, but the workflow does not directly execute the validated handoff subworkflow. Instead, it sends the item to `AI Agent` and relies on the model to choose the `Submit Validated Human Handoff` tool.

A System Message can request a tool call, but cannot guarantee it. Therefore the main flow may end without executing the tool or producing its output.

## Secondary risk

The tool maps personal lead fields with `$fromAI(...)`. These values should already exist in confirmed `sales_state`; asking the model to reconstruct them introduces omission, stale-value, and validation risks. Only the session and confirmation booleans are mapped deterministically.

## Graph observations

- `Submit Validated Human Handoff` → `AI Agent` through `ai_tool`.
- `AI Agent` → `Is Unanswered Trigger?` through the normal main path.
- No main-path edge calls the validated handoff workflow immediately after confirmed decision.
- Legacy direct lead nodes exist but are not connected; they should not be reactivated as a second writer.

## Closure result

- Owner confirmed that lead recording now works without remaining reported problems.
- Complete R1 focused tests passed.
- Phase status: `APPROVED AND LOCKED`.
- Locked baseline: `ChatBotMSE_v2_R1_LOCKED_2026-08-17.json`.
- Future changes must use a new version and re-run permanent regression tests.

## Permanent R1 regression set

New lead; corrected email; repeated confirmation; invalid email; no consent; duplicate session; subworkflow failure; lead summary; operational correction not unanswered; unknown academy question still unanswered.
