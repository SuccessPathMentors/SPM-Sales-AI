#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

from build_candidate import ANALYTICS_SHEET_ID, BASELINE_SHA256, FIELDS, LEADS_SHEET_ID, build

BASE = Path('n8n/workflows/production/SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json')
EXPECTED_CANDIDATE_SHA256 = '45f82c338eb3535f6ed72e4081aced19b4319da377ae02374a07855e52258c41'

assert BASE.is_file(), BASE
assert hashlib.sha256(BASE.read_bytes()).hexdigest() == BASELINE_SHA256
base = json.loads(BASE.read_text(encoding='utf-8'))
wf = build(BASE)

def node(name):
    matches = [n for n in wf['nodes'] if n.get('name') == name]
    assert len(matches) == 1, (name, len(matches))
    return matches[0]

serialized = json.dumps(wf, ensure_ascii=False, indent=2) + '\n'
serialized2 = json.dumps(build(BASE), ensure_ascii=False, indent=2) + '\n'
digest = hashlib.sha256(serialized.encode('utf-8')).hexdigest()
assert digest == hashlib.sha256(serialized2.encode('utf-8')).hexdigest()
assert digest == EXPECTED_CANDIDATE_SHA256, digest

assert wf['name'] == 'SPM WU101 Conversation Analytics Candidate'
assert wf.get('active') is False
assert 'id' not in wf
assert len(base['nodes']) == 114
assert len(wf['nodes']) == 117
assert len({n['name'] for n in wf['nodes']}) == 117
ids = [n.get('id') for n in wf['nodes'] if n.get('id')]
assert len(ids) == len(set(ids))
names = {n['name'] for n in wf['nodes']}
assert set(wf['connections']).issubset(names)

def walk(value):
    if isinstance(value, dict):
        target = value.get('node')
        if isinstance(target, str):
            assert target in names, target
        for child in value.values():
            walk(child)
    elif isinstance(value, list):
        for child in value:
            walk(child)

walk(wf['connections'])

js = node('Build Canonical Session Envelope')['parameters']['jsCode']
assert "workflow_mode:'STAGING_INACTIVE'" in js
assert 'spm:staging:sales:' in js
assert 'spm:prod:sales:' not in js
assert 'test_mode:true' in js
assert 'production_cutover_authorized:false' in js

state_js = node('Initialize + Merge Sales State Contract')['parameters']['jsCode']
assert 'analytics:{session_key:null,turn_index:0}' in state_js
assert 'state.analytics.session_key' in state_js
assert 'state.analytics.turn_index' in state_js
analytics_state_section = state_js[state_js.find('state.analytics='):state_js.find('state.flags=')]
assert 'j.session_id' not in analytics_state_section
assert 'j.correlation_id' not in analytics_state_section

serialize90 = node('Serialize WU90 Production Sales State')['parameters']['jsCode']
assert "namespace:'spm:staging:sales:*'" in serialize90
assert 'production_namespace:false' in serialize90
serialize95 = node('Serialize WU95 STAGING Sales State')['parameters']['jsCode']
assert 'spm:staging:sales:' in serialize95
assert 'spm:prod:sales:' not in serialize95

for name in ['Check WU95 Existing Lead [READ ONLY]','Upsert WU95 Lead [STAGING ISOLATED ADAPTER]','Verify WU95 Lead Write [READBACK]']:
    assert node(name)['parameters']['sheetName']['value'] == LEADS_SHEET_ID
assert 'production_write_enabled:false' in node('Apply WU95 Lead Truth Guard')['parameters']['jsCode']

builder_js = node('Build WU101 Conversation Analytics Event')['parameters']['jsCode']
for forbidden in ['j.correlation_id','j.session_id','j.message','j.chatInput','parent_name','student_name','j.phone','j.email']:
    assert forbidden not in builder_js, forbidden
assert 'correlation_id_logged:false' in builder_js
assert "const eventId=`evt-${sessionKey.slice(5)}-${turn}`" in builder_js

logger = node('Upsert WU101 Analytics [STAGING]')
assert logger['parameters']['operation'] == 'appendOrUpdate'
assert logger['parameters']['sheetName']['value'] == ANALYTICS_SHEET_ID
assert logger['parameters']['columns']['matchingColumns'] == ['event_id']
assert logger.get('onError') == 'continueRegularOutput'
assert not logger.get('retryOnFail', False)
assert list(logger['parameters']['columns']['value']) == FIELDS
assert 'correlation_id' not in FIELDS
assert 'correlation_id_logged' in FIELDS

assert wf['connections']['Redact WU97 Observability Telemetry']['main'][0][0]['node'] == 'Build WU101 Conversation Analytics Event'
assert wf['connections']['Build WU101 Conversation Analytics Event']['main'][0][0]['node'] == 'Upsert WU101 Analytics [STAGING]'
assert wf['connections']['Upsert WU101 Analytics [STAGING]']['main'][0][0]['node'] == 'Restore Customer Context After WU101 Analytics'
assert wf['connections']['Restore Customer Context After WU101 Analytics']['main'][0][0]['node'] == 'Save AI Message to Chat History'
restore_js = node('Restore Customer Context After WU101 Analytics')['parameters']['jsCode']
assert "$('Build WU101 Conversation Analytics Event').first().json" in restore_js
assert 'fail_open:true' in restore_js

assert not [n['name'] for n in wf['nodes'] if 'executeWorkflow' in n.get('type', '')]
assert not [n['name'] for n in wf['nodes'] if n.get('disabled') is True]

print('WU101_STATIC_TESTS_PASS')
print(json.dumps({'nodes': len(wf['nodes']), 'connections': len(wf['connections']), 'candidate_sha256': digest}, indent=2))
