#!/usr/bin/env python3
import json
import os
import sys
import urllib.request

TARGET = os.getenv('N8N_TARGET_WORKFLOW_ID', '').strip()
BASE = os.getenv('N8N_API_BASE_URL', '').strip().rstrip('/')
KEY = os.getenv('N8N_API_KEY', '').strip()

PRODUCTION_ID = 'CMBMpxX5AqqK2UTn'
LOCKED_WU101_STAGING_ID = 'mMZVFxJIxE7a9SSW'
QUEUE_SHEET_ID = 2026102001
QUEUE_SHEET_NAME = 'WU102_UNANSWERED_STAGING'
EXPECTED_MEMORY = "={{ 'spm:staging:chat:' + $json.sessionId }}"

FIELDS = (
    'event_schema', 'queue_event_id', 'event_timestamp', 'workflow_release', 'channel',
    'queue_session_key', 'turn_index', 'redacted_question', 'question_capture_status',
    'language', 'dialect_hint', 'predicted_intent', 'secondary_intent', 'confidence',
    'kb_match_status', 'fallback_used', 'clarification_used', 'human_requested',
    'out_of_scope', 'trigger_reasons', 'resolution_status', 'approved_answer_status',
    'added_to_kb_status', 'pii_redacted', 'raw_message_logged', 'raw_session_logged',
    'secret_values_logged',
)
NUMERIC_FIELDS = ('turn_index', 'confidence')
BOOLEAN_FIELDS = (
    'fallback_used', 'clarification_used', 'human_requested', 'out_of_scope',
    'pii_redacted', 'raw_message_logged', 'raw_session_logged', 'secret_values_logged',
)
TRIGGERS = (
    'NO_STATIC_EVIDENCE',
    'LOW_CONFIDENCE_FALLBACK',
    'AMBIGUOUS_OR_BELOW_THRESHOLD',
    'FALLBACK_USED',
    'HUMAN_REQUESTED',
    'OUT_OF_SCOPE',
)


def ordinary_expr(field):
    return '={{ $json.wu102_queue_event.' + field + ' }}'


def boolean_text_expr(field):
    return '={{ $json.wu102_queue_event.' + field + " === true ? 'true' : 'false' }}"


if not TARGET or not BASE or not KEY:
    raise SystemExit('missing required n8n readback environment')
if TARGET == PRODUCTION_ID:
    raise SystemExit('production workflow ID denied')
if TARGET == LOCKED_WU101_STAGING_ID:
    raise SystemExit('locked WU-101 STAGING workflow ID denied for WU-102')

req = urllib.request.Request(
    f'{BASE}/workflows/{TARGET}',
    headers={'accept': 'application/json', 'X-N8N-API-KEY': KEY},
    method='GET',
)
with urllib.request.urlopen(req, timeout=45) as resp:
    wf = json.loads(resp.read().decode('utf-8'))

nodes = {n.get('name'): n for n in wf.get('nodes', [])}
required_nodes = [
    'Build WU101 Conversation Analytics Event',
    'Upsert WU101 Analytics [STAGING]',
    'Restore Customer Context After WU101 Analytics',
    'Build WU102 Unanswered Queue Decision',
    'Is WU102 Queue Write Required?',
    'Upsert WU102 Unanswered [STAGING]',
    'Restore Customer Context After WU102 Queue',
    'Redis Chat Memory',
]
missing = [name for name in required_nodes if name not in nodes]
if missing:
    raise SystemExit('required remote nodes missing: ' + ', '.join(missing))

logger = nodes['Upsert WU102 Unanswered [STAGING]']
builder = nodes['Build WU102 Unanswered Queue Decision']
gate = nodes['Is WU102 Queue Write Required?']
restore = nodes['Restore Customer Context After WU102 Queue']
memory = nodes['Redis Chat Memory']

cols = logger.get('parameters', {}).get('columns', {})
vals = cols.get('value', {})
schema = {f.get('id'): f for f in cols.get('schema', []) if isinstance(f, dict)}
builder_js = builder.get('parameters', {}).get('jsCode', '')
restore_js = restore.get('parameters', {}).get('jsCode', '')

sheet = logger.get('parameters', {}).get('sheetName', {})
observed = {
    'workflow_id': wf.get('id'),
    'workflow_name': wf.get('name'),
    'active': wf.get('active'),
    'versionId': wf.get('versionId'),
    'node_count': len(wf.get('nodes', [])),
    'queue_sheet_id': sheet.get('value'),
    'queue_sheet_name': sheet.get('cachedResultName'),
    'matching_columns': cols.get('matchingColumns'),
    'attemptToConvertTypes': cols.get('attemptToConvertTypes'),
    'onError': logger.get('onError'),
    'chat_memory_session_key': memory.get('parameters', {}).get('sessionKey'),
    'trigger_reasons_present': [t for t in TRIGGERS if t in builder_js],
    'dialect_unknown_only': "dialect_hint:'unknown'" in builder_js,
    'identity_fail_open_present': 'WU102_QUEUE_IDENTITY_UNAVAILABLE' in builder_js,
    'sink_expression_fields': {field: vals.get(field) for field in FIELDS},
}
print(json.dumps(observed, indent=2, ensure_ascii=False))

errors = []
if wf.get('active') is True:
    errors.append('remote workflow unexpectedly active')
