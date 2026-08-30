#!/usr/bin/env python3
import json
import os
import sys
import urllib.request

TARGET = os.getenv('N8N_TARGET_WORKFLOW_ID', '').strip()
BASE = os.getenv('N8N_API_BASE_URL', '').strip().rstrip('/')
KEY = os.getenv('N8N_API_KEY', '').strip()

ALLOWED_TURN = {
    "={{ $json.wu101_analytics_event.turn_index }}",
    "={{ Number($json.wu101_analytics_event.turn_index ?? 1) }}",
}
EXPECTED_CONF = "={{ $json.wu101_analytics_event.confidence == null ? null : Number($json.wu101_analytics_event.confidence) }}"
EXPECTED_DURATION = "={{ Number($json.wu101_analytics_event.duration_ms ?? 0) }}"
EXPECTED_ERROR_CODES = "={{ JSON.stringify($json.wu101_analytics_event.error_codes || []) }}"
EXPECTED_MEMORY = "={{ 'spm:staging:chat:' + $json.sessionId }}"
NUMERIC_FIELDS = ('turn_index', 'confidence', 'duration_ms')
BOOLEAN_FIELDS = (
    'clarification_used',
    'fallback_used',
    'human_requested',
    'lead_id_present',
    'opt_out',
    'degraded',
    'pii_redacted',
    'raw_message_logged',
    'raw_session_logged',
    'correlation_id_logged',
    'secret_values_logged',
)
ALL_FIELDS = (
    'event_schema','event_id','event_timestamp','workflow_release','channel','analytics_session_key','turn_index',
    'primary_intent','secondary_intent','confidence','language','journey_stage','source_gate','classifier_route',
    'clarification_used','fallback_used','human_requested','lead_outcome','lead_id_present','opt_out','action_status',
    'degraded','recovery_mode','duration_ms','error_codes','pii_redacted','raw_message_logged','raw_session_logged',
    'correlation_id_logged','secret_values_logged',
)


def field_expr(field):
    return '={{ $json.wu101_analytics_event.' + field + ' }}'


def boolean_text_expr(field):
    return '={{ $json.wu101_analytics_event.' + field + " === true ? 'true' : 'false' }}"


if not TARGET or not BASE or not KEY:
    raise SystemExit('missing required n8n readback environment')
if TARGET == 'CMBMpxX5AqqK2UTn':
    raise SystemExit('production workflow ID denied')

req = urllib.request.Request(
    f'{BASE}/workflows/{TARGET}',
    headers={'accept': 'application/json', 'X-N8N-API-KEY': KEY},
    method='GET',
)
with urllib.request.urlopen(req, timeout=45) as resp:
    wf = json.loads(resp.read().decode('utf-8'))

nodes = {n.get('name'): n for n in wf.get('nodes', [])}
logger = nodes.get('Upsert WU101 Analytics [STAGING]')
memory = nodes.get('Redis Chat Memory')
if not logger or not memory:
    raise SystemExit('required WU-101 nodes not found in remote workflow')

cols = logger.get('parameters', {}).get('columns', {})
vals = cols.get('value', {})
schema = {f.get('id'): f for f in cols.get('schema', []) if isinstance(f, dict)}
turn_schema_type = (schema.get('turn_index') or {}).get('type')
boolean_observed = {
    field: {
        'mapping': vals.get(field),
        'schema_type': (schema.get(field) or {}).get('type'),
    }
    for field in BOOLEAN_FIELDS
}
observed = {
    'workflow_id': wf.get('id'),
    'workflow_name': wf.get('name'),
    'active': wf.get('active'),
    'versionId': wf.get('versionId'),
    'turn_index': vals.get('turn_index'),
    'turn_index_schema_type': turn_schema_type,
    'confidence': vals.get('confidence'),
    'duration_ms': vals.get('duration_ms'),
    'attemptToConvertTypes': cols.get('attemptToConvertTypes'),
    'boolean_sink_fields': boolean_observed,
    'expression_fields': {field: vals.get(field) for field in ALL_FIELDS},
    'chat_memory_session_key': memory.get('parameters', {}).get('sessionKey'),
}
print(json.dumps(observed, indent=2, ensure_ascii=False))

errors = []
if wf.get('active') is True:
    errors.append('remote workflow unexpectedly active')
if vals.get('turn_index') not in ALLOWED_TURN:
    errors.append('turn_index remote mapping does not reference the approved analytics field')
if turn_schema_type != 'number':
    errors.append('turn_index remote schema is not number')
if vals.get('confidence') != EXPECTED_CONF:
    errors.append('confidence remote value mismatch')
if vals.get('duration_ms') != EXPECTED_DURATION:
    errors.append('duration_ms remote value mismatch')
if vals.get('error_codes') != EXPECTED_ERROR_CODES:
    errors.append('error_codes remote value mismatch')
if cols.get('attemptToConvertTypes') is not True:
    errors.append('attemptToConvertTypes remote value mismatch')
for field in BOOLEAN_FIELDS:
    expected = boolean_text_expr(field)
    if vals.get(field) != expected:
        errors.append(f'{field} remote boolean sink mapping mismatch')
    if (schema.get(field) or {}).get('type') != 'string':
        errors.append(f'{field} remote sink schema is not string')
for field in ALL_FIELDS:
    mapping = vals.get(field)
    if not isinstance(mapping, str) or not mapping.startswith('={{ ') or not mapping.endswith(' }}'):
        errors.append(f'{field} remote n8n expression delimiter malformed')
    if isinstance(mapping, str) and mapping.startswith('={ '):
        errors.append(f'{field} remote mapping contains collapsed f-string braces')
    if field not in NUMERIC_FIELDS and field not in BOOLEAN_FIELDS and field != 'error_codes':
        if mapping != field_expr(field):
            errors.append(f'{field} remote ordinary mapping mismatch')
if memory.get('parameters', {}).get('sessionKey') != EXPECTED_MEMORY:
    errors.append('Redis Chat Memory sessionKey remote value mismatch')

if errors:
    print('WU101_REMOTE_READBACK_FAIL: ' + '; '.join(errors), file=sys.stderr)
    raise SystemExit(1)
print('WU101_REMOTE_READBACK_PASS')
