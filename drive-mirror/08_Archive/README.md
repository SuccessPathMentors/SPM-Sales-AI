# 08_Archive — Cold Storage Reference

Source Drive folder ID: `191AtJ609-9wdulAmi0q4vmWuVbgWu9Rl`
Migration classification: `ARCHIVE_SECONDARY_REFERENCE`

## Authority rule
Files in this folder are historical evidence only. They must never override current GitHub `docs/STATE.yaml`, approved specifications, locked decisions, current release evidence, or verified runtime identity.

The Drive archive contains historical pasted transcripts/text snapshots and older workflow JSON exports. Examples visible in the provider inventory include multiple `Pasted text(20260816-...).txt` / `Pasted text(20260817-...).txt` files, `ChatBotMSE v2 - Refactor Working Copy (1).json`, `ChatBotMSE v2 - Refactor Working Copy.json`, and `Validated Human Handoff.json`.

## Migration policy
- Do not load archive transcripts into normal agent context.
- Do not treat archive workflow exports as implementation baselines unless an approved current document explicitly names one as rollback/reference evidence.
- Preserve Drive folder identity and provider metadata for traceability.
- Exact-byte archive migration is optional for engineering source-of-truth cutover because this directory is cold historical storage, not an active project authority.
- If Drive is ever scheduled for deletion, perform a separate cold-archive export before deletion.

## Retrieval rule
Use archive material only when investigating historical decisions, regressions, provenance, or rollback ancestry. Prefer current GitHub specs/evidence first.
