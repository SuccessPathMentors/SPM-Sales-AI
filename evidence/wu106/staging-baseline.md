# WU-106 — Baseline STAGING Creation Evidence

Status: PASS — LIVE JOURNEY CERTIFICATION PENDING
Issue: #65
PR: #66

## Candidate identity
- mode: `OBSERVE_ONLY_BASELINE`
- candidate SHA-256: `134b2d861d6c5060ca52d8fd838b2cdd7d5d88ffa74855e3de1665e302afda67`
- node count: `132`
- locked upstream: WU-105 `CR-105-04`, SHA-256 `42ba2b9de1f52c0db1fc32e59974dc40ebce80b787677ac6b0d4418a6315bca1`, 131 nodes
- WU-106 delta: one deterministic Code node, `Build WU106 Journey Orchestration Envelope`
- existing upstream nodes mutated: `0`
- prompt mutation: `false`
- authoritative `sales_state` mutation: `false`
- action-permission mutation: `false`
- `irreversible_action_allowed=false`

## Offline certification
GitHub Actions run `33700001249` — SUCCESS.

Evidence artifact:
- name: `wu106-observe-only-candidate`
- artifact ID: `9873158651`
- ZIP SHA-256: `25d866bc6109d1a56b245499d6fc9416bd6e069c9cec954a5f8b746d15b1d410`

The run rebuilt the exact locked WU-105 final lineage from the locked WU-104 artifact and verified the final WU-105 SHA before adding the single WU-106 node.

## Controlled STAGING creation
One-time controlled create run `33700339495` — SUCCESS.

Operation:
- `CREATE_INACTIVE_NONPROD`
- created workflow ID: `vvHvidUHVxM5wTVT`
- workflow name: `[STAGING] SPM_WU106_END_TO_END_JOURNEYS_V1`
- remote versionId: `de2d9eb9-5632-4ebc-988f-a555253daa82`
- remote node count: `132`
- remote active: `false`
- published/activated: `false`

Remote readback result: `WU106_REMOTE_READBACK_PASS`.

Remote verification confirmed:
- WU-106 observe-only envelope exists;
- WU-105 overlay feeds the WU-106 envelope, which returns to the original WU92 response generator;
- CR-105-01, CR-105-02, CR-105-03, and the CR-105-04 POLICIES loader remain present;
- WU-102 queue remains `appendOrUpdate` with `queue_event_id` idempotency;
- STAGING Redis Chat Memory remains isolated with `spm:staging:chat:<sessionId>`;
- Production write performed: `false`.

Creation evidence artifact:
- name: `wu106-one-time-staging-create-evidence`
- artifact ID: `9873274375`
- ZIP SHA-256: `796ae4c94de402db8e6ed990b1959f8e266a25810f38634f7cda93da61bf2d07`

## Protected workflow IDs
The controlled create explicitly protected and did not update:
- Production: `CMBMpxX5AqqK2UTn`
- WU-101 STAGING: `mMZVFxJIxE7a9SSW`
- WU-102 STAGING: `1kaRBBFVJYbPxvQG`
- WU-103 STAGING: `5COEoxXjk8AvuGBa`
- WU-104 STAGING: `Bt3PvOIbFzU0O9gk`
- locked WU-105 STAGING: `KXfalaYSCLdgmf4X`

The temporary one-time creation workflow was removed from the WU-106 branch immediately after successful creation/readback.

## Next gate
This evidence certifies the WU-106 baseline identity and inactive STAGING deployment only. It does **not** certify the 12 Golden Journeys. Owner-observed multi-turn live journey testing is the next gate; any customer-output defect must be remediated through a versioned CR-106 and exact retest before final review/lock.
