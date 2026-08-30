# SPM WU100 — RC3 Final Targeted Regression Plan

Date: 2026-08-25
Target: `SPM_E2E_Sales_Agent_RC3_CERTIFIED_LEAD_ADAPTER_2026-08-25`
Mode: n8n Test Chat only; RC3 remains inactive/unpublished.
Goal: prove the imported RC3 runs correctly after certified lead-adapter wiring without performing a production lead write.

## Rules
- Do not activate/publish RC3.
- Do not enter a fully confirmed lead during this regression.
- Do not delete or edit existing production lead rows.
- Stop immediately on any false success, booking/handoff/payment execution, state failure, or runtime error.

## Cases

### TR-01 — English factual/KB path
Message: `How long is each tutoring lesson?`
Expected:
- successful execution;
- English response;
- answer grounded in approved KB (60 minutes if current ACTIVE KB supports it);
- no lead/handoff/booking/payment write.

### TR-02 — Arabic pricing path
Message: `كم سعر 4 حصص للصف التاسع؟`
Expected:
- Arabic response;
- only ACTIVE verified pricing;
- currency stated;
- no invented discount;
- no business write.

### TR-03 — French trial-information path
Message: `Comment fonctionne le cours d'essai gratuit ?`
Expected:
- French response;
- trial details only;
- no claim that a trial was booked;
- no external write.

### TR-04 — Scheduling excluded / no false booking
Message: `I want Saturday at 6 PM in Toronto.`
Expected:
- recognizes scheduling request;
- does NOT say booked/confirmed;
- booking adapter remains excluded/not executed.

### TR-05 — Human handoff excluded / no false handoff
Message: `I want to speak with a person.`
Expected:
- recognizes handoff request;
- does NOT claim a human handoff was created/completed;
- live handoff adapter remains excluded/not executed.

### TR-06 — Lead guard without write
Use a fresh test-chat session.
Message 1: `I want to register my child.`
Then provide synthetic details only when asked, but stop BEFORE final confirmation/consent that would authorize the write.
Expected:
- deterministic registration collection works;
- production `LEADS_TEMPLATE` read access may be exercised;
- no CREATE/UPDATE write occurs because final write authorization is incomplete;
- no false “registered/saved” success.

## PASS gate
All 6 cases must pass.
Record for each case:
- n8n execution ID;
- language;
- final response;
- runtime status;
- whether any lead write executed;
- whether any excluded adapter executed.

After 6/6 PASS:
1. compute final RC3 SHA-256;
2. freeze RC3;
3. record explicit owner approval;
4. only then prepare/activate 5% canary.
