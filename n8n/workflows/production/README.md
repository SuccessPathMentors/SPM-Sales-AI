# Production n8n workflow artifacts

This directory stores exact exported n8n workflow artifacts that have been checksum-verified before being treated as authoritative engineering evidence.

## Rules
- Exact export only; do not reconstruct or pretty-print before checksum verification.
- Record SHA-256 before and after GitHub transport.
- Do not commit credential secret values.
- Production artifacts are evidence/versioned inputs; GitHub automation must not activate production directly.
