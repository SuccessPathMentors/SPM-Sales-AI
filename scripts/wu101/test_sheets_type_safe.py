#!/usr/bin/env python3
import json
from pathlib import Path

from build_candidate_chat_memory_isolated import build as build_before
from build_candidate_sheets_type_safe import build

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
assert columns['attemptToConvertTypes'] is True
assert columns['value']['turn_index'] == "={{ Number($json.wu101_analytics_event.turn_index ?? 1) }}"
assert columns['value']['confidence'] == "={{ $json.wu101_analytics_event.confidence == null ? null : Number($json.wu101_analytics_event.confidence) }}"
assert columns['value']['duration_ms'] == "={{ Number($json.wu101_analytics_event.duration_ms ?? 0) }}"

schema = {f['id']: f for f in columns['schema']}
for field in ('turn_index', 'confidence', 'duration_ms'):
    assert schema[field]['type'] == 'number'

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
    'numeric_fields': ['turn_index', 'confidence', 'duration_ms'],
    'active': after.get('active'),
}, indent=2))
