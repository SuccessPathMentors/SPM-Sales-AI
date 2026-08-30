# External Automation and Sales-Knowledge Reuse Policy

External automations may be studied and adapted later, but never copied blindly.

## Evaluation checklist

- license and ownership permit reuse;
- no customer, credential, or confidential data is imported;
- sales claims match Success Path Mentors approved facts;
- prompts do not bypass consent, grounding, or security rules;
- integrations support idempotency, retries, logging, and rollback;
- token/cost impact is measured;
- a sandbox test passes before production;
- an internal owner approves the change.

## Safe reuse pattern

Extract the general pattern (for example lead qualification, objection classification, or follow-up scheduling), rewrite it to the project data contracts, and validate it against the project test suite. Store the external source URL, license, adaptation notes, and reviewer in `SOURCE_LOG` or this workspace.

## Expansion order

1. Analytics and read-only reporting.
2. CRM synchronization with idempotent upserts.
3. Sales playbook/nurture content after factual review.
4. Voice and additional channels only after the text system is locked.
