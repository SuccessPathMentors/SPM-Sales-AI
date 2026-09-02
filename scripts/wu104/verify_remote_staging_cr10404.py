#!/usr/bin/env python3
import json
import os
import sys
import urllib.request

TARGET = os.getenv('N8N_TARGET_WORKFLOW_ID', '').strip()
BASE = os.getenv('N8N_API_BASE_URL', '').strip().rstrip('/')
KEY = os.getenv('N8N_API_KEY', '').strip()
PRODUCTION_ID = 'CMBMpxX5AqqK2UTn'

if not TARGET or not BASE or not KEY:
    raise SystemExit('missing required n8n readback environment')
if TARGET == PRODUCTION_ID:
    raise SystemExit('production workflow ID denied')

req = urllib.request.Request(
    f'{BASE}/workflows/{TARGET}',
    headers={'accept': 'application/json', 'X-N8N-API-KEY': KEY},
    method='GET',
)
with urllib.request.urlopen(req, timeout=45) as resp:
    wf = json.loads(resp.read().decode('utf-8'))

if wf.get('active') is True:
    raise SystemExit('WU-104 STAGING unexpectedly active')
if len(wf.get('nodes', [])) != 125:
    raise SystemExit(f'unexpected remote node count: {len(wf.get("nodes", []))}')

nodes = {n.get('name'): n for n in wf.get('nodes', [])}
persist = nodes.get('Persist WU104 Awaited Context Hint')
if not persist:
    raise SystemExit('Persist WU104 Awaited Context Hint missing remotely')
js = persist.get('parameters', {}).get('jsCode', '')
required = [
    'SPM_WU104_KNOWN_SLOT_RECONCILE_V1',
    'VALIDATED_CURRENT_TURN_ENTITY_RECORDS',
    'eligible_single_student',
    'subject_reconciled',
    'grade_reconciled',
    'skipped_multi_student',
    "latestValid(['subject','subjects'])",
    "latestValid(['grade','grades'])",
]
missing = [token for token in required if token not in js]
if missing:
    raise SystemExit('CR-104-04 remote markers missing: ' + ', '.join(missing))

print(json.dumps({
    'workflow_id': wf.get('id'),
    'active': wf.get('active'),
    'node_count': len(wf.get('nodes', [])),
    'cr10404_known_slot_markers': True,
    'production_targeted': False,
}, indent=2))
print('WU104_CR10404_REMOTE_READBACK_PASS')
