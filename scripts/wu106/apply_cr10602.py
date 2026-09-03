#!/usr/bin/env python3
import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path

EXPECTED_INPUT_SHA256 = "5db680c1e2b51d35408f78077ef4bb098da542bdf5e071125532948ad6783e2e"
EXPECTED_INPUT_NODE_COUNT = 133

INIT = "Initialize + Merge Sales State Contract"
CATALOG = "Load SPM V2 62 Intent Catalog"
CR10601 = "Apply WU106 Journey Transition Recovery [CR-106-01]"
SHORT_TRIAL = "Apply WU104 Short Trial Inquiry Guard"
PERSIST_FINAL = "Persist WU104 Final Asked Field"
SERIALIZE_WU95 = "Serialize WU95 STAGING Sales State"

LOAD_CTRL = "Load WU106 Registration Control [CR-106-02]"
MERGE_CTRL = "Merge WU106 Durable Registration Control [CR-106-02]"
ROOT_RECOVERY = "Apply WU106 Root Journey Recovery [CR-106-02]"
BUILD_CTRL = "Build WU106 Registration Control Snapshot [CR-106-02]"
SAVE_CTRL = "Save WU106 Registration Control [CR-106-02]"
RESTORE_CTRL = "Restore After WU106 Registration Control Save [CR-106-02]"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def code_node(name, node_id, position, js, notes):
    return {
        "parameters": {"jsCode": js},
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": position,
        "id": node_id,
        "name": name,
        "notesInFlow": True,
        "notes": notes,
    }


