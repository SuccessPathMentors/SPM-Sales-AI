#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
change = json.loads((ROOT / 'contracts' / 'WU103_KNOWLEDGE_CHANGE_V1.schema.json').read_text(encoding='utf-8'))
shadow = json.loads((ROOT / 'contracts' / 'WU103_KB_SHADOW_RECORD_V1.schema.json').read_text(encoding='utf-8'))
adapters = json.loads((ROOT / 'contracts' / 'WU103_FAMILY_ADAPTERS_V1.json').read_text(encoding='utf-8'))

assert change['$id'] == 'SPM_WU103_KNOWLEDGE_CHANGE_V1'
assert change['type'] == 'object'
assert change['additionalProperties'] is False
assert set(change['required']) == set(change['properties'])
assert shadow['$id'] == 'SPM_WU103_KB_SHADOW_RECORD_V1'
assert shadow['additionalProperties'] is False
assert set(shadow['required']) == set(shadow['properties'])

for forbidden in [
    'session_id','correlation_id','raw_message','raw_question','phone','email',
    'parent_name','student_name','contact','api_key','token','password','secret','credential'
]:
    assert forbidden not in change['properties'], forbidden
    assert forbidden not in shadow['properties'], forbidden

assert change['properties']['raw_customer_message_logged']['const'] is False
assert change['properties']['raw_session_logged']['const'] is False
assert change['properties']['secret_values_logged']['const'] is False
assert change['properties']['publish_environment']['const'] == 'STAGING'
assert change['properties']['candidate_key']['pattern'] == '^[a-f0-9]{64}$'

expected_families = [
    'FAQ','SUBJECTS','SUBJECT_PATHWAYS','SERVICES','LOCATIONS','FALLBACKS','PACKAGES','POLICIES'
]
assert change['properties']['target_family']['enum'] == expected_families
assert shadow['properties']['target_family']['enum'] == expected_families
assert list(adapters['families'].keys()) == expected_families

expected_ids = {
    'FAQ':'record_id','SUBJECTS':'record_id','SUBJECT_PATHWAYS':'pathway_id',
    'SERVICES':'service_id','LOCATIONS':'record_id','FALLBACKS':'record_id',
    'PACKAGES':'record_id','POLICIES':'record_id'
}
for family, id_field in expected_ids.items():
    a = adapters['families'][family]
    assert a['id_field'] == id_field
    assert id_field in a['fields']
    assert 'status' in a['fields']

assert adapters['families']['PACKAGES']['business_truth_required'] is True
assert adapters['families']['POLICIES']['business_truth_required'] is True
for family in expected_families[:-2]:
    assert adapters['families'][family]['business_truth_required'] is False

print('WU103_CONTRACT_TESTS_PASS')
print(json.dumps({
    'change_fields': len(change['properties']),
    'shadow_fields': len(shadow['properties']),
    'families': len(expected_families),
    'production_publish_environment_allowed': False
}, indent=2))
