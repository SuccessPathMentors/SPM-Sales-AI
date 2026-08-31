#!/usr/bin/env python3
import json
import os
import sys
import urllib.request

TARGET=os.getenv('N8N_TARGET_WORKFLOW_ID','').strip()
BASE=os.getenv('N8N_API_BASE_URL','').strip().rstrip('/')
KEY=os.getenv('N8N_API_KEY','').strip()

DENIED={'CMBMpxX5AqqK2UTn','mMZVFxJIxE7a9SSW','1kaRBBFVJYbPxvQG'}
LEDGER_ID=2026103001
SHADOW_ID=2026103002
FAMILY_IDS={
 'FAQ':146862879,'SUBJECTS':1025604941,'SUBJECT_PATHWAYS':697486995,'SERVICES':1799267217,
 'LOCATIONS':856311166,'FALLBACKS':1793105221,'PACKAGES':448568694,'POLICIES':1408992606,
}

if not TARGET or not BASE or not KEY:
    raise SystemExit('missing required n8n readback environment')
if TARGET in DENIED:
    raise SystemExit('protected/locked workflow ID denied for WU-103')

req=urllib.request.Request(f'{BASE}/workflows/{TARGET}',headers={'accept':'application/json','X-N8N-API-KEY':KEY},method='GET')
with urllib.request.urlopen(req,timeout=45) as resp:
    wf=json.loads(resp.read().decode('utf-8'))

nodes={n.get('name'):n for n in wf.get('nodes',[])}
required=[
 'Manual Trigger','Load WU103 Change Ledger [STAGING]','Load WU103 KB Shadow [STAGING]',
 'Build WU103 Publish Decisions','Is WU103 Publish Allowed?','Prepare WU103 Shadow Writes',
 'Upsert WU103 KB Shadow [STAGING]','Prepare WU103 Ledger Publication Updates',
 'Upsert WU103 Change Ledger [STAGING]','WU103 Published Result','WU103 Blocked Result',
]+[f'Load {f} [WU103 READ ONLY]' for f in FAMILY_IDS]
missing=[n for n in required if n not in nodes]
errors=[]
if missing:errors.append('missing nodes: '+','.join(missing))
if wf.get('active') is True:errors.append('remote workflow unexpectedly active')
if wf.get('name')!='[STAGING] SPM WU103 Knowledge Maintenance STAGING Candidate':errors.append('remote workflow name mismatch')
if len(wf.get('nodes',[]))!=19:errors.append('remote node count mismatch')

for n in wf.get('nodes',[]):
    if n.get('type') in {'@n8n/n8n-nodes-langchain.chatTrigger','n8n-nodes-base.webhook'}:
        errors.append('public/customer trigger present')

ledger=nodes.get('Upsert WU103 Change Ledger [STAGING]',{})
shadow=nodes.get('Upsert WU103 KB Shadow [STAGING]',{})
for node,expected_id,label in [(ledger,LEDGER_ID,'ledger'),(shadow,SHADOW_ID,'shadow')]:
    p=node.get('parameters',{})
    if p.get('operation')!='appendOrUpdate':errors.append(f'{label} write operation mismatch')
    if p.get('sheetName',{}).get('value')!=expected_id:errors.append(f'{label} sheet ID mismatch')
    if p.get('columns',{}).get('matchingColumns')!=['change_id']:errors.append(f'{label} idempotency key mismatch')
    if node.get('onError') is not None:errors.append(f'{label} sink must remain fail-closed')

for family,sid in FAMILY_IDS.items():
    n=nodes.get(f'Load {family} [WU103 READ ONLY]',{})
    p=n.get('parameters',{})
    if p.get('sheetName',{}).get('value')!=sid:errors.append(f'{family} canonical sheet ID mismatch')
    if p.get('operation') not in (None,'read'):errors.append(f'{family} canonical node is not read-only')
    vals=p.get('filtersUI',{}).get('values',[])
    if vals!=[{'lookupColumn':'status','lookupValue':'ACTIVE'}]:errors.append(f'{family} ACTIVE filter mismatch')

js=nodes.get('Build WU103 Publish Decisions',{}).get('parameters',{}).get('jsCode','')
for token in [
 'REGRESSION_PAYLOAD_HASH_MISMATCH','CANDIDATE_PAYLOAD_HASH_MISMATCH','STALE_BASE_RECORD',
 'HUMAN_APPROVAL_REQUIRED','RELEASE_APPROVAL_REQUIRED','BUSINESS_TRUTH_APPROVAL_REQUIRED',
 'DUPLICATE_ACTIVE_CANDIDATE_KEY','ADD_ID_COLLISION_CANONICAL','BASE_RECORD_NOT_UNIQUE',
 "clean(r.publish_environment)!=='STAGING'",'new TextEncoder().encode(str)',
]:
    if token not in js:errors.append('missing gate: '+token)
for forbidden in ["review_decision:'APPROVED'","business_truth_approval:true","release_approval_status:'APPROVED'"]:
    if forbidden in js:errors.append('self-approval assignment present: '+forbidden)

connections=wf.get('connections',{})
def targets(name):
    return [[c.get('node') for c in group] for group in connections.get(name,{}).get('main',[])]
if targets('Is WU103 Publish Allowed?')!=[['Prepare WU103 Shadow Writes'],['WU103 Blocked Result']]:errors.append('publish gate branch mismatch')
if targets('Prepare WU103 Shadow Writes')!=[['Upsert WU103 KB Shadow [STAGING]']]:errors.append('shadow write path mismatch')
if targets('Upsert WU103 KB Shadow [STAGING]')!=[['Prepare WU103 Ledger Publication Updates']]:errors.append('shadow-to-ledger path mismatch')
if targets('Prepare WU103 Ledger Publication Updates')!=[['Upsert WU103 Change Ledger [STAGING]']]:errors.append('ledger update path mismatch')

observed={
 'workflow_id':wf.get('id'),'workflow_name':wf.get('name'),'active':wf.get('active'),
 'node_count':len(wf.get('nodes',[])),'ledger_sheet_id':ledger.get('parameters',{}).get('sheetName',{}).get('value'),
 'shadow_sheet_id':shadow.get('parameters',{}).get('sheetName',{}).get('value'),
 'ledger_matching':ledger.get('parameters',{}).get('columns',{}).get('matchingColumns'),
 'shadow_matching':shadow.get('parameters',{}).get('columns',{}).get('matchingColumns'),
 'canonical_family_count':len(FAMILY_IDS),'fail_closed_writes':ledger.get('onError') is None and shadow.get('onError') is None,
}
print(json.dumps(observed,indent=2,ensure_ascii=False))
if errors:
    print('WU103_REMOTE_READBACK_FAIL: '+'; '.join(errors),file=sys.stderr)
    raise SystemExit(1)
print('WU103_REMOTE_READBACK_PASS')
