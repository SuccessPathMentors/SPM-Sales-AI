#!/usr/bin/env python3
import json
import os
import sys
import urllib.request

TARGET = os.getenv('N8N_TARGET_WORKFLOW_ID', '').strip()
BASE = os.getenv('N8N_API_BASE_URL', '').strip().rstrip('/')
KEY = os.getenv('N8N_API_KEY', '').strip()

PRODUCTION_ID = 'CMBMpxX5AqqK2UTn'
LOCKED_IDS = {
    'mMZVFxJIxE7a9SSW': 'WU-101 STAGING',
    '1kaRBBFVJYbPxvQG': 'WU-102 STAGING',
    '5COEoxXjk8AvuGBa': 'WU-103 STAGING',
}
EXPECTED_NAME = '[STAGING] SPM WU104 Short Query + Ambiguity UX Candidate'

if not TARGET or not BASE or not KEY:
    raise SystemExit('missing required n8n readback environment')
if TARGET == PRODUCTION_ID:
    raise SystemExit('production workflow ID denied')
if TARGET in LOCKED_IDS:
    raise SystemExit(f'locked {LOCKED_IDS[TARGET]} workflow ID denied for WU-104')

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
    'Persist WU104 Awaited Context Hint',
    'Persist WU104 Final Asked Field',
    'Apply WU104 Clarification Response Override',
    'Merge Durable Sales State + Decide Journey [WU90]',
    'Serialize WU90 Production Sales State',
    'Apply WU97 Fail-Closed Privacy Security Guard',
    'Serialize WU95 STAGING Sales State',
    'Capture WU89 Classifier Context',
    'Build Telemetry Envelope',
    'Redact WU97 Observability Telemetry',
    'Save AI Message to Chat History',
    'Redis Chat Memory',
]
missing = [x for x in required if x not in nodes]
if missing:
    raise SystemExit('required remote nodes missing: ' + ', '.join(missing))

errors = []
if wf.get('active') is True:
    errors.append('remote WU-104 workflow unexpectedly active')
if wf.get('name') != EXPECTED_NAME:
    errors.append(f'remote workflow name mismatch: {wf.get("name")!r}')
if len(wf.get('nodes', [])) != 125:
    errors.append(f'remote node count mismatch: {len(wf.get("nodes", []))}')

builder_js = nodes['Build WU104 Short Query Decision'].get('parameters', {}).get('jsCode', '')
persist_js = nodes['Persist WU104 Awaited Context Hint'].get('parameters', {}).get('jsCode', '')
asked_js = nodes['Persist WU104 Final Asked Field'].get('parameters', {}).get('jsCode', '')
override_js = nodes['Apply WU104 Clarification Response Override'].get('parameters', {}).get('jsCode', '')
for token in [
    'SPM_WU104_SHORT_QUERY_DECISION_V1',
    'SPM_WU104_CLARIFICATION_STATE_V1',
    'BOUND_DETERMINISTIC',
    'BARE_FRAGMENT_NO_CONTEXT',
    'UNSAFE_YES_NO',
    'UNKNOWN_AWAITED_ENTITY',
    'LOOP_CAP_REACHED',
    'ASK_ONE_CLARIFYING_QUESTION',
    'SAFE_FALLBACK_OR_HUMAN_HELP',
    'REGISTRATION_CONFIRMATION_GUARD',
    'irreversible_action_allowed:false',
    'raw_message_logged:false',
    'raw_session_logged:false',
    'secret_values_logged:false',
]:
    if token not in builder_js:
        errors.append(f'WU-104 decision token missing: {token}')
for token in [
    'SPM_WU104_AWAIT_CONTEXT_WRITE_V1',
    'state.journey.awaiting_entity=safe',
    'state.journey.awaiting_entity=registrationAwait',
    'state.journey.awaiting_entity=null',
    "source='WU90_REQUIRED_MISSING_FIELDS'",
    'raw_message_logged:false',
    'raw_session_logged:false',
    'secret_values_logged:false',
]:
    if token not in persist_js:
        errors.append(f'WU-104 early await-context token missing: {token}')
