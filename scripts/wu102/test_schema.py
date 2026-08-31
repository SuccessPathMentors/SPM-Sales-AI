#!/usr/bin/env python3
import json
from pathlib import Path

SCHEMA = Path('contracts/WU102_UNANSWERED_QUESTION_EVENT_V1.schema.json')
s = json.loads(SCHEMA.read_text(encoding='utf-8'))

assert s['$id'] == 'SPM_WU102_UNANSWERED_QUESTION_EVENT_V1'
assert s['type'] == 'object'
assert s['additionalProperties'] is False
required = s['required']
props = s['properties']
assert set(required) == set(props), (set(required) ^ set(props))

for forbidden in [
    'session_id', 'correlation_id', 'raw_question', 'raw_message', 'message',
    'phone', 'email', 'parent_name', 'student_name', 'contact', 'token',
    'api_key', 'password', 'secret', 'credential',
]:
    assert forbidden not in props, forbidden

assert props['event_schema']['const'] == 'SPM_WU102_UNANSWERED_QUESTION_V1'
assert props['queue_session_key']['pattern'].startswith('^conv-')
assert props['queue_event_id']['pattern'].startswith('^uq-')
assert props['dialect_hint']['const'] == 'unknown'
assert props['pii_redacted']['const'] is True
assert props['raw_message_logged']['const'] is False
assert props['raw_session_logged']['const'] is False
assert props['secret_values_logged']['const'] is False
assert props['resolution_status']['const'] == 'OPEN'
assert props['approved_answer_status']['const'] == 'NOT_REVIEWED'
assert props['added_to_kb_status']['const'] == 'NOT_ADDED'

triggers = props['trigger_reasons']['items']['enum']
assert triggers == [
    'NO_STATIC_EVIDENCE',
    'LOW_CONFIDENCE_FALLBACK',
    'AMBIGUOUS_OR_BELOW_THRESHOLD',
    'FALLBACK_USED',
    'HUMAN_REQUESTED',
    'OUT_OF_SCOPE',
]
assert props['trigger_reasons']['uniqueItems'] is True
assert props['trigger_reasons']['minItems'] == 1

print('WU102_SCHEMA_TESTS_PASS')
print(json.dumps({'fields': len(props), 'triggers': len(triggers), 'additionalProperties': False}, indent=2))
