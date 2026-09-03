#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_INPUT_SHA256 = "fc4263b6bf029195a58b819ce4b06d6f499090d39017ff6ca906f173b7443f59"
EXPECTED_NODE_COUNT = 151
TARGET = "Build WU107 Handoff Execution Request [STAGING]"

BUILD_CODE_CR10701 = r"""const j=$input.first().json||{};
const c=j.classification||{};
const state=j.sales_state||{};
const g=state.entities?.global||{};
const students=Array.isArray(state.entities?.students)?state.entities.students:[];
const analytics=state.analytics||{};
const comm=(j.wu96_communication_decision&&typeof j.wu96_communication_decision==='object')?j.wu96_communication_decision:{};
const commCtx=(j.wu96_communication_context&&typeof j.wu96_communication_context==='object')?j.wu96_communication_context:{};
const orch=(j.wu106_orchestration&&typeof j.wu106_orchestration==='object')?j.wu106_orchestration:{};
const primary=String(c.spm_intent||'');
const secondary=String(c.secondary_spm_intent||'');
const approvedSupport=new Set([
 'human_handoff','complaint','technical_issue','technical_support',
 'account_login','update_contact_info','account_update','contact_update',
 'payment_problem','change_teacher'
]);
const currentTurnWU96=Boolean(
 comm.mode==='support' &&
 comm.support_requires_handoff===true &&
 comm.reason==='CURRENT_SUPPORT_INTENT_OVERRIDES_SALES'
);
const currentTurnWU106=Boolean(orch.support_override_active===true);
const supportCandidates=[
 primary,secondary,
 String(comm.intent||''),String(comm.secondary_intent||''),
 String(commCtx.support_intent||''),String(orch.active_objective_intent||'')
].filter(Boolean);
let matched='';
for(const x of [primary,secondary]){if(approvedSupport.has(x)){matched=x;break;}}
if(!matched && (currentTurnWU96||currentTurnWU106)){
 for(const x of supportCandidates){if(approvedSupport.has(x)){matched=x;break;}}
}
// Sticky historical support state is evidence for context only. It cannot initiate a new handoff turn by itself.
const requested=Boolean(matched);
let reason='OTHER_APPROVED_HANDOFF';
if(matched==='human_handoff')reason='EXPLICIT_HUMAN_REQUEST';
else if(['technical_issue','technical_support'].includes(matched))reason='TECHNICAL_SUPPORT';
else if(matched==='complaint')reason='COMPLAINT_ESCALATION';
else if(['account_login','update_contact_info','account_update','contact_update'].includes(matched))reason='ACCOUNT_OR_CONTACT_SENSITIVE_CHANGE';
const sessionKey=String(analytics.session_key||'');
const identityAvailable=/^conv-[A-Za-z0-9._:-]{12,160}$/.test(sessionKey);
const langRaw=String(c.language||j.language_hint||'en').toLowerCase();
const lang=langRaw.startsWith('ar')?'ar':(langRaw.startsWith('fr')?'fr':'en');
const stage=String(j.journey_decision?.stage||state.journey?.stage||'unknown').slice(0,80);
const priority=['technical_issue','technical_support','complaint','account_login','update_contact_info','account_update','contact_update','payment_problem'].includes(matched)?'HIGH':'NORMAL';
const signalSource=(currentTurnWU96&&approvedSupport.has(matched))?'WU96_CURRENT_SUPPORT_DECISION':((currentTurnWU106&&approvedSupport.has(matched))?'WU106_CURRENT_SUPPORT_OVERRIDE':'CURRENT_CLASSIFICATION');
const request={
 schema:'SPM_WU107_HANDOFF_REQUEST_V1',
 requested,
 execution_required:Boolean(requested&&identityAvailable),
 execution_blocked_reason:requested&&!identityAvailable?'PSEUDONYMOUS_SESSION_KEY_UNAVAILABLE':null,
 handoff_session_key:identityAvailable?sessionKey:null,
 queue_key:identityAvailable?`spm:staging:handoff:${sessionKey}`:null,
 reason_code:reason,
 source_intent:matched||primary||null,
 source_stage:stage,
 priority,
 requested_language:lang,
 channel:j.channel==='website_chat'?'website_chat':'unknown',
 correlation_id:j.correlation_id||null,
 customer_context_summary:{
   journey_stage:stage,
   current_intent:matched||primary||null,
   known_contact:{phone_present:Boolean(g.phone||g.contact?.phone),email_present:Boolean(g.email||g.contact?.email)},
   student_count:students.length,
   academic_context_present:Boolean(students.some(s=>s&&(s.grade||s.subject))||g.grade||g.subject)
 },
 support_context_flags:{
   current_turn_wu96_support:currentTurnWU96,
   current_turn_wu106_support:currentTurnWU106,
   signal_source:signalSource,
   support_override:Boolean(state.support?.active_override),
   handoff_requested:Boolean(state.support?.handoff_requested)
 },
 pii_policy_version:'WU107_MINIMAL_V1',
 raw_message_logged:false,
 raw_session_logged:false,
 raw_contact_logged:false,
 secret_values_logged:false,
 production_mutation_allowed:false
};
return [{json:{...j,wu107_handoff_request:request,wu107_queue_key:request.queue_key}}];"""


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    a=p.parse_args()
    actual=digest(a.input)
    if actual!=EXPECTED_INPUT_SHA256:
        raise SystemExit(f'CR10701_INPUT_SHA_FAIL:{actual}')
    d=json.loads(a.input.read_text(encoding='utf-8'))
    if len(d.get('nodes',[]))!=EXPECTED_NODE_COUNT:
        raise SystemExit('CR10701_INPUT_NODE_COUNT_FAIL')
    matches=[n for n in d['nodes'] if n.get('name')==TARGET]
    if len(matches)!=1:
        raise SystemExit('CR10701_TARGET_IDENTITY_FAIL')
    node=matches[0]
    old=node.get('parameters',{}).get('jsCode','')
    required_old=[
        "const supported=new Set(['human_handoff','technical_support','complaint','account_update','contact_update']);",
        "const requested=Boolean(matched);",
        "support_override:Boolean(state.support?.active_override)"
    ]
    for marker in required_old:
        if marker not in old:
            raise SystemExit('CR10701_UNEXPECTED_INPUT_BUILD_CODE:'+marker)
    node['parameters']['jsCode']=BUILD_CODE_CR10701
    node['notes']='CR-107-01: current-turn support recovery consumes authoritative WU96/WU106 support metadata (including technical_issue) without using sticky support state alone. Queue truth still requires Redis evidence.'
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'CR10701_INPUT_SHA256={actual}')
    print(f'CR10701_OUTPUT_SHA256={digest(a.output)}')
    print(f'CR10701_NODE_COUNT={len(d["nodes"])}')
    print('CR10701_WU106_LOCKED_NODES_MUTATED=false')
    print('CR10701_PRODUCTION_MUTATION=false')

if __name__=='__main__': main()
