#!/usr/bin/env python3
import json
import os
import sys
import urllib.request

TARGET = os.getenv('N8N_TARGET_WORKFLOW_ID', '').strip()
BASE = os.getenv('N8N_API_BASE_URL', '').strip().rstrip('/')
KEY = os.getenv('N8N_API_KEY', '').strip()

PRODUCTION_ID = 'CMBMpxX5AqqK2UTn'
LOCKED_IDS = {'mMZVFxJIxE7a9SSW', '1kaRBBFVJYbPxvQG', '5COEoxXjk8AvuGBa'}
EXPECTED_NAME = '[STAGING] SPM WU104 Short Query + Ambiguity UX Candidate'

if not TARGET or not BASE or not KEY:
    raise SystemExit('missing required n8n readback environment')
if TARGET == PRODUCTION_ID or TARGET in LOCKED_IDS:
    raise SystemExit('protected workflow ID denied')

req = urllib.request.Request(
    f'{BASE}/workflows/{TARGET}',
    headers={'accept': 'application/json', 'X-N8N-API-KEY': KEY},
    method='GET',
)
with urllib.request.urlopen(req, timeout=45) as resp:
    wf = json.loads(resp.read().decode('utf-8'))

nodes = {n.get('name'): n for n in wf.get('nodes', [])}
required = [
    'Build WU101 Conversation Analytics Event',
    'Upsert WU101 Analytics [STAGING]',
    'Build WU102 Unanswered Queue Decision',
    'Upsert WU102 Unanswered [STAGING]',
    'Build WU104 Short Query Decision',
    'Apply WU104 Short Trial Inquiry Guard',
    'Persist WU104 Awaited Context Hint',
    'Persist WU104 Final Asked Field',
    'Apply WU104 Clarification Response Override',
    'Capture WU89 Classifier Context',
    'Merge Durable Sales State + Decide Journey [WU90]',
    'Apply WU97 Fail-Closed Privacy Security Guard',
    'Serialize WU95 STAGING Sales State',
    'Redis Chat Memory',
]
errors = []
missing = [x for x in required if x not in nodes]
if missing:
    errors.append('required remote nodes missing: ' + ', '.join(missing))

if wf.get('active') is True:
    errors.append('remote WU-104 workflow unexpectedly active')
if wf.get('name') != EXPECTED_NAME:
    errors.append(f'remote workflow name mismatch: {wf.get("name")!r}')
if len(wf.get('nodes', [])) != 126:
    errors.append(f'remote node count mismatch: {len(wf.get("nodes", []))}')

if not missing:
    guard_js = nodes['Apply WU104 Short Trial Inquiry Guard'].get('parameters', {}).get('jsCode', '')
    for token in [
        'SPM_WU104_SHORT_SEMANTIC_GUARD_V1',
        'REMAP_FREE_TRIAL_QUESTION_TO_TRIAL_DETAILS',
        'TARGET_INTENT_MISSING_FAIL_CLOSED',
        'WU104_SHORT_TRIAL_INFO_QUESTION',
        "spm_intent:'trial_details'",
        "intent==='free_trial'",
        'raw_message_logged:false',
        'raw_session_logged:false',
        'secret_values_logged:false',
    ]:
        if token not in guard_js:
            errors.append(f'CR-104-05 guard token missing: {token}')

    decision_js = nodes['Build WU104 Short Query Decision'].get('parameters', {}).get('jsCode', '')
    for token in ['SPM_WU104_SHORT_QUERY_DECISION_V1', 'LOOP_CAP_REACHED', 'UNSAFE_YES_NO', 'BOUND_DETERMINISTIC']:
        if token not in decision_js:
            errors.append(f'prior WU-104 decision token missing: {token}')

    persist_js = nodes['Persist WU104 Awaited Context Hint'].get('parameters', {}).get('jsCode', '')
    if 'SPM_WU104_KNOWN_SLOT_RECONCILE_V1' not in persist_js:
        errors.append('CR-104-04 known-slot reconciliation marker missing')
    if 'SPM_WU104_AWAIT_CONTEXT_WRITE_V1' not in persist_js:
        errors.append('prior awaited-context marker missing')

    asked_js = nodes['Persist WU104 Final Asked Field'].get('parameters', {}).get('jsCode', '')
    if 'SPM_WU104_FINAL_ASKED_FIELD_WRITE_V1' not in asked_js:
        errors.append('prior final asked-field marker missing')

connections = wf.get('connections', {})
def targets(name):
    return [[c.get('node') for c in group] for group in connections.get(name, {}).get('main', [])]

for upstream in ['Mark Direct Classification', 'Mark Clarification Required', 'Mark Classifier Fallback', 'Build Catalog Failure Classification']:
    if targets(upstream) != [['Build WU104 Short Query Decision']]:
        errors.append(f'classifier convergence mismatch for {upstream}')
if targets('Build WU104 Short Query Decision') != [['Apply WU104 Short Trial Inquiry Guard']]:
    errors.append('CR-104-05 decision-to-guard connection mismatch')
if targets('Apply WU104 Short Trial Inquiry Guard') != [['Capture WU89 Classifier Context']]:
    errors.append('CR-104-05 guard downstream mismatch')
if targets('Merge Durable Sales State + Decide Journey [WU90]') != [['Persist WU104 Awaited Context Hint']]:
    errors.append('prior WU-104 awaited-context connection mismatch')
if targets('Apply WU97 Fail-Closed Privacy Security Guard') != [['Persist WU104 Final Asked Field']]:
    errors.append('prior WU-104 final asked-field connection mismatch')

for n in wf.get('nodes', []):
    if 'WU104' in str(n.get('name', '')) and n.get('type') in {
        '@n8n/n8n-nodes-langchain.lmChatOpenAi', '@n8n/n8n-nodes-langchain.agent'
    }:
        errors.append('WU-104 second LLM/classifier node detected')

if 'Upsert WU102 Unanswered [STAGING]' in nodes:
    q = nodes['Upsert WU102 Unanswered [STAGING]']
    qcols = q.get('parameters', {}).get('columns', {})
    if q.get('parameters', {}).get('operation') != 'appendOrUpdate':
        errors.append('WU-102 queue operation changed')
    if qcols.get('matchingColumns') != ['queue_event_id']:
        errors.append('WU-102 queue idempotency key changed')
    if q.get('onError') != 'continueRegularOutput':
        errors.append('WU-102 queue fail-open changed')

if 'Redis Chat Memory' in nodes:
    memory_key = nodes['Redis Chat Memory'].get('parameters', {}).get('sessionKey')
    if memory_key != "={{ 'spm:staging:chat:' + $json.sessionId }}":
        errors.append('Redis Chat Memory STAGING isolation mismatch')

observed = {
    'workflow_id': wf.get('id'),
    'workflow_name': wf.get('name'),
    'active': wf.get('active'),
    'versionId': wf.get('versionId'),
    'node_count': len(wf.get('nodes', [])),
    'cr10405_guard_present': 'Apply WU104 Short Trial Inquiry Guard' in nodes,
    'production_targeted': TARGET == PRODUCTION_ID,
}
print(json.dumps(observed, indent=2, ensure_ascii=False))
if errors:
    print('WU104_CR10405_REMOTE_READBACK_FAIL: ' + '; '.join(errors), file=sys.stderr)
    raise SystemExit(1)
print('WU104_CR10405_REMOTE_READBACK_PASS')
