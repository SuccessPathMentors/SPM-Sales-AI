# CR-XXX — Change Request

Status: DRAFT
Requested by: <WU/owner>

## Trigger
Why the current Working Unit cannot proceed without changing a locked/baselined dependency.

## Locked artifact impacted
- WU / artifact:
- Current version/hash:

## Proposed change
Describe the smallest required change.

## Impact analysis
- Directly affected WUs:
- Tests to rerun:
- n8n workflows/nodes affected:
- Release/canary impact:

## Decision
- [ ] Reject — continue with current locked baseline
- [ ] Approve new version

## If approved
1. Create new version/release candidate.
2. Do not overwrite the locked artifact.
3. Re-run targeted and impacted regression.
4. Review and relock.
5. Resume blocked downstream work only after the new dependency is locked.
