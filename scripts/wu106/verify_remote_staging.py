#!/usr/bin/env python3
import json, os, sys, urllib.request

TARGET=os.getenv('N8N_TARGET_WORKFLOW_ID','').strip()
BASE=os.getenv('N8N_API_BASE_URL','').strip().rstrip('/')
KEY=os.getenv('N8N_API_KEY','').strip()
EXPECTED_ID='vvHvidUHVxM5wTVT'
EXPECTED_NAME='[STAGING] SPM_WU106_END_TO_END_JOURNEYS_V1'
EXPECTED_NODES=141
PROTECTED={'CMBMpxX5AqqK2UTn','mMZVFxJIxE7a9SSW','1kaRBBFVJYbPxvQG','5COEoxXjk8AvuGBa','Bt3PvOIbFzU0O9gk','KXfalaYSCLdgmf4X'}

INIT='Initialize + Merge Sales State Contract'; CATALOG='Load SPM V2 62 Intent Catalog'
CR10601='Apply WU106 Journey Transition Recovery [CR-106-01]'
ROOT='Apply WU106 Root Journey Recovery [CR-106-02]'; SHORT='Apply WU104 Short Trial Inquiry Guard'
LOAD='Load WU106 Registration Control [CR-106-02]'; MERGE='Merge WU106 Durable Registration Control [CR-106-02]'
BUILD='Build WU106 Registration Control Snapshot [CR-106-02]'; SAVE='Save WU106 Registration Control [CR-106-02]'; RESTORE='Restore After WU106 Registration Control Save [CR-106-02]'
PERSIST='Persist WU104 Final Asked Field'; SERIAL='Serialize WU95 STAGING Sales State'
ALT='Apply WU106 Alternative Slot Recovery [CR-106-03]'
ALT_RESP='Apply WU106 Alternative Availability Response Guard [CR-106-03]'
AVAIL='Apply WU105 Availability Answer-First Guard'; CONV='Resolve WU95 Conversion Mode'
WU89='Validate + Normalize WU89 Entities'
CANON_LOAD='Load Sales State [STAGING NAMESPACE]'; CANON_SAVE='Save WU95 Sales State [STAGING NAMESPACE]'

if not TARGET or not BASE or not KEY: raise SystemExit('missing n8n readback environment')
if TARGET!=EXPECTED_ID or TARGET in PROTECTED: raise SystemExit('unexpected/protected target')
req=urllib.request.Request(f'{BASE}/workflows/{TARGET}',headers={'accept':'application/json','X-N8N-API-KEY':KEY})
with urllib.request.urlopen(req,timeout=45) as r: wf=json.loads(r.read().decode())
nodes={n.get('name'):n for n in wf.get('nodes',[])}; conns=wf.get('connections',{}); errors=[]

def target(name, output=0):
    m=conns.get(name,{}).get('main')
    if not isinstance(m,list) or len(m)<=output or not isinstance(m[output],list) or len(m[output])!=1: return None
    return m[output][0].get('node')
def must(src,dst,out=0):
    got=target(src,out)
    if got!=dst: errors.append(f'{src}[{out}] -> {got!r}, expected {dst!r}')

if str(wf.get('id'))!=EXPECTED_ID: errors.append('workflow id mismatch')
if wf.get('name')!=EXPECTED_NAME: errors.append('workflow name mismatch')
if wf.get('active') is True: errors.append('workflow unexpectedly active')
if len(wf.get('nodes',[]))!=EXPECTED_NODES: errors.append(f'node count {len(wf.get("nodes",[]))} != {EXPECTED_NODES}')

required=[INIT,CATALOG,CR10601,ROOT,SHORT,LOAD,MERGE,BUILD,SAVE,RESTORE,PERSIST,SERIAL,ALT,ALT_RESP,AVAIL,CONV,WU89,CANON_LOAD,CANON_SAVE,
'Build WU106 Journey Orchestration Envelope','Apply WU105 Explicit Free Trial Action Guard','Apply WU105 Refund Policy Answer-First Guard','Load POLICIES [WU91 READ ONLY]','Upsert WU102 Unanswered [STAGING]','Redis Chat Memory']
for n in required:
    if n not in nodes: errors.append('missing node: '+n)

