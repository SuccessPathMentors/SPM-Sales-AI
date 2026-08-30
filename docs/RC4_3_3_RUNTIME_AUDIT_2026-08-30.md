# RC4.3.3 Runtime Artifact Audit — 2026-08-30

## Identity

- Workflow: `SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json`
- n8n workflow ID: `CMBMpxX5AqqK2UTn`
- Export `active`: `true`
- n8n version ID: `ee6d40dc-440a-4b3e-9948-090a73ae9222`
- Exact uploaded export size: `330119` bytes
- SHA-256: `680496f2b68b13dd7105e72fd132a2066d70ec969e6e0675f138ebb1fb16fe39`
- Node count: `114`
- Disabled nodes: `0`
- `Execute Workflow` nodes: `0`

## Runtime evidence

Owner-provided n8n UI evidence on 2026-08-30 showed this workflow Published and a successful live execution:

- Execution ID: `2539`
- Timestamp: `2026-08-30 18:56:47` as displayed by n8n
- Status: `Succeeded`
- Duration: `19.745s`

The trigger is `Greenfield Chat Trigger`, public embedded chat, with CORS restricted to `https://successpathmentors.net` and previous-session loading from memory.

## Release scope encoded by the artifact

The canonical session envelope declares `workflow_mode: PRODUCTION_ACTIVE` and `production_cutover_authorized: true`.

Included:
- Knowledge / FAQ
- Redis conversation state
- EN / AR / FR
- Lead / CRM write (`INCLUDED_CERTIFIED`)

Explicitly excluded from live execution:
- Scheduling / booking
- Human handoff
- Payment
- External follow-up

## Dependency findings

There are no `Execute Workflow` nodes in the export. RC4.3.3 therefore does not call an n8n sub-workflow through the native Execute Workflow node.

Human handoff is represented by `Build WU95 Handoff Contract`, but its contract is configured as execution excluded / adapter not configured. The separately published historical Human Handoff workflow must not be assumed to be invoked by RC4.3.3.

Scheduling contains WU94 truth/contract/adapter-result nodes, but the release envelope explicitly excludes scheduling/booking execution.

Lead/CRM contains a certified production path including:
- `Check WU95 Existing Lead [READ ONLY]`
- `Upsert WU95 Lead [CERTIFIED PRODUCTION ADAPTER]`
- `Verify WU95 Lead Write [READBACK]`
- deterministic truth/failure handling

## External systems / credentials referenced

Credential references exist for Redis, Google Sheets, and OpenAI. The workflow export contains credential IDs/names as n8n references; no credential secret values were intentionally added to this audit document.

The authoritative intent catalog is loaded from the SPM Google Sheet and requires 62 unique ACTIVE intents before direct classification is permitted.

## Migration conclusion

For MIG-001 purposes, the current main production website-chat workflow identity is VERIFIED:

`SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json` / `CMBMpxX5AqqK2UTn`

The exact uploaded export is now the artifact identity reference for MIG-002 reconciliation, keyed by the SHA-256 above.

Remaining MIG-001 work is limited to reconciling any separately published/support workflows that matter operationally; they are not native Execute Workflow dependencies of RC4.3.3.

Do not enable excluded adapters merely because their contract nodes exist. Any expansion of production scope requires the relevant Working Unit, regression evidence, approval, and release lock.