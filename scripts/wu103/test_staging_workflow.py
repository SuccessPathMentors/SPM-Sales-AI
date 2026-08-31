#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BUILDER=ROOT/'scripts'/'wu103'/'build_staging_workflow_hardened.py'

with tempfile.TemporaryDirectory() as td:
    out=Path(td)/'wu103.json'
    subprocess.run([sys.executable,str(BUILDER),'--output',str(out)],check=True,cwd=ROOT)
    wf=json.loads(out.read_text(encoding='utf-8'))

assert wf['active'] is False
assert wf['name']=='SPM WU103 Knowledge Maintenance STAGING Candidate'
nodes={n['name']:n for n in wf['nodes']}
assert len(nodes)==len(wf['nodes'])
assert nodes['Manual Trigger']['type']=='n8n-nodes-base.manualTrigger'

for n in wf['nodes']:
    assert n['type'] not in {'@n8n/n8n-nodes-langchain.chatTrigger','n8n-nodes-base.webhook'}
    assert 'PRODUCTION' not in n['name'].upper()

read_only_families=['FAQ','SUBJECTS','SUBJECT_PATHWAYS','SERVICES','LOCATIONS','FALLBACKS','PACKAGES','POLICIES']
for family in read_only_families:
    n=nodes[f'Load {family} [WU103 READ ONLY]']
    assert n['type']=='n8n-nodes-base.googleSheets'
    assert n['parameters'].get('operation') in (None,'read')
    assert n['parameters']['filtersUI']['values'][0]=={'lookupColumn':'status','lookupValue':'ACTIVE'}

# Shadow history is deliberately unfiltered for interrupted-publication repair.
shadow_read=nodes['Load WU103 KB Shadow [STAGING]']
assert 'filtersUI' not in shadow_read['parameters']

write_nodes=[n for n in wf['nodes'] if n['type']=='n8n-nodes-base.googleSheets' and n['parameters'].get('operation')=='appendOrUpdate']
assert {n['name'] for n in write_nodes}=={'Upsert WU103 KB Shadow [STAGING]','Upsert WU103 Change Ledger [STAGING]'}
for n in write_nodes:
    assert n['parameters']['sheetName']['value'] in {2026103001,2026103002}

shadow=nodes['Upsert WU103 KB Shadow [STAGING]']
ledger=nodes['Upsert WU103 Change Ledger [STAGING]']
assert shadow['parameters']['columns']['matchingColumns']==['change_id']
assert ledger['parameters']['columns']['matchingColumns']==['change_id']
assert shadow.get('onError') is None
assert ledger.get('onError') is None

js=nodes['Build WU103 Publish Decisions']['parameters']['jsCode']
for required in [
    'REGRESSION_PAYLOAD_HASH_MISMATCH','REGRESSION_EVIDENCE_REQUIRED','REGRESSION_CASES_INCOMPLETE',
    'CANDIDATE_PAYLOAD_HASH_MISMATCH','STALE_BASE_RECORD','HUMAN_APPROVAL_REQUIRED',
    'RELEASE_APPROVAL_REQUIRED','BUSINESS_TRUTH_APPROVAL_REQUIRED','SOURCE_REFERENCE_REQUIRED',
    'DUPLICATE_ACTIVE_CANDIDATE_KEY','BASE_RECORD_NOT_UNIQUE','ADD_ID_COLLISION_CANONICAL',
    'INTERRUPTED_PUBLISH_LINEAGE_MISMATCH',"clean(r.publish_environment)!=='STAGING'",'new TextEncoder().encode(str)',
]:
    assert required in js, required

prepare_shadow=nodes['Prepare WU103 Shadow Writes']['parameters']['jsCode']
assert prepare_shadow.find('new_shadow_row') < prepare_shadow.find('supersede_shadow_row')
assert 'idempotentExisting' in js
assert 'activeShadow.length===2&&sameCurrent.length===1' in js

prepare_ledger=nodes['Prepare WU103 Ledger Publication Updates']['parameters']['jsCode']
for forbidden_assignment in ["review_decision:'APPROVED'","business_truth_approval:true","release_approval_status:'APPROVED'"]:
    assert forbidden_assignment not in js
    assert forbidden_assignment not in prepare_ledger

raw=json.dumps(wf,ensure_ascii=False)
for denied in ['CMBMpxX5AqqK2UTn','mMZVFxJIxE7a9SSW','1kaRBBFVJYbPxvQG']:
    assert denied not in raw

print('WU103_STAGING_WORKFLOW_STATIC_PASS')
print(json.dumps({'nodes':len(wf['nodes']),'write_nodes':len(write_nodes),'canonical_read_families':len(read_only_families),'shadow_history_read':True,'new_before_supersede':True,'retry_recovery':True,'active':wf['active']},indent=2))
