#!/usr/bin/env python3
import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path

EXPECTED_INPUT_SHA256 = "50dbf22e2496e3c1b0ce7c9ff37edab752dbf6b69ddc62f80026942b31146014"
EXPECTED_INPUT_NODE_COUNT = 139

WU89 = "Validate + Normalize WU89 Entities"
ROOT = "Apply WU106 Root Journey Recovery [CR-106-02]"
SHORT_TRIAL = "Apply WU104 Short Trial Inquiry Guard"
AVAIL_GUARD = "Apply WU105 Availability Answer-First Guard"
CONVERSION = "Resolve WU95 Conversion Mode"

ALT = "Apply WU106 Alternative Slot Recovery [CR-106-03]"
ALT_RESPONSE = "Apply WU106 Alternative Availability Response Guard [CR-106-03]"


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
    main = conns.get(source, {}).get("main")
    if not isinstance(main, list) or len(main) != 1 or len(main[0]) != 1:
        return None
    return main[0][0].get("node")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()

    actual = sha256(a.input)
    if actual != EXPECTED_INPUT_SHA256:
        raise SystemExit(f"CR-106-03 refuses unexpected CR-106-02 SHA: {actual}")

    wf = json.loads(a.input.read_text(encoding="utf-8"))
    if len(wf.get("nodes", [])) != EXPECTED_INPUT_NODE_COUNT:
        raise SystemExit("CR-106-03 input node count mismatch")

    out = deepcopy(wf)
    nodes = {n.get("name"): n for n in out.get("nodes", [])}
    for required in [WU89, ROOT, SHORT_TRIAL, AVAIL_GUARD, CONVERSION]:
        if required not in nodes:
            raise SystemExit(f"CR-106-03 missing required node: {required}")
    if ALT in nodes or ALT_RESPONSE in nodes:
        raise SystemExit("CR-106-03 already applied")

    conns = out.setdefault("connections", {})
    if one_target(conns, ROOT) != SHORT_TRIAL:
        raise SystemExit("CR-106-03 unexpected root-recovery topology")
    if one_target(conns, AVAIL_GUARD) != CONVERSION:
        raise SystemExit("CR-106-03 unexpected availability-guard topology")

    wu89 = nodes[WU89]
    code = wu89.get("parameters", {}).get("jsCode", "")
    anchor = "const noTimezoneInference="
    if anchor not in code:
        raise SystemExit("CR-106-03 WU89 anchor missing")
    if "SPM_WU106_CR10603_SCHEDULING_NORMALIZATION_V1" in code:
        raise SystemExit("CR-106-03 WU89 patch already present")

    insertion = r"""
// SPM_WU106_CR10603_SCHEDULING_NORMALIZATION_V1
// Explicit city-time wording is customer-provided scheduling context, not country-based timezone inference.
const wu106SchedulingSignal=/\b(?:available|availability|schedule|scheduled|book|booking|slot|lesson|tutoring)\b|(?:متاح|متوفر|موعد|حجز|حصة|درس)|\b(?:disponible|disponibilité|disponibilite|réserver|reserver|créneau|creneau|cours)\b/iu.test(msg);
const wu106CityTimeAlias=msg.match(/\b(Toronto|Mississauga|Milton)\s+(?:local\s+)?time\b/i);
if(wu106CityTimeAlias){
  const cityRaw=wu106CityTimeAlias[1];
  const cityCanonical={toronto:'Toronto',mississauga:'Mississauga',milton:'Milton'}[searchNorm(cityRaw)]||cityRaw;
  setAuthoritative('city',cityCanonical,'customer_deterministic_city_time_alias');
  setAuthoritative('timezone','America/Toronto','customer_deterministic_city_time_alias');
}
if(wu106SchedulingSignal){
  const dayMap=[
    ['Monday',/\bmonday\b|\blundi\b|الاثنين|الإثنين/iu],
    ['Tuesday',/\btuesday\b|\bmardi\b|الثلاثاء/iu],
    ['Wednesday',/\bwednesday\b|\bmercredi\b|الأربعاء|الاربعاء/iu],
    ['Thursday',/\bthursday\b|\bjeudi\b|الخميس/iu],
    ['Friday',/\bfriday\b|\bvendredi\b|الجمعة/iu],
    ['Saturday',/\bsaturday\b|\bsamedi\b|السبت/iu],
    ['Sunday',/\bsunday\b|\bdimanche\b|الأحد|الاحد/iu]
  ];
  for(const [dayName,rx] of dayMap){
    if(rx.test(msg)){setAuthoritative('preferred_day',dayName,'customer_deterministic_schedule_preference');break;}
  }
  const time12=msg.match(/\b(?:at\s*)?((?:1[0-2]|0?[1-9])(?::[0-5]\d)?\s*(?:a\.?m\.?|p\.?m\.?))\b/i);
  if(time12){
    setAuthoritative('preferred_time',time12[1].replace(/\./g,'').replace(/\s+/g,' ').trim().toUpperCase(),'customer_deterministic_schedule_preference');
  }
}
"""
    wu89["parameters"]["jsCode"] = code.replace(anchor, insertion + "\n" + anchor, 1)

    root = nodes[ROOT]
    rx, ry = root.get("position", [0, 0])
    alt_js = r"""const j=$input.first().json||{};
const c=(j.classification&&typeof j.classification==='object')?{...j.classification}:{};
const state=(j.sales_state&&typeof j.sales_state==='object')?JSON.parse(JSON.stringify(j.sales_state)):{};
const d=(j.wu104_short_query_decision&&typeof j.wu104_short_query_decision==='object')?{...j.wu104_short_query_decision}:{};
const raw=String(j.message?.raw??'').normalize('NFKC').trim();
const norm=raw.toLowerCase().replace(/\s+/g,' ');
const altEn=Boolean(
  /\b(?:if|when)\b.{0,70}\b(?:not\s+available|unavailable)\b.{0,90}\b(?:other|another|alternative)\b.{0,35}\b(?:time|times|slot|slots|option|options)\b/iu.test(norm) ||
  /\b(?:what|which|any)\s+(?:other|alternative)\s+(?:time|times|slot|slots|option|options)\b/iu.test(norm) ||
  /\b(?:other|alternative)\s+(?:time|times|slot|slots|option|options)\b.{0,30}\b(?:work|works|available)\b/iu.test(norm)
);
const altAr=/(?:إذا|اذا).{0,50}(?:مش|غير)\s*(?:متاح|متوفر).{0,70}(?:وقت|موعد|مواعيد)\s*(?:آخر|اخر|بديل)|(?:وقت|موعد|مواعيد)\s*(?:آخر|اخر|بديل).{0,30}(?:متاح|متوفر|ينفع)/u.test(raw);
const altFr=/(?:si).{0,50}(?:pas\s+disponible|indisponible).{0,70}(?:autre|alternatif).{0,30}(?:heure|créneau|creneau)|(?:autre|alternatif).{0,20}(?:heure|créneau|creneau).{0,30}(?:possible|disponible|convient)/iu.test(norm);
const alternativeAvailability=Boolean(altEn||altAr||altFr);
const hardInterrupt=Boolean(/\b(?:human|agent|person|complain|complaint|technical|login|stop contacting|do not contact|don't contact|unsubscribe)\b|(?:موظف|شخص|شكوى|مشكلة تقنية|لا تتواصل|لا ترسل|أوقف الرسائل)|\b(?:agent|humain|personne|plainte|technique|connexion|désabonnez)\b/iu.test(norm));
function clearClar(){return {schema:'SPM_WU104_CLARIFICATION_STATE_V1',active:false,clarification_key:null,attempt:0,reason_code:'NONE',language:String(c.language||j.language_hint||'en'),expected_response_type:'NONE',last_intent:null,updated_at:new Date().toISOString(),raw_message_logged:false,raw_session_logged:false,secret_values_logged:false};}
let applied=false;
if(alternativeAvailability&&!hardInterrupt){
  c.spm_intent='availability';
  c.secondary_spm_intent='';
  c.ambiguous=false;
  c.confidence=Math.max(Number(c.confidence||0),Number(c.threshold||0.85),0.99);
  c.rationale_code='WU106_CR10603_ALTERNATIVE_AVAILABILITY';
  state.clarification=clearClar();
  d.context_binding_status='CURRENT_MESSAGE_OVERRIDE';
  d.binding_source='WU106_CR10603_ALTERNATIVE_AVAILABILITY';
  d.resolved_intent='availability';
  d.resolved_entity_type='alternative_slot_availability';
  d.clarification_required=false;
  d.clarification_reason='NONE';
  d.safe_action='CONTINUE';
  applied=true;
}
const ev={schema:'SPM_WU106_CR10603_ALTERNATIVE_SLOT_RECOVERY_V1',applied,alternative_availability:alternativeAvailability,hard_interrupt:hardInterrupt,result_intent:String(c.spm_intent||''),existing_schedule_preferences_mutated:false,action_permission_mutated:false,irreversible_action_allowed:false,production_mutation_allowed:false,raw_message_logged:false,raw_session_logged:false,secret_values_logged:false};
return [{json:{...j,classification:c,sales_state:state,classifier_route:applied?'direct':j.classifier_route,customer_clarification_required:applied?false:Boolean(j.customer_clarification_required),classifier_safe_action:applied?'CONTINUE':j.classifier_safe_action,wu104_short_query_decision:d,wu104_clarification_text:applied?null:j.wu104_clarification_text,wu106_cr10603_alternative_recovery:ev}}];"""
    alt = code_node(
        ALT,
        "wu106-cr10603-alternative-slot-recovery-v1",
        [rx + 160, ry + 80],
        alt_js,
        "CR-106-03: alternative-slot wording becomes availability inquiry without overwriting the existing requested day/time/timezone.",
    )

    ag = nodes[AVAIL_GUARD]
    ax, ay = ag.get("position", [0, 0])
    response_js = r"""const j=$input.first().json||{};
const o=(j.sales_agent_output&&typeof j.sales_agent_output==='object')?{...j.sales_agent_output}:{};
const ev=j.wu106_cr10603_alternative_recovery||{};
const ctx=j.scheduling_context||{};
const lang=String(j.classification?.language||j.language_hint||'en').toLowerCase();
let applied=false;
if(ev.applied===true && ctx.availability_verified!==true){
  if(lang==='ar'){
    o.answer_text='أحتاج إلى التحقق من جدول المواعيد المباشر لمعرفة الأوقات البديلة المتاحة. سأبقي الوقت الذي طلبته كتفضيلك الحالي ما لم تختَر وقتًا آخر.';
  }else if(lang==='fr'){
    o.answer_text='Je dois vérifier le planning en direct pour connaître les autres créneaux disponibles. Je garderai l’heure demandée comme préférence actuelle sauf si vous choisissez une autre heure.';
  }else{
    o.answer_text='I need to check the live schedule for other available times. I will keep your requested time as the current preference unless you choose a different time.';
  }
  o.purposeful_question=null;
  o.proposed_action='request_live_check';
  o.action_requires_gateway=true;
  applied=true;
}
const guard={schema:'SPM_WU106_CR10603_ALTERNATIVE_AVAILABILITY_RESPONSE_V1',applied,availability_verified:Boolean(ctx.availability_verified),requested_preference_preserved:true,slot_invented:false,booking_claimed:false,action_permission_mutated:false,irreversible_action_allowed:false,production_mutation_allowed:false};
return [{json:{...j,sales_agent_output:o,wu106_cr10603_alternative_response_guard:guard}}];"""
    alt_response = code_node(
        ALT_RESPONSE,
        "wu106-cr10603-alternative-availability-response-v1",
        [ax + 160, ay + 96],
        response_js,
        "CR-106-03: answer alternative-slot questions with a live-check boundary and preserve the customer's requested preference; never invent an alternative slot.",
    )

    out["nodes"].extend([alt, alt_response])

    conns[ROOT] = {"main": [[{"node": ALT, "type": "main", "index": 0}]]}
    conns[ALT] = {"main": [[{"node": SHORT_TRIAL, "type": "main", "index": 0}]]}
    conns[AVAIL_GUARD] = {"main": [[{"node": ALT_RESPONSE, "type": "main", "index": 0}]]}
    conns[ALT_RESPONSE] = {"main": [[{"node": CONVERSION, "type": "main", "index": 0}]]}

    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"CR10603_INPUT_SHA256={actual}")
    print(f"CR10603_OUTPUT_SHA256={sha256(a.output)}")
    print(f"CR10603_NODE_COUNT={len(out.get('nodes', []))}")
    print("CR10603_PRODUCTION_MUTATION=false")


if __name__ == "__main__":
    main()
