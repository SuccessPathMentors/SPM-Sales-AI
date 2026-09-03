#!/usr/bin/env python3
import json
import os
import sys
import urllib.request

TARGET = os.getenv('N8N_TARGET_WORKFLOW_ID', '').strip()
BASE = os.getenv('N8N_API_BASE_URL', '').strip().rstrip('/')
KEY = os.getenv('N8N_API_KEY', '').strip()
EXPECTED_NAME = '[STAGING] SPM_WU107_HUMAN_HANDOFF_EXECUTION_V1'
EXPECTED_NODES = 151
PROTECTED = {
    'CMBMpxX5AqqK2UTn', 'mMZVFxJIxE7a9SSW', '1kaRBBFVJYbPxvQG',
    '5COEoxXjk8AvuGBa', 'Bt3PvOIbFzU0O9gk', 'KXfalaYSCLdgmf4X',
    'vvHvidUHVxM5wTVT',
}

GATEWAY = 'Deterministic Action Gateway [RC3 SCOPE LOCK]'
TELEMETRY = 'Build Telemetry Envelope'
BUILD = 'Build WU107 Handoff Execution Request [STAGING]'
IF_EXEC = 'Is WU107 Handoff Execution Required?'
LOAD = 'Load WU107 Handoff Record [STAGING]'
DECIDE = 'Build WU107 Queue Decision'
IF_WRITE = 'Is WU107 Queue Write Required?'
SAVE = 'Save WU107 Handoff Record [STAGING]'
SUCCESS = 'Apply WU107 Verified Queue Result'
EXISTING = 'Apply WU107 Existing Handoff Result'
LOAD_FAIL = 'Build WU107 Handoff Load Failure Context'
SAVE_FAIL = 'Build WU107 Handoff Save Failure Context'
CANON_REDIS = 'Load Sales State [STAGING NAMESPACE]'
NEW = [BUILD, IF_EXEC, LOAD, DECIDE, IF_WRITE, SAVE, SUCCESS, EXISTING, LOAD_FAIL, SAVE_FAIL]

if not TARGET or not BASE or not KEY:
    raise SystemExit('missing n8n readback environment')
if TARGET in PROTECTED:
    raise SystemExit('unexpected/protected target')

req = urllib.request.Request(
    f'{BASE}/workflows/{TARGET}',
    headers={'accept': 'application/json', 'X-N8N-API-KEY': KEY},
)
with urllib.request.urlopen(req, timeout=45) as r:
    wf = json.loads(r.read().decode())

nodes = {n.get('name'): n for n in wf.get('nodes', [])}
conns = wf.get('connections', {})
errors = []


def targets(name, output=0):
    m = conns.get(name, {}).get('main')
    if not isinstance(m, list) or len(m) <= output or not isinstance(m[output], list):
        return []
    return [x.get('node') for x in m[output]]


def must(src, dst, out=0):
    got = targets(src, out)
    if got != [dst]:
        errors.append(f'{src}[{out}] -> {got!r}, expected {[dst]!r}')


if str(wf.get('id')) != TARGET:
    errors.append('workflow id mismatch')
if wf.get('name') != EXPECTED_NAME:
    errors.append(f'workflow name mismatch: {wf.get("name")!r}')
if wf.get('active') is True:
    errors.append('workflow unexpectedly active/published')
if len(wf.get('nodes', [])) != EXPECTED_NODES:
    errors.append(f'node count {len(wf.get("nodes", []))} != {EXPECTED_NODES}')

for name in NEW + [GATEWAY, TELEMETRY, CANON_REDIS]:
    if name not in nodes:
        errors.append('missing node: ' + name)

must(GATEWAY, BUILD)
must(BUILD, IF_EXEC)
must(IF_EXEC, LOAD, 0)
must(IF_EXEC, TELEMETRY, 1)
must(LOAD, DECIDE, 0)
must(LOAD, LOAD_FAIL, 1)
must(DECIDE, IF_WRITE)
must(IF_WRITE, SAVE, 0)
must(IF_WRITE, EXISTING, 1)
must(SAVE, SUCCESS, 0)
must(SAVE, SAVE_FAIL, 1)
for name in [SUCCESS, EXISTING, LOAD_FAIL, SAVE_FAIL]:
    must(name, TELEMETRY)

canon_creds = nodes.get(CANON_REDIS, {}).get('credentials', {}).get('redis')
for name in [LOAD, SAVE]:
    node = nodes.get(name, {})
    if node.get('type') != 'n8n-nodes-base.redis':
        errors.append(name + ' is not Redis')
    if node.get('credentials', {}).get('redis') != canon_creds:
        errors.append(name + ' Redis credential drift')
    if node.get('retryOnFail') is not True or int(node.get('maxTries', 0)) != 3:
        errors.append(name + ' bounded retry drift')
    if node.get('onError') != 'continueErrorOutput':
        errors.append(name + ' error-path drift')

for value, label in [
    (str(nodes.get(LOAD, {}).get('parameters', {}).get('key', '')), 'load'),
    (str(nodes.get(SAVE, {}).get('parameters', {}).get('key', '')), 'save'),
]:
    if 'wu107_queue_key' not in value:
        errors.append(f'{label} queue key expression drift')

