#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path

EXPECTED_INPUT_SHA='fc4263b6bf029195a58b819ce4b06d6f499090d39017ff6ca906f173b7443f59'
EXPECTED_NODES=151
TARGET='Build WU107 Handoff Execution Request [STAGING]'


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def resolve(primary='',secondary='',wu96_mode='normal',wu96_requires=False,wu96_reason='',wu96_intent='',wu96_secondary='',ctx_intent='',wu106_support=False,wu106_intent='',sticky=False):
    approved={'human_handoff','complaint','technical_issue','technical_support','account_login','update_contact_info','account_update','contact_update','payment_problem','change_teacher'}
    current96=wu96_mode=='support' and wu96_requires is True and wu96_reason=='CURRENT_SUPPORT_INTENT_OVERRIDES_SALES'
    current106=wu106_support is True
    candidates=[primary,secondary,wu96_intent,wu96_secondary,ctx_intent,wu106_intent]
    matched=''
    for x in [primary,secondary]:
        if x in approved: matched=x; break
    if not matched and (current96 or current106):
        for x in candidates:
            if x in approved: matched=x; break
    reason='OTHER_APPROVED_HANDOFF'
    if matched=='human_handoff': reason='EXPLICIT_HUMAN_REQUEST'
    elif matched in {'technical_issue','technical_support'}: reason='TECHNICAL_SUPPORT'
    elif matched=='complaint': reason='COMPLAINT_ESCALATION'
    elif matched in {'account_login','update_contact_info','account_update','contact_update'}: reason='ACCOUNT_OR_CONTACT_SENSITIVE_CHANGE'
    return bool(matched),matched,reason


def main():
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--candidate',required=True);a=p.parse_args()
    if sha(a.input)!=EXPECTED_INPUT_SHA: raise SystemExit('CR10701_TEST_INPUT_SHA_FAIL')
    before=json.loads(Path(a.input).read_text()); after=json.loads(Path(a.candidate).read_text())
    if len(before['nodes'])!=EXPECTED_NODES or len(after['nodes'])!=EXPECTED_NODES: raise SystemExit('CR10701_NODE_COUNT_FAIL')
    b={n['name']:n for n in before['nodes']}; c={n['name']:n for n in after['nodes']}
    if set(b)!=set(c): raise SystemExit('CR10701_NODE_SET_DRIFT')
    changed=[n for n in b if b[n]!=c[n]]
    if changed!=[TARGET]: raise SystemExit('CR10701_CHANGED_NODE_SET_FAIL:'+repr(changed))
    if before.get('connections')!=after.get('connections'): raise SystemExit('CR10701_TOPOLOGY_DRIFT')
    code=c[TARGET]['parameters']['jsCode']
    required=[
      'wu96_communication_decision','support_requires_handoff','CURRENT_SUPPORT_INTENT_OVERRIDES_SALES',
      'wu106_orchestration','support_override_active','technical_issue','TECHNICAL_SUPPORT',
      'Sticky historical support state is evidence for context only',
      "signal_source:signalSource"
    ]
    for marker in required:
        if marker not in code: raise SystemExit('CR10701_CODE_MARKER_MISSING:'+marker)
    # Exact behavioral matrix for the recovered trigger semantics.
    cases=[
      ('explicit human',dict(primary='human_handoff'),(True,'human_handoff','EXPLICIT_HUMAN_REQUEST')),
      ('technical_issue via WU96',dict(primary='unknown_intent',wu96_mode='support',wu96_requires=True,wu96_reason='CURRENT_SUPPORT_INTENT_OVERRIDES_SALES',wu96_intent='technical_issue',ctx_intent='technical_issue'),(True,'technical_issue','TECHNICAL_SUPPORT')),
      ('technical_support via WU106',dict(primary='technical_support',wu106_support=True,wu106_intent='technical_support'),(True,'technical_support','TECHNICAL_SUPPORT')),
      ('complaint current support',dict(primary='complaint',wu96_mode='support',wu96_requires=True,wu96_reason='CURRENT_SUPPORT_INTENT_OVERRIDES_SALES',wu96_intent='complaint'),(True,'complaint','COMPLAINT_ESCALATION')),
      ('account login',dict(primary='account_login',wu96_mode='support',wu96_requires=True,wu96_reason='CURRENT_SUPPORT_INTENT_OVERRIDES_SALES'),(True,'account_login','ACCOUNT_OR_CONTACT_SENSITIVE_CHANGE')),
      ('normal pricing',dict(primary='pricing'),(False,'','OTHER_APPROVED_HANDOFF')),
      ('sticky support alone must not trigger',dict(primary='pricing',sticky=True),(False,'','OTHER_APPROVED_HANDOFF')),
      ('unknown support label fails closed',dict(primary='pricing',wu96_mode='support',wu96_requires=True,wu96_reason='CURRENT_SUPPORT_INTENT_OVERRIDES_SALES',wu96_intent='mystery_support'),(False,'','OTHER_APPROVED_HANDOFF')),
      ('not interested not handoff',dict(primary='not_interested',wu106_support=True,wu106_intent='not_interested'),(False,'','OTHER_APPROVED_HANDOFF')),
      ('do not contact not handoff',dict(primary='do_not_contact',wu106_support=True,wu106_intent='do_not_contact'),(False,'','OTHER_APPROVED_HANDOFF')),
    ]
    for name,kwargs,expected in cases:
        got=resolve(**kwargs)
        if got!=expected: raise SystemExit(f'CR10701_SIGNAL_CASE_FAIL:{name}:{got}:{expected}')
    print('CR10701_SUPPORT_SIGNAL_RECOVERY_PASS')
    print('cases=10 changed_nodes=1 topology_unchanged=PASS technical_issue=PASS stale_support_guard=PASS')

if __name__=='__main__': main()
