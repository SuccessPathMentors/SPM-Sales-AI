#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

WORKBOOK_ID = '1JJu6eNurnNbBdikOnOe1u7OvUjcTS8Q14TPHjUiT3lM'
GOOGLE_CRED = {'googleSheetsOAuth2Api': {'id': 'k57sEBp5UiDsjtRE', 'name': 'Google Sheets account'}}

LEDGER = {'name': 'WU103_CHANGE_LEDGER_STAGING', 'id': 2026103001}
SHADOW = {'name': 'WU103_KB_SHADOW_STAGING', 'id': 2026103002}
FAMILY_SHEETS = {
    'FAQ': 146862879,
    'SUBJECTS': 1025604941,
    'SUBJECT_PATHWAYS': 697486995,
    'SERVICES': 1799267217,
    'LOCATIONS': 856311166,
    'FALLBACKS': 1793105221,
    'PACKAGES': 448568694,
    'POLICIES': 1408992606,
}

LEDGER_FIELDS = [
    'change_schema','change_id','candidate_key','source_queue_event_id','created_at','updated_at',
    'change_state','review_decision','target_family','change_type','target_record_id','target_id_field',
    'base_revision','candidate_revision','base_fingerprint_sha256','candidate_payload_sha256',
    'language_scope','intent_mapping','source_reference','source_type','business_truth_approval',
    'regression_case_ids','regression_evidence_sha256','regression_status','release_approval_status',
    'publish_environment','publish_status','published_at','published_record_id','published_payload_sha256',
    'supersedes_change_id','reviewer_note','pii_reviewed','raw_customer_message_logged','raw_session_logged',
    'secret_values_logged','candidate_payload_json','regression_payload_sha256'
]
BOOLEAN_LEDGER_FIELDS = {
    'business_truth_approval','pii_reviewed','raw_customer_message_logged','raw_session_logged','secret_values_logged'
}
ARRAY_LEDGER_FIELDS = {'language_scope','intent_mapping','regression_case_ids'}
SHADOW_FIELDS = [
    'target_family','logical_record_id','revision','change_id','source_queue_event_id','payload_json',
    'payload_sha256','base_fingerprint_sha256','record_status','published_at','supersedes_revision'
]


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def doc_ref():
    return {
        '__rl': True,
        'value': WORKBOOK_ID,
        'mode': 'list',
        'cachedResultName': 'Success_Path_Mentors_AI_KB_V2_SPM_2026-08-18',
        'cachedResultUrl': f'https://docs.google.com/spreadsheets/d/{WORKBOOK_ID}/edit',
    }


def sheet_ref(name, sheet_id):
    return {
        '__rl': True,
        'value': sheet_id,
        'mode': 'list',
        'cachedResultName': name,
        'cachedResultUrl': f'https://docs.google.com/spreadsheets/d/{WORKBOOK_ID}/edit#gid={sheet_id}',
    }


def read_node(node_id, name, sheet_name, sheet_id, x, *, active_filter=None):
    params = {
        'documentId': doc_ref(),
        'sheetName': sheet_ref(sheet_name, sheet_id),
        'options': {},
    }
    if active_filter:
        params['filtersUI'] = {'values': [{'lookupColumn': active_filter[0], 'lookupValue': active_filter[1]}]}
    return {
        'id': node_id,
        'name': name,
        'type': 'n8n-nodes-base.googleSheets',
        'typeVersion': 4.7,
        'position': [x, 320],
        'parameters': params,
        'credentials': GOOGLE_CRED,
        'alwaysOutputData': True,
    }


def string_expr(field):
    return (
        "={{ (() => { const v=$json." + field + "; if(v===null||v===undefined)return ''; "
        "const s=String(v); return /^[=+\\-@]/.test(s) ? \"'\"+s : s; })() }}"
    )


def bool_expr(field):
    return "={{ $json." + field + " === true ? 'true' : 'false' }}"


def array_expr(field):
    return "={{ JSON.stringify(Array.isArray($json." + field + ") ? $json." + field + " : []) }}"


