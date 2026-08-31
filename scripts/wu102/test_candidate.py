#!/usr/bin/env python3
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('wu102_build_candidate', HERE / 'build_candidate.py')
assert spec and spec.loader
wu102 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wu102)

BOOLEAN_FIELDS = wu102.BOOLEAN_FIELDS
FIELDS = wu102.FIELDS
NUMERIC_FIELDS = wu102.NUMERIC_FIELDS
QUEUE_SHEET_ID = wu102.QUEUE_SHEET_ID
QUEUE_SHEET_NAME = wu102.QUEUE_SHEET_NAME
build = wu102.build

BASE = Path('n8n/workflows/production/SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json')
assert BASE.is_file(), BASE
wf = build(BASE)


def node(name):
    matches = [n for n in wf['nodes'] if n.get('name') == name]
    assert len(matches) == 1, (name, len(matches))
    return matches[0]


serialized = json.dumps(wf, ensure_ascii=False, indent=2) + '\n'
serialized2 = json.dumps(build(BASE), ensure_ascii=False, indent=2) + '\n'
digest = hashlib.sha256(serialized.encode('utf-8')).hexdigest()
assert digest == hashlib.sha256(serialized2.encode('utf-8')).hexdigest()

assert wf['name'] == 'SPM WU102 Unanswered Question Queue Candidate'
assert wf.get('active') is False
assert 'id' not in wf
assert len(wf['nodes']) == 121, len(wf['nodes'])
assert len({n['name'] for n in wf['nodes']}) == 121
ids = [n.get('id') for n in wf['nodes'] if n.get('id')]
assert len(ids) == len(set(ids))

names = {n['name'] for n in wf['nodes']}
assert set(wf['connections']).issubset(names)


def walk(value):
    if isinstance(value, dict):
        target = value.get('node')
        if isinstance(target, str):
            assert target in names, target
        for child in value.values():
            walk(child)
    elif isinstance(value, list):
        for child in value:
            walk(child)


walk(wf['connections'])

canonical_js = node('Build Canonical Session Envelope')['parameters']['jsCode']
assert "workflow_release:'WU102_STAGING_UNANSWERED_V1'" in canonical_js
assert "workflow_mode:'STAGING_INACTIVE'" in canonical_js
assert 'spm:staging:sales:' in canonical_js
assert 'spm:prod:sales:' not in canonical_js
assert 'test_mode:true' in canonical_js
assert 'production_cutover_authorized:false' in canonical_js

builder_js = node('Build WU102 Unanswered Queue Decision')['parameters']['jsCode']
for required in [
    "NO_STATIC_EVIDENCE",
    "LOW_CONFIDENCE_FALLBACK",
    "AMBIGUOUS_OR_BELOW_THRESHOLD",
    "FALLBACK_USED",
    "HUMAN_REQUESTED",
    "OUT_OF_SCOPE",
    "dialect_hint:'unknown'",
    "WU102_QUEUE_IDENTITY_UNAVAILABLE",
    "WITHHELD_PII_RISK",
    "STORED_REDACTED",
    "queue_session_key:queueKey",
]:
    assert required in builder_js, required
for forbidden in [
    'queue_session_key:j.session_id',
    'queue_session_key:j.correlation_id',
    'queue_session_key:j.message',
    'dialect_hint:j.',
]:
    assert forbidden not in builder_js, forbidden

# Raw message is permitted only as transient redaction input, never in the sink contract.
assert "const raw=String(j.message?.raw||'')" in builder_js
assert 'raw_question' not in FIELDS
assert 'raw_message' not in FIELDS
assert 'session_id' not in FIELDS
assert 'correlation_id' not in FIELDS
assert 'phone' not in FIELDS
assert 'email' not in FIELDS
assert 'parent_name' not in FIELDS
assert 'student_name' not in FIELDS

logger = node('Upsert WU102 Unanswered [STAGING]')
assert logger['parameters']['operation'] == 'appendOrUpdate'
assert logger['parameters']['sheetName']['value'] == QUEUE_SHEET_ID
assert logger['parameters']['sheetName']['cachedResultName'] == QUEUE_SHEET_NAME
assert logger['parameters']['columns']['matchingColumns'] == ['queue_event_id']
assert logger['parameters']['columns']['attemptToConvertTypes'] is True
assert logger.get('onError') == 'continueRegularOutput'
assert not logger.get('retryOnFail', False)
assert list(logger['parameters']['columns']['value']) == FIELDS

columns = logger['parameters']['columns']
for field, expression in columns['value'].items():
    assert isinstance(expression, str)
    assert expression.startswith('={{'), (field, expression)
    assert not expression.startswith('={ '), (field, expression)

schema = {f['id']: f for f in columns['schema']}
for field in NUMERIC_FIELDS:
    assert schema[field]['type'] == 'number', (field, schema[field])
for field in BOOLEAN_FIELDS:
    assert schema[field]['type'] == 'string', (field, schema[field])
    assert "'true' : 'false'" in columns['value'][field], field
assert 'JSON.stringify' in columns['value']['trigger_reasons']
assert "Number($json.wu102_queue_event.turn_index" in columns['value']['turn_index']
assert 'Number($json.wu102_queue_event.confidence)' in columns['value']['confidence']
assert '/^[=+\\-@]/' in columns['value']['redacted_question']

# Approved insertion path only.
assert wf['connections']['Restore Customer Context After WU101 Analytics']['main'][0][0]['node'] == 'Build WU102 Unanswered Queue Decision'
assert wf['connections']['Build WU102 Unanswered Queue Decision']['main'][0][0]['node'] == 'Is WU102 Queue Write Required?'
gate_main = wf['connections']['Is WU102 Queue Write Required?']['main']
assert gate_main[0][0]['node'] == 'Upsert WU102 Unanswered [STAGING]'
assert gate_main[1][0]['node'] == 'Restore Customer Context After WU102 Queue'
assert wf['connections']['Upsert WU102 Unanswered [STAGING]']['main'][0][0]['node'] == 'Restore Customer Context After WU102 Queue'
assert wf['connections']['Restore Customer Context After WU102 Queue']['main'][0][0]['node'] == 'Save AI Message to Chat History'

restore_js = node('Restore Customer Context After WU102 Queue')['parameters']['jsCode']
assert 'FAILED_FAIL_OPEN' in restore_js
assert 'SKIPPED_IDENTITY_UNAVAILABLE' in restore_js
assert 'NOT_REQUIRED' in restore_js
assert 'fail_open:true' in restore_js

assert not [n['name'] for n in wf['nodes'] if 'executeWorkflow' in n.get('type', '')]
assert not [n['name'] for n in wf['nodes'] if n.get('disabled') is True]

print('WU102_STATIC_TESTS_PASS')
print(json.dumps({
    'nodes': len(wf['nodes']),
    'connections': len(wf['connections']),
    'candidate_sha256': digest,
    'queue_sheet_id': QUEUE_SHEET_ID,
}, indent=2))
