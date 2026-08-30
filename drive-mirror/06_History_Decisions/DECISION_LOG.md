# Decision Log

| ID | Date | Decision | Reason | Status |
|---|---|---|---|---|
| D-001 | 2026-08-17 | Use the dedicated Drive workspace as the project reference | Preserve traceability | Approved |
| D-002 | 2026-08-17 | Do not move the live AI Knowledge Sheet | Preserve n8n IDs and permissions | Approved |
| D-003 | 2026-08-17 | Work one small phase at a time with approval gates | Prevent scope drift and regression mixing | Approved |
| D-004 | 2026-08-17 | Core functionality precedes voice/CRM/advanced retrieval | Focus on stable delivery | Approved |
| D-005 | 2026-08-17 | Keep one authoritative lead writer | Prevent duplicate/conflicting writes | Approved |
| D-006 | 2026-08-17 | Use Redis for temporary conversation/sales state | Session memory with TTL | Approved |
| D-007 | 2026-08-17 | Plan PostgreSQL/Supabase as future durable storage | Sheets is not the final transactional store | Planned |
| D-008 | 2026-08-17 | R1 cannot lock until lead submission is deterministic | False success without sheet write is P0 | Active |
| D-009 | 2026-08-17 | Canada uses CAD and USA uses USD with package numbers 110/220/280; verified province/state/city may resolve country | Owner-approved business rule | Approved and locked |
| D-010 | 2026-08-17 | Apply case-by-case service recovery with no automatic remedy or guaranteed result | Owner-approved refund/recovery policy | Approved and locked |
| D-011 | 2026-08-17 | Keep knowledge governance and n8n implementation as separate work tracks | Prevent mixing approved content with runtime fixes | Approved |
| D-012 | 2026-08-17 | Pause at R1 diagnosis; make no additional live changes | Owner needs to stop and resume from the exact checkpoint | Approved |
| D-013 | 2026-08-17 | R1 Reliable Lead Submission is approved and locked | Owner confirmed the complete phase and tests passed with successful lead recording | Approved and locked |
| D-014 | 2026-08-17 | Preserve an immutable R1 workflow snapshot and begin future work from a new version | Prevent regression and preserve rollback | Approved |

## Next required decision

Approve the first bounded R2 reliability task before changing n8n. Separately, decide `PHR-004` before the next knowledge-base write.