def upsert_node(node_id, name, sheet_name, sheet_id, x, fields, matching_columns, *, bool_fields=None, array_fields=None):
    bool_fields = bool_fields or set()
    array_fields = array_fields or set()
    values = {}
    schema = []
    for field in fields:
        if field in bool_fields:
            values[field] = bool_expr(field)
        elif field in array_fields:
            values[field] = array_expr(field)
        else:
            values[field] = string_expr(field)
        schema.append({
            'id': field, 'displayName': field, 'required': False, 'defaultMatch': False,
            'display': True, 'type': 'string', 'canBeUsedToMatch': True,
        })
    return {
        'id': node_id,
        'name': name,
        'type': 'n8n-nodes-base.googleSheets',
        'typeVersion': 4.7,
        'position': [x, 208],
        'parameters': {
            'operation': 'appendOrUpdate',
            'documentId': doc_ref(),
            'sheetName': sheet_ref(sheet_name, sheet_id),
            'columns': {
                'mappingMode': 'defineBelow',
                'value': values,
                'matchingColumns': matching_columns,
                'schema': schema,
                'attemptToConvertTypes': False,
                'convertFieldsToString': True,
            },
            'options': {},
        },
        'credentials': GOOGLE_CRED,
    }


DECISION_JS = r'''function rows(name){
  return $(name).all().map(i=>i.json||{}).filter(r=>Object.keys(r).length>0);
}
function clean(v){return v===null||v===undefined?'':String(v).trim();}
function bool(v){return v===true||['true','1','yes'].includes(clean(v).toLowerCase());}
function arr(v){if(Array.isArray(v))return v; const s=clean(v); if(!s)return []; try{const x=JSON.parse(s);return Array.isArray(x)?x:[];}catch{return s.split(/[,;|]/).map(x=>x.trim()).filter(Boolean);}}
function stable(v){if(Array.isArray(v))return v.map(stable); if(v&&typeof v==='object'){const o={}; for(const k of Object.keys(v).sort())o[k]=stable(v[k]); return o;} return v;}
function canonical(v){return JSON.stringify(stable(v));}
function rotr(x,n){return (x>>>n)|(x<<(32-n));}
function sha256(str){
 const K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
 let H=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
 const bytes=Array.from(new TextEncoder().encode(str)); const bitLen=bytes.length*8; bytes.push(0x80); while(bytes.length%64!==56)bytes.push(0); for(let i=7;i>=0;i--)bytes.push(i>=4?0:(bitLen>>>((i)*8))&255);
 for(let off=0;off<bytes.length;off+=64){const w=new Array(64); for(let i=0;i<16;i++){const j=off+i*4;w[i]=(((bytes[j]<<24)|(bytes[j+1]<<16)|(bytes[j+2]<<8)|bytes[j+3])>>>0);} for(let i=16;i<64;i++){const a=w[i-15],b=w[i-2];const s0=(rotr(a,7)^rotr(a,18)^(a>>>3))>>>0;const s1=(rotr(b,17)^rotr(b,19)^(b>>>10))>>>0;w[i]=(w[i-16]+s0+w[i-7]+s1)>>>0;} let [a,b,c,d,e,f,g,h]=H; for(let i=0;i<64;i++){const S1=(rotr(e,6)^rotr(e,11)^rotr(e,25))>>>0;const ch=((e&f)^((~e)&g))>>>0;const t1=(h+S1+ch+K[i]+w[i])>>>0;const S0=(rotr(a,2)^rotr(a,13)^rotr(a,22))>>>0;const maj=((a&b)^(a&c)^(b&c))>>>0;const t2=(S0+maj)>>>0;h=g;g=f;f=e;e=(d+t1)>>>0;d=c;c=b;b=a;a=(t1+t2)>>>0;} H=[(H[0]+a)>>>0,(H[1]+b)>>>0,(H[2]+c)>>>0,(H[3]+d)>>>0,(H[4]+e)>>>0,(H[5]+f)>>>0,(H[6]+g)>>>0,(H[7]+h)>>>0];}
 return H.map(x=>x.toString(16).padStart(8,'0')).join('');
}
const A={
 FAQ:{id:'record_id',prefix:'FAQ-WU103-',biz:false,fields:['record_id','category','language','question','answer','keywords','priority','status','last_reviewed']},
 SUBJECTS:{id:'record_id',prefix:'SUB-WU103-',biz:false,fields:['record_id','language','subject','grade_from','grade_to','delivery_mode','description','keywords','status']},
 SUBJECT_PATHWAYS:{id:'pathway_id',prefix:'P-WU103-',biz:false,fields:['pathway_id','subject','strand','language','grade_range','description','keywords','source_url','status']},
 SERVICES:{id:'service_id',prefix:'S-WU103-',biz:false,fields:['service_id','language','service_name','description','customer_value','keywords','source_url','status']},
 LOCATIONS:{id:'record_id',prefix:'LOC-WU103-',biz:false,fields:['record_id','country','region','city','language','service_note','keywords','status']},
 FALLBACKS:{id:'record_id',prefix:'FB-WU103-',biz:false,fields:['record_id','scenario','language','message','next_action','status']},
 PACKAGES:{id:'record_id',prefix:'PKG-WU103-',biz:true,fields:['record_id','package_name','class_count','price','currency','language','answer_text','keywords','status','last_reviewed']},
 POLICIES:{id:'record_id',prefix:'POL-WU103-',biz:true,fields:['record_id','policy_type','language','rule','customer_answer','keywords','status','last_reviewed']}
};
const ledger=rows('Load WU103 Change Ledger [STAGING]').filter(r=>clean(r.change_id));
const shadow=rows('Load WU103 KB Shadow [STAGING]').filter(r=>clean(r.change_id));
const canonical={}; for(const f of Object.keys(A))canonical[f]=rows(`Load ${f} [WU103 READ ONLY]`).filter(r=>clean(r.status).toUpperCase()==='ACTIVE');
const candidateGroups={}; for(const r of ledger){const k=clean(r.candidate_key); if(k)(candidateGroups[k]??=[]).push(r);}
const out=[];
for(const r0 of ledger){
 if(clean(r0.change_state)!=='RELEASE_APPROVED'||clean(r0.publish_status)==='PUBLISHED')continue;
 const r={...r0}; const reasons=[]; const family=clean(r.target_family); const a=A[family]; const type=clean(r.change_type); const now=new Date().toISOString();
 if(!a)reasons.push('UNKNOWN_TARGET_FAMILY');
 if(!/^chg-[a-z0-9-]+$/.test(clean(r.change_id)))reasons.push('INVALID_CHANGE_ID');
 if(!/^uq-/.test(clean(r.source_queue_event_id)))reasons.push('INVALID_QUEUE_PROVENANCE');
 if(!/^[a-f0-9]{64}$/.test(clean(r.candidate_key)))reasons.push('INVALID_CANDIDATE_KEY');
 if((candidateGroups[clean(r.candidate_key)]||[]).filter(x=>!['REJECTED','SUPERSEDED'].includes(clean(x.change_state))).length>1)reasons.push('DUPLICATE_ACTIVE_CANDIDATE_KEY');
 if(clean(r.review_decision)!=='APPROVED')reasons.push('HUMAN_APPROVAL_REQUIRED');
 if(clean(r.regression_status)!=='PASS')reasons.push('REGRESSION_PASS_REQUIRED');
 if(clean(r.release_approval_status)!=='APPROVED')reasons.push('RELEASE_APPROVAL_REQUIRED');
 if(!bool(r.pii_reviewed))reasons.push('PII_REVIEW_REQUIRED');
 if(clean(r.publish_environment)!=='STAGING')reasons.push('STAGING_ONLY');
 if(bool(r.raw_customer_message_logged)||bool(r.raw_session_logged)||bool(r.secret_values_logged))reasons.push('FORBIDDEN_PRIVACY_FLAG');
 if(clean(r.regression_payload_sha256)!==clean(r.candidate_payload_sha256))reasons.push('REGRESSION_PAYLOAD_HASH_MISMATCH');
 if(type!=='ADD'&&type!=='UPDATE')reasons.push('INVALID_CHANGE_TYPE');
 let payload=null,payloadCanonical='',payloadSha='';
 if(a){try{payload=JSON.parse(clean(r.candidate_payload_json));if(!payload||Array.isArray(payload)||typeof payload!=='object')throw new Error('not object');const unknown=Object.keys(payload).filter(k=>!a.fields.includes(k));if(unknown.length)reasons.push('UNKNOWN_PAYLOAD_FIELDS:'+unknown.join(','));if('status' in payload&&clean(payload.status).toUpperCase()!=='ACTIVE')reasons.push('NON_ACTIVE_CANDIDATE_STATUS');if(clean(r.target_id_field)!==a.id)reasons.push('TARGET_ID_FIELD_MISMATCH');if(type==='UPDATE'){if(!clean(r.target_record_id))reasons.push('TARGET_RECORD_ID_REQUIRED');if(clean(payload[a.id])!==clean(r.target_record_id))reasons.push('PAYLOAD_TARGET_ID_MISMATCH');}const norm={};for(const f of a.fields)if(f in payload)norm[f]=payload[f];payloadCanonical=canonical(norm);payloadSha=sha256(payloadCanonical);if(payloadSha!==clean(r.candidate_payload_sha256))reasons.push('CANDIDATE_PAYLOAD_HASH_MISMATCH');}catch(e){reasons.push('CANDIDATE_PAYLOAD_JSON_INVALID');}}
 if(a&&a.biz){if(!bool(r.business_truth_approval))reasons.push('BUSINESS_TRUTH_APPROVAL_REQUIRED');if(!['OWNER_DECISION','INTERNAL_APPROVED_SOURCE'].includes(clean(r.source_type)))reasons.push('APPROVED_BUSINESS_SOURCE_REQUIRED');if(!clean(r.source_reference))reasons.push('SOURCE_REFERENCE_REQUIRED');}
 let logicalId=null,baseRevision=null,baseFp=null,supersede=null;
 if(a&&type==='ADD'){
   if(clean(r.target_record_id))reasons.push('ADD_TARGET_MUST_BE_NULL');
   logicalId=a.prefix+clean(r.candidate_key).slice(0,12).toUpperCase(); baseRevision=null; baseFp=null;
   const canonCollision=canonical[family].some(x=>clean(x[a.id])===logicalId);
   const shadowCollision=shadow.find(x=>clean(x.target_family)===family&&clean(x.logical_record_id)===logicalId&&clean(x.record_status)==='ACTIVE');
   if(canonCollision)reasons.push('ADD_ID_COLLISION_CANONICAL');
   if(shadowCollision&&clean(shadowCollision.change_id)!==clean(r.change_id))reasons.push('ADD_ID_COLLISION_SHADOW');
   if(shadowCollision&&clean(shadowCollision.change_id)===clean(r.change_id)&&clean(shadowCollision.payload_sha256)!==payloadSha)reasons.push('CHANGE_ID_PAYLOAD_MISMATCH');
   if(clean(r.candidate_revision)!=='v1')reasons.push('ADD_REVISION_MUST_BE_V1');
 } else if(a&&type==='UPDATE'){
   logicalId=clean(r.target_record_id);
   const activeShadow=shadow.filter(x=>clean(x.target_family)===family&&clean(x.logical_record_id)===logicalId&&clean(x.record_status)==='ACTIVE');
   if(activeShadow.length>1)reasons.push('BASE_RECORD_NOT_UNIQUE');
   if(activeShadow.length===1){const b=activeShadow[0];baseRevision=clean(b.revision);baseFp=clean(b.payload_sha256);if(clean(b.change_id)===clean(r.change_id)){if(baseFp!==payloadSha||baseRevision!==clean(r.candidate_revision))reasons.push('CHANGE_ID_PAYLOAD_MISMATCH');}else{supersede=b;}}
   else {const matches=canonical[family].filter(x=>clean(x[a.id])===logicalId&&clean(x.status).toUpperCase()==='ACTIVE');if(matches.length!==1)reasons.push('BASE_RECORD_NOT_UNIQUE');else{const norm={};for(const f of a.fields)if(f!=='last_reviewed')norm[f]=matches[0][f];baseRevision='LEGACY_UNVERSIONED';baseFp=sha256(canonical(norm));}}
   if(baseRevision&&clean(r.base_revision)!==baseRevision)reasons.push('STALE_BASE_REVISION');
   if(baseFp&&clean(r.base_fingerprint_sha256)!==baseFp)reasons.push('STALE_BASE_RECORD');
   const next=baseRevision==='LEGACY_UNVERSIONED'?'v1':(/^v\d+$/.test(baseRevision)?`v${Number(baseRevision.slice(1))+1}`:null);
   if(next&&clean(r.candidate_revision)!==next&&!(activeShadow.length===1&&clean(activeShadow[0].change_id)===clean(r.change_id)&&clean(activeShadow[0].revision)===clean(r.candidate_revision)))reasons.push('CANDIDATE_REVISION_MISMATCH');
 }
 const allowed=reasons.length===0; const newShadow=allowed?{target_family:family,logical_record_id:logicalId,revision:clean(r.candidate_revision),change_id:clean(r.change_id),source_queue_event_id:clean(r.source_queue_event_id),payload_json:payloadCanonical,payload_sha256:payloadSha,base_fingerprint_sha256:baseFp||'',record_status:'ACTIVE',published_at:now,supersedes_revision:supersede?clean(supersede.revision):''}:null;
 const ledgerUpdate=allowed?{...r,updated_at:now,change_state:'PUBLISHED',publish_status:'PUBLISHED',published_at:now,published_record_id:logicalId,published_payload_sha256:payloadSha,supersedes_change_id:supersede?clean(supersede.change_id):clean(r.supersedes_change_id)}:null;
 out.push({json:{wu103_publish_allowed:allowed,wu103_reasons:reasons,change_id:clean(r.change_id),new_shadow_row:newShadow,supersede_shadow_row:supersede?{...supersede,record_status:'SUPERSEDED'}:null,ledger_update:ledgerUpdate}});
}
if(!out.length)return [{json:{wu103_publish_allowed:false,wu103_reasons:['NO_RELEASE_APPROVED_CANDIDATES'],change_id:null}}];
return out;'''

