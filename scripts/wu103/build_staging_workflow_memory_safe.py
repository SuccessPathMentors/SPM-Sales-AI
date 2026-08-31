#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from build_staging_workflow_hardened import build as build_hardened
from build_staging_workflow import sha256_file

FAMILY_META={
    'FAQ':('record_id','FAQ-WU103-'),
    'SUBJECTS':('record_id','SUB-WU103-'),
    'SUBJECT_PATHWAYS':('pathway_id','P-WU103-'),
    'SERVICES':('service_id','S-WU103-'),
    'LOCATIONS':('record_id','LOC-WU103-'),
    'FALLBACKS':('record_id','FB-WU103-'),
    'PACKAGES':('record_id','PKG-WU103-'),
    'POLICIES':('record_id','POL-WU103-'),
}

PRECHECK_JS=r'''function clean(v){return v===null||v===undefined?'':String(v).trim();}
const rows=$input.all().map(i=>i.json||{}).filter(r=>clean(r.change_id));
const eligible=rows.filter(r=>clean(r.change_state)==='RELEASE_APPROVED'&&clean(r.publish_status)!=='PUBLISHED');
const meta={FAQ:{id:'record_id',prefix:'FAQ-WU103-'},SUBJECTS:{id:'record_id',prefix:'SUB-WU103-'},SUBJECT_PATHWAYS:{id:'pathway_id',prefix:'P-WU103-'},SERVICES:{id:'service_id',prefix:'S-WU103-'},LOCATIONS:{id:'record_id',prefix:'LOC-WU103-'},FALLBACKS:{id:'record_id',prefix:'FB-WU103-'},PACKAGES:{id:'record_id',prefix:'PKG-WU103-'},POLICIES:{id:'record_id',prefix:'POL-WU103-'}};
if(eligible.length===0)return [{json:{wu103_deep_validation_required:false,wu103_reasons:['NO_RELEASE_APPROVED_CANDIDATES'],change_id:null}}];
if(eligible.length>1)return [{json:{wu103_deep_validation_required:false,wu103_reasons:['MULTIPLE_RELEASE_APPROVED_CANDIDATES_V1'],change_id:null,wu103_candidate_count:eligible.length}}];
const r=eligible[0]; const family=clean(r.target_family); const type=clean(r.change_type); const reasons=[]; const m=meta[family];
if(!m)reasons.push('UNKNOWN_TARGET_FAMILY');
if(type!=='ADD'&&type!=='UPDATE')reasons.push('INVALID_CHANGE_TYPE');
if(!/^chg-[a-z0-9-]+$/.test(clean(r.change_id)))reasons.push('INVALID_CHANGE_ID');
if(!/^[a-f0-9]{64}$/.test(clean(r.candidate_key)))reasons.push('INVALID_CANDIDATE_KEY');
let lookup='';
if(m&&type==='UPDATE'){lookup=clean(r.target_record_id);if(!lookup)reasons.push('TARGET_RECORD_ID_REQUIRED');}
if(m&&type==='ADD'){if(clean(r.target_record_id))reasons.push('ADD_TARGET_MUST_BE_NULL');lookup=m.prefix+clean(r.candidate_key).slice(0,12).toUpperCase();}
return [{json:{...r,wu103_deep_validation_required:reasons.length===0,wu103_reasons:reasons,wu103_selected_change_id:clean(r.change_id),wu103_target_family:family,wu103_lookup_id:lookup,wu103_target_id_field:m?m.id:null,change_id:clean(r.change_id)}}];'''

COLLAPSE_JS=r'''const p=$('Build WU103 Early Preflight').first().json||{};return [{json:{...p,wu103_shadow_history_loaded:true}}];'''
ROUTING_BLOCK_JS=r'''const p=$('Build WU103 Early Preflight').first().json||{};return [{json:{wu103_publish_allowed:false,wu103_reasons:['TARGET_FAMILY_ROUTING_FAILED'],change_id:p.wu103_selected_change_id||null,target_family:p.wu103_target_family||null}}];'''


def node_by_name(wf,name):
    xs=[n for n in wf['nodes'] if n.get('name')==name]
    if len(xs)!=1: raise RuntimeError(f'expected one node {name!r}, found {len(xs)}')
    return xs[0]


def if_node(node_id,name,left,right,x,y=320):
    return {
        'id':node_id,'name':name,'type':'n8n-nodes-base.if','typeVersion':2.2,'position':[x,y],
        'parameters':{'conditions':{'options':{'caseSensitive':True,'leftValue':'','typeValidation':'strict','version':3},'conditions':[{'id':node_id[:-3]+'201','leftValue':left,'rightValue':right,'operator':{'type':'string','operation':'equals'}}],'combinator':'and'},'options':{}}
    }


def bool_if_node(node_id,name,left,x,y=320):
    return {
        'id':node_id,'name':name,'type':'n8n-nodes-base.if','typeVersion':2.2,'position':[x,y],
        'parameters':{'conditions':{'options':{'caseSensitive':True,'leftValue':'','typeValidation':'strict','version':3},'conditions':[{'id':node_id[:-3]+'202','leftValue':left,'rightValue':True,'operator':{'type':'boolean','operation':'true','singleValue':True}}],'combinator':'and'},'options':{}}
    }