if wf.get('name') != '[STAGING] SPM WU102 Unanswered Question Queue Candidate':
    errors.append('remote workflow name mismatch')
if len(wf.get('nodes', [])) != 121:
    errors.append('remote WU-102 node count mismatch')
if sheet.get('value') != QUEUE_SHEET_ID:
    errors.append('remote WU-102 queue sheet ID mismatch')
if sheet.get('cachedResultName') != QUEUE_SHEET_NAME:
    errors.append('remote WU-102 queue sheet name mismatch')
if logger.get('parameters', {}).get('operation') != 'appendOrUpdate':
    errors.append('remote WU-102 queue operation mismatch')
if cols.get('matchingColumns') != ['queue_event_id']:
    errors.append('remote queue idempotency key mismatch')
if cols.get('attemptToConvertTypes') is not True:
    errors.append('remote attemptToConvertTypes mismatch')
if logger.get('onError') != 'continueRegularOutput':
    errors.append('remote queue sink is not fail-open')
if logger.get('retryOnFail') is True:
    errors.append('remote queue sink must not retry business-path writes')

for field in FIELDS:
    mapping = vals.get(field)
    if not isinstance(mapping, str) or not mapping.startswith('={{') or not mapping.endswith('}}'):
        errors.append(f'{field} remote n8n expression delimiter malformed')
    if isinstance(mapping, str) and mapping.startswith('={ '):
        errors.append(f'{field} remote mapping contains collapsed braces')

for field in BOOLEAN_FIELDS:
    if vals.get(field) != boolean_text_expr(field):
        errors.append(f'{field} remote boolean mapping mismatch')
    if (schema.get(field) or {}).get('type') != 'string':
        errors.append(f'{field} remote boolean sink schema mismatch')

if (schema.get('turn_index') or {}).get('type') != 'number':
    errors.append('turn_index remote schema mismatch')
if (schema.get('confidence') or {}).get('type') != 'number':
    errors.append('confidence remote schema mismatch')
if vals.get('turn_index') != '={{ Number($json.wu102_queue_event.turn_index ?? 1) }}':
    errors.append('turn_index remote mapping mismatch')
if vals.get('confidence') != '={{ $json.wu102_queue_event.confidence == null ? null : Number($json.wu102_queue_event.confidence) }}':
    errors.append('confidence remote mapping mismatch')
if vals.get('trigger_reasons') != '={{ JSON.stringify($json.wu102_queue_event.trigger_reasons || []) }}':
    errors.append('trigger_reasons remote mapping mismatch')
if '/^[=+\\-@]/' not in str(vals.get('redacted_question')):
    errors.append('redacted_question spreadsheet injection guard missing')

for field in FIELDS:
    if field in NUMERIC_FIELDS or field in BOOLEAN_FIELDS or field in {'trigger_reasons', 'redacted_question'}:
        continue
    if vals.get(field) != ordinary_expr(field):
        errors.append(f'{field} remote ordinary mapping mismatch')

for trigger in TRIGGERS:
    if trigger not in builder_js:
        errors.append(f'missing frozen trigger {trigger}')
if "dialect_hint:'unknown'" not in builder_js:
    errors.append('dialect_hint is not frozen to unknown')
if 'WU102_QUEUE_IDENTITY_UNAVAILABLE' not in builder_js or 'SKIPPED_IDENTITY_UNAVAILABLE' not in builder_js:
    errors.append('identity-unavailable fail-open behavior missing')
for unsafe in ['queue_session_key:j.session_id', 'queue_session_key:j.correlation_id', 'queue_session_key:j.message']:
    if unsafe in builder_js:
        errors.append(f'unsafe queue identity fallback present: {unsafe}')
if 'FAILED_FAIL_OPEN' not in restore_js or 'fail_open:true' not in restore_js:
    errors.append('queue restore fail-open contract missing')

# Exact approved path.
connections = wf.get('connections', {})
def targets(name):
    out = []
    for group in connections.get(name, {}).get('main', []):
        out.append([c.get('node') for c in group])
    return out
if targets('Restore Customer Context After WU101 Analytics') != [['Build WU102 Unanswered Queue Decision']]:
    errors.append('WU-102 insertion upstream mismatch')
if targets('Build WU102 Unanswered Queue Decision') != [['Is WU102 Queue Write Required?']]:
    errors.append('WU-102 builder/gate connection mismatch')
if targets('Is WU102 Queue Write Required?') != [['Upsert WU102 Unanswered [STAGING]'], ['Restore Customer Context After WU102 Queue']]:
    errors.append('WU-102 gate branches mismatch')
if targets('Upsert WU102 Unanswered [STAGING]') != [['Restore Customer Context After WU102 Queue']]:
    errors.append('WU-102 queue sink restore connection mismatch')
if targets('Restore Customer Context After WU102 Queue') != [['Save AI Message to Chat History']]:
    errors.append('WU-102 restore customer path mismatch')

if memory.get('parameters', {}).get('sessionKey') != EXPECTED_MEMORY:
    errors.append('Redis Chat Memory STAGING isolation mismatch')

if errors:
    print('WU102_REMOTE_READBACK_FAIL: ' + '; '.join(errors), file=sys.stderr)
    raise SystemExit(1)
print('WU102_REMOTE_READBACK_PASS')
