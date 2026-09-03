#!/usr/bin/env python3
import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path

EXPECTED_BASE_SHA256 = "134b2d861d6c5060ca52d8fd838b2cdd7d5d88ffa74855e3de1665e302afda67"
EXPECTED_BASE_NODE_COUNT = 132
SOURCE_NODE = "Build WU104 Short Query Decision"
TARGET_NODE = "Apply WU104 Short Trial Inquiry Guard"
CR_NODE = "Apply WU106 Journey Transition Recovery [CR-106-01]"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_node(position):
    js_code = r"""const j=$input.first().json||{};
const c=(j.classification&&typeof j.classification==='object')?{...j.classification}:{};
const state=(j.sales_state&&typeof j.sales_state==='object')?JSON.parse(JSON.stringify(j.sales_state)):{};
state.conversion=(state.conversion&&typeof state.conversion==='object')?state.conversion:{};
const reg=state.conversion;
const decision=(j.wu104_short_query_decision&&typeof j.wu104_short_query_decision==='object')?{...j.wu104_short_query_decision}:{};
const raw=String(j.message?.raw??'').normalize('NFKC').trim();
const norm=raw.toLowerCase().replace(/\s+/g,' ');
const tokens=(norm.match(/[\p{L}\p{N}_@.+\/'’-]+/gu)||[]);
const intent=String(c.spm_intent||'');
const confidence=Number.isFinite(Number(c.confidence))?Number(c.confidence):0;
const threshold=Number.isFinite(Number(c.threshold))?Number(c.threshold):0.85;
const awaited=String(reg.awaiting_field||state.journey?.awaiting_entity||'').trim().toLowerCase().replace(/[-\s]+/g,'_');
const registrationActive=Boolean(reg.registration_active===true||reg.awaiting_field||['collecting','awaiting_confirmation','ready_to_write'].includes(String(reg.registration_status||'')));
const clarificationWasRaised=['ASK_ONE_CLARIFYING_QUESTION','SAFE_FALLBACK_OR_HUMAN_HELP'].includes(String(decision.safe_action||''))||j.customer_clarification_required===true||['clarify','fallback'].includes(String(j.classifier_route||''));
const clearClassifier=Boolean(c.ambiguous!==true&&confidence>=threshold&&!['','unknown_intent','out_of_scope'].includes(intent));
const interruptIntents=new Set(['availability','schedule_request','human_handoff','complaint','technical_issue','technical_support','account_login','payment_problem','payment_methods','not_interested','do_not_contact','pricing','package_comparison','price_objection','discount_request','refund_policy','cancellation_policy','trial_details']);
const clearInterrupt=clearClassifier&&interruptIntents.has(intent);
const weakClassifier=Boolean(c.ambiguous===true||confidence<threshold||['','unknown_intent','out_of_scope'].includes(intent));

const stopWords=new Set(['yes','no','maybe','later','price','cost','available','availability','lesson','lessons','tutor','tutoring','register','registration','refund','human','agent','person','help','please','schedule','scheduling','monday','tuesday','wednesday','thursday','friday','saturday','sunday','today','tomorrow','نعم','لا','ربما','لاحقا','لاحقاً','السعر','سعر','متاح','متوفر','حصة','حصص','مدرس','تسجيل','استرجاع','موظف','شخص','مساعدة','السبت','الأحد','الاحد','الاثنين','الثلاثاء','الأربعاء','الاربعاء','الخميس','الجمعة','oui','non','peut','plus','tard','prix','disponible','cours','tuteur','inscription','remboursement','agent','personne','aide','samedi','dimanche','lundi','mardi','mercredi','jeudi','vendredi']);
const wordsOnly=(norm.match(/[\p{L}][\p{L}'’-]*/gu)||[]);
const nameLike=Boolean(raw.length>=2&&raw.length<=100&&wordsOnly.length>=1&&wordsOnly.length<=5&&wordsOnly.join(' ').length===norm.replace(/[^\p{L}'’\-\s]/gu,'').replace(/\s+/g,' ').trim().length&&!wordsOnly.some(x=>stopWords.has(x)));
const digits=raw.replace(/\D/g,'');
const phoneLike=Boolean(digits.length>=8&&digits.length<=15&&/^[+()\d\s.\-]+$/.test(raw));
const emailLike=/^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/.test(raw);
const placeLike=Boolean(raw.length>=2&&raw.length<=100&&wordsOnly.length>=1&&wordsOnly.length<=5&&!wordsOnly.some(x=>stopWords.has(x)));
const timezoneLike=/^(?:UTC|GMT|[A-Za-z_]+(?:\/[A-Za-z0-9_+\-]+)+)$/.test(raw);
const languageLike=/^(?:english|arabic|french|العربية|العربيه|الإنجليزية|الانجليزية|الفرنسية|الفرنسيه|anglais|arabe|français|francais)$/iu.test(norm);
const validators={parent_name:nameLike,student_name:nameLike,phone:phoneLike,email:emailLike,country:placeLike,city:placeLike,timezone:timezoneLike,preferred_language:languageLike};
const contextualValueValid=Boolean(validators[awaited]);

const day='(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|today|tomorrow)';
const availabilityWord='(?:available|availability|open|slot|slots)';
const enAvailability=new RegExp(`(?:\\b${day}\\b.{0,32}\\b${availabilityWord}\\b|\\b${availabilityWord}\\b.{0,32}\\b${day}\\b)`,'iu').test(norm);
const arAvailability=/(?:السبت|الأحد|الاحد|الاثنين|الإثنين|الثلاثاء|الأربعاء|الاربعاء|الخميس|الجمعة|اليوم|غدا|غداً).{0,28}(?:متاح|متوفر|موعد|مواعيد)|(?:متاح|متوفر|موعد|مواعيد).{0,28}(?:السبت|الأحد|الاحد|الاثنين|الإثنين|الثلاثاء|الأربعاء|الاربعاء|الخميس|الجمعة|اليوم|غدا|غداً)/u.test(raw);
const frAvailability=/(?:lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche|aujourd'hui|aujourd’hui|demain).{0,32}(?:disponible|disponibilité|disponibilite|créneau|creneau)|(?:disponible|disponibilité|disponibilite|créneau|creneau).{0,32}(?:lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche|aujourd'hui|aujourd’hui|demain)/iu.test(norm);
const explicitAvailability=Boolean(enAvailability||arAvailability||frAvailability);

function clearedClarification(lang){
 return {schema:'SPM_WU104_CLARIFICATION_STATE_V1',active:false,clarification_key:null,attempt:0,reason_code:'NONE',language:lang||String(c.language||j.language_hint||'en'),expected_response_type:'NONE',last_intent:null,updated_at:new Date().toISOString(),raw_message_logged:false,raw_session_logged:false,secret_values_logged:false};
}
let applied=false;
let reason='NONE';
let classifierRoute=j.classifier_route;
let customerClarification=j.customer_clarification_required;
let classifierSafeAction=j.classifier_safe_action;
let clarificationText=j.wu104_clarification_text;

if(registrationActive&&awaited&&contextualValueValid&&weakClassifier&&!clearInterrupt&&clarificationWasRaised){
 state.clarification=clearedClarification(decision.clarification_language);
 decision.context_binding_status='BOUND_DETERMINISTIC';
 decision.binding_source='WU106_REGISTRATION_AWAITED_FIELD';
 decision.resolved_entity_type=awaited;
 decision.clarification_required=false;
 decision.clarification_reason='NONE';
 decision.clarification_key=null;
 decision.clarification_attempt=0;
 decision.safe_action='CONTINUE';
 classifierRoute='direct';
 customerClarification=false;
 classifierSafeAction='CONTINUE';
 clarificationText=null;
 applied=true;
 reason='REGISTRATION_AWAITED_FIELD_RECOVERED';
}else if(explicitAvailability&&!clearInterrupt&&(weakClassifier||intent==='availability'||clarificationWasRaised)){
 state.clarification=clearedClarification(decision.clarification_language);
 c.spm_intent='availability';
 c.ambiguous=false;
 c.confidence=Math.max(confidence,threshold);
 c.rationale_code='WU106_EXPLICIT_AVAILABILITY_PATTERN';
 decision.context_binding_status='CURRENT_MESSAGE_OVERRIDE';
 decision.binding_source='WU106_EXPLICIT_AVAILABILITY_PATTERN';
 decision.resolved_intent='availability';
 decision.resolved_entity_type='day_or_time_availability';
 decision.clarification_required=false;
 decision.clarification_reason='NONE';
 decision.clarification_key=null;
 decision.clarification_attempt=0;
 decision.safe_action='CONTINUE';
 classifierRoute='direct';
 customerClarification=false;
 classifierSafeAction='CONTINUE';
 clarificationText=null;
 applied=true;
 reason='EXPLICIT_AVAILABILITY_CURRENT_MESSAGE_OVERRIDE';
}

const recovery={schema:'SPM_WU106_CR10601_JOURNEY_TRANSITION_RECOVERY_V1',applied,reason,awaiting_field:awaited||null,registration_active:registrationActive,explicit_availability_pattern:explicitAvailability,original_intent:intent||null,result_intent:String(c.spm_intent||intent||''),action_permission_mutated:false,irreversible_action_allowed:false,production_mutation_allowed:false,raw_message_logged:false,raw_session_logged:false,secret_values_logged:false};
return [{json:{...j,classification:c,sales_state:state,classifier_route:classifierRoute,customer_clarification_required:Boolean(customerClarification),classifier_safe_action:classifierSafeAction,wu104_short_query_decision:decision,wu104_clarification_text:clarificationText,wu106_cr10601_recovery:recovery}}];"""
    return {
        "parameters": {"jsCode": js_code},
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": position,
        "id": "wu106-cr10601-journey-transition-recovery-v1",
        "name": CR_NODE,
        "notesInFlow": True,
        "notes": (
            "CR-106-01 STAGING-only deterministic recovery for two GJ-04 failures. It is inserted after the locked WU-104 short-query decision and before the locked WU-104 short-trial guard, so CR-104-05 remains authoritative downstream. No external action or Production mutation is introduced."
        ),
    }


