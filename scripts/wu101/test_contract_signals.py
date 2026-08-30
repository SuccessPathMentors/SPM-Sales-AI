#!/usr/bin/env python3
import copy
import json
import subprocess
from pathlib import Path

from build_candidate_sheets_type_safe import build

BASE = Path('n8n/workflows/production/SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json')
wf = build(BASE)
builder = next(n for n in wf['nodes'] if n.get('name') == 'Build WU101 Conversation Analytics Event')
js_code = builder['parameters']['jsCode']

NODE_HARNESS = r'''
const input = JSON.parse(process.argv[1]);
const code = JSON.parse(process.argv[2]);
const $input = { first: () => ({ json: input }) };
const fn = new Function('$input', code);
const out = fn($input);
if (!Array.isArray(out) || !out[0] || !out[0].json || !out[0].json.wu101_analytics_event) {
  throw new Error('WU101 analytics event missing');
}
process.stdout.write(JSON.stringify(out[0].json.wu101_analytics_event));
'''

BASE_INPUT = {
    'channel': 'website_chat',
    'session_id': 'RAW-SESSION-MUST-NOT-LEAK',
    'correlation_id': 'USER-CONTROLLED-CORRELATION-MUST-NOT-LEAK',
    'message': {'raw': 'RAW-CUSTOMER-MESSAGE-MUST-NOT-LEAK'},
    'classification': {
        'spm_intent': 'subject_inquiry',
        'secondary_spm_intent': None,
        'confidence': 0.90,
        'language': 'en',
    },
    'classifier_route': 'direct',
    'customer_clarification_required': False,
    'journey_decision': {'stage': 'discovery'},
    'source_gate_result': {'gate': 'APPROVED_KB_OR_LOGIC'},
    'action_result': {'status': 'RC3_SCOPE_LOCK_NOOP'},
    'telemetry': {
        'degraded': False,
        'recovery_mode': 'NORMAL',
        'duration_ms': 1234,
        'error_codes': [],
    },
    'sales_state': {
        'analytics': {'session_key': 'conv-contract-session-001', 'turn_index': 7},
        'nurture': {'opt_out': False},
        'support': {'handoff_requested': False},
    },
    'lead_write_result': {},
    'wu95_lead_validation': {},
    'wu95_handoff_contract': {'requested': False},
}


def deep_merge(base, patch):
    out = copy.deepcopy(base)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def run_case(name, patch):
    payload = deep_merge(BASE_INPUT, patch)
    proc = subprocess.run(
        ['node', '-e', NODE_HARNESS, json.dumps(payload), json.dumps(js_code)],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise AssertionError(f'{name}: node harness failed: {proc.stderr}')
    event = json.loads(proc.stdout)

    # Common contract / privacy invariants.
    assert event['event_schema'] == 'SPM_WU101_CONVERSATION_ANALYTICS_V1', name
    assert event['workflow_release'] == 'WU101_STAGING_ANALYTICS_V1', name
    assert event['channel'] == 'website_chat', name
    assert event['analytics_session_key'] == 'conv-contract-session-001', name
    assert event['turn_index'] == 7, name
    assert event['language'] == 'en', name
    assert event['pii_redacted'] is True, name
    assert event['raw_message_logged'] is False, name
    assert event['raw_session_logged'] is False, name
    assert event['correlation_id_logged'] is False, name
    assert event['secret_values_logged'] is False, name
    assert event['event_id'] == 'evt-contract-session-001-7', name

    serialized = json.dumps(event, ensure_ascii=False)
    for forbidden_value in [
        'RAW-SESSION-MUST-NOT-LEAK',
        'USER-CONTROLLED-CORRELATION-MUST-NOT-LEAK',
        'RAW-CUSTOMER-MESSAGE-MUST-NOT-LEAK',
    ]:
        assert forbidden_value not in serialized, (name, forbidden_value)
    return event


results = {}

results['direct'] = run_case('direct', {})
assert results['direct']['classifier_route'] == 'direct'
assert results['direct']['clarification_used'] is False
assert results['direct']['fallback_used'] is False
assert results['direct']['human_requested'] is False
assert results['direct']['lead_outcome'] == 'none'

results['clarify'] = run_case('clarify', {'classifier_route': 'clarify'})
assert results['clarify']['clarification_used'] is True
assert results['clarify']['fallback_used'] is False

results['fallback'] = run_case('fallback', {'classifier_route': 'fallback'})
assert results['fallback']['fallback_used'] is True
assert results['fallback']['clarification_used'] is False

results['human_request'] = run_case('human_request', {
    'classification': {'spm_intent': 'human_handoff'},
    'wu95_handoff_contract': {'requested': True},
})
assert results['human_request']['human_requested'] is True

results['lead_created'] = run_case('lead_created', {
    'lead_write_result': {'success': True, 'operation': 'created', 'lead_id': 'LEAD-123'},
})
assert results['lead_created']['lead_outcome'] == 'created'
assert results['lead_created']['lead_id_present'] is True

results['lead_updated'] = run_case('lead_updated', {
    'lead_write_result': {'success': True, 'operation': 'updated', 'lead_id': 'LEAD-456'},
})
assert results['lead_updated']['lead_outcome'] == 'updated'
assert results['lead_updated']['lead_id_present'] is True

results['lead_failed'] = run_case('lead_failed', {
    'lead_write_result': {'success': False, 'adapter_status': 'FAILED', 'reason_code': 'WRITE_FAILED'},
})
assert results['lead_failed']['lead_outcome'] == 'failed'
assert results['lead_failed']['lead_id_present'] is False

results['opt_out'] = run_case('opt_out', {
    'sales_state': {'nurture': {'opt_out': True}},
})
assert results['opt_out']['opt_out'] is True

results['degraded'] = run_case('degraded', {
    'telemetry': {
        'degraded': True,
        'recovery_mode': 'DEGRADED',
        'duration_ms': 9999,
        'error_codes': ['CONTRACT_TEST_DEGRADED'],
    },
})
assert results['degraded']['degraded'] is True
assert results['degraded']['recovery_mode'] == 'DEGRADED'
assert results['degraded']['duration_ms'] == 9999
assert results['degraded']['error_codes'] == ['CONTRACT_TEST_DEGRADED']

print('WU101_CONTRACT_SIGNAL_PACK_PASS')
print(json.dumps({
    'cases': list(results),
    'case_count': len(results),
    'privacy_negative_values_verified': 3,
    'event_schema': 'SPM_WU101_CONVERSATION_ANALYTICS_V1',
}, indent=2))
