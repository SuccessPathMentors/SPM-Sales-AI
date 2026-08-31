#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BUILDER=ROOT/'scripts'/'wu103'/'build_staging_workflow.py'

with tempfile.TemporaryDirectory() as td:
    out=Path(td)/'wu103.json'
    subprocess.run([sys.executable,str(BUILDER),'--output',str(out)],check=True,cwd=ROOT)
    wf=json.loads(out.read_text(encoding='utf-8'))

assert wf['active'] is False
assert wf['name']=='SPM WU103 Knowledge Maintenance STAGING Candidate'
nodes={n['name']:n for n in wf['nodes']}
assert len(nodes)==len(wf['nodes'])
assert 'Manual Trigger' in nodes
assert nodes['Manual Trigger']['type']=='n8n-nodes-base.manualTrigger'

# No customer/public triggers and no Sales Agent workflow embedding.
for n in wf['nodes']:
    assert n['type'] not in {'@n8n/n8n-nodes-langchain.chatTrigger','n8n-nodes-base.webhook'}
    assert 'PRODUCTION' not in n['name'].upper()

read_only_families=['FAQ','SUBJECTS','SUBJECT_PATHWAYS','SERVICES','LOCATIONS','FALLBACKS','PACKAGES','POLICIES']
for family in read_only_families:
    n=nodes[f'Load {family} [WU103 READ ONLY]']
    assert n['type']=='n8n-nodes-base.googleSheets'
    assert n['parameters'].get('operation') in (None,'read')
    assert n['parameters']['filtersUI']['values'][0]=={'lookupColumn':'status','lookupValue':'ACTIVE'}

# Only the two dedicated WU103 STAGING tabs may be write targets.
write_nodes=[n for n in wf['nodes'] if n['type']=='n8n-nodes-base.googleSheets' and n['parameters'].get('operation')=='appendOrUpdate']
assert {n['name'] for n in write_nodes}=={
    'Upsert WU103 KB Shadow [STAGING]',
    'Upsert WU103 Change Ledger [STAGING]',
}
for n in write_nodes:
    sid=n['parameters']['sheetName']['value']
    assert sid in {2026103001,2026103002}

shadow=nodes['Upsert WU103 KB Shadow [STAGING]']
ledger=nodes['Upsert WU103 Change Ledger [STAGING]']
assert shadow['parameters']['columns']['matchingColumns']==['change_id']
assert ledger['parameters']['columns']['matchingColumns']==['change_id']
assert shadow.get('onError') is None
assert ledger.get('onError') is None

js=nodes['Build WU103 Publish Decisions']['parameters']['jsCode']
for required in [
    'REGRESSION_PAYLOAD_HASH_MISMATCH','CANDIDATE_PAYLOAD_HASH_MISMATCH','STALE_BASE_RECORD',
    'HUMAN_APPROVAL_REQUIRED','RELEASE_APPROVAL_REQUIRED','BUSINESS_TRUTH_APPROVAL_REQUIRED',
    'DUPLICATE_ACTIVE_CANDIDATE_KEY','BASE_RECORD_NOT_UNIQUE','ADD_ID_COLLISION_CANONICAL',
    "clean(r.publish_environment)!=='STAGING'",'new TextEncoder().encode(str)',
]:
    assert required in js, required

# The automated publisher preserves approval fields; it never generates APPROVED values.
prepare_ledger=nodes['Prepare WU103 Ledger Publication Updates']['parameters']['jsCode']
assert "change_state:'PUBLISHED'" not in prepare_ledger
for forbidden_assignment in [
    "review_decision:'APPROVED'",
    "business_truth_approval:true",
    "release_approval_status:'APPROVED'",
]:
    assert forbidden_assignment not in js
    assert forbidden_assignment not in prepare_ledger

# WU102 and Production workflow IDs are not embedded in the maintenance artifact.
raw=json.dumps(wf,ensure_ascii=False)
for denied in ['CMBMpxX5AqqK2UTn','mMZVFxJIxE7a9SSW','1kaRBBFVJYbPxvQG']:
    assert denied not in raw

print('WU103_STAGING_WORKFLOW_STATIC_PASS')
print(json.dumps({'nodes':len(wf['nodes']),'write_nodes':len(write_nodes),'canonical_read_families':len(read_only_families),'active':wf['active']},indent=2))
