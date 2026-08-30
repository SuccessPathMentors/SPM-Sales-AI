# Success Path Mentors AI Sales Bot — Engineering Constitution

Version: 1.0
Adopted: 2026-08-19
Scope: AI Sales Chatbot, n8n workflows, knowledge base, lead capture, scheduling, human handoff, Google Sheets/Redis integrations, notifications, and future GitHub-managed code/configuration.

## 1. Specification Before Implementation
Every material feature or behavioral change must begin with an explicit specification describing the problem, user outcome, requirements, acceptance criteria, failure behavior, and non-goals. Implementation must not begin while material requirements remain ambiguous.

Required production path: constitution → specify → clarify → plan → checklist → tasks → analyze → implement → converge.

## 2. Preserve Locked Behavior
Approved and locked releases are immutable baselines. R1 Reliable Lead Submission remains protected. A locked behavior may change only when a reproduced regression requires repair or a new approved release explicitly supersedes it. Every new change must include regression coverage for affected locked behavior.

## 3. Deterministic-First Engineering
Use deterministic logic for IDs, validation, country/province/state/city/time-zone/currency mapping, fixed routing rules, persistence, deduplication, status transitions, writes, and success/failure confirmation. Use the language model only where semantic understanding, ambiguity resolution, or natural-language generation is genuinely required.

## 4. No Unsupported Commercial Claims
The bot must never invent or infer a price, discount, refund entitlement, teacher qualification, teacher origin, language/gender match, class availability, booking status, policy exception, or other material commercial fact. Claims must come from an approved knowledge source or live system lookup as defined by the relevant specification.

## 5. Live Verification for Volatile Facts
Teacher availability, lesson slots, weekend/evening availability, booking confirmation, and any other time-sensitive operational fact require a live source when the specification says the fact is volatile. Booking success requires successful scheduling plus a valid booking identifier. Failure must never be represented as success.

## 6. Data Integrity and Canonical Identity
Student, parent, lead, session, and activity records must use canonical identifiers and synchronized shared attributes. Country, province/state, city, time zone, currency, subject, status, and other linked fields must follow explicit source-of-truth and conflict-resolution rules. Invalid combinations must be rejected or normalized deterministically.

## 7. Safe Lead Capture and Handoff
Unconfirmed or invalid lead data must not be persisted as confirmed data. Repeated confirmation must not create duplicate leads. Corrected data must update the intended lead/session. Human handoff must preserve relevant conversation state and must not silently lose captured information.

## 8. Multilingual Behavioral Parity
English and Arabic are production languages and must preserve the same business rules, safeguards, pricing logic, qualification behavior, and operational outcomes. Translation differences may change wording but not policy or truth conditions. Additional languages must meet the same standard before release.

## 9. Privacy and Minimum Necessary Data
Collect and expose only data necessary for the sales, scheduling, service, support, or compliance purpose defined by the feature. Secrets, credentials, tokens, private keys, and sensitive operational values must never be committed to GitHub or embedded in specifications, test fixtures, logs, screenshots, or exported workflows.

## 10. Observability and Evidence
A production action must be diagnosable. Important flows must expose enough structured evidence to identify intent, route, validation result, write result, scheduling result, handoff result, and failure category without relying on model narrative. Test evidence must be retained for release gates.

## 11. Test-Gated Releases
Every implementation requires focused functional tests plus regression tests for affected locked behavior. Production-impacting changes require acceptance criteria with PASS/FAIL evidence. Static validation alone does not prove runtime behavior. A release is not complete until its applicable tests pass.

## 12. Smallest Safe Change
Work in bounded changes. Inspect only necessary dependencies, modify the smallest safe surface, test it, record evidence, update project state/change log, and archive obsolete working artifacts when appropriate. Avoid broad rewrites when a targeted change satisfies the specification.

## 13. Source-of-Truth Priority
When artifacts conflict, use this order unless a later approved specification explicitly changes it:
1. Current locked/published runtime artifact
2. PROJECT_STATE.md
3. Current approved feature specification
4. Release/QA evidence
5. Architecture documentation
6. Decision/change logs
7. Archive/history
8. Prior conversation context

## 14. Spec-to-Code Traceability
Every production feature must be traceable from requirement → plan → task → implementation artifact → test evidence → release/change record. GitHub issue/PR references should be attached when GitHub becomes the execution repository.

## 15. Change Governance
Changes to this constitution require an explicit version increment, rationale, impact review, and propagation to dependent templates/specifications. New specifications must pass a constitution check before planning and again before release.

## Release Gate
A change is eligible for production only when:
- requirements and acceptance criteria are complete;
- architecture and data implications are understood;
- privacy/security implications are addressed;
- tasks map to the specification;
- cross-artifact analysis shows no unresolved critical conflict;
- focused runtime tests pass;
- affected regression tests pass;
- project state and change log are updated;
- rollback/recovery behavior is known for production-impacting changes.
