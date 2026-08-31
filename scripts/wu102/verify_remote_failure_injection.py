#!/usr/bin/env python3
import json
import os
import sys
import urllib.request

TARGET = os.getenv('N8N_TARGET_WORKFLOW_ID', '').strip()
BASE = os.getenv('N8N_API_BASE_URL', '').strip().rstrip('/')
KEY = os.getenv('N8N_API_KEY', '').strip()
EXPECTED_TARGET = '1kaRBBFVJYbPxvQG'
PRODUCTION_ID = 'CMBMpxX5AqqK2UTn'
WU101_STAGING_ID = 'mMZVFxJIxE7a9SSW'
FAILURE_DOCUMENT_ID = 'WU102_FAILURE_INJECTION_NONEXISTENT_SPREADSHEET'
EXPECTED_MEMORY = "={{ 'spm:staging:chat:' + $json.sessionId }}"

if not TARGET or not BASE or not KEY:
    raise SystemExit('missing required n8n readback environment')
if TARGET != EXPECTED_TARGET:
    raise SystemExit(f'failure injection is restricted to WU-102 STAGING ID {EXPECTED_TARGET}')
if TARGET in {PRODUCTION_ID, WU101_STAGING_ID}:
    raise SystemExit('protected workflow ID denied')

req = urllib.request.Request(
    f'{BASE}/workflows/{TARGET}',
    headers={'accept': 'application/json', 'X-N8N-API-KEY': KEY},
    method='GET',
)
with urllib.request.urlopen(req, timeout=45) as resp:
    wf = json.loads(resp.read().decode('utf-8'))

nodes = {n.get('name'): n for n in wf.get('nodes', [])}
logger = nodes.get('Upsert WU102 Unanswered [STAGING]')
memory = nodes.get('Redis Chat Memory')
canonical = nodes.get('Build Canonical Session Envelope')
if not logger or not memory or not canonical:
    raise SystemExit('required WU-102 nodes not found')

doc = logger.get('parameters', {}).get('documentId', {})
sheet = logger.get('parameters', {}).get('sheetName', {})
observed = {
    'workflow_id': wf.get('id'),
    'workflow_name': wf.get('name'),
    'active': wf.get('active'),
    'queue_document_id': doc.get('value') if isinstance(doc, dict) else doc,
    'queue_sheet_id': sheet.get('value') if isinstance(sheet, dict) else sheet,
    'queue_sheet_name': sheet.get('cachedResultName') if isinstance(sheet, dict) else None,
    'queue_on_error': logger.get('onError'),
    'queue_matching_columns': logger.get('parameters', {}).get('columns', {}).get('matchingColumns'),
    'chat_memory_session_key': memory.get('parameters', {}).get('sessionKey'),
}
print(json.dumps(observed, indent=2, ensure_ascii=False))

errors = []
if wf.get('active') is True:
    errors.append('remote workflow unexpectedly active')
if observed['queue_document_id'] != FAILURE_DOCUMENT_ID:
    errors.append('failure-injection document ID not present remotely')
if logger.get('onError') != 'continueRegularOutput':
    errors.append('queue sink is not fail-open')
if observed['queue_sheet_name'] != 'WU102_UNANSWERED_STAGING' or str(observed['queue_sheet_id']) != '2026102001':
    errors.append('WU-102 queue sheet contract changed')
if observed['queue_matching_columns'] != ['queue_event_id']:
    errors.append('WU-102 queue idempotency matching column changed')
if observed['chat_memory_session_key'] != EXPECTED_MEMORY:
    errors.append('STAGING Redis Chat Memory isolation mismatch')
if "workflow_release:'WU102_STAGING_UNANSWERED_V1'" not in canonical.get('parameters', {}).get('jsCode', ''):
    errors.append('WU-102 STAGING release marker missing')

if errors:
    print('WU102_FAILURE_INJECTION_REMOTE_FAIL: ' + '; '.join(errors), file=sys.stderr)
    raise SystemExit(1)
print('WU102_FAILURE_INJECTION_REMOTE_PASS')