PREPARE_SHADOW_JS = r'''const out=[]; for(const i of $input.all()){const d=i.json||{}; if(d.wu103_publish_allowed!==true)continue; if(d.supersede_shadow_row)out.push({json:d.supersede_shadow_row}); if(d.new_shadow_row)out.push({json:d.new_shadow_row});} return out;'''

PREPARE_LEDGER_JS = r'''const out=[]; for(const i of $('Build WU103 Publish Decisions').all()){const d=i.json||{}; if(d.wu103_publish_allowed===true&&d.ledger_update)out.push({json:d.ledger_update});} return out;'''

FINAL_PUBLISHED_JS = r'''const published=$input.all().map(i=>i.json||{});return [{json:{schema:'SPM_WU103_STAGING_MAINTENANCE_RESULT_V1',status:'PUBLISHED',count:published.length,change_ids:published.map(x=>x.change_id).filter(Boolean)}}];'''
FINAL_BLOCKED_JS = r'''const items=$input.all().map(i=>i.json||{});return [{json:{schema:'SPM_WU103_STAGING_MAINTENANCE_RESULT_V1',status:'BLOCKED_OR_NOOP',results:items.map(x=>({change_id:x.change_id||null,reasons:x.wu103_reasons||[]}))}}];'''


def build():
    nodes=[]
    nodes.append({'id':'10300000-0000-4000-8000-000000000001','name':'Manual Trigger','type':'n8n-nodes-base.manualTrigger','typeVersion':1,'position':[-2200,320],'parameters':{}})
    chain=[]
    chain.append(read_node('10300000-0000-4000-8000-000000000010','Load WU103 Change Ledger [STAGING]',LEDGER['name'],LEDGER['id'],-1960))
    chain.append(read_node('10300000-0000-4000-8000-000000000011','Load WU103 KB Shadow [STAGING]',SHADOW['name'],SHADOW['id'],-1720,active_filter=('record_status','ACTIVE')))
    x=-1480
    for idx,(family,sid) in enumerate(FAMILY_SHEETS.items(),start=20):
        chain.append(read_node(f'10300000-0000-4000-8000-{idx:012d}',f'Load {family} [WU103 READ ONLY]',family,sid,x,active_filter=('status','ACTIVE')))
        x+=240
    nodes.extend(chain)
    decision_x=x
    nodes.append({'id':'10300000-0000-4000-8000-000000000100','name':'Build WU103 Publish Decisions','type':'n8n-nodes-base.code','typeVersion':2,'position':[decision_x,320],'parameters':{'jsCode':DECISION_JS}})
    nodes.append({'id':'10300000-0000-4000-8000-000000000101','name':'Is WU103 Publish Allowed?','type':'n8n-nodes-base.if','typeVersion':2.2,'position':[decision_x+240,320],'parameters':{'conditions':{'options':{'caseSensitive':True,'leftValue':'','typeValidation':'strict','version':3},'conditions':[{'id':'10300000-0000-4000-8000-000000000201','leftValue':'={{ $json.wu103_publish_allowed }}','rightValue':True,'operator':{'type':'boolean','operation':'true','singleValue':True}}],'combinator':'and'},'options':{}}})
    nodes.append({'id':'10300000-0000-4000-8000-000000000102','name':'Prepare WU103 Shadow Writes','type':'n8n-nodes-base.code','typeVersion':2,'position':[decision_x+480,176],'parameters':{'jsCode':PREPARE_SHADOW_JS}})
    nodes.append(upsert_node('10300000-0000-4000-8000-000000000103','Upsert WU103 KB Shadow [STAGING]',SHADOW['name'],SHADOW['id'],decision_x+720,SHADOW_FIELDS,['change_id']))
    nodes.append({'id':'10300000-0000-4000-8000-000000000104','name':'Prepare WU103 Ledger Publication Updates','type':'n8n-nodes-base.code','typeVersion':2,'position':[decision_x+960,176],'parameters':{'jsCode':PREPARE_LEDGER_JS}})
    nodes.append(upsert_node('10300000-0000-4000-8000-000000000105','Upsert WU103 Change Ledger [STAGING]',LEDGER['name'],LEDGER['id'],decision_x+1200,LEDGER_FIELDS,['change_id'],bool_fields=BOOLEAN_LEDGER_FIELDS,array_fields=ARRAY_LEDGER_FIELDS))
    nodes.append({'id':'10300000-0000-4000-8000-000000000106','name':'WU103 Published Result','type':'n8n-nodes-base.code','typeVersion':2,'position':[decision_x+1440,176],'parameters':{'jsCode':FINAL_PUBLISHED_JS}})
    nodes.append({'id':'10300000-0000-4000-8000-000000000107','name':'WU103 Blocked Result','type':'n8n-nodes-base.code','typeVersion':2,'position':[decision_x+480,464],'parameters':{'jsCode':FINAL_BLOCKED_JS}})

    connections={}
    previous='Manual Trigger'
    for n in chain:
        connections[previous]={'main':[[{'node':n['name'],'type':'main','index':0}]]}
        previous=n['name']
    connections[previous]={'main':[[{'node':'Build WU103 Publish Decisions','type':'main','index':0}]]}
    connections['Build WU103 Publish Decisions']={'main':[[{'node':'Is WU103 Publish Allowed?','type':'main','index':0}]]}
    connections['Is WU103 Publish Allowed?']={'main':[[{'node':'Prepare WU103 Shadow Writes','type':'main','index':0}],[{'node':'WU103 Blocked Result','type':'main','index':0}]]}
    connections['Prepare WU103 Shadow Writes']={'main':[[{'node':'Upsert WU103 KB Shadow [STAGING]','type':'main','index':0}]]}
    connections['Upsert WU103 KB Shadow [STAGING]']={'main':[[{'node':'Prepare WU103 Ledger Publication Updates','type':'main','index':0}]]}
    connections['Prepare WU103 Ledger Publication Updates']={'main':[[{'node':'Upsert WU103 Change Ledger [STAGING]','type':'main','index':0}]]}
    connections['Upsert WU103 Change Ledger [STAGING]']={'main':[[{'node':'WU103 Published Result','type':'main','index':0}]]}

    return {
        'name':'SPM WU103 Knowledge Maintenance STAGING Candidate',
        'nodes':nodes,
        'connections':connections,
        'active':False,
        'settings':{'executionOrder':'v1'},
        'versionId':'10300000-0000-4000-8000-000000000999',
        'meta':{'templateCredsSetupCompleted':True},
        'pinData':{},
        'tags':[],
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',required=True)
    args=ap.parse_args()
    wf=build()
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(wf,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(out),'sha256':sha256_file(out),'nodes':len(wf['nodes']),'connections':len(wf['connections']),'active':wf['active'],'ledger_sheet_id':LEDGER['id'],'shadow_sheet_id':SHADOW['id']},indent=2))

if __name__=='__main__':
    main()
