#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BUILDER=ROOT/'scripts'/'wu103'/'build_staging_workflow_memory_safe.py'
FAMILY_IDS={
    'FAQ':'record_id','SUBJECTS':'record_id','SUBJECT_PATHWAYS':'pathway_id','SERVICES':'service_id',
    'LOCATIONS':'record_id','FALLBACKS':'record_id','PACKAGES':'record_id','POLICIES':'record_id'
}

with tempfile.TemporaryDirectory() as td:
    out=Path(td)/'wu103.json'
    subprocess.run([sys.executable,str(BUILDER),'--output',str(out)],check=True,cwd=ROOT)
    wf=json.loads(out.read_text(encoding='utf-8'))

assert wf['active'] is False
assert wf['name']=='SPM WU103 Knowledge Maintenance STAGING Candidate'
nodes={n['name']:n for n in wf['nodes']}
assert len(nodes)==len(wf['nodes'])
for name in ['Manual Trigger','Build WU103 Early Preflight','Any WU103 Candidate Needs Deep Validation?','Load WU103 Change Ledger [STAGING]','Load WU103 KB Shadow [STAGING]','Build WU103 Publish Decisions','Is WU103 Publish Allowed?','WU103 Routing Guard Blocked']:
    assert name in nodes,name

for n in wf['nodes']:
    assert n['type'] not in {'@n8n/n8n-nodes-langchain.chatTrigger','n8n-nodes-base.webhook'}
    assert 'PRODUCTION' not in n['name'].upper()

pre=nodes['Build WU103 Early Preflight']['parameters']['jsCode']
for token in ['MULTIPLE_RELEASE_APPROVED_CANDIDATES_V1','wu103_target_family','wu103_lookup_id','wu103_selected_change_id','RELEASE_APPROVED']:
    assert token in pre,token

shadow_read=nodes['Load WU103 KB Shadow [STAGING]']
assert shadow_read['parameters']['filtersUI']['values']==[{
    'lookupColumn':'logical_record_id',
    'lookupValue':"={{ $('Build WU103 Early Preflight').first().json.wu103_lookup_id }}"
}]

for family,id_field in FAMILY_IDS.items():
    n=nodes[f'Load {family} [WU103 READ ONLY]']
    assert n['type']=='n8n-nodes-base.googleSheets'
    assert n['parameters'].get('operation') in (None,'read')
    assert n['parameters']['filtersUI']['values']==[{
        'lookupColumn':id_field,
        'lookupValue':"={{ $('Build WU103 Early Preflight').first().json.wu103_lookup_id }}"
    }]
    assert nodes[f'Is WU103 Target {family}?']['type']=='n8n-nodes-base.if'

write_nodes=[n for n in wf['nodes'] if n['type']=='n8n-nodes-base.googleSheets' and n['parameters'].get('operation')=='appendOrUpdate']
assert {n['name'] for n in write_nodes}=={'Upsert WU103 KB Shadow [STAGING]','Upsert WU103 Change Ledger [STAGING]'}
for n in write_nodes:
    assert n['parameters']['sheetName']['value'] in {2026103001,2026103002}
    assert n.get('onError') is None

shadow=nodes['Upsert WU103 KB Shadow [STAGING]']
ledger=nodes['Upsert WU103 Change Ledger [STAGING]']
assert shadow['parameters']['columns']['matchingColumns']==['change_id']
assert ledger['parameters']['columns']['matchingColumns']==['change_id']

js=nodes['Build WU103 Publish Decisions']['parameters']['jsCode']
for required in [
    'REGRESSION_PAYLOAD_HASH_MISMATCH','REGRESSION_EVIDENCE_REQUIRED','REGRESSION_CASES_INCOMPLETE',
    'CANDIDATE_PAYLOAD_HASH_MISMATCH','STALE_BASE_RECORD','HUMAN_APPROVAL_REQUIRED',
    'RELEASE_APPROVAL_REQUIRED','BUSINESS_TRUTH_APPROVAL_REQUIRED','SOURCE_REFERENCE_REQUIRED',
    'DUPLICATE_ACTIVE_CANDIDATE_KEY','BASE_RECORD_NOT_UNIQUE','ADD_ID_COLLISION_CANONICAL',
    'INTERRUPTED_PUBLISH_LINEAGE_MISMATCH',"clean(r.publish_environment)!=='STAGING'",'new TextEncoder().encode(str)',
    'selectedChangeId','allLedger','catch{return [];}'
]:
    assert required in js,required
assert 'idempotentExisting' in js
assert 'activeShadow.length===2&&sameCurrent.length===1' in js

prepare_shadow=nodes['Prepare WU103 Shadow Writes']['parameters']['jsCode']
assert prepare_shadow.find('new_shadow_row') < prepare_shadow.find('supersede_shadow_row')
prepare_ledger=nodes['Prepare WU103 Ledger Publication Updates']['parameters']['jsCode']
for forbidden in ["review_decision:'APPROVED'","business_truth_approval:true","release_approval_status:'APPROVED'"]:
    assert forbidden not in js and forbidden not in prepare_ledger

connections=wf['connections']
def targets(name): return [[x['node'] for x in group] for group in connections.get(name,{}).get('main',[])]
assert targets('Load WU103 Change Ledger [STAGING]')==[['Build WU103 Early Preflight']]
assert targets('Build WU103 Early Preflight')==[['Any WU103 Candidate Needs Deep Validation?']]
assert targets('Any WU103 Candidate Needs Deep Validation?')==[['Load WU103 KB Shadow [STAGING]'],['WU103 Blocked Result']]
for family in FAMILY_IDS:
    assert targets(f'Load {family} [WU103 READ ONLY]')==[['Build WU103 Publish Decisions']]
    for other in FAMILY_IDS:
        assert f'Load {other} [WU103 READ ONLY]' not in targets(f'Load {family} [WU103 READ ONLY]')[0]

raw=json.dumps(wf,ensure_ascii=False)
for denied in ['CMBMpxX5AqqK2UTn','mMZVFxJIxE7a9SSW','1kaRBBFVJYbPxvQG']:
    assert denied not in raw

print('WU103_STAGING_WORKFLOW_STATIC_PASS')
print(json.dumps({'nodes':len(wf['nodes']),'write_nodes':len(write_nodes),'canonical_family_nodes':len(FAMILY_IDS),'max_canonical_family_reads_per_run':1,'shadow_exact_record_filter':True,'canonical_exact_id_filter':True,'retry_recovery':True,'active':wf['active']},indent=2))
