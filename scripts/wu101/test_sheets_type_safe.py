#!/usr/bin/env python3
import json
from pathlib import Path

from build_candidate import FIELDS
from build_candidate_chat_memory_isolated import build as build_before
from build_candidate_sheets_type_safe import BOOLEAN_FIELDS, NUMERIC_FIELDS, boolean_text_expr, build, field_expr

BASE = Path('n8n/workflows/production/SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json')


def node(wf, name):
    matches = [n for n in wf['nodes'] if n.get('name') == name]
    assert len(matches) == 1, (name, len(matches))
    return matches[0]


before = build_before(BASE)
after = build(BASE)
after2 = build(BASE)

logger = node(after, 'Upsert WU101 Analytics [STAGING]')
columns = logger['parameters']['columns']
values = columns['value']
assert columns['attemptToConvertTypes'] is True
assert values['turn_index'] == "={{ Number($json.wu101_analytics_event.turn_index ?? 1) }}"
assert values['confidence'] == "={{ $json.wu101_analytics_event.confidence == null ? null : Number($json.wu101_analytics_event.confidence) }}"
assert values['duration_ms'] == "={{ Number($json.wu101_analytics_event.duration_ms ?? 0) }}"
assert values['error_codes'] == "={{ JSON.stringify($json.wu101_analytics_event.error_codes || []) }}"

schema = {f['id']: f for f in columns['schema']}
for field in NUMERIC_FIELDS:
    assert schema[field]['type'] == 'number'

for field in BOOLEAN_FIELDS:
    assert schema[field]['type'] == 'string', (field, schema[field])
    assert values[field] == boolean_text_expr(field), (field, values[field])

for field in FIELDS:
    mapping = values[field]
    assert isinstance(mapping, str), (field, mapping)
    assert mapping.startswith('={{ '), (field, mapping)
    assert mapping.endswith(' }}'), (field, mapping)
    assert not mapping.startswith('={ '), (field, mapping)
    if field not in NUMERIC_FIELDS and field not in BOOLEAN_FIELDS and field != 'error_codes':
        assert mapping == field_expr(field), (field, mapping)

# Prove this repair changes only the analytics Sheets column configuration.
before_copy = json.loads(json.dumps(before))
after_copy = json.loads(json.dumps(after))
before_logger = node(before_copy, 'Upsert WU101 Analytics [STAGING]')
after_logger = node(after_copy, 'Upsert WU101 Analytics [STAGING]')
after_logger['parameters']['columns'] = before_logger['parameters']['columns']
assert before_copy == after_copy

assert json.dumps(after, ensure_ascii=False, sort_keys=True) == json.dumps(after2, ensure_ascii=False, sort_keys=True)
assert after.get('active') is False
assert 'id' not in after

print('WU101_SHEETS_TYPE_SAFE_PASS')
print(json.dumps({
    'attemptToConvertTypes': columns['attemptToConvertTypes'],
    'numeric_fields': list(NUMERIC_FIELDS),
    'boolean_sink_fields': list(BOOLEAN_FIELDS),
    'boolean_sink_encoding': 'canonical_string_true_false',
    'expression_fields_verified': len(FIELDS),
    'expression_prefix': '={{',
    'active': after.get('active'),
}, indent=2))
