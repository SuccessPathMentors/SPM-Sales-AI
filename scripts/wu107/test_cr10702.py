#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

TARGET = 'Apply WU107 Existing Handoff Result'
EXPECTED_NODES = 151


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', required=True, type=Path)
    p.add_argument('--candidate', required=True, type=Path)
    a = p.parse_args()

    before = json.loads(a.input.read_text(encoding='utf-8'))
    after = json.loads(a.candidate.read_text(encoding='utf-8'))
    if len(before.get('nodes', [])) != EXPECTED_NODES or len(after.get('nodes', [])) != EXPECTED_NODES:
        raise SystemExit('CR10702_NODE_COUNT_FAIL')
    if before.get('connections') != after.get('connections'):
        raise SystemExit('CR10702_TOPOLOGY_CHANGED')

    bm = {n['name']: n for n in before['nodes']}
    am = {n['name']: n for n in after['nodes']}
    if set(bm) != set(am):
        raise SystemExit('CR10702_NODE_IDENTITY_SET_CHANGED')
    changed = [name for name in bm if bm[name] != am[name]]
    if changed != [TARGET]:
        raise SystemExit('CR10702_CHANGED_NODE_SET_FAIL:' + repr(changed))

    code = am[TARGET].get('parameters', {}).get('jsCode', '')
    required = [
        "const persistedState=String(r.handoff_state||'FAILED');",
        "const queueVerified=r.downstream_receipt_present===true;",
        "persistedState==='ACCEPTED'",
        "r.downstream_acceptance_present===true",
        "effectiveState='QUEUED'",
        "handoff_state:effectiveState",
        "persisted_handoff_state:persistedState",
        "truth_reconciled:truthReconciled",
        "human_acceptance_verified:Boolean(acceptanceVerified)",
        "fail_closed:failClosed",
    ]
    for marker in required:
        if marker not in code:
            raise SystemExit('CR10702_MARKER_MISSING:' + marker)

    forbidden_old = [
        "handoff_state:accepted?'ACCEPTED':state",
        "success:['QUEUED','ACCEPTED'].includes(state)",
        "fail_closed:!['QUEUED','ACCEPTED'].includes(state)",
    ]
    for marker in forbidden_old:
        if marker in code:
            raise SystemExit('CR10702_OLD_TRUTH_LOGIC_REMAINS:' + marker)

    # All pre-existing locked WU-106 nodes must remain untouched. The CR only changes one WU-107 node.
    locked_mutations = [name for name in changed if not name.startswith('Apply WU107')]
    if locked_mutations:
        raise SystemExit('CR10702_LOCKED_NODE_MUTATION:' + repr(locked_mutations))

    print('CR10702_ACCEPTANCE_EVIDENCE_RECONCILIATION_STATIC_PASS')
    print('changed_nodes=1 topology_unchanged=PASS wu106_locked_nodes_mutated=false')


if __name__ == '__main__':
    main()
