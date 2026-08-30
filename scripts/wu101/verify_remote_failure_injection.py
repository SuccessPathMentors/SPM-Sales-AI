#!/usr/bin/env python3
import json
import os
import sys
import urllib.request

TARGET = os.getenv('N8N_TARGET_WORKFLOW_ID', '').strip()
BASE = os.getenv('N8N_API_BASE_URL', '').strip().rstrip('/')
KEY = os.getenv('N8N_API_KEY', '').strip()
EXPECTED_TARGET = 'mMZVFxJIxE7a9SSW'
FAILURE_DOCUMENT_ID = 'WU101_FAILURE_INJECTION_NONEXISTENT_SPREADSHEET'
EXPECTED_MEMORY = "={{ 'spm:staging:chat:' + $json.sessionId }}"

if not TARGET or not BASE or not KEY:
    raise SystemExit('missing required n8n readback environment')
if TARGET != EXPECTED_TARGET:
    raise SystemExit(f'failure injection is restricted to WU-101 STAGING ID {EXPECTED_TARGET}')
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
    raise SystemExit('required WU-101 nodes not found')

doc = logger.get('parameters', {}).get('documentId', {})
observed = {
    'workflow_id': wf.get('id'),
    'workflow_name': wf.get('name'),
    'active': wf.get('active'),
    'analytics_document_id': doc.get('value') if isinstance(doc, dict) else doc,
    'analytics_on_error': logger.get('onError'),
    'chat_memory_session_key': memory.get('parameters', {}).get('sessionKey'),
}
print(json.dumps(observed, indent=2, ensure_ascii=False))

errors = []
if wf.get('active') is True:
    errors.append('remote workflow unexpectedly active')
if observed['analytics_document_id'] != FAILURE_DOCUMENT_ID:
    errors.append('failure-injection document ID not present remotely')
if logger.get('onError') != 'continueRegularOutput':
    errors.append('analytics sink is not fail-open')
if observed['chat_memory_session_key'] != EXPECTED_MEMORY:
    errors.append('STAGING Redis Chat Memory isolation mismatch')

if errors:
    print('WU101_FAILURE_INJECTION_REMOTE_FAIL: ' + '; '.join(errors), file=sys.stderr)
    raise SystemExit(1)
print('WU101_FAILURE_INJECTION_REMOTE_PASS')