def one_target(conns, source):
    return deepcopy(conns.get(source, {}).get("main"))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()

    actual = sha256(a.input)
    if actual != EXPECTED_INPUT_SHA256:
        raise SystemExit(f"CR-106-02 refuses unexpected CR-106-01 SHA: {actual}")
    wf = json.loads(a.input.read_text(encoding="utf-8"))
    if len(wf.get("nodes", [])) != EXPECTED_INPUT_NODE_COUNT:
        raise SystemExit("CR-106-02 input node count mismatch")

    out = deepcopy(wf)
    names = [n.get("name") for n in out["nodes"]]
    required = [INIT, CATALOG, CR10601, SHORT_TRIAL, PERSIST_FINAL, SERIALIZE_WU95,
                "Load Sales State [STAGING NAMESPACE]", "Save WU95 Sales State [STAGING NAMESPACE]"]
    if any(names.count(x) != 1 for x in required):
        raise SystemExit("CR-106-02 required node identity mismatch")
    if any(x in names for x in [LOAD_CTRL, MERGE_CTRL, ROOT_RECOVERY, BUILD_CTRL, SAVE_CTRL, RESTORE_CTRL]):
        raise SystemExit("CR-106-02 node already exists")

    conns = out.setdefault("connections", {})
    if one_target(conns, INIT) != [[{"node": CATALOG, "type": "main", "index": 0}]]:
        raise SystemExit("CR-106-02 unexpected init topology")
    if one_target(conns, CR10601) != [[{"node": SHORT_TRIAL, "type": "main", "index": 0}]]:
        raise SystemExit("CR-106-02 unexpected CR-106-01 topology")
    if one_target(conns, PERSIST_FINAL) != [[{"node": SERIALIZE_WU95, "type": "main", "index": 0}]]:
        raise SystemExit("CR-106-02 unexpected WU95 persistence topology")

    by_name = {n["name"]: n for n in out["nodes"]}
    load_template = deepcopy(by_name["Load Sales State [STAGING NAMESPACE]"])
    save_template = deepcopy(by_name["Save WU95 Sales State [STAGING NAMESPACE]"])

    ix, iy = by_name[INIT]["position"]
    cx, cy = by_name[CR10601]["position"]
    px, py = by_name[PERSIST_FINAL]["position"]

    load_ctrl = load_template
    load_ctrl.update({
        "name": LOAD_CTRL,
        "id": "wu106-cr10602-load-registration-control-v1",
        "position": [ix + 160, iy - 160],
        "notes": "CR-106-02 loads a PII-free registration control snapshot from a dedicated STAGING Redis key. It does not load customer values.",
    })
    load_ctrl["parameters"] = {
        "operation": "get",
        "propertyName": "wu106_registration_control_raw",
        "key": "={{ 'spm:staging:regctrl:' + $json.session_id }}",
        "options": {},
    }

    merge_js = r"""const redisOut=$input.first().json||{};
const base=$('Initialize + Merge Sales State Contract').first().json||{};
const state=(base.sales_state&&typeof base.sales_state==='object')?JSON.parse(JSON.stringify(base.sales_state)):{};
state.conversion=(state.conversion&&typeof state.conversion==='object')?state.conversion:{};
let ctrl={};
try{const raw=redisOut.wu106_registration_control_raw;ctrl=typeof raw==='string'?JSON.parse(raw):(raw&&typeof raw==='object'?raw:{});}catch{ctrl={};}
const schemaOk=ctrl&&ctrl.schema==='SPM_WU106_REGISTRATION_CONTROL_V1';
const ctrlActive=Boolean(schemaOk&&ctrl.active===true&&ctrl.awaiting_field);
const current=state.conversion;
const currentActive=Boolean(current.registration_active===true||current.awaiting_field||['collecting','awaiting_confirmation','ready_to_write'].includes(String(current.registration_status||'')));
let applied=false;
if(ctrlActive&&!currentActive){
 current.registration_active=true;
 current.registration_status=String(ctrl.registration_status||'collecting');
 current.awaiting_field=String(ctrl.awaiting_field||'')||null;
 current.request_type=ctrl.request_type||current.request_type||null;
 current.pending_confirmation=Boolean(ctrl.pending_confirmation);
 state.journey=(state.journey&&typeof state.journey==='object')?state.journey:{};
 state.journey.awaiting_entity=current.awaiting_field;
 applied=true;
}
const ev={schema:'SPM_WU106_CR10602_CONTROL_MERGE_V1',control_present:Boolean(schemaOk),control_active:ctrlActive,current_active_before:currentActive,applied,awaiting_field:current.awaiting_field||null,pii_values_loaded:false,raw_message_logged:false,raw_session_logged:false,production_mutation_allowed:false};
return [{json:{...base,sales_state:state,wu106_cr10602_control_merge:ev}}];"""

    merge_ctrl = code_node(
        MERGE_CTRL,
        "wu106-cr10602-merge-registration-control-v1",
        [ix + 320, iy - 160],
        merge_js,
        "CR-106-02 merges only control metadata when the canonical sales_state lost an active registration continuation. Existing active canonical state always wins.",
    )

    root_js = r"""const j=$input.first().json||{};
const c=(j.classification&&typeof j.classification==='object')?{...j.classification}:{};
const state=(j.sales_state&&typeof j.sales_state==='object')?JSON.parse(JSON.stringify(j.sales_state)):{};
state.conversion=(state.conversion&&typeof state.conversion==='object')?state.conversion:{};
state.journey=(state.journey&&typeof state.journey==='object')?state.journey:{};
const d=(j.wu104_short_query_decision&&typeof j.wu104_short_query_decision==='object')?{...j.wu104_short_query_decision}:{};
const raw=String(j.message?.raw??'').normalize('NFKC').trim();
const norm=raw.toLowerCase().replace(/\s+/g,' ');
const awaited=String(state.conversion.awaiting_field||state.journey.awaiting_entity||'').trim().toLowerCase().replace(/[-\s]+/g,'_');
const registrationActive=Boolean(state.conversion.registration_active===true||awaited||['collecting','awaiting_confirmation','ready_to_write'].includes(String(state.conversion.registration_status||'')));
const words=(norm.match(/[\p{L}][\p{L}\p{M}'’.-]*/gu)||[]);
const stop=new Set(['yes','no','maybe','later','price','cost','available','availability','lesson','lessons','tutor','tutoring','register','registration','refund','human','agent','person','help','please','schedule','monday','tuesday','wednesday','thursday','friday','saturday','sunday','today','tomorrow','math','science','physics','chemistry','english','french','arabic']);
const nameLike=Boolean(raw.length>=2&&raw.length<=100&&words.length>=1&&words.length<=5&&!words.some(x=>stop.has(x.toLowerCase()))&&/^[\p{L}\p{M}'’ .-]+$/u.test(raw));
const digits=raw.replace(/\D/g,'');
const phoneLike=Boolean(digits.length>=8&&digits.length<=15&&/^[+()\d\s.\-]+$/.test(raw));
const emailLike=/^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/.test(raw);
const placeLike=Boolean(raw.length>=2&&raw.length<=100&&words.length>=1&&words.length<=5);
const tzLike=/^(?:UTC|GMT|[A-Za-z_]+(?:\/[A-Za-z0-9_+\-]+)+)$/.test(raw);
const langLike=/^(?:english|arabic|french|العربية|العربيه|الإنجليزية|الانجليزية|الفرنسية|الفرنسيه|anglais|arabe|français|francais)$/iu.test(norm);
const validators={parent_name:nameLike,student_name:nameLike,phone:phoneLike,email:emailLike,country:placeLike,city:placeLike,timezone:tzLike,preferred_language:langLike};
const validAwaited=Boolean(validators[awaited]);
const explicitAvailability=Boolean(/\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|today|tomorrow)\b.{0,36}\b(?:available|availability|open|slot|slots)\b|\b(?:available|availability|open|slot|slots)\b.{0,36}\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|today|tomorrow)\b/iu.test(norm)||/(?:السبت|الأحد|الاحد|الاثنين|الإثنين|الثلاثاء|الأربعاء|الاربعاء|الخميس|الجمعة|اليوم|غدا|غداً).{0,30}(?:متاح|متوفر|موعد|مواعيد)|(?:متاح|متوفر|موعد|مواعيد).{0,30}(?:السبت|الأحد|الاحد|الاثنين|الإثنين|الثلاثاء|الأربعاء|الاربعاء|الخميس|الجمعة|اليوم|غدا|غداً)/u.test(raw)||/(?:lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche|aujourd'hui|aujourd’hui|demain).{0,36}(?:disponible|disponibilité|disponibilite|créneau|creneau)|(?:disponible|disponibilité|disponibilite|créneau|creneau).{0,36}(?:lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche|aujourd'hui|aujourd’hui|demain)/iu.test(norm));
const hardInterrupt=Boolean(/\b(?:human|agent|person|complain|complaint|technical|login|stop contacting|do not contact|don't contact|unsubscribe)\b|(?:موظف|شخص|شكوى|مشكلة تقنية|لا تتواصل|لا ترسل|أوقف الرسائل)|\b(?:agent|humain|personne|plainte|technique|connexion|désabonnez)\b/iu.test(norm));
function clearClar(){return {schema:'SPM_WU104_CLARIFICATION_STATE_V1',active:false,clarification_key:null,attempt:0,reason_code:'NONE',language:String(c.language||j.language_hint||'en'),expected_response_type:'NONE',last_intent:null,updated_at:new Date().toISOString(),raw_message_logged:false,raw_session_logged:false,secret_values_logged:false};}
let applied=false,reason='NONE';
if(explicitAvailability&&!hardInterrupt){
 c.spm_intent='availability';c.secondary_spm_intent='';c.ambiguous=false;c.confidence=Math.max(Number(c.confidence||0),Number(c.threshold||0.85),0.99);c.rationale_code='WU106_CR10602_EXPLICIT_AVAILABILITY';
 state.clarification=clearClar();
 d.context_binding_status='CURRENT_MESSAGE_OVERRIDE';d.binding_source='WU106_CR10602_EXPLICIT_AVAILABILITY';d.resolved_intent='availability';d.resolved_entity_type='day_or_time_availability';d.clarification_required=false;d.clarification_reason='NONE';d.safe_action='CONTINUE';
 applied=true;reason='EXPLICIT_AVAILABILITY_ROOT_OVERRIDE';
}else if(registrationActive&&awaited&&validAwaited&&!hardInterrupt){
 c.spm_intent='registration';c.secondary_spm_intent='';c.ambiguous=false;c.confidence=Math.max(Number(c.confidence||0),Number(c.threshold||0.85),0.99);c.rationale_code='WU106_CR10602_DURABLE_REGISTRATION_BIND';
 state.clarification=clearClar();state.conversion.registration_active=true;state.conversion.registration_status=state.conversion.registration_status||'collecting';state.conversion.awaiting_field=awaited;state.journey.awaiting_entity=awaited;
 d.context_binding_status='BOUND_DETERMINISTIC';d.binding_source='WU106_CR10602_DURABLE_REGISTRATION_CONTROL';d.resolved_intent='registration';d.resolved_entity_type=awaited;d.clarification_required=false;d.clarification_reason='NONE';d.safe_action='CONTINUE';
 applied=true;reason='DURABLE_REGISTRATION_FIELD_BOUND';
}
const ev={schema:'SPM_WU106_CR10602_ROOT_RECOVERY_V1',applied,reason,registration_active:registrationActive,awaiting_field:awaited||null,explicit_availability:explicitAvailability,hard_interrupt:hardInterrupt,result_intent:String(c.spm_intent||''),pii_values_logged:false,action_permission_mutated:false,irreversible_action_allowed:false,production_mutation_allowed:false};
return [{json:{...j,classification:c,sales_state:state,classifier_route:applied?'direct':j.classifier_route,customer_clarification_required:applied?false:Boolean(j.customer_clarification_required),classifier_safe_action:applied?'CONTINUE':j.classifier_safe_action,wu104_short_query_decision:d,wu104_clarification_text:applied?null:j.wu104_clarification_text,wu106_cr10602_root_recovery:ev}}];"""

    root_recovery = code_node(
        ROOT_RECOVERY,
        "wu106-cr10602-root-journey-recovery-v1",
        [cx + 160, cy - 160],
        root_js,
        "CR-106-02 root recovery: deterministic current-message availability and durable registration awaited-field binding. Classifier confidence cannot suppress these two explicit/context-bound transitions.",
    )

    build_js = r"""const j=$input.first().json||{};
const conv=(j.sales_state&&j.sales_state.conversion&&typeof j.sales_state.conversion==='object')?j.sales_state.conversion:{};
const active=Boolean(conv.registration_active===true||conv.awaiting_field||['collecting','awaiting_confirmation','ready_to_write'].includes(String(conv.registration_status||'')));
const ctrl={schema:'SPM_WU106_REGISTRATION_CONTROL_V1',active,registration_status:String(conv.registration_status||'not_started'),awaiting_field:conv.awaiting_field||null,request_type:conv.request_type||null,pending_confirmation:Boolean(conv.pending_confirmation),updated_at:new Date().toISOString(),pii_values_stored:false,raw_message_stored:false,production_namespace:false};
return [{json:{...j,wu106_registration_control_key:`spm:staging:regctrl:${j.session_id}`,wu106_registration_control_text:JSON.stringify(ctrl),wu106_cr10602_control_snapshot:{schema:'SPM_WU106_CR10602_CONTROL_SNAPSHOT_V1',active,awaiting_field:ctrl.awaiting_field,pii_values_stored:false,raw_message_stored:false,production_mutation_allowed:false}}}];"""

    build_ctrl = code_node(
        BUILD_CTRL,
        "wu106-cr10602-build-registration-control-v1",
        [px + 160, py - 160],
        build_js,
        "CR-106-02 builds a PII-free registration control snapshot after final WU95 state is known. It stores control fields only, never customer values.",
    )

    save_ctrl = save_template
    save_ctrl.update({
        "name": SAVE_CTRL,
        "id": "wu106-cr10602-save-registration-control-v1",
        "position": [px + 320, py - 160],
        "notes": "CR-106-02 redundant STAGING Redis persistence for registration control metadata only. Main canonical WU95 sales-state persistence remains unchanged downstream.",
    })
    save_ctrl["parameters"] = {
        "operation": "set",
        "key": "={{ $json.wu106_registration_control_key }}",
        "value": "={{ $json.wu106_registration_control_text }}",
        "expire": True,
        "ttl": 2592000,
    }

    restore_js = r"""const base=$('Build WU106 Registration Control Snapshot [CR-106-02]').first().json||{};
const x=$input.first().json||{};
const failed=Boolean(x.error||x.message&&String(x.message).toLowerCase().includes('error'));
return [{json:{...base,wu106_cr10602_control_persist:{schema:'SPM_WU106_CR10602_CONTROL_PERSIST_V1',attempted:true,failed,pii_values_stored:false,production_mutation_allowed:false}}}];"""
    restore_ctrl = code_node(
        RESTORE_CTRL,
        "wu106-cr10602-restore-registration-control-v1",
        [px + 480, py - 160],
        restore_js,
        "Restores canonical payload after the redundant registration-control Redis SET. Failure does not block the pre-existing canonical WU95 Redis save.",
    )

    out["nodes"].extend([load_ctrl, merge_ctrl, root_recovery, build_ctrl, save_ctrl, restore_ctrl])

    conns[INIT] = {"main": [[{"node": LOAD_CTRL, "type": "main", "index": 0}]]}
    conns[LOAD_CTRL] = {"main": [
        [{"node": MERGE_CTRL, "type": "main", "index": 0}],
        [{"node": MERGE_CTRL, "type": "main", "index": 0}],
    ]}
    conns[MERGE_CTRL] = {"main": [[{"node": CATALOG, "type": "main", "index": 0}]]}

    conns[CR10601] = {"main": [[{"node": ROOT_RECOVERY, "type": "main", "index": 0}]]}
    conns[ROOT_RECOVERY] = {"main": [[{"node": SHORT_TRIAL, "type": "main", "index": 0}]]}

    conns[PERSIST_FINAL] = {"main": [[{"node": BUILD_CTRL, "type": "main", "index": 0}]]}
    conns[BUILD_CTRL] = {"main": [[{"node": SAVE_CTRL, "type": "main", "index": 0}]]}
    conns[SAVE_CTRL] = {"main": [
        [{"node": RESTORE_CTRL, "type": "main", "index": 0}],
        [{"node": RESTORE_CTRL, "type": "main", "index": 0}],
    ]}
    conns[RESTORE_CTRL] = {"main": [[{"node": SERIALIZE_WU95, "type": "main", "index": 0}]]}

    out["active"] = False
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"CR10602_INPUT_SHA256={actual}")
    print(f"CR10602_OUTPUT_SHA256={sha256(a.output)}")
    print(f"CR10602_NODE_COUNT={len(out['nodes'])}")
    print("CR10602_PRODUCTION_MUTATION=false")


if __name__ == "__main__":
    main()
