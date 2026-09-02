#!/usr/bin/env python3
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / 'n8n' / 'workflows' / 'production' / 'SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json'
WRAPPER = ROOT / 'scripts' / 'wu104' / 'build_context_await_candidate.py'
BASE_BUILDER = ROOT / 'scripts' / 'wu104' / 'build_candidate.py'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


wrapper = load(WRAPPER, 'wu104_context_wrapper_test')
base_mod = load(BASE_BUILDER, 'wu104_base_builder_test')
wf = wrapper.build(BASELINE)
base = base_mod.build(BASELINE)


def node(name):
    matches = [n for n in wf['nodes'] if n.get('name') == name]
    assert len(matches) == 1, (name, len(matches))
    return matches[0]


persist = node('Persist WU104 Awaited Context Hint')
js = persist['parameters']['jsCode']
assert persist['type'] == 'n8n-nodes-base.code'
for token in [
    'SPM_WU104_AWAIT_CONTEXT_WRITE_V1',
    "state.journey.awaiting_entity=safe",
    "state.journey.awaiting_entity=registrationAwait",
    "state.journey.awaiting_entity=null",
    "source='WU90_REQUIRED_MISSING_FIELDS'",
    "source='CONVERSION_AWAITING_FIELD'",
    "raw_message_logged:false",
    "raw_session_logged:false",
    "secret_values_logged:false",
]:
    assert token in js, token

asked = node('Persist WU104 Final Asked Field')
asked_js = asked['parameters']['jsCode']
assert asked['type'] == 'n8n-nodes-base.code'
for token in [
    'SPM_WU104_FINAL_ASKED_FIELD_WRITE_V1',
    'intake_question_candidate',
    'journey_decision?.required_missing_fields',
    'purposeful_question',
    'answer_text',
    'questionPresent',
    'detectAskedField',
    'FINAL_RESPONSE_QUESTION_PATTERN',
    'WU92_INTAKE_NEXT_FIELD',
    'WU90_REQUIRED_MISSING_FIELDS',
    'WU104_CLARIFICATION_GUARD',
    "status='PERSISTED_FROM_FINAL_QUESTION'",
    "state.journey.awaiting_entity=safe",
    "state.journey.awaiting_entity=registrationAwait",
    "state.journey.awaiting_entity=null",
    "raw_message_logged:false",
    "raw_session_logged:false",
    "secret_values_logged:false",
]:
    assert token in asked_js, token

for slot in ['grade', 'subject', 'location', 'day', 'time']:
    assert slot in js and slot in asked_js, slot
for forbidden in ['email:', 'phone:', 'parent_name:', 'student_name:', 'session_id:', 'correlation_id:', 'api_key:', 'password:']:
    assert forbidden not in js, forbidden
    assert forbidden not in asked_js, forbidden

assert len(wf['nodes']) == len(base['nodes']) + 2
assert len(wf['nodes']) == 125, len(wf['nodes'])
assert wf.get('active') is False

upstream = 'Merge Durable Sales State + Decide Journey [WU90]'
downstream = 'Serialize WU90 Production Sales State'
assert wf['connections'][upstream]['main'] == [[{
    'node': 'Persist WU104 Awaited Context Hint', 'type': 'main', 'index': 0
}]]
assert wf['connections']['Persist WU104 Awaited Context Hint']['main'] == [[{
    'node': downstream, 'type': 'main', 'index': 0
}]]

final_upstream = 'Apply WU97 Fail-Closed Privacy Security Guard'
final_downstream = 'Serialize WU95 STAGING Sales State'
assert wf['connections'][final_upstream]['main'] == [[{
    'node': 'Persist WU104 Final Asked Field', 'type': 'main', 'index': 0
}]]
assert wf['connections']['Persist WU104 Final Asked Field']['main'] == [[{
    'node': final_downstream, 'type': 'main', 'index': 0
}]]

normalized = json.loads(json.dumps(wf))
normalized['nodes'] = [n for n in normalized['nodes'] if n.get('name') not in {
    'Persist WU104 Awaited Context Hint', 'Persist WU104 Final Asked Field'
}]
normalized['connections'][upstream] = {'main': [[{'node': downstream, 'type': 'main', 'index': 0}]]}
normalized['connections'].pop('Persist WU104 Awaited Context Hint', None)
normalized['connections'][final_upstream] = {'main': [[{'node': final_downstream, 'type': 'main', 'index': 0}]]}
normalized['connections'].pop('Persist WU104 Final Asked Field', None)
assert normalized == base

decision_js = node('Build WU104 Short Query Decision')['parameters']['jsCode']
assert 'state.journey?.awaiting_entity' in decision_js
assert "awaitedType==='subject'" in decision_js
assert 'BOUND_DETERMINISTIC' in decision_js

print('WU104_CONTEXT_AWAIT_INTEGRATION_TESTS_PASS')
print(json.dumps({
    'base_nodes': len(base['nodes']),
    'candidate_nodes': len(wf['nodes']),
    'added_nodes': 2,
    'wu90_early_hint_before_redis': True,
    'final_question_pattern_fallback': True,
    'wu104_ambiguity_guard': True,
    'registration_awaiting_field_preserved': True,
    'privacy_safe': True,
    'normalized_wu104_parity': True,
}, indent=2))
