#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
decision = json.loads((ROOT / 'contracts' / 'WU104_SHORT_QUERY_DECISION_V1.schema.json').read_text(encoding='utf-8'))
state = json.loads((ROOT / 'contracts' / 'WU104_CLARIFICATION_STATE_V1.schema.json').read_text(encoding='utf-8'))

for schema, expected_id in [
    (decision, 'SPM_WU104_SHORT_QUERY_DECISION_V1'),
    (state, 'SPM_WU104_CLARIFICATION_STATE_V1'),
]:
    assert schema['$id'] == expected_id
    assert schema['type'] == 'object'
    assert schema['additionalProperties'] is False
    assert set(schema['required']) == set(schema['properties'])

for forbidden in [
    'raw_message','raw_question','message','session_id','correlation_id','phone','email',
    'parent_name','student_name','contact','token','api_key','password','secret','credential'
]:
    assert forbidden not in decision['properties'], forbidden
    assert forbidden not in state['properties'], forbidden

assert decision['properties']['schema']['const'] == 'SPM_WU104_SHORT_QUERY_DECISION_V1'
assert decision['properties']['short_query_type']['enum'] == [
    'NONE','AFFIRMATION','NEGATION','GRADE_ONLY','SUBJECT_ONLY','LOCATION_ONLY',
    'DAY_ONLY','TIME_ONLY','SEMANTIC_FRAGMENT','OTHER_SHORT'
]
assert decision['properties']['context_binding_status']['enum'] == [
    'NOT_NEEDED','BOUND_DETERMINISTIC','NEEDS_CLARIFICATION','UNSAFE_TO_BIND'
]
assert decision['properties']['safe_action']['enum'] == [
    'CONTINUE','ASK_ONE_CLARIFYING_QUESTION','SAFE_FALLBACK_OR_HUMAN_HELP'
]
assert decision['properties']['irreversible_action_allowed']['const'] is False
assert decision['properties']['raw_message_logged']['const'] is False
assert decision['properties']['raw_session_logged']['const'] is False
assert decision['properties']['secret_values_logged']['const'] is False
assert decision['properties']['clarification_attempt']['maximum'] == 2
assert decision['properties']['clarification_language']['enum'] == ['en','ar','fr']

assert state['properties']['schema']['const'] == 'SPM_WU104_CLARIFICATION_STATE_V1'
assert state['properties']['attempt']['minimum'] == 0
assert state['properties']['attempt']['maximum'] == 2
assert state['properties']['raw_message_logged']['const'] is False
assert state['properties']['raw_session_logged']['const'] is False
assert state['properties']['secret_values_logged']['const'] is False
assert state['properties']['language']['enum'] == ['en','ar','fr']

print('WU104_CONTRACT_TESTS_PASS')
print(json.dumps({
    'decision_fields': len(decision['properties']),
    'clarification_state_fields': len(state['properties']),
    'additionalProperties': False,
    'irreversible_action_allowed': False,
}, indent=2))
