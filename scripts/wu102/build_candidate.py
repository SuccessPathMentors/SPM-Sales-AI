#!/usr/bin/env python3
import argparse
import copy
import json
import sys
from pathlib import Path

WU101_DIR = Path(__file__).resolve().parents[1] / 'wu101'
sys.path.insert(0, str(WU101_DIR))

from build_candidate_sheets_type_safe import build as build_wu101  # noqa: E402
from build_candidate import sha256  # noqa: E402

WORKBOOK_ID = '1JJu6eNurnNbBdikOnOe1u7OvUjcTS8Q14TPHjUiT3lM'
QUEUE_SHEET_ID = 2026102001
QUEUE_SHEET_NAME = 'WU102_UNANSWERED_STAGING'
GOOGLE_CRED = {'googleSheetsOAuth2Api': {'id': 'k57sEBp5UiDsjtRE', 'name': 'Google Sheets account'}}

FIELDS = [
    'event_schema', 'queue_event_id', 'event_timestamp', 'workflow_release', 'channel',
    'queue_session_key', 'turn_index', 'redacted_question', 'question_capture_status',
    'language', 'dialect_hint', 'predicted_intent', 'secondary_intent', 'confidence',
    'kb_match_status', 'fallback_used', 'clarification_used', 'human_requested',
    'out_of_scope', 'trigger_reasons', 'resolution_status', 'approved_answer_status',
    'added_to_kb_status', 'pii_redacted', 'raw_message_logged', 'raw_session_logged',
    'secret_values_logged'
]

NUMERIC_FIELDS = {'turn_index', 'confidence'}
BOOLEAN_FIELDS = {
    'fallback_used', 'clarification_used', 'human_requested', 'out_of_scope',
    'pii_redacted', 'raw_message_logged', 'raw_session_logged', 'secret_values_logged'
}


def node_by_name(wf, name):
    matches = [n for n in wf['nodes'] if n.get('name') == name]
    if len(matches) != 1:
        raise RuntimeError(f'expected exactly one node {name!r}, found {len(matches)}')
    return matches[0]


def replace_exact(text, old, new):
    if old not in text:
        raise RuntimeError(f'expected text not found: {old}')
    return text.replace(old, new)


def doc_ref():
    return {
        '__rl': True,
        'value': WORKBOOK_ID,
        'mode': 'list',
        'cachedResultName': 'Success_Path_Mentors_AI_KB_V2_SPM_2026-08-18',
        'cachedResultUrl': f'https://docs.google.com/spreadsheets/d/{WORKBOOK_ID}/edit',
    }


def sheet_ref():
    return {
        '__rl': True,
        'value': QUEUE_SHEET_ID,
        'mode': 'list',
        'cachedResultName': QUEUE_SHEET_NAME,
        'cachedResultUrl': f'https://docs.google.com/spreadsheets/d/{WORKBOOK_ID}/edit#gid={QUEUE_SHEET_ID}',
    }


def expr(field):
    return '={{ $json.wu102_queue_event.' + field + ' }}'


def bool_expr(field):
    return '={{ $json.wu102_queue_event.' + field + " === true ? 'true' : 'false' }}"