build_code = str(nodes.get(BUILD, {}).get('parameters', {}).get('jsCode', ''))
decide_code = str(nodes.get(DECIDE, {}).get('parameters', {}).get('jsCode', ''))
success_code = str(nodes.get(SUCCESS, {}).get('parameters', {}).get('jsCode', ''))
existing_code = str(nodes.get(EXISTING, {}).get('parameters', {}).get('jsCode', ''))
load_fail_code = str(nodes.get(LOAD_FAIL, {}).get('parameters', {}).get('jsCode', ''))
save_fail_code = str(nodes.get(SAVE_FAIL, {}).get('parameters', {}).get('jsCode', ''))

# CR-107-01 support signal recovery must remain intact.
for marker in [
    'spm:staging:handoff:', 'SPM_WU107_HANDOFF_REQUEST_V1',
    'PSEUDONYMOUS_SESSION_KEY_UNAVAILABLE', 'production_mutation_allowed:false',
    'wu96_communication_decision', 'support_requires_handoff',
    'CURRENT_SUPPORT_INTENT_OVERRIDES_SALES', 'wu106_orchestration',
    'support_override_active', 'technical_issue', "reason='TECHNICAL_SUPPORT'",
    'Sticky historical support state is evidence for context only',
    'current_turn_wu96_support:currentTurnWU96',
    'current_turn_wu106_support:currentTurnWU106',
]:
    if marker not in build_code:
        errors.append('build/CR-107-01 marker missing: ' + marker)

for marker in [
    'SPM_WU107_HANDOFF_RECORD_V1', "handoff_state:'QUEUED'",
    'downstream_receipt_present:true', 'downstream_acceptance_present:false',
    'idempotencyKey',
]:
    if marker not in decide_code:
        errors.append('queue decision marker missing: ' + marker)

for marker in [
    "handoff_state:'QUEUED'", 'queue_receipt_verified:true',
    'human_acceptance_verified:false', 'WU107_VERIFIED_QUEUE_WRITE',
    'A specific team member has not yet been confirmed',
]:
    if marker not in success_code:
        errors.append('verified queue truth marker missing: ' + marker)

# CR-107-02: existing-state truth must be derived from evidence, not the persisted label.
for marker in [
    "const persistedState=String(r.handoff_state||'FAILED');",
    'const queueVerified=r.downstream_receipt_present===true;',
    'const acceptanceVerified=Boolean(',
    "persistedState==='ACCEPTED'",
    'r.downstream_acceptance_present===true',
    "effectiveState='QUEUED'",
    'handoff_state:effectiveState',
    'persisted_handoff_state:persistedState',
    'truth_reconciled:truthReconciled',
    'human_acceptance_verified:Boolean(acceptanceVerified)',
    'fail_closed:failClosed',
    'WU107_EXISTING_TRUTH_RECONCILED',
]:
    if marker not in existing_code:
        errors.append('existing/CR-107-02 marker missing: ' + marker)
for forbidden_old in [
    "handoff_state:accepted?'ACCEPTED':state",
    "success:['QUEUED','ACCEPTED'].includes(state)",
    "fail_closed:!['QUEUED','ACCEPTED'].includes(state)",
]:
    if forbidden_old in existing_code:
        errors.append('pre-CR-107-02 truth logic still present: ' + forbidden_old)

for code, label in [(load_fail_code, 'load failure'), (save_fail_code, 'save failure')]:
    if "handoff_state:'REQUESTED'" not in code or 'queue_receipt_verified:false' not in code or 'human_acceptance_verified:false' not in code:
        errors.append(label + ' does not fail closed to REQUESTED')

for name in NEW:
    node = nodes.get(name, {})
    if node.get('type') in {'n8n-nodes-base.googleSheets', 'n8n-nodes-base.httpRequest', 'n8n-nodes-base.whatsApp'}:
        errors.append('out-of-scope adapter type in ' + name)
new_text = json.dumps([nodes.get(n, {}) for n in NEW], ensure_ascii=False)
for forbidden in ['CMBMpxX5AqqK2UTn', 'spm:production:', 'raw_conversation', 'raw_session_id']:
    if forbidden in new_text:
        errors.append('forbidden WU-107 surface: ' + forbidden)

gateway_code = str(nodes.get(GATEWAY, {}).get('parameters', {}).get('jsCode', ''))
for marker in ["human_handoff_execution:'EXCLUDED'", 'RC3_HUMAN_HANDOFF_EXECUTION_EXCLUDED', 'human_handoff_enabled:false']:
    if marker not in gateway_code:
        errors.append('locked upstream gateway marker missing: ' + marker)

observed = {
    'workflow_id': wf.get('id'),
    'workflow_name': wf.get('name'),
    'versionId': wf.get('versionId'),
    'active': wf.get('active'),
    'node_count': len(wf.get('nodes', [])),
    'cr10701_support_signal_recovery_present': all(x in build_code for x in ['wu96_communication_decision','technical_issue','support_override_active']),
    'cr10702_acceptance_truth_reconciliation_present': all(x in existing_code for x in ['persistedState','queueVerified','acceptanceVerified','effectiveState','truth_reconciled']),
    'handoff_namespace_isolated': 'spm:staging:handoff:' in build_code,
    'queue_receipt_is_human_acceptance': False,
    'production_write_performed': False,
    'published_or_activated': False,
}
print(json.dumps(observed, indent=2, ensure_ascii=False))
if errors:
    print('WU107_REMOTE_FAIL: ' + '; '.join(errors), file=sys.stderr)
    raise SystemExit(1)
print('WU107_CR10702_REMOTE_PASS')
