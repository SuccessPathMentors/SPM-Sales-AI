#!/usr/bin/env python3
from wu107_handoff_runtime import HandoffStore, HandoffExecutor, ProviderResult


def assert_eq(a, b, msg):
    if a != b:
        raise AssertionError(f'{msg}: expected={b!r} actual={a!r}')


def main():
    # 1. Queue receipt is not human acceptance.
    store = HandoffStore(); ex = HandoffExecutor(store)
    r = ex.execute('k1', ProviderResult('accepted_for_queue', receipt_id='R1'))
    assert_eq(r.state, 'QUEUED', 'queue receipt state')
    assert_eq(r.may_claim_human_received, False, 'queue receipt acceptance claim')

    # 2. Verified human acceptance transitions QUEUED -> ACCEPTED.
    r = ex.accept_human('k1', 'A1')
    assert_eq(r.state, 'ACCEPTED', 'verified acceptance state')
    assert_eq(r.may_claim_human_received, True, 'verified acceptance claim')

    # 3. Duplicate logical request is idempotent.
    store = HandoffStore(); ex = HandoffExecutor(store)
    ex.execute('dup', ProviderResult('accepted_for_queue', receipt_id='R2'))
    ex.execute('dup', ProviderResult('accepted_for_queue', receipt_id='R2'))
    assert_eq(store.created_count, 1, 'duplicate logical case count')

    # 4. Retryable failure remains REQUESTED until bounded retry exhausted.
    store = HandoffStore(); ex = HandoffExecutor(store)
    r = ex.execute('retry', ProviderResult('failed', failure_class='TIMEOUT'))
    assert_eq(r.state, 'REQUESTED', 'timeout attempt 1')
    r = ex.execute('retry', ProviderResult('failed', failure_class='RATE_LIMIT'))
    assert_eq(r.state, 'REQUESTED', 'rate limit attempt 2')
    r = ex.execute('retry', ProviderResult('failed', failure_class='TRANSIENT_5XX'))
    assert_eq(r.state, 'FAILED', 'retry exhaustion')
    assert_eq(r.attempt_count, 3, 'bounded attempt count')

    # 5. Permanent failure fails immediately.
    store = HandoffStore(); ex = HandoffExecutor(store)
    r = ex.execute('perm', ProviderResult('failed', failure_class='AUTHORIZATION'))
    assert_eq(r.state, 'FAILED', 'permanent failure')
    assert_eq(r.attempt_count, 1, 'permanent failure attempts')

    # 6. Missing receipt cannot create QUEUED truth.
    store = HandoffStore(); ex = HandoffExecutor(store)
    r = ex.execute('badreceipt', ProviderResult('accepted_for_queue'))
    assert_eq(r.state, 'FAILED', 'missing queue receipt')
    assert_eq(r.may_claim_human_received, False, 'missing receipt acceptance claim')

    # 7. Human acceptance cannot be applied before verified queue state.
    store = HandoffStore(); store.get_or_create('early'); ex = HandoffExecutor(store)
    try:
        ex.accept_human('early', 'A2')
        raise AssertionError('early acceptance should fail')
    except ValueError:
        pass

    # 8. Cancellation is explicit and terminal.
    store = HandoffStore(); ex = HandoffExecutor(store)
    store.get_or_create('cancel')
    r = ex.cancel('cancel')
    assert_eq(r.state, 'CANCELLED', 'cancel state')
    r2 = ex.execute('cancel', ProviderResult('accepted_for_queue', receipt_id='R3'))
    assert_eq(r2.state, 'CANCELLED', 'cancel remains terminal')

    # 9. Provider may return queue receipt and acceptance together only when both evidence exist.
    store = HandoffStore(); ex = HandoffExecutor(store)
    r = ex.execute('both', ProviderResult('accepted_for_queue', receipt_id='R4', human_acceptance_id='A4'))
    assert_eq(r.state, 'ACCEPTED', 'queue+acceptance evidence')
    assert_eq(r.may_claim_human_received, True, 'queue+acceptance claim')

    # 10. Unknown provider result fails closed for execution truth.
    store = HandoffStore(); ex = HandoffExecutor(store)
    r = ex.execute('unknown', ProviderResult('mystery'))
    assert_eq(r.state, 'FAILED', 'unknown provider result')
    assert_eq(r.may_claim_human_received, False, 'unknown result acceptance claim')

    print('WU107_HANDOFF_RUNTIME_EXECUTABLE_PASS')
    print('cases=10 idempotency=PASS retry=PASS truth_separation=PASS')


if __name__ == '__main__':
    main()