for token in [
    'SPM_WU104_FINAL_ASKED_FIELD_WRITE_V1',
    'intake_question_candidate',
    'purposeful_question',
    'questionPresent',
    "source='WU92_INTAKE_NEXT_FIELD'",
    "status='PERSISTED_FROM_FINAL_QUESTION'",
    'state.journey.awaiting_entity=safe',
    'state.journey.awaiting_entity=registrationAwait',
    'state.journey.awaiting_entity=null',
    'raw_message_logged:false',
    'raw_session_logged:false',
    'secret_values_logged:false',
]:
    if token not in asked_js:
        errors.append(f'WU-104 final asked-field token missing: {token}')
for token in ['sales_agent_output', 'answer_text:text', 'ASK_ONE_CLARIFYING_QUESTION', 'SAFE_FALLBACK_OR_HUMAN_HELP']:
    if token not in override_js:
        errors.append(f'WU-104 response override token missing: {token}')

for n in wf.get('nodes', []):
    if 'WU104' in n.get('name','') and n.get('type') in {
        '@n8n/n8n-nodes-langchain.lmChatOpenAi', '@n8n/n8n-nodes-langchain.agent'
    }:
        errors.append('WU-104 second LLM/classifier node detected')

connections = wf.get('connections', {})
def targets(name):
    return [[c.get('node') for c in group] for group in connections.get(name, {}).get('main', [])]

for upstream in [
    'Mark Direct Classification','Mark Clarification Required','Mark Classifier Fallback','Build Catalog Failure Classification'
]:
    if targets(upstream) != [['Build WU104 Short Query Decision']]:
        errors.append(f'classifier convergence mismatch for {upstream}')
if targets('Build WU104 Short Query Decision') != [['Capture WU89 Classifier Context']]:
    errors.append('WU-104 decision downstream mismatch')
if targets('Merge Durable Sales State + Decide Journey [WU90]') != [['Persist WU104 Awaited Context Hint']]:
    errors.append('WU-104 early awaited-context upstream mismatch')
if targets('Persist WU104 Awaited Context Hint') != [['Serialize WU90 Production Sales State']]:
    errors.append('WU-104 early awaited-context downstream mismatch')
if targets('Apply WU97 Fail-Closed Privacy Security Guard') != [['Persist WU104 Final Asked Field']]:
    errors.append('WU-104 final asked-field upstream mismatch')
if targets('Persist WU104 Final Asked Field') != [['Serialize WU95 STAGING Sales State']]:
    errors.append('WU-104 final asked-field downstream mismatch')
if targets('Build Telemetry Envelope') != [['Apply WU104 Clarification Response Override']]:
    errors.append('WU-104 response override upstream mismatch')
if targets('Apply WU104 Clarification Response Override') != [['Redact WU97 Observability Telemetry']]:
    errors.append('WU-104 response override downstream mismatch')

q = nodes['Upsert WU102 Unanswered [STAGING]']
qcols = q.get('parameters', {}).get('columns', {})
if q.get('parameters', {}).get('operation') != 'appendOrUpdate':
    errors.append('WU-102 queue operation changed')
if qcols.get('matchingColumns') != ['queue_event_id']:
    errors.append('WU-102 queue idempotency key changed')
if q.get('onError') != 'continueRegularOutput':
    errors.append('WU-102 queue fail-open changed')

memory_key = nodes['Redis Chat Memory'].get('parameters', {}).get('sessionKey')
if memory_key != "={{ 'spm:staging:chat:' + $json.sessionId }}":
    errors.append('Redis Chat Memory STAGING isolation mismatch')

mem_text = json.dumps(nodes['Save AI Message to Chat History'], ensure_ascii=False)
if 'Redact WU97 Observability Telemetry' not in mem_text or 'sales_agent_output.answer_text' not in mem_text:
    errors.append('AI memory/redaction path changed')

observed = {
    'workflow_id': wf.get('id'),
    'workflow_name': wf.get('name'),
    'active': wf.get('active'),
    'versionId': wf.get('versionId'),
    'node_count': len(wf.get('nodes', [])),
    'wu104_nodes': [n for n in nodes if 'WU104' in n],
    'wu102_queue_operation': q.get('parameters', {}).get('operation'),
    'wu102_queue_matching_columns': qcols.get('matchingColumns'),
    'wu102_queue_onError': q.get('onError'),
    'chat_memory_session_key': memory_key,
}
print(json.dumps(observed, indent=2, ensure_ascii=False))

if errors:
    print('WU104_REMOTE_READBACK_FAIL: ' + '; '.join(errors), file=sys.stderr)
    raise SystemExit(1)
print('WU104_REMOTE_READBACK_PASS')
