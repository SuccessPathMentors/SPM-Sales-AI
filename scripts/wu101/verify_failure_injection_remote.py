#!/usr/bin/env python3
import json
import os
import sys
import urllib.request

from build_failure_injection_candidate import FAIL_DOCUMENT_ID, FAIL_WORKFLOW_NAME, LOGGER_NAME

TARGET = os.getenv('N8N_TARGET_WORKFLOW_ID', '').strip()
BASE = os.getenv('N8N_API_BASE_URL', '').strip().rstrip('/')
KEY = os.getenv('N8N_API_KEY', '').strip()

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
logger = nodes.get(LOGGER_NAME)
restore = nodes.get('Restore Customer Context After WU101 Analytics')
if not logger or not restore:
    raise SystemExit('required WU-101 failure-injection nodes not found')

doc = logger.get('parameters', {}).get('documentId', {})
conn = wf.get('connections', {}).get(LOGGER_NAME, {}).get('main', [])
next_node = None
if conn and conn[0]:
    next_node = conn[0][0].get('node')

observed = {
    'workflow_id': wf.get('id'),
    'workflow_name': wf.get('name'),
    'active': wf.get('active'),
    'failure_document_id': doc.get('value'),
    'failure_document_mode': doc.get('mode'),
    'logger_on_error': logger.get('onError'),
    'logger_next_node': next_node,
    'restore_fail_open_declared': 'fail_open:true' in restore.get('parameters', {}).get('jsCode', ''),
}
print(json.dumps(observed, indent=2, ensure_ascii=False))

errors = []
if wf.get('name') != FAIL_WORKFLOW_NAME:
    errors.append('unexpected failure-injection workflow name')
if wf.get('active') is True:
    errors.append('failure-injection workflow unexpectedly active')
if doc.get('value') != FAIL_DOCUMENT_ID or doc.get('mode') != 'id':
    errors.append('analytics sink is not pointed at the deliberate invalid document target')
if logger.get('onError') != 'continueRegularOutput':
    errors.append('analytics sink is not configured to continue regular output on error')
if next_node != 'Restore Customer Context After WU101 Analytics':
    errors.append('analytics sink does not route into the fail-open restore node')
if 'fail_open:true' not in restore.get('parameters', {}).get('jsCode', ''):
    errors.append('restore node does not declare fail_open:true')

if errors:
    print('WU101_FAILURE_REMOTE_READBACK_FAIL: ' + '; '.join(errors), file=sys.stderr)
    raise SystemExit(1)
print('WU101_FAILURE_REMOTE_READBACK_PASS')
