#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from build_staging_workflow_hardened import build as build_hardened
from build_staging_workflow import sha256_file


PREFLIGHT_JS = r'''function clean(v){return v===null||v===undefined?'':String(v).trim();}
function bool(v){return v===true||['true','1','yes'].includes(clean(v).toLowerCase());}
function arr(v){if(Array.isArray(v))return v;const s=clean(v);if(!s)return [];try{const x=JSON.parse(s);return Array.isArray(x)?x:[];}catch{return s.split(/[,;|]/).map(x=>x.trim()).filter(Boolean);}}
const rows=$input.all().map(i=>i.json||{}).filter(r=>clean(r.change_id));
const groups={};for(const r of rows){const k=clean(r.candidate_key);if(k)(groups[k]??=[]).push(r);}
const families={FAQ:false,SUBJECTS:false,SUBJECT_PATHWAYS:false,SERVICES:false,LOCATIONS:false,FALLBACKS:false,PACKAGES:true,POLICIES:true};
const sourceTypes=['WEBSITE','ATTACHMENT','QUALITY_NOTE','OWNER_DECISION','INTERNAL_APPROVED_SOURCE'];
const candidates=rows.filter(r=>clean(r.change_state)==='RELEASE_APPROVED'&&clean(r.publish_status)!=='PUBLISHED');
const evaluated=[];
for(const r of candidates){
 const reasons=[];const family=clean(r.target_family);const type=clean(r.change_type);const biz=families[family];
 if(!(family in families))reasons.push('UNKNOWN_TARGET_FAMILY');
 if(!/^chg-[a-z0-9-]+$/.test(clean(r.change_id)))reasons.push('INVALID_CHANGE_ID');
 if(!/^uq-/.test(clean(r.source_queue_event_id)))reasons.push('INVALID_QUEUE_PROVENANCE');
 if(!/^[a-f0-9]{64}$/.test(clean(r.candidate_key)))reasons.push('INVALID_CANDIDATE_KEY');
 if((groups[clean(r.candidate_key)]||[]).filter(x=>!['REJECTED','SUPERSEDED'].includes(clean(x.change_state))).length>1)reasons.push('DUPLICATE_ACTIVE_CANDIDATE_KEY');
 if(clean(r.review_decision)!=='APPROVED')reasons.push('HUMAN_APPROVAL_REQUIRED');
 if(clean(r.regression_status)!=='PASS')reasons.push('REGRESSION_PASS_REQUIRED');
 if(clean(r.release_approval_status)!=='APPROVED')reasons.push('RELEASE_APPROVAL_REQUIRED');
 if(!bool(r.pii_reviewed))reasons.push('PII_REVIEW_REQUIRED');
 if(clean(r.publish_environment)!=='STAGING')reasons.push('STAGING_ONLY');
 if(bool(r.raw_customer_message_logged)||bool(r.raw_session_logged)||bool(r.secret_values_logged))reasons.push('FORBIDDEN_PRIVACY_FLAG');
 if(clean(r.regression_payload_sha256)!==clean(r.candidate_payload_sha256))reasons.push('REGRESSION_PAYLOAD_HASH_MISMATCH');
 if(!/^[a-f0-9]{64}$/.test(clean(r.regression_evidence_sha256)))reasons.push('REGRESSION_EVIDENCE_REQUIRED');
 if(new Set(arr(r.regression_case_ids)).size<2)reasons.push('REGRESSION_CASES_INCOMPLETE');
 if(!sourceTypes.includes(clean(r.source_type)))reasons.push('SOURCE_TYPE_REQUIRED');
 if(!clean(r.source_reference))reasons.push('SOURCE_REFERENCE_REQUIRED');
 if(arr(r.language_scope).length<1)reasons.push('LANGUAGE_SCOPE_REQUIRED');
 if(type!=='ADD'&&type!=='UPDATE')reasons.push('INVALID_CHANGE_TYPE');
 if(biz===true){if(!bool(r.business_truth_approval))reasons.push('BUSINESS_TRUTH_APPROVAL_REQUIRED');if(!['OWNER_DECISION','INTERNAL_APPROVED_SOURCE'].includes(clean(r.source_type)))reasons.push('APPROVED_BUSINESS_SOURCE_REQUIRED');}
 evaluated.push({change_id:clean(r.change_id)||null,reasons:[...new Set(reasons)]});
}
const deep=evaluated.some(x=>x.reasons.length===0);
return [{json:{schema:'SPM_WU103_PREFLIGHT_V1',deep_validation_required:deep,candidate_count:evaluated.length,preflight_blocked_results:deep?[]:evaluated}}];'''

BLOCKED_JS = r'''const items=$input.all().map(i=>i.json||{});const pre=items.find(x=>x.schema==='SPM_WU103_PREFLIGHT_V1');const results=pre?pre.preflight_blocked_results:items.map(x=>({change_id:x.change_id||null,reasons:x.wu103_reasons||[]}));return [{json:{schema:'SPM_WU103_STAGING_MAINTENANCE_RESULT_V1',status:'BLOCKED_OR_NOOP',results}}];'''


def node_by_name(wf, name):
    matches=[n for n in wf['nodes'] if n.get('name')==name]
    if len(matches)!=1:
        raise RuntimeError(f'expected one node {name!r}, found {len(matches)}')
    return matches[0]


def build():
    wf=build_hardened()
    ledger='Load WU103 Change Ledger [STAGING]'
    shadow='Load WU103 KB Shadow [STAGING]'
    blocked='WU103 Blocked Result'
    expected={'main':[[{'node':shadow,'type':'main','index':0}]]}
    if wf['connections'].get(ledger)!=expected:
        raise RuntimeError(f'unexpected ledger connection: {wf["connections"].get(ledger)!r}')

    preflight={
        'id':'10300000-0000-4000-8000-000000000108',
        'name':'Build WU103 Early Preflight',
        'type':'n8n-nodes-base.code','typeVersion':2,
        'position':[-1840,560],
        'parameters':{'jsCode':PREFLIGHT_JS},
    }
    gate={
        'id':'10300000-0000-4000-8000-000000000109',
        'name':'Any WU103 Candidate Needs Deep Validation?',
        'type':'n8n-nodes-base.if','typeVersion':2.2,
        'position':[-1600,560],
        'parameters':{'conditions':{'options':{'caseSensitive':True,'leftValue':'','typeValidation':'strict','version':3},'conditions':[{'id':'10300000-0000-4000-8000-000000000209','leftValue':'={{ $json.deep_validation_required }}','rightValue':True,'operator':{'type':'boolean','operation':'true','singleValue':True}}],'combinator':'and'},'options':{}},
    }
    wf['nodes'].extend([preflight,gate])
    wf['connections'][ledger]={'main':[[{'node':preflight['name'],'type':'main','index':0}]]}
    wf['connections'][preflight['name']]={'main':[[{'node':gate['name'],'type':'main','index':0}]]}
    wf['connections'][gate['name']]={'main':[[{'node':shadow,'type':'main','index':0}],[{'node':blocked,'type':'main','index':0}]]}
    node_by_name(wf,blocked)['parameters']['jsCode']=BLOCKED_JS
    return wf


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);args=ap.parse_args()
    wf=build();out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(wf,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(out),'sha256':sha256_file(out),'nodes':len(wf['nodes']),'connections':len(wf['connections']),'active':wf['active'],'hardening':'evidence+retry-recovery+early-preflight'},indent=2))

if __name__=='__main__':main()
