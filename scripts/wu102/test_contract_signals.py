#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WU101_DIR = HERE.parent / 'wu101'
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(WU101_DIR))

from build_candidate import build  # noqa: E402

BASE = Path('n8n/workflows/production/SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json')
wf = build(BASE)


def node(name):
    matches = [n for n in wf['nodes'] if n.get('name') == name]
    assert len(matches) == 1, (name, len(matches))
    return matches[0]


BUILDER_JS = node('Build WU102 Unanswered Queue Decision')['parameters']['jsCode']


def run_builder(payload):
    wrapper = f"""
const fs=require('fs');
const payload=JSON.parse(fs.readFileSync(0,'utf8'));
const $input={{first:()=>({{json:payload}})}};
const result=(()=>{{
{BUILDER_JS}
}})();
process.stdout.write(JSON.stringify(result[0].json));
"""
    proc = subprocess.run(
        ['node', '-e', wrapper],
        input=json.dumps(payload, ensure_ascii=False),
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise AssertionError(f'node builder execution failed: {proc.stderr}')
    return json.loads(proc.stdout)


def base_payload():
    return {
        'channel': 'website_chat',
        'message': {'raw': 'What subjects do you offer?'},
        'classification': {
            'spm_intent': 'subject_inquiry',
            'secondary_spm_intent': '',
            'confidence': 0.95,
            'threshold': 0.85,
            'ambiguous': False,
            'language': 'en',
        },
        'classifier_route': 'direct',
        'customer_clarification_required': False,
        'source_plan': {
            'static_claims_allowed': True,
            'live_verification_required': False,
        },
        'source_gate_result': {
            'evidence_count': 1,
            'retrieval_status': 'STATIC_EVIDENCE_FOUND',
            'live_verification_required': False,
        },
        'source_gate_decision': {
            'evidence_count': 1,
            'reason_code': 'APPROVED_STATIC_EVIDENCE_READY',
        },
        'sales_state': {
            'analytics': {'session_key': 'conv-unit-test-session-123456', 'turn_index': 3},
            'support': {'handoff_requested': False},
        },
        'entity_extraction': {'records': [], 'student_profiles': []},
        'entity_guard': {'pii_present': False},
    }


# Negative control: normal confident answer must not queue.
j = base_payload()
out = run_builder(j)
d = out['wu102_queue_decision']
assert d['queue_required'] is False, d
assert d['queue_write_allowed'] is False, d
assert d['trigger_reasons'] == [], d
assert out['wu102_queue_event'] is None

# No static evidence.
j = base_payload()
j['source_gate_result']['evidence_count'] = 0
j['source_gate_result']['retrieval_status'] = 'NO_MATCHING_ACTIVE_EVIDENCE'
j['source_gate_decision']['evidence_count'] = 0
j['source_gate_decision']['reason_code'] = 'NO_MATCHING_ACTIVE_EVIDENCE'
out = run_builder(j)
assert out['wu102_queue_decision']['trigger_reasons'] == ['NO_STATIC_EVIDENCE']
assert out['wu102_queue_event']['kb_match_status'] == 'NO_STATIC_EVIDENCE'

# Live-required no-evidence is not mislabeled as a KB gap.
j = base_payload()
j['source_plan']['static_claims_allowed'] = False
j['source_plan']['live_verification_required'] = True
j['source_gate_result']['evidence_count'] = 0
j['source_gate_result']['live_verification_required'] = True
j['source_gate_decision']['evidence_count'] = 0
j['source_gate_decision']['reason_code'] = 'SCHEDULING_LIVE'
out = run_builder(j)
assert 'NO_STATIC_EVIDENCE' not in out['wu102_queue_decision']['trigger_reasons']
assert out['wu102_queue_decision']['queue_required'] is False

# Low-confidence fallback; one event may carry multiple deterministic reasons.
j = base_payload()
j['classification']['confidence'] = 0.4
j['classifier_route'] = 'fallback'
out = run_builder(j)
reasons = out['wu102_queue_decision']['trigger_reasons']
assert 'LOW_CONFIDENCE_FALLBACK' in reasons
assert 'FALLBACK_USED' in reasons
assert 'AMBIGUOUS_OR_BELOW_THRESHOLD' in reasons
assert len(reasons) == len(set(reasons))

# Ambiguous/below-threshold clarification.
j = base_payload()
j['classification']['confidence'] = 0.75
j['classification']['ambiguous'] = True
j['classifier_route'] = 'clarify'
j['customer_clarification_required'] = True
out = run_builder(j)
assert out['wu102_queue_decision']['trigger_reasons'] == ['AMBIGUOUS_OR_BELOW_THRESHOLD']
assert out['wu102_queue_event']['clarification_used'] is True

# Human request does not imply execution success.
j = base_payload()
j['classification']['spm_intent'] = 'human_handoff'
out = run_builder(j)
assert out['wu102_queue_decision']['trigger_reasons'] == ['HUMAN_REQUESTED']
assert out['wu102_queue_event']['human_requested'] is True

# Out-of-scope is queued deterministically.
j = base_payload()
j['classification']['spm_intent'] = 'out_of_scope'
out = run_builder(j)
assert out['wu102_queue_decision']['trigger_reasons'] == ['OUT_OF_SCOPE']
assert out['wu102_queue_event']['out_of_scope'] is True

# Redact explicit PII/contact values; raw values must not survive.
j = base_payload()
j['classification']['spm_intent'] = 'human_handoff'
j['message']['raw'] = 'I am Ahmad Hassan. Email parent@example.com or call +1 416 555 0198. I need a person.'
j['entity_extraction'] = {
    'records': [
        {'entity': 'parent_name', 'raw': 'Ahmad Hassan', 'canonical': 'Ahmad Hassan', 'sensitivity': 'High'},
        {'entity': 'email', 'raw': 'parent@example.com', 'canonical': 'parent@example.com', 'sensitivity': 'High'},
        {'entity': 'phone', 'raw': '+1 416 555 0198', 'canonical': '+14165550198', 'sensitivity': 'High'},
    ],
    'student_profiles': [],
}
j['entity_guard'] = {'pii_present': True}
out = run_builder(j)
e = out['wu102_queue_event']
assert e['question_capture_status'] == 'STORED_REDACTED', e
q = e['redacted_question']
for raw in ['Ahmad Hassan', 'parent@example.com', '+1 416 555 0198']:
    assert raw.lower() not in q.lower(), (raw, q)
assert '[REDACTED_' in q
assert e['pii_redacted'] is True
assert e['raw_message_logged'] is False
assert e['raw_session_logged'] is False
assert e['secret_values_logged'] is False
assert e['dialect_hint'] == 'unknown'

# PII risk without a usable detected value must withhold text entirely.
j = base_payload()
j['classification']['spm_intent'] = 'human_handoff'
j['message']['raw'] = 'Sensitive customer detail that detector marked as PII.'
j['entity_extraction'] = {'records': [], 'student_profiles': []}
j['entity_guard'] = {'pii_present': True}
out = run_builder(j)
e = out['wu102_queue_event']
assert e['question_capture_status'] == 'WITHHELD_PII_RISK'
assert e['redacted_question'] is None

# Missing internal identity must never fall back to raw session/correlation values.
j = base_payload()
j['classification']['spm_intent'] = 'out_of_scope'
j['session_id'] = 'raw-session-must-not-be-used'
j['correlation_id'] = 'customer-controlled-correlation'
j['sales_state']['analytics']['session_key'] = None
out = run_builder(j)
d = out['wu102_queue_decision']
assert d['queue_required'] is True
assert d['identity_available'] is False
assert d['queue_write_allowed'] is False
assert d['status'] == 'SKIPPED_IDENTITY_UNAVAILABLE'
assert d['error_code'] == 'WU102_QUEUE_IDENTITY_UNAVAILABLE'
assert out['wu102_queue_event'] is None

# Same internal session + turn yields the same idempotency key.
j = base_payload()
j['classification']['spm_intent'] = 'human_handoff'
a = run_builder(j)['wu102_queue_event']['queue_event_id']
b = run_builder(j)['wu102_queue_event']['queue_event_id']
assert a == b, (a, b)
assert a.startswith('uq-unit-test-session-123456-3')

print('WU102_CONTRACT_SIGNALS_PASS')
print(json.dumps({'cases': 10, 'node_runtime': 'node', 'dialect_v1': 'unknown'}, indent=2))
