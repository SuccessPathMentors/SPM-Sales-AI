#!/usr/bin/env python3
import argparse, copy, hashlib, json
from pathlib import Path

BASELINE_SHA256='680496f2b68b13dd7105e72fd132a2066d70ec969e6e0675f138ebb1fb16fe39'
WORKBOOK_ID='1JJu6eNurnNbBdikOnOe1u7OvUjcTS8Q14TPHjUiT3lM'
ANALYTICS_SHEET_ID=2026101001
ANALYTICS_SHEET_NAME='WU101_ANALYTICS_STAGING'
LEADS_SHEET_ID=2026101002
LEADS_SHEET_NAME='WU101_LEADS_STAGING'
GOOGLE_CRED={'googleSheetsOAuth2Api': {'id':'k57sEBp5UiDsjtRE','name':'Google Sheets account'}}

FIELDS=[
'event_schema','event_id','event_timestamp','workflow_release','channel','analytics_session_key','turn_index',
'primary_intent','secondary_intent','confidence','language','journey_stage','source_gate','classifier_route',
'clarification_used','fallback_used','human_requested','lead_outcome','lead_id_present','opt_out','action_status',
'degraded','recovery_mode','duration_ms','error_codes','pii_redacted','raw_message_logged','raw_session_logged',
'correlation_id_logged','secret_values_logged']

