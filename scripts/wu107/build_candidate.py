#!/usr/bin/env python3
import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path

EXPECTED_WU106_SHA256 = "2e219adbdd612106b782993cbcb2f94da6c0737b250264060b473f12f0fcc81f"
EXPECTED_WU106_NODE_COUNT = 141
UPSTREAM_GATEWAY = "Deterministic Action Gateway [RC3 SCOPE LOCK]"
UPSTREAM_TELEMETRY = "Build Telemetry Envelope"
REDIS_REFERENCE = "Load Sales State [STAGING NAMESPACE]"

N_BUILD = "Build WU107 Handoff Execution Request [STAGING]"
N_IF = "Is WU107 Handoff Execution Required?"
N_LOAD = "Load WU107 Handoff Record [STAGING]"
N_DECIDE = "Build WU107 Queue Decision"
N_WRITE_IF = "Is WU107 Queue Write Required?"
N_SAVE = "Save WU107 Handoff Record [STAGING]"
N_SUCCESS = "Apply WU107 Verified Queue Result"
N_EXISTING = "Apply WU107 Existing Handoff Result"
N_LOAD_FAIL = "Build WU107 Handoff Load Failure Context"
N_SAVE_FAIL = "Build WU107 Handoff Save Failure Context"

NEW_NAMES = {
    N_BUILD, N_IF, N_LOAD, N_DECIDE, N_WRITE_IF,
    N_SAVE, N_SUCCESS, N_EXISTING, N_LOAD_FAIL, N_SAVE_FAIL,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def code_node(name, code, position, node_id, notes):
    return {
        "parameters": {"jsCode": code},
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": position,
        "id": node_id,
        "name": name,
        "notesInFlow": True,
        "notes": notes,
    }


def if_node(name, expression, position, node_id):
    return {
        "parameters": {
            "conditions": {
                "options": {
                    "caseSensitive": True,
                    "leftValue": "",
                    "typeValidation": "strict",
                    "version": 3,
                },
                "conditions": [{
                    "id": node_id + "-condition",
                    "leftValue": expression,
                    "rightValue": True,
                    "operator": {
                        "type": "boolean",
                        "operation": "true",
                        "singleValue": True,
                    },
                }],
                "combinator": "and",
            },
            "options": {},
        },
        "type": "n8n-nodes-base.if",
        "typeVersion": 2.2,
        "position": position,
        "id": node_id,
        "name": name,
    }


def redis_get_node(credentials, position):
    return {
        "parameters": {
            "operation": "get",
            "propertyName": "wu107_handoff_raw",
            "key": "={{ $json.wu107_queue_key }}",
            "options": {},
        },
        "type": "n8n-nodes-base.redis",
        "typeVersion": 1,
        "position": position,
        "id": "wu107-load-handoff-record-v1",
        "name": N_LOAD,
        "retryOnFail": True,
        "maxTries": 3,
        "waitBetweenTries": 500,
        "onError": "continueErrorOutput",
        "credentials": deepcopy(credentials),
        "notesInFlow": True,
        "notes": "WU-107 STAGING-only read from isolated handoff namespace. No Production key or raw chat/session payload is written.",
    }


def redis_set_node(credentials, position):
    return {
        "parameters": {
            "operation": "set",
            "key": "={{ $json.wu107_queue_key }}",
            "value": "={{ $json.wu107_queue_record_text }}",
            "expire": True,
            "ttl": 2592000,
        },
        "type": "n8n-nodes-base.redis",
        "typeVersion": 1,
        "position": position,
        "id": "wu107-save-handoff-record-v1",
        "name": N_SAVE,
        "retryOnFail": True,
        "maxTries": 3,
        "waitBetweenTries": 500,
        "onError": "continueErrorOutput",
        "credentials": deepcopy(credentials),
        "notesInFlow": True,
        "notes": "A successful atomic Redis SET is the WU-107 queue receipt. It proves QUEUED only, never human ACCEPTED.",
    }


BUILD_CODE = r"""const j=$input.first().json||{};
const c=j.classification||{};
const state=j.sales_state||{};
const g=state.entities?.global||{};
const students=Array.isArray(state.entities?.students)?state.entities.students:[];
const analytics=state.analytics||{};
const primary=String(c.spm_intent||'');
const secondary=String(c.secondary_spm_intent||'');
const current=new Set([primary,secondary].filter(Boolean));
const supported=new Set(['human_handoff','technical_support','complaint','account_update','contact_update']);
let matched='';
for(const x of current){if(supported.has(x)){matched=x;break;}}
const requested=Boolean(matched);
let reason='OTHER_APPROVED_HANDOFF';
if(matched==='human_handoff')reason='EXPLICIT_HUMAN_REQUEST';
else if(matched==='technical_support')reason='TECHNICAL_SUPPORT';
else if(matched==='complaint')reason='COMPLAINT_ESCALATION';
else if(['account_update','contact_update'].includes(matched))reason='ACCOUNT_OR_CONTACT_SENSITIVE_CHANGE';
const sessionKey=String(analytics.session_key||'');
const identityAvailable=/^conv-[A-Za-z0-9._:-]{12,160}$/.test(sessionKey);
const langRaw=String(c.language||j.language_hint||'en').toLowerCase();
const lang=langRaw.startsWith('ar')?'ar':(langRaw.startsWith('fr')?'fr':'en');
const stage=String(j.journey_decision?.stage||state.journey?.stage||'unknown').slice(0,80);
const priority=['technical_support','complaint','account_update','contact_update'].includes(matched)?'HIGH':'NORMAL';
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
 support_context_flags:{support_override:Boolean(state.support?.active_override),handoff_requested:Boolean(state.support?.handoff_requested)},
 pii_policy_version:'WU107_MINIMAL_V1',
 raw_message_logged:false,
 raw_session_logged:false,
 raw_contact_logged:false,
 secret_values_logged:false,
 production_mutation_allowed:false
};
return [{json:{...j,wu107_handoff_request:request,wu107_queue_key:request.queue_key}}];"""

DECIDE_CODE = r"""const base=$('Build WU107 Handoff Execution Request [STAGING]').first().json||{};
const cur=$input.first().json||{};
const req=base.wu107_handoff_request||{};
const raw=String(cur.wu107_handoff_raw||'').trim();
let existing=null;
let parseError=false;
if(raw){try{existing=JSON.parse(raw);}catch(e){parseError=true;}}
const validExisting=Boolean(existing&&existing.handoff_schema==='SPM_WU107_HANDOFF_RECORD_V1'&&existing.handoff_session_key===req.handoff_session_key);
let writeRequired=false;
let decision='NO_EXISTING_RECORD';
let generation=1;
if(parseError||(existing&&!validExisting)){
 decision='CORRUPT_EXISTING_FAIL_CLOSED';
}else if(validExisting){
 generation=Math.max(1,Math.floor(Number(existing.generation||1))||1);
 const s=String(existing.handoff_state||'');
 if(['QUEUED','ACCEPTED'].includes(s))decision=`EXISTING_${s}`;
 else if(['FAILED','CANCELLED'].includes(s)){generation+=1;writeRequired=true;decision='REOPEN_TERMINAL_RECORD';}
 else if(s==='REQUESTED'){writeRequired=true;decision='RECOVER_REQUESTED_RECORD';}
 else decision='CORRUPT_EXISTING_FAIL_CLOSED';
}else{
 writeRequired=true;
}
const now=new Date().toISOString();
const eventId=`ho-${String(req.handoff_session_key||'').slice(5)}-g${generation}`;
const idempotencyKey=`wu107:${String(req.handoff_session_key||'')}:g${generation}`;
const record={
 handoff_schema:'SPM_WU107_HANDOFF_RECORD_V1',
 handoff_event_id:eventId,
 created_at:(validExisting&&existing.created_at&&generation===Number(existing.generation||1))?existing.created_at:now,
 queued_at:now,
 workflow_release:'WU107_STAGING_HANDOFF_V1',
 channel:req.channel,
 handoff_session_key:req.handoff_session_key,
 correlation_id:req.correlation_id,
 reason_code:req.reason_code,
 source_intent:req.source_intent,
 source_stage:req.source_stage,
 priority:req.priority,
 requested_language:req.requested_language,
 customer_context_summary:req.customer_context_summary,
 support_context_flags:req.support_context_flags,
 handoff_state:'QUEUED',
 attempt_count:1,
 generation,
 idempotency_key:idempotencyKey,
 downstream_receipt_present:true,
 downstream_acceptance_present:false,
 accepted_at:null,
 queue_provider:'STAGING_REDIS',
 pii_policy_version:req.pii_policy_version,
 raw_message_logged:false,
 raw_session_logged:false,
 raw_contact_logged:false,
 secret_values_logged:false
};
const d={schema:'SPM_WU107_QUEUE_DECISION_V1',write_required:Boolean(writeRequired&&!parseError),decision,existing_state:validExisting?String(existing.handoff_state||null):null,existing_record:validExisting?existing:null,record_candidate:record};
return [{json:{...base,wu107_queue_decision:d,wu107_queue_record_text:JSON.stringify(record)}}];"""

SUCCESS_CODE = r"""const base=$('Build WU107 Queue Decision').first().json||{};
const d=base.wu107_queue_decision||{};
const r=d.record_candidate||{};
const o={...(base.sales_agent_output||{})};
const lang=String(base.wu107_handoff_request?.requested_language||'en');
if(lang==='ar')o.answer_text='تم وضع طلبك في قائمة دعم موثقة. لم يتم بعد تأكيد استلامه من موظف محدد.';
else if(lang==='fr')o.answer_text='Votre demande a été placée dans notre file d’assistance. Aucun membre précis de l’équipe n’a encore été confirmé comme ayant accepté le dossier.';
else o.answer_text='Your request has been placed in our support queue. A specific team member has not yet been confirmed as having accepted the case.';
o.purposeful_question=null;
o.proposed_action='human_handoff_create';
o.action_requires_gateway=true;
const result={schema:'SPM_WU107_HANDOFF_EXECUTION_RESULT_V1',handoff_state:'QUEUED',tool_executed:true,success:true,idempotency_key:r.idempotency_key||null,handoff_event_id:r.handoff_event_id||null,queue_receipt_verified:true,human_acceptance_verified:false,provider:'STAGING_REDIS',reason_code:'WU107_VERIFIED_QUEUE_WRITE'};
const action={...(base.action_result||{}),requested_action:'human_handoff_create',executed:true,status:'WU107_HANDOFF_QUEUED',business_reference:r.handoff_event_id||null,reason_code:'WU107_VERIFIED_QUEUE_WRITE',irreversible_action:true,fail_closed:false};
return [{json:{...base,sales_agent_output:o,action_result:action,wu107_handoff_execution:result}}];"""

EXISTING_CODE = r"""const j=$input.first().json||{};
const d=j.wu107_queue_decision||{};
const r=d.existing_record||{};
const o={...(j.sales_agent_output||{})};
const lang=String(j.wu107_handoff_request?.requested_language||'en');
const state=String(r.handoff_state||'FAILED');
const accepted=state==='ACCEPTED'&&r.downstream_acceptance_present===true;
if(accepted){
 if(lang==='ar')o.answer_text='تم تأكيد قبول طلب الدعم من جهة بشرية مخولة.';
 else if(lang==='fr')o.answer_text='L’acceptation de votre demande d’assistance par une personne autorisée a été confirmée.';
 else o.answer_text='An authorized human acceptance of your support request has been verified.';
}else if(state==='QUEUED'){
 if(lang==='ar')o.answer_text='طلبك موجود بالفعل في قائمة الدعم. لم يتم بعد تأكيد استلامه من موظف محدد.';
 else if(lang==='fr')o.answer_text='Votre demande est déjà dans la file d’assistance. Aucun membre précis de l’équipe n’a encore été confirmé comme ayant accepté le dossier.';
 else o.answer_text='Your request is already in the support queue. A specific team member has not yet been confirmed as having accepted the case.';
}else{
 if(lang==='ar')o.answer_text='تم حفظ طلبك، لكن لا أستطيع تأكيد وضعه في قائمة الدعم الآن.';
 else if(lang==='fr')o.answer_text='Votre demande est préservée, mais je ne peux pas confirmer sa mise en file d’assistance pour le moment.';
 else o.answer_text='Your request is preserved, but I cannot confirm that it is in the support queue right now.';
}
o.purposeful_question=null;
const result={schema:'SPM_WU107_HANDOFF_EXECUTION_RESULT_V1',handoff_state:accepted?'ACCEPTED':state,tool_executed:false,success:['QUEUED','ACCEPTED'].includes(state),idempotency_key:r.idempotency_key||null,handoff_event_id:r.handoff_event_id||null,queue_receipt_verified:Boolean(r.downstream_receipt_present),human_acceptance_verified:Boolean(accepted),provider:r.queue_provider||'STAGING_REDIS',reason_code:`WU107_${d.decision||'EXISTING_STATE'}`};
const action={...(j.action_result||{}),requested_action:'human_handoff_create',executed:false,status:accepted?'WU107_HANDOFF_ALREADY_ACCEPTED':(state==='QUEUED'?'WU107_HANDOFF_ALREADY_QUEUED':'WU107_HANDOFF_NOT_CONFIRMED'),business_reference:r.handoff_event_id||null,reason_code:result.reason_code,irreversible_action:true,fail_closed:!['QUEUED','ACCEPTED'].includes(state)};
return [{json:{...j,sales_agent_output:o,action_result:action,wu107_handoff_execution:result}}];"""

LOAD_FAIL_CODE = r"""const base=$('Build WU107 Handoff Execution Request [STAGING]').first().json||{};
const cur=$input.first().json||{};
const o={...(base.sales_agent_output||{})};
const lang=String(base.wu107_handoff_request?.requested_language||'en');
if(lang==='ar')o.answer_text='تم حفظ طلبك في سياق المحادثة، لكن تعذر التحقق من قائمة الدعم الآن. لن أدعي أن التحويل تم.';
else if(lang==='fr')o.answer_text='Votre demande reste préservée dans le contexte de la conversation, mais la file d’assistance ne peut pas être vérifiée maintenant. Je ne prétendrai pas que le transfert a réussi.';
else o.answer_text='Your request remains preserved in the conversation context, but I could not verify the support queue right now. I will not claim that the handoff succeeded.';
const health={...(base.wu97_runtime_health||{})};
const codes=[...(Array.isArray(health.error_codes)?health.error_codes:[])];if(!codes.includes('WU107_HANDOFF_QUEUE_LOAD_FAILED'))codes.push('WU107_HANDOFF_QUEUE_LOAD_FAILED');
health.error_codes=codes;health.degraded=true;
const action={...(base.action_result||{}),requested_action:'human_handoff_create',executed:false,status:'WU107_HANDOFF_QUEUE_FAILED',reason_code:'WU107_QUEUE_LOAD_FAILED',fail_closed:true};
return [{json:{...base,sales_agent_output:o,action_result:action,wu97_runtime_health:health,wu107_handoff_execution:{schema:'SPM_WU107_HANDOFF_EXECUTION_RESULT_V1',handoff_state:'REQUESTED',tool_executed:true,success:false,queue_receipt_verified:false,human_acceptance_verified:false,reason_code:'WU107_QUEUE_LOAD_FAILED',error_present:Boolean(cur.error||cur.errorMessage||cur.description)}}}];"""

SAVE_FAIL_CODE = r"""const base=$('Build WU107 Queue Decision').first().json||{};
const cur=$input.first().json||{};
const o={...(base.sales_agent_output||{})};
const lang=String(base.wu107_handoff_request?.requested_language||'en');
if(lang==='ar')o.answer_text='تم حفظ طلبك في سياق المحادثة، لكن تعذر وضعه في قائمة الدعم الآن. لن أدعي أن التحويل تم.';
else if(lang==='fr')o.answer_text='Votre demande reste préservée dans le contexte de la conversation, mais elle n’a pas pu être placée dans la file d’assistance maintenant. Je ne prétendrai pas que le transfert a réussi.';
else o.answer_text='Your request remains preserved in the conversation context, but I could not place it in the support queue right now. I will not claim that the handoff succeeded.';
const health={...(base.wu97_runtime_health||{})};
const codes=[...(Array.isArray(health.error_codes)?health.error_codes:[])];if(!codes.includes('WU107_HANDOFF_QUEUE_SAVE_FAILED'))codes.push('WU107_HANDOFF_QUEUE_SAVE_FAILED');
health.error_codes=codes;health.degraded=true;
const action={...(base.action_result||{}),requested_action:'human_handoff_create',executed:false,status:'WU107_HANDOFF_QUEUE_FAILED',reason_code:'WU107_QUEUE_SAVE_FAILED',fail_closed:true};
return [{json:{...base,sales_agent_output:o,action_result:action,wu97_runtime_health:health,wu107_handoff_execution:{schema:'SPM_WU107_HANDOFF_EXECUTION_RESULT_V1',handoff_state:'REQUESTED',tool_executed:true,success:false,queue_receipt_verified:false,human_acceptance_verified:false,reason_code:'WU107_QUEUE_SAVE_FAILED',error_present:Boolean(cur.error||cur.errorMessage||cur.description)}}}];"""


def build(baseline: Path, output: Path):
    actual = sha256(baseline)
    if actual != EXPECTED_WU106_SHA256:
        raise SystemExit(f"WU-107 refuses non-locked WU-106 baseline SHA: {actual}")
    workflow = json.loads(baseline.read_text(encoding="utf-8"))
    if len(workflow.get("nodes", [])) != EXPECTED_WU106_NODE_COUNT:
        raise SystemExit("WU-107 locked WU-106 node count mismatch")

    candidate = deepcopy(workflow)
    candidate["name"] = "[STAGING] SPM_WU107_HUMAN_HANDOFF_EXECUTION_V1"
    candidate["active"] = False

    nodes = candidate.get("nodes", [])
    names = [n.get("name") for n in nodes]
    if NEW_NAMES.intersection(names):
        raise SystemExit("WU-107 nodes already present")
    for required in [UPSTREAM_GATEWAY, UPSTREAM_TELEMETRY, REDIS_REFERENCE]:
        if names.count(required) != 1:
            raise SystemExit(f"WU-107 required upstream identity mismatch: {required}")

    gate = next(n for n in nodes if n.get("name") == UPSTREAM_GATEWAY)
    redis_ref = next(n for n in nodes if n.get("name") == REDIS_REFERENCE)
    redis_creds = redis_ref.get("credentials", {}).get("redis")
    if not redis_creds:
        raise SystemExit("WU-107 cannot find certified STAGING Redis credential")
    credentials = {"redis": deepcopy(redis_creds)}
    x, y = gate.get("position", [0, 0])

    new_nodes = [
        code_node(N_BUILD, BUILD_CODE, [x + 160, y], "wu107-build-handoff-request-v1", "Builds a PII-minimized current-turn handoff request using the existing pseudonymous conversation key. No execution truth is created here."),
        if_node(N_IF, "={{ $json.wu107_handoff_request.execution_required === true }}", [x + 360, y], "wu107-if-execution-required-v1"),
        redis_get_node(credentials, [x + 560, y - 120]),
        code_node(N_DECIDE, DECIDE_CODE, [x + 760, y - 120], "wu107-build-queue-decision-v1", "Deterministically separates absent/existing/corrupt records and constructs one idempotent PII-minimized queue record."),
        if_node(N_WRITE_IF, "={{ $json.wu107_queue_decision.write_required === true }}", [x + 960, y - 120], "wu107-if-queue-write-v1"),
        redis_set_node(credentials, [x + 1160, y - 220]),
        code_node(N_SUCCESS, SUCCESS_CODE, [x + 1360, y - 220], "wu107-verified-queue-result-v1", "Only a successful Redis SET may create QUEUED customer-facing truth. Human ACCEPTED remains false."),
        code_node(N_EXISTING, EXISTING_CODE, [x + 1160, y + 20], "wu107-existing-handoff-result-v1", "Reuses already verified queue/acceptance truth without creating a duplicate case or action."),
        code_node(N_LOAD_FAIL, LOAD_FAIL_CODE, [x + 760, y + 140], "wu107-load-failure-context-v1", "Fail-closed load behavior: preserves request but never claims queue or human acceptance."),
        code_node(N_SAVE_FAIL, SAVE_FAIL_CODE, [x + 1360, y - 60], "wu107-save-failure-context-v1", "Fail-closed save behavior: preserves request but never claims queue or human acceptance."),
    ]
    nodes.extend(new_nodes)

    connections = candidate.setdefault("connections", {})
    original = deepcopy(connections.get(UPSTREAM_GATEWAY))
    if not original or len(original.get("main", [])) != 1 or len(original["main"][0]) != 1 or original["main"][0][0].get("node") != UPSTREAM_TELEMETRY:
        raise SystemExit("WU-107 unexpected locked gateway-to-telemetry topology")
    telemetry_target = deepcopy(original["main"][0][0])
    connections[UPSTREAM_GATEWAY] = {**original, "main": [[{"node": N_BUILD, "type": "main", "index": 0}]]}
    connections[N_BUILD] = {"main": [[{"node": N_IF, "type": "main", "index": 0}]]}
    connections[N_IF] = {"main": [
        [{"node": N_LOAD, "type": "main", "index": 0}],
        [deepcopy(telemetry_target)],
    ]}
    connections[N_LOAD] = {"main": [
        [{"node": N_DECIDE, "type": "main", "index": 0}],
        [{"node": N_LOAD_FAIL, "type": "main", "index": 0}],
    ]}
    connections[N_DECIDE] = {"main": [[{"node": N_WRITE_IF, "type": "main", "index": 0}]]}
    connections[N_WRITE_IF] = {"main": [
        [{"node": N_SAVE, "type": "main", "index": 0}],
        [{"node": N_EXISTING, "type": "main", "index": 0}],
    ]}
    connections[N_SAVE] = {"main": [
        [{"node": N_SUCCESS, "type": "main", "index": 0}],
        [{"node": N_SAVE_FAIL, "type": "main", "index": 0}],
    ]}
    connections[N_SUCCESS] = {"main": [[deepcopy(telemetry_target)]]}
    connections[N_EXISTING] = {"main": [[deepcopy(telemetry_target)]]}
    connections[N_LOAD_FAIL] = {"main": [[deepcopy(telemetry_target)]]}
    connections[N_SAVE_FAIL] = {"main": [[deepcopy(telemetry_target)]]}

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"WU107_INPUT_WU106_SHA256={actual}")
    print(f"WU107_CANDIDATE={output}")
    print(f"WU107_CANDIDATE_SHA256={sha256(output)}")
    print(f"WU107_NODE_COUNT={len(nodes)}")
    print("WU107_PROVIDER=STAGING_REDIS_QUEUE")
    print("WU107_PRODUCTION_MUTATION_ALLOWED=false")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--baseline", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    build(a.baseline, a.output)


if __name__ == "__main__":
    main()
