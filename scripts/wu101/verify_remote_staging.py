#!/usr/bin/env python3
import json
import os
import sys
import urllib.request

TARGET = os.getenv('N8N_TARGET_WORKFLOW_ID', '').strip()
BASE = os.getenv('N8N_API_BASE_URL', '').strip().rstrip('/')
KEY = os.getenv('N8N_API_KEY', '').strip()

EXPECTED_TURN = "={{ Number($json.wu101_analytics_event.turn_index ?? 1) }}"
EXPECTED_CONF = "={{ $json.wu101_analytics_event.confidence == null ? null : Number($json.wu101_analytics_event.confidence) }}"
EXPECTED_DURATION = "={{ Number($json.wu101_analytics_event.duration_ms ?? 0) }}"
EXPECTED_MEMORY = "={{ 'spm:staging:chat:' + $json.sessionId }}"

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
observed = {
    'workflow_id': wf.get('id'),
    'workflow_name': wf.get('name'),
    'active': wf.get('active'),
    'versionId': wf.get('versionId'),
    'turn_index': vals.get('turn_index'),
    'confidence': vals.get('confidence'),
    'duration_ms': vals.get('duration_ms'),
    'attemptToConvertTypes': cols.get('attemptToConvertTypes'),
    'chat_memory_session_key': memory.get('parameters', {}).get('sessionKey'),
}
print(json.dumps(observed, indent=2, ensure_ascii=False))

errors = []
if wf.get('active') is True:
    errors.append('remote workflow unexpectedly active')
if vals.get('turn_index') != EXPECTED_TURN:
    errors.append('turn_index remote value mismatch')
if vals.get('confidence') != EXPECTED_CONF:
    errors.append('confidence remote value mismatch')
if vals.get('duration_ms') != EXPECTED_DURATION:
    errors.append('duration_ms remote value mismatch')
if cols.get('attemptToConvertTypes') is not True:
    errors.append('attemptToConvertTypes remote value mismatch')
if memory.get('parameters', {}).get('sessionKey') != EXPECTED_MEMORY:
    errors.append('Redis Chat Memory sessionKey remote value mismatch')

if errors:
    print('WU101_REMOTE_READBACK_FAIL: ' + '; '.join(errors), file=sys.stderr)
    raise SystemExit(1)
print('WU101_REMOTE_READBACK_PASS')