def sha256(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def node_by_name(wf,name):
    matches=[n for n in wf['nodes'] if n.get('name')==name]
    if len(matches)!=1: raise RuntimeError(f'expected exactly one node {name!r}, found {len(matches)}')
    return matches[0]

def replace_exact(text, old, new):
    if old not in text: raise RuntimeError(f'expected text not found: {old}')
    return text.replace(old,new)

def sheet_ref(sheet_id, name):
    return {'__rl':True,'value':sheet_id,'mode':'list','cachedResultName':name,
            'cachedResultUrl':f'https://docs.google.com/spreadsheets/d/{WORKBOOK_ID}/edit#gid={sheet_id}'}

def doc_ref():
    return {'__rl':True,'value':WORKBOOK_ID,'mode':'list','cachedResultName':'Success_Path_Mentors_AI_KB_V2_SPM_2026-08-18',
            'cachedResultUrl':f'https://docs.google.com/spreadsheets/d/{WORKBOOK_ID}/edit'}

def build(baseline_path):
    raw=Path(baseline_path).read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    if digest!=BASELINE_SHA256: raise RuntimeError(f'baseline sha mismatch {digest}')
    wf=json.loads(raw.decode('utf-8'))
    wf=copy.deepcopy(wf)
    wf['name']='SPM WU101 Conversation Analytics Candidate'
    wf['active']=False
    for k in ['id','versionId','activeVersionId','versionCounter','triggerCount','updatedAt','createdAt']:
        wf.pop(k,None)

    n=node_by_name(wf,'Build Canonical Session Envelope')
    js=n['parameters']['jsCode']
    js=replace_exact(js,"workflow_release:'WU100_RC4_3_3_CONTEXTUAL_CONSENT_DECLINE_FIX'","workflow_release:'WU101_STAGING_ANALYTICS_V1'")
    js=replace_exact(js,"workflow_mode:'PRODUCTION_ACTIVE'","workflow_mode:'STAGING_INACTIVE'")
    js=replace_exact(js,"sales_state_key:`spm:prod:sales:${safeSession}`","sales_state_key:`spm:staging:sales:${safeSession}`")
    js=replace_exact(js,"test_mode:false","test_mode:true")
    js=replace_exact(js,"production_cutover_authorized:true","production_cutover_authorized:false")
    js=replace_exact(js,"lead_crm_write:'INCLUDED_CERTIFIED'","lead_crm_write:'INCLUDED_STAGING_ISOLATED'")
    n['parameters']['jsCode']=js

    n=node_by_name(wf,'Initialize + Merge Sales State Contract')
    js=n['parameters']['jsCode']
    js=replace_exact(js,"nurture:{opt_out:false,follow_up_eligible:false},\n  recovery:",
        "nurture:{opt_out:false,follow_up_eligible:false},\n  analytics:{session_key:null,turn_index:0},\n  recovery:")
    marker="state.session_id=j.session_id;\nstate.flags="
    insert=("state.session_id=j.session_id;\n"
            "state.analytics=state.analytics&&typeof state.analytics==='object'?state.analytics:{};\n"
            "if(!String(state.analytics.session_key||'').startsWith('conv-')){\n"
            "  const r=()=>Math.random().toString(36).slice(2,14);\n"
            "  state.analytics.session_key=`conv-${Date.now().toString(36)}-${r()}-${r()}`;\n"
            "}\n"
            "const prevTurn=Number(state.analytics.turn_index||0);\n"
            "state.analytics.turn_index=Number.isFinite(prevTurn)&&prevTurn>=0?Math.floor(prevTurn)+1:1;\n"
            "state.flags=")
    js=replace_exact(js,marker,insert)
    n['parameters']['jsCode']=js

    for old,new in [
        ('Load Sales State [PRODUCTION NAMESPACE]','Load Sales State [STAGING NAMESPACE]'),
        ('Save Sales State [PRODUCTION NAMESPACE]','Save Sales State [STAGING NAMESPACE]'),
        ('Serialize WU95 Production Sales State','Serialize WU95 STAGING Sales State'),
        ('Save WU95 Sales State [PRODUCTION NAMESPACE]','Save WU95 Sales State [STAGING NAMESPACE]')]:
        n=node_by_name(wf,old); n['name']=new
        if old in wf['connections']:
            wf['connections'][new]=wf['connections'].pop(old)
        for outgroups in wf['connections'].values():
            for lists in outgroups.values():
                for arr in lists:
                    for c in arr:
                        if c.get('node')==old: c['node']=new
    n=node_by_name(wf,'Serialize WU95 STAGING Sales State')
    n['parameters']['jsCode']=replace_exact(n['parameters']['jsCode'],"`spm:prod:sales:${j.session_id}`","`spm:staging:sales:${j.session_id}`")

    n=node_by_name(wf,'Serialize WU90 Production Sales State')
    js=n['parameters']['jsCode']
    js=replace_exact(js,"namespace:'spm:prod:sales:*'","namespace:'spm:staging:sales:*'")
    js=replace_exact(js,"production_namespace:true","production_namespace:false")
    n['parameters']['jsCode']=js

    for name in ['Check WU95 Existing Lead [READ ONLY]','Upsert WU95 Lead [CERTIFIED PRODUCTION ADAPTER]','Verify WU95 Lead Write [READBACK]']:
        n=node_by_name(wf,name)
        n['parameters']['documentId']=doc_ref()
        n['parameters']['sheetName']=sheet_ref(LEADS_SHEET_ID,LEADS_SHEET_NAME)
    node_by_name(wf,'Upsert WU95 Lead [CERTIFIED PRODUCTION ADAPTER]')['name']='Upsert WU95 Lead [STAGING ISOLATED ADAPTER]'
    old='Upsert WU95 Lead [CERTIFIED PRODUCTION ADAPTER]'; new='Upsert WU95 Lead [STAGING ISOLATED ADAPTER]'
    if old in wf['connections']: wf['connections'][new]=wf['connections'].pop(old)
    for outgroups in wf['connections'].values():
        for lists in outgroups.values():
            for arr in lists:
                for c in arr:
                    if c.get('node')==old: c['node']=new

    n=node_by_name(wf,'Apply WU95 Lead Truth Guard')
    js=n['parameters']['jsCode']
    js=replace_exact(js,"production_write_enabled:true","production_write_enabled:false")
    js=replace_exact(js,"release_scope:'INCLUDED_CERTIFIED'","release_scope:'STAGING_ISOLATED'")
    n['parameters']['jsCode']=js

    builder_name='Build WU101 Conversation Analytics Event'
    builder_js=r"""const j=$input.first().json||{};
const t=j.telemetry||{};
const state=j.sales_state||{};
const a=state.analytics||{};
const r=()=>Math.random().toString(36).slice(2,14);
const sessionKey=String(a.session_key||'').startsWith('conv-')?String(a.session_key):`conv-${Date.now().toString(36)}-${r()}-${r()}`;
const turn=Math.max(1,Math.floor(Number(a.turn_index||1))||1);
const eventId=`evt-${sessionKey.slice(5)}-${turn}`;
function lang(v){const s=String(v||'').toLowerCase();if(s.startsWith('ar'))return'ar';if(s.startsWith('fr'))return'fr';if(s.startsWith('en'))return'en';return'unknown';}
const route=['direct','clarify','fallback'].includes(String(j.classifier_route||''))?String(j.classifier_route):'unknown';
const wr=j.lead_write_result||{};
const validation=j.wu95_lead_validation||{};
let leadOutcome='none';
if(wr.success===true&&['created','updated'].includes(String(wr.operation)))leadOutcome=String(wr.operation);
else if(['FAILED','READBACK_VERIFICATION_FAILED'].includes(String(wr.adapter_status))||String(wr.reason_code||'').includes('FAILED'))leadOutcome='failed';
else if(validation.mode==='lead'&&validation.flow&&validation.flow!=='none'&&validation.flow!=='declined')leadOutcome='pending';
const primary=j.classification?.spm_intent??null;
const secondary=j.classification?.secondary_spm_intent??null;
const human=primary==='human_handoff'||secondary==='human_handoff'||j.wu95_handoff_contract?.requested===true||state.support?.handoff_requested===true;
const codes=[...(Array.isArray(t.error_codes)?t.error_codes:[])];
if(!String(a.session_key||'').startsWith('conv-')&&!codes.includes('WU101_ANALYTICS_SESSION_KEY_FALLBACK'))codes.push('WU101_ANALYTICS_SESSION_KEY_FALLBACK');
const e={
 event_schema:'SPM_WU101_CONVERSATION_ANALYTICS_V1',event_id:eventId,event_timestamp:new Date().toISOString(),workflow_release:'WU101_STAGING_ANALYTICS_V1',channel:j.channel==='website_chat'?'website_chat':'unknown',analytics_session_key:sessionKey,turn_index:turn,
 primary_intent:primary,secondary_intent:secondary,confidence:Number.isFinite(Number(j.classification?.confidence))?Number(j.classification.confidence):null,language:lang(j.classification?.language||j.language_hint),journey_stage:j.journey_decision?.stage??null,source_gate:j.source_gate_result?.gate??j.source_gate_decision?.gate??null,classifier_route:route,
 clarification_used:j.customer_clarification_required===true||route==='clarify',fallback_used:route==='fallback',human_requested:Boolean(human),lead_outcome:leadOutcome,lead_id_present:Boolean(wr.success===true&&wr.lead_id),opt_out:state.nurture?.opt_out===true,action_status:j.action_result?.status??null,degraded:Boolean(t.degraded),recovery_mode:t.recovery_mode??null,duration_ms:Math.max(0,Math.floor(Number(t.duration_ms||0))||0),error_codes:[...new Set(codes.map(x=>String(x).slice(0,120)))].slice(0,20),
 pii_redacted:true,raw_message_logged:false,raw_session_logged:false,correlation_id_logged:false,secret_values_logged:false
};
return [{json:{...j,wu101_analytics_event:e}}];"""
    builder={
        'id':'10100000-0000-4000-8000-000000000101','name':builder_name,'type':'n8n-nodes-base.code','typeVersion':2,
        'position':[-78976,5536],'parameters':{'jsCode':builder_js}
    }

    schema=[]
    for f in FIELDS:
        typ='number' if f in {'turn_index','confidence','duration_ms'} else ('boolean' if f in {'clarification_used','fallback_used','human_requested','lead_id_present','opt_out','degraded','pii_redacted','raw_message_logged','raw_session_logged','correlation_id_logged','secret_values_logged'} else 'string')
        schema.append({'id':f,'displayName':f,'required':False,'defaultMatch':False,'display':True,'type':typ,'canBeUsedToMatch':True})
    values={}
    for f in FIELDS:
        if f=='error_codes': values[f]="={{ JSON.stringify($json.wu101_analytics_event.error_codes || []) }}"
        else: values[f]=f"={{ $json.wu101_analytics_event.{f} }}"
    logger_name='Upsert WU101 Analytics [STAGING]'
    logger={
        'id':'10100000-0000-4000-8000-000000000102','name':logger_name,'type':'n8n-nodes-base.googleSheets','typeVersion':4.7,
        'position':[-78736,5536],
        'parameters':{
            'operation':'appendOrUpdate','documentId':doc_ref(),'sheetName':sheet_ref(ANALYTICS_SHEET_ID,ANALYTICS_SHEET_NAME),
            'columns':{'mappingMode':'defineBelow','value':values,'matchingColumns':['event_id'],'schema':schema,'attemptToConvertTypes':False,'convertFieldsToString':False},'options':{}
        },
        'credentials':copy.deepcopy(GOOGLE_CRED),'onError':'continueRegularOutput'
    }
    restore_name='Restore Customer Context After WU101 Analytics'
    restore_js=r"""const base=$('Build WU101 Conversation Analytics Event').first().json||{};
const cur=$input.first().json||{};
const failed=Boolean(cur.error||cur.description||cur.errorMessage);
const result={schema:'SPM_WU101_ANALYTICS_WRITE_V1',status:failed?'FAILED_FAIL_OPEN':'UPSERTED',success:!failed,fail_open:true,event_id:base.wu101_analytics_event?.event_id||null};
return [{json:{...base,wu101_analytics_write:result}}];"""
    restore={'id':'10100000-0000-4000-8000-000000000103','name':restore_name,'type':'n8n-nodes-base.code','typeVersion':2,'position':[-78496,5536],'parameters':{'jsCode':restore_js}}
    wf['nodes'].extend([builder,logger,restore])

    red='Redact WU97 Observability Telemetry'; save='Save AI Message to Chat History'
    conn=wf['connections'].get(red,{}).get('main',[])
    if conn!=[[{'node':save,'type':'main','index':0}]]:
        raise RuntimeError(f'unexpected redaction connection: {conn!r}')
    wf['connections'][red]={'main':[[{'node':builder_name,'type':'main','index':0}]]}
    wf['connections'][builder_name]={'main':[[{'node':logger_name,'type':'main','index':0}]]}
    wf['connections'][logger_name]={'main':[[{'node':restore_name,'type':'main','index':0}]]}
    wf['connections'][restore_name]={'main':[[{'node':save,'type':'main','index':0}]]}

    node_by_name(wf,save)['position']=[-78256,5536]
    node_by_name(wf,'Restore Final Response Payload')['position']=[-78016,5536]
    node_by_name(wf,'RC3 Chat Response')['position']=[-77776,5536]
    return wf

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--baseline',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
    wf=build(args.baseline)
    Path(args.output).write_text(json.dumps(wf,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':args.output,'sha256':sha256(args.output),'node_count':len(wf['nodes']),'connection_sources':len(wf['connections'])},indent=2))
if __name__=='__main__': main()