def build():
    wf=build_hardened()
    wf['name']='SPM WU103 Knowledge Maintenance STAGING Candidate'

    pre={'id':'10310000-0000-4000-8000-000000000001','name':'Build WU103 Early Preflight','type':'n8n-nodes-base.code','typeVersion':2,'position':[-1720,320],'parameters':{'jsCode':PRECHECK_JS}}
    gate=bool_if_node('10310000-0000-4000-8000-000000000002','Any WU103 Candidate Needs Deep Validation?','={{ $json.wu103_deep_validation_required }}',-1480)
    route_block={'id':'10310000-0000-4000-8000-000000000003','name':'WU103 Routing Guard Blocked','type':'n8n-nodes-base.code','typeVersion':2,'position':[840,560],'parameters':{'jsCode':ROUTING_BLOCK_JS}}
    collapse={'id':'10310000-0000-4000-8000-000000000004','name':'Collapse WU103 Routing Context','type':'n8n-nodes-base.code','typeVersion':2,'position':[-1080,320],'parameters':{'jsCode':COLLAPSE_JS}}
    wf['nodes'].extend([pre,gate,route_block,collapse])

    shadow=node_by_name(wf,'Load WU103 KB Shadow [STAGING]')
    shadow['position']=[-1240,208]
    shadow['parameters']['filtersUI']={'values':[{'lookupColumn':'logical_record_id','lookupValue':"={{ $('Build WU103 Early Preflight').first().json.wu103_lookup_id }}"}]}

    family_ifs=[]
    start_x=-840
    for i,(family,(id_field,_prefix)) in enumerate(FAMILY_META.items()):
        load=node_by_name(wf,f'Load {family} [WU103 READ ONLY]')
        load['position']=[start_x+i*240,80]
        load['parameters']['filtersUI']={'values':[{'lookupColumn':id_field,'lookupValue':"={{ $('Build WU103 Early Preflight').first().json.wu103_lookup_id }}"}]}
        test=if_node(f'10310000-0000-4000-8000-{100+i:012d}',f'Is WU103 Target {family}?',"={{ $('Build WU103 Early Preflight').first().json.wu103_target_family }}",family,start_x+i*240,320)
        family_ifs.append(test)
    wf['nodes'].extend(family_ifs)

    decision=node_by_name(wf,'Build WU103 Publish Decisions')
    decision['position']=[1320,208]
    js=decision['parameters']['jsCode']
    old="function rows(name){\n  return $(name).all().map(i=>i.json||{}).filter(r=>Object.keys(r).length>0);\n}"
    new="function rows(name){try{return $(name).all().map(i=>i.json||{}).filter(r=>Object.keys(r).length>0);}catch{return [];}}"
    if old not in js: raise RuntimeError('rows helper marker not found')
    js=js.replace(old,new)
    old_ledger="const ledger=rows('Load WU103 Change Ledger [STAGING]').filter(r=>clean(r.change_id));"
    new_ledger="const allLedger=rows('Load WU103 Change Ledger [STAGING]').filter(r=>clean(r.change_id));\nconst selectedChangeId=clean($('Build WU103 Early Preflight').first().json.wu103_selected_change_id);\nconst ledger=allLedger.filter(r=>clean(r.change_id)===selectedChangeId);"
    if old_ledger not in js: raise RuntimeError('ledger selection marker not found')
    js=js.replace(old_ledger,new_ledger)
    old_groups="const candidateGroups={}; for(const r of ledger){const k=clean(r.candidate_key); if(k)(candidateGroups[k]??=[]).push(r);}"
    new_groups="const candidateGroups={}; for(const r of allLedger){const k=clean(r.candidate_key); if(k)(candidateGroups[k]??=[]).push(r);}"
    if old_groups not in js: raise RuntimeError('candidate group marker not found')
    js=js.replace(old_groups,new_groups)
    decision['parameters']['jsCode']=js

    c=wf['connections']
    c['Manual Trigger']={'main':[[{'node':'Load WU103 Change Ledger [STAGING]','type':'main','index':0}]]}
    c['Load WU103 Change Ledger [STAGING]']={'main':[[{'node':'Build WU103 Early Preflight','type':'main','index':0}]]}
    c['Build WU103 Early Preflight']={'main':[[{'node':'Any WU103 Candidate Needs Deep Validation?','type':'main','index':0}]]}
    c['Any WU103 Candidate Needs Deep Validation?']={'main':[[{'node':'Load WU103 KB Shadow [STAGING]','type':'main','index':0}],[{'node':'WU103 Blocked Result','type':'main','index':0}]]}
    c['Load WU103 KB Shadow [STAGING]']={'main':[[{'node':'Collapse WU103 Routing Context','type':'main','index':0}]]}
    c['Collapse WU103 Routing Context']={'main':[[{'node':family_ifs[0]['name'],'type':'main','index':0}]]}
    for i,(family,_meta) in enumerate(FAMILY_META.items()):
        false_target=family_ifs[i+1]['name'] if i+1<len(family_ifs) else 'WU103 Routing Guard Blocked'
        c[family_ifs[i]['name']]={'main':[[{'node':f'Load {family} [WU103 READ ONLY]','type':'main','index':0}],[{'node':false_target,'type':'main','index':0}]]}
        c[f'Load {family} [WU103 READ ONLY]']={'main':[[{'node':'Build WU103 Publish Decisions','type':'main','index':0}]]}
    c.pop('WU103 Routing Guard Blocked',None)

    return wf


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);args=ap.parse_args()
    wf=build();out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(wf,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(out),'sha256':sha256_file(out),'nodes':len(wf['nodes']),'connections':len(wf['connections']),'active':wf['active'],'memory_safety':'single-candidate+single-routing-item+single-family+exact-id-read'},indent=2))

if __name__=='__main__':main()