# CR-106-02 durable control remains intact.
must(INIT,LOAD); must(LOAD,MERGE,0); must(LOAD,MERGE,1); must(MERGE,CATALOG)
must(CR10601,ROOT); must(PERSIST,BUILD); must(BUILD,SAVE); must(SAVE,RESTORE,0); must(SAVE,RESTORE,1); must(RESTORE,SERIAL)
# CR-106-03 topology.
must(ROOT,ALT); must(ALT,SHORT); must(AVAIL,ALT_RESP); must(ALT_RESP,CONV)

load=nodes.get(LOAD,{}); save=nodes.get(SAVE,{}); cl=nodes.get(CANON_LOAD,{}); cs=nodes.get(CANON_SAVE,{})
if load.get('credentials')!=cl.get('credentials') or save.get('credentials')!=cs.get('credentials'): errors.append('registration-control Redis credential drift')
if 'spm:staging:regctrl:' not in str(load.get('parameters',{}).get('key','')): errors.append('registration-control namespace drift')

wu89=str(nodes.get(WU89,{}).get('parameters',{}).get('jsCode',''))
alt=str(nodes.get(ALT,{}).get('parameters',{}).get('jsCode',''))
altresp=str(nodes.get(ALT_RESP,{}).get('parameters',{}).get('jsCode',''))
for marker in ['SPM_WU106_CR10603_SCHEDULING_NORMALIZATION_V1','customer_deterministic_city_time_alias','America/Toronto','customer_deterministic_schedule_preference']:
    if marker not in wu89: errors.append('WU89 CR-106-03 marker missing: '+marker)
for marker in ['SPM_WU106_CR10603_ALTERNATIVE_SLOT_RECOVERY_V1','WU106_CR10603_ALTERNATIVE_AVAILABILITY','existing_schedule_preferences_mutated:false','production_mutation_allowed:false']:
    if marker not in alt: errors.append('alternative recovery marker missing: '+marker)
for marker in ['SPM_WU106_CR10603_ALTERNATIVE_AVAILABILITY_RESPONSE_V1','requested_preference_preserved:true','slot_invented:false','booking_claimed:false','production_mutation_allowed:false']:
    if marker not in altresp: errors.append('alternative response marker missing: '+marker)

# Preserve upstream safety/idempotency/isolation.
q=nodes.get('Upsert WU102 Unanswered [STAGING]',{}); cols=q.get('parameters',{}).get('columns',{})
if q.get('parameters',{}).get('operation')!='appendOrUpdate': errors.append('WU102 operation drift')
if cols.get('matchingColumns')!=['queue_event_id']: errors.append('WU102 idempotency drift')
mem=nodes.get('Redis Chat Memory',{}).get('parameters',{}).get('sessionKey')
if mem!="={{ 'spm:staging:chat:' + $json.sessionId }}": errors.append('chat-memory namespace drift')
for code,name in [(alt,'ALT'),(altresp,'ALT_RESPONSE')]:
    for forbidden in ['booking_success=true','availability_verified=true','httpRequest','executeWorkflow','lead_upsert']:
        if forbidden in code: errors.append(f'{name} forbidden surface: {forbidden}')

observed={'workflow_id':wf.get('id'),'active':wf.get('active'),'versionId':wf.get('versionId'),'node_count':len(wf.get('nodes',[])),
'cr10603_present':ALT in nodes and ALT_RESP in nodes,'toronto_time_normalizer_present':'SPM_WU106_CR10603_SCHEDULING_NORMALIZATION_V1' in wu89,
'root_to_alternative':target(ROOT),'alternative_to_short_guard':target(ALT),'availability_guard_to_alt_response':target(AVAIL),'alt_response_to_conversion':target(ALT_RESP),
'registration_control_namespace_isolated':'spm:staging:regctrl:' in str(load.get('parameters',{}).get('key','')),
'chat_memory_session_key':mem,'production_write_performed':False}
print(json.dumps(observed,indent=2,ensure_ascii=False))
if errors:
    print('WU106_CR10603_REMOTE_FAIL: '+'; '.join(errors),file=sys.stderr); raise SystemExit(1)
print('WU106_CR10603_REMOTE_PASS')