def apply(input_path: Path, output_path: Path):
    actual = sha256(input_path)
    if actual != EXPECTED_BASE_SHA256:
        raise SystemExit(f"CR-106-01 refuses unexpected WU-106 baseline SHA: {actual}")
    wf = json.loads(input_path.read_text(encoding="utf-8"))
    if len(wf.get("nodes", [])) != EXPECTED_BASE_NODE_COUNT:
        raise SystemExit(f"CR-106-01 baseline node count mismatch: {len(wf.get('nodes', []))}")
    candidate = deepcopy(wf)
    names = [n.get("name") for n in candidate.get("nodes", [])]
    if names.count(SOURCE_NODE) != 1 or names.count(TARGET_NODE) != 1:
        raise SystemExit("CR-106-01 source/target identity mismatch")
    if CR_NODE in names:
        raise SystemExit("CR-106-01 node already exists")
    source = next(n for n in candidate["nodes"] if n.get("name") == SOURCE_NODE)
    x, y = source.get("position", [0, 0])
    candidate["nodes"].append(make_node([x + 160, y - 112]))
    conns = candidate.setdefault("connections", {})
    existing = deepcopy(conns.get(SOURCE_NODE, {}).get("main"))
    if existing != [[{"node": TARGET_NODE, "type": "main", "index": 0}]]:
        raise SystemExit(f"CR-106-01 unexpected source topology: {existing!r}")
    conns[SOURCE_NODE] = {"main": [[{"node": CR_NODE, "type": "main", "index": 0}]]}
    conns[CR_NODE] = {"main": [[{"node": TARGET_NODE, "type": "main", "index": 0}]]}
    candidate["active"] = False
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"CR10601_INPUT_SHA256={actual}")
    print(f"CR10601_OUTPUT={output_path}")
    print(f"CR10601_OUTPUT_SHA256={sha256(output_path)}")
    print(f"CR10601_NODE_COUNT={len(candidate.get('nodes', []))}")
    print("CR10601_PRODUCTION_MUTATION=false")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    apply(args.input, args.output)


if __name__ == "__main__":
    main()