def build(baseline_path):
    wf = build_wu101(baseline_path)
    wf = copy.deepcopy(wf)
    wf['name'] = 'SPM WU102 Unanswered Question Queue Candidate'
    wf['active'] = False

    canonical = node_by_name(wf, 'Build Canonical Session Envelope')
    canonical['parameters']['jsCode'] = replace_exact(
        canonical['parameters']['jsCode'],
        "workflow_release:'WU101_STAGING_ANALYTICS_V1'",
        "workflow_release:'WU102_STAGING_UNANSWERED_V1'",
    )

    builder_name = 'Build WU102 Unanswered Queue Decision'
    builder_js = r"""const j=$input.first().json||{};
const c=j.classification||{};
const p=j.source_plan||{};
const sr=j.source_gate_result||{};
const sd=j.source_gate_decision||{};
const state=j.sales_state||{};
const analytics=state.analytics||{};
const route=String(j.classifier_route||'unknown');
const confidence=Number.isFinite(Number(c.confidence))?Number(c.confidence):null;
const threshold=Number.isFinite(Number(c.threshold))?Number(c.threshold):null;
const primary=c.spm_intent??null;
const secondary=c.secondary_spm_intent??null;
const liveRequired=Boolean(p.live_verification_required||sr.live_verification_required);
const evidenceCount=Number.isFinite(Number(sd.evidence_count))?Number(sd.evidence_count):(Number.isFinite(Number(sr.evidence_count))?Number(sr.evidence_count):0);
const reasonCode=String(sd.reason_code||sr.retrieval_status||p.blocked_reason||'');
const staticEligible=Boolean(p.static_claims_allowed)&&!liveRequired;
const noStaticEvidence=staticEligible&&evidenceCount===0&&['NO_MATCHING_ACTIVE_EVIDENCE','NO_AUTHORIZED_STATIC_SOURCE','NO_AUTHORIZED_EVIDENCE'].some(x=>reasonCode.includes(x));
const reasons=[];
if(noStaticEvidence)reasons.push('NO_STATIC_EVIDENCE');
if(route==='fallback'&&((confidence!==null&&confidence<0.60)||Boolean(j.classifier_error_code)))reasons.push('LOW_CONFIDENCE_FALLBACK');
if(route==='clarify'||c.ambiguous===true||(confidence!==null&&threshold!==null&&confidence<threshold))reasons.push('AMBIGUOUS_OR_BELOW_THRESHOLD');
if(route==='fallback')reasons.push('FALLBACK_USED');
const human=primary==='human_handoff'||secondary==='human_handoff'||j.wu95_handoff_contract?.requested===true||state.support?.handoff_requested===true;
if(human)reasons.push('HUMAN_REQUESTED');
const outOfScope=primary==='out_of_scope'||secondary==='out_of_scope';
if(outOfScope)reasons.push('OUT_OF_SCOPE');
const triggerReasons=[...new Set(reasons)];
const queueRequired=triggerReasons.length>0;
const queueKey=String(analytics.session_key||'');
const identityAvailable=/^conv-[A-Za-z0-9._:-]{12,160}$/.test(queueKey);
const turn=Math.max(1,Math.floor(Number(analytics.turn_index||1))||1);
const queueEventId=identityAvailable?`uq-${queueKey.slice(5)}-${turn}`:null;
function lang(v){const s=String(v||'').toLowerCase();if(s.startsWith('ar'))return'ar';if(s.startsWith('fr'))return'fr';if(s.startsWith('en'))return'en';return'unknown';}
function escRe(s){return String(s).replace(/[.*+?^${}()|[\]\\]/g,'\\$&');}
function safeToken(v){return String(v||'PII').toUpperCase().replace(/[^A-Z0-9_]/g,'_').slice(0,40)||'PII';}
const raw=String(j.message?.raw||'').slice(0,4000);
let redacted=raw
 .replace(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/ig,'[REDACTED_EMAIL]')
 .replace(/\+?\d[\d\s().-]{6,}\d/g,'[REDACTED_PHONE]');
const ex=j.entity_extraction||{};
const guard=j.entity_guard||{};
const piiNames=new Set(['parent_name','student_name','phone','email','contact','transaction_reference','lesson_id','booking_id','lead_id']);
const values=[];
for(const r of (Array.isArray(ex.records)?ex.records:[])){
 if(!r||typeof r!=='object')continue;
 const sensitive=['High','Medium','Sensitive preference'].includes(String(r.sensitivity||''))||piiNames.has(String(r.entity||''));
 if(!sensitive)continue;
 for(const v of [r.raw,r.canonical]){
  const s=String(v||'').trim();
  if(s.length>=2)values.push({value:s,entity:safeToken(r.entity)});
 }
}
for(const sp of (Array.isArray(ex.student_profiles)?ex.student_profiles:[])){
 const s=String(sp?.student_name||'').trim();
 if(s.length>=2)values.push({value:s,entity:'STUDENT_NAME'});
}
values.sort((a,b)=>b.value.length-a.value.length);
for(const x of values){redacted=redacted.replace(new RegExp(escRe(x.value),'ig'),`[REDACTED_${x.entity}]`);}
let unresolved=false;
for(const x of values){if(redacted.toLowerCase().includes(x.value.toLowerCase())){unresolved=true;break;}}
if(guard.pii_present===true&&values.length===0)unresolved=true;
let captureStatus=unresolved?'WITHHELD_PII_RISK':'STORED_REDACTED';
let redactedQuestion=unresolved?null:redacted.slice(0,1500);
let kbMatchStatus='UNKNOWN';
if(evidenceCount>0)kbMatchStatus='MATCHED';
else if(noStaticEvidence)kbMatchStatus='NO_STATIC_EVIDENCE';
else if(liveRequired)kbMatchStatus='NOT_APPLICABLE_LIVE_REQUIRED';
const queueWriteAllowed=Boolean(queueRequired&&identityAvailable);
const event=queueWriteAllowed?{
 event_schema:'SPM_WU102_UNANSWERED_QUESTION_V1',queue_event_id:queueEventId,event_timestamp:new Date().toISOString(),workflow_release:'WU102_STAGING_UNANSWERED_V1',channel:j.channel==='website_chat'?'website_chat':'unknown',queue_session_key:queueKey,turn_index:turn,
 redacted_question:redactedQuestion,question_capture_status:captureStatus,language:lang(c.language||j.language_hint),dialect_hint:'unknown',predicted_intent:primary,secondary_intent:secondary,confidence,kb_match_status:kbMatchStatus,fallback_used:route==='fallback',clarification_used:j.customer_clarification_required===true||route==='clarify',human_requested:Boolean(human),out_of_scope:Boolean(outOfScope),trigger_reasons:triggerReasons,
 resolution_status:'OPEN',approved_answer_status:'NOT_REVIEWED',added_to_kb_status:'NOT_ADDED',pii_redacted:true,raw_message_logged:false,raw_session_logged:false,secret_values_logged:false
}:null;
const decision={schema:'SPM_WU102_QUEUE_DECISION_V1',queue_required:queueRequired,queue_write_allowed:queueWriteAllowed,identity_available:identityAvailable,trigger_reasons:triggerReasons,kb_match_status:kbMatchStatus,question_capture_status:captureStatus,status:!queueRequired?'NOT_REQUIRED':(!identityAvailable?'SKIPPED_IDENTITY_UNAVAILABLE':'READY_TO_WRITE'),error_code:queueRequired&&!identityAvailable?'WU102_QUEUE_IDENTITY_UNAVAILABLE':null};
return [{json:{...j,wu102_queue_decision:decision,wu102_queue_event:event}}];"""
    builder = {
        'id': '10200000-0000-4000-8000-000000000101',
        'name': builder_name,
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': [-78256, 5536],
        'parameters': {'jsCode': builder_js},
    }

    gate_name = 'Is WU102 Queue Write Required?'
    gate = {
        'id': '10200000-0000-4000-8000-000000000102',
        'name': gate_name,
        'type': 'n8n-nodes-base.if',
        'typeVersion': 2.2,
        'position': [-78016, 5536],
        'parameters': {
            'conditions': {
                'options': {'caseSensitive': True, 'leftValue': '', 'typeValidation': 'strict', 'version': 3},
                'conditions': [{
                    'id': '10200000-0000-4000-8000-000000000202',
                    'leftValue': '={{ $json.wu102_queue_decision.queue_write_allowed }}',
                    'rightValue': True,
                    'operator': {'type': 'boolean', 'operation': 'true', 'singleValue': True},
                }],
                'combinator': 'and',
            },
            'options': {},
        },
    }

    schema = []
    for field in FIELDS:
        if field in NUMERIC_FIELDS:
            typ = 'number'
        elif field in BOOLEAN_FIELDS:
            typ = 'string'
        else:
            typ = 'string'
        schema.append({'id': field, 'displayName': field, 'required': False, 'defaultMatch': False, 'display': True, 'type': typ, 'canBeUsedToMatch': True})

    values = {}
    for field in FIELDS:
        if field == 'trigger_reasons':
            values[field] = '={{ JSON.stringify($json.wu102_queue_event.trigger_reasons || []) }}'
        elif field in BOOLEAN_FIELDS:
            values[field] = bool_expr(field)
        elif field == 'turn_index':
            values[field] = '={{ Number($json.wu102_queue_event.turn_index ?? 1) }}'
        elif field == 'confidence':
            values[field] = '={{ $json.wu102_queue_event.confidence == null ? null : Number($json.wu102_queue_event.confidence) }}'
        elif field == 'redacted_question':
            values[field] = "={{ /^[=+\\-@]/.test(String($json.wu102_queue_event.redacted_question ?? '')) ? \"'\" + String($json.wu102_queue_event.redacted_question ?? '') : String($json.wu102_queue_event.redacted_question ?? '') }}"
        else:
            values[field] = expr(field)

    logger_name = 'Upsert WU102 Unanswered [STAGING]'
    logger = {
        'id': '10200000-0000-4000-8000-000000000103',
        'name': logger_name,
        'type': 'n8n-nodes-base.googleSheets',
        'typeVersion': 4.7,
        'position': [-77776, 5424],
        'parameters': {
            'operation': 'appendOrUpdate',
            'documentId': doc_ref(),
            'sheetName': sheet_ref(),
            'columns': {
                'mappingMode': 'defineBelow',
                'value': values,
                'matchingColumns': ['queue_event_id'],
                'schema': schema,
                'attemptToConvertTypes': True,
                'convertFieldsToString': False,
            },
            'options': {},
        },
        'credentials': copy.deepcopy(GOOGLE_CRED),
        'onError': 'continueRegularOutput',
    }

    restore_name = 'Restore Customer Context After WU102 Queue'
    restore_js = r"""const base=$('Build WU102 Unanswered Queue Decision').first().json||{};
const cur=$input.first().json||{};
const d=base.wu102_queue_decision||{};
const failed=Boolean(cur.error||cur.description||cur.errorMessage);
let status='NOT_REQUIRED';
let success=false;
if(d.queue_required===true&&d.identity_available!==true)status='SKIPPED_IDENTITY_UNAVAILABLE';
else if(d.queue_write_allowed===true){status=failed?'FAILED_FAIL_OPEN':'UPSERTED';success=!failed;}
const result={schema:'SPM_WU102_QUEUE_WRITE_V1',status,success,fail_open:true,queue_event_id:base.wu102_queue_event?.queue_event_id||null,trigger_reasons:Array.isArray(d.trigger_reasons)?d.trigger_reasons:[],error_code:d.error_code||null};
return [{json:{...base,wu102_queue_write:result}}];"""
    restore = {
        'id': '10200000-0000-4000-8000-000000000104',
        'name': restore_name,
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': [-77536, 5536],
        'parameters': {'jsCode': restore_js},
    }

    wf['nodes'].extend([builder, gate, logger, restore])

    upstream = 'Restore Customer Context After WU101 Analytics'
    save = 'Save AI Message to Chat History'
    existing = wf['connections'].get(upstream, {}).get('main', [])
    if existing != [[{'node': save, 'type': 'main', 'index': 0}]]:
        raise RuntimeError(f'unexpected WU101 restore connection: {existing!r}')

    wf['connections'][upstream] = {'main': [[{'node': builder_name, 'type': 'main', 'index': 0}]]}
    wf['connections'][builder_name] = {'main': [[{'node': gate_name, 'type': 'main', 'index': 0}]]}
    wf['connections'][gate_name] = {
        'main': [
            [{'node': logger_name, 'type': 'main', 'index': 0}],
            [{'node': restore_name, 'type': 'main', 'index': 0}],
        ]
    }
    wf['connections'][logger_name] = {'main': [[{'node': restore_name, 'type': 'main', 'index': 0}]]}
    wf['connections'][restore_name] = {'main': [[{'node': save, 'type': 'main', 'index': 0}]]}

    node_by_name(wf, save)['position'] = [-77296, 5536]
    node_by_name(wf, 'Restore Final Response Payload')['position'] = [-77056, 5536]
    node_by_name(wf, 'RC3 Chat Response')['position'] = [-76816, 5536]
    return wf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--baseline', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    wf = build(args.baseline)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(wf, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({
        'output': args.output,
        'sha256': sha256(args.output),
        'node_count': len(wf['nodes']),
        'connection_sources': len(wf['connections']),
        'queue_sheet': QUEUE_SHEET_NAME,
        'queue_sheet_id': QUEUE_SHEET_ID,
        'workflow_active': wf.get('active'),
    }, indent=2))


if __name__ == '__main__':
    main()
