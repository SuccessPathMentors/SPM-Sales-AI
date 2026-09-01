#!/usr/bin/env python3
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WU102_BUILDER = ROOT / 'scripts' / 'wu102' / 'build_candidate.py'


def load_wu102_builder():
    spec = importlib.util.spec_from_file_location('wu102_builder_for_wu104', WU102_BUILDER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def node_by_name(wf, name):
    matches = [n for n in wf['nodes'] if n.get('name') == name]
    if len(matches) != 1:
        raise RuntimeError(f'expected exactly one node {name!r}, found {len(matches)}')
    return matches[0]


def replace_exact(text, old, new):
    if old not in text:
        raise RuntimeError(f'expected text not found: {old}')
    return text.replace(old, new)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(baseline_path):
    wu102 = load_wu102_builder()
    wf = copy.deepcopy(wu102.build(baseline_path))
    wf['name'] = 'SPM WU104 Short Query + Ambiguity UX Candidate'
    wf['active'] = False

    canonical = node_by_name(wf, 'Build Canonical Session Envelope')
    canonical['parameters']['jsCode'] = replace_exact(
        canonical['parameters']['jsCode'],
        "workflow_release:'WU102_STAGING_UNANSWERED_V1'",
        "workflow_release:'WU104_STAGING_SHORT_QUERY_V1'",
    )

    decision_name = 'Build WU104 Short Query Decision'
    decision_js = r"""const j=$input.first().json||{};
const c=j.classification||{};
const state=(j.sales_state&&typeof j.sales_state==='object')?j.sales_state:{};
const previous=(state.clarification&&typeof state.clarification==='object')?state.clarification:{};
const raw=String(j.message?.raw??'');
const normalize=s=>String(s??'').normalize('NFKC').trim().toLowerCase().replace(/\s+/g,' ');
const norm=normalize(raw);
const tokens=(norm.match(/[\p{L}\p{N}_]+/gu)||[]);
const short=Boolean(norm)&&norm.length<=48&&tokens.length<=5;
const bucket=!norm?'EMPTY':(norm.length<=12?'VERY_SHORT':(short?'SHORT':'NOT_SHORT'));
const compact=s=>normalize(s).replace(/[^\p{L}\p{N}_]+/gu,'');
const affirm=new Set(['yes','y','yeah','yep','ok','okay','sure','correct','نعم','ايوه','أيوه','اه','آه','تمام','صح','oui','ouais','daccord','d’accord'].map(compact));
const negate=new Set(['no','n','nope','not','لا','كلا','مش','non','pas'].map(compact));
const days=new Set(['monday','tuesday','wednesday','thursday','friday','saturday','sunday','today','tomorrow','الاثنين','الإثنين','الثلاثاء','الأربعاء','الاربعاء','الخميس','الجمعة','السبت','الأحد','الاحد','اليوم','غدا','غداً','بكرة','lundi','mardi','mercredi','jeudi','vendredi','samedi','dimanche','aujourd’hui','aujourdhui','demain'].map(normalize));
const semantic=[/\b(?:price|cost|pricing|how much|refund|discount|human|agent|person|login|register|registration|cancel|reschedule|payment)\b/iu,/(?:سعر|السعر|كم\s+السعر|استرجاع|استرداد|خصم|موظف|موظفة|شخص|إنسان|انسان|تسجيل|دفع|إلغاء|الغاء|تغيير\s+موعد)/iu,/\b(?:prix|coût|cout|remboursement|réduction|reduction|agent|humain|conseiller|connexion|inscription|paiement|annuler)\b/iu,/\b(?:tutor|tutoring|lesson|lessons|course|courses|cours|soutien)\b/iu,/(?:مدرس|مدرسة|معلم|معلمة|دروس|حصص|حصة)/iu];
const correction=[/\b(?:actually|correction|correcting|instead)\b/iu,/(?:تصحيح|بالعكس|لا،)/u,/\b(?:correction|en fait|plutôt|plutot)\b/iu].some(r=>r.test(norm));
const isGrade=short&&[/^(?:grade|gr|g)\s*(?:[1-9]|1[0-2])$/iu,/^(?:[1-9]|1[0-2])(?:st|nd|rd|th)?\s*grade$/iu,/^(?:صف|الصف)\s*(?:ال)?(?:[1-9]|1[0-2]|أول|اول|ثاني|ثالث|رابع|خامس|سادس|سابع|ثامن|تاسع|عاشر|حادي\s*عشر|ثاني\s*عشر)$/u,/^(?:classe|niveau)\s*(?:[1-9]|1[0-2])$/iu].some(r=>r.test(norm));
const isDay=short&&days.has(norm);
const isTime=short&&/^(?:[01]?\d|2[0-3])(?::[0-5]\d)?\s*(?:am|pm|a\.m\.|p\.m\.)?$/iu.test(norm.replace('٫',':'));
const intent=String(c.spm_intent||'');
const awaitedRaw=state.conversion?.awaiting_field||state.journey?.awaiting_entity||null;
const awaited=normalize(awaitedRaw).replace(/[-\s]+/g,'_');
const aliases={grade_level:'grade',grade:'grade',student_grade:'grade',subject:'subject',student_subject:'subject',city:'location',location:'location',student_city:'location',parent_city:'location',day:'day',date:'day',lesson_day:'day',schedule_day:'day',scheduling_day:'day',scheduling_date:'day',time:'time',lesson_time:'time',schedule_time:'time',scheduling_time:'time',time_window:'time',scheduling_time_window:'time',consent_to_contact:'confirmation',final_confirmation:'confirmation'};
const awaitedType=aliases[awaited]||null;
let shortType='NONE';
if(short){
 if(affirm.has(compact(norm)))shortType='AFFIRMATION';
 else if(negate.has(compact(norm)))shortType='NEGATION';
 else if(isGrade)shortType='GRADE_ONLY';
 else if(isDay)shortType='DAY_ONLY';
 else if(isTime)shortType='TIME_ONLY';
 else if(semantic.some(r=>r.test(norm)))shortType='SEMANTIC_FRAGMENT';
 else if(awaitedType==='subject'||(['subject_inquiry','learning_goal','teacher_availability'].includes(intent)&&tokens.length>=1&&tokens.length<=3))shortType='SUBJECT_ONLY';
 else if(awaitedType==='location'||(['timezone','schedule_request','availability','registration'].includes(intent)&&tokens.length>=1&&tokens.length<=3))shortType='LOCATION_ONLY';
 else shortType='OTHER_SHORT';
}
const confidence=Number.isFinite(Number(c.confidence))?Number(c.confidence):0;
const threshold=Number.isFinite(Number(c.threshold))?Number(c.threshold):0.85;
const direct=j.classifier_route==='direct'&&c.ambiguous!==true&&confidence>=threshold;
const lang=String(c.language||j.language_hint||'en').toLowerCase().startsWith('ar')?'ar':(String(c.language||j.language_hint||'en').toLowerCase().startsWith('fr')?'fr':'en');
const reg=state.conversion||{};
const registrationActive=Boolean(reg.registration_active)||['collecting','awaiting_confirmation','ready_to_submit'].includes(String(reg.registration_status||''));
const registrationGuard=registrationActive&&['consent_to_contact','final_confirmation'].includes(awaited);
const entityByType={GRADE_ONLY:'grade',SUBJECT_ONLY:'subject',LOCATION_ONLY:'location',DAY_ONLY:'day',TIME_ONLY:'time',AFFIRMATION:'confirmation',NEGATION:'confirmation'};
const expectedByType={GRADE_ONLY:'grade',SUBJECT_ONLY:'subject',LOCATION_ONLY:'location',DAY_ONLY:'day',TIME_ONLY:'time'};
const texts={
 en:{SUBJECT_ONLY:['Are you asking whether we offer this subject, or are you giving me the subject you need tutoring in?','Which do you mean: subject availability, or tutoring for a student?'],GRADE_ONLY:['Are you asking whether we support this grade, or are you giving me the student’s grade?','Which do you mean: grade eligibility, or the student’s grade for tutoring?'],DAY_ONLY:['Are you asking whether we offer lessons that day, or do you want to schedule a lesson for that day?','Which do you mean: general availability that day, or a specific scheduling request?'],TIME_ONLY:['Are you asking about lessons around that time, or do you want that specific lesson time?','Which do you mean: general time availability, or a specific time request?'],AFFIRMATION:['What would you like to confirm?','What exactly are you confirming?'],NEGATION:['What would you like to correct or decline?','What exactly are you saying no to?'],DEFAULT:['Could you tell me what you mean by that?','Which part would you like help with?'],FALLBACK:'I’m still not sure what you mean. You can tell me the topic in a few words, or ask to speak with our team.'},
 ar:{SUBJECT_ONLY:['هل تسأل إذا كنا ندرّس هذه المادة، أم أنك تحدد المادة التي تحتاج فيها إلى دروس؟','أيّهما تقصد: توفر تدريس المادة، أم دروس لطالب في هذه المادة؟'],GRADE_ONLY:['هل تسأل إذا كنا ندعم هذا الصف، أم أنك تخبرني بصف الطالب؟','أيّهما تقصد: هل الصف مدعوم، أم أن هذا هو صف الطالب للدروس؟'],DAY_ONLY:['هل تسأل إذا كانت لدينا حصص في هذا اليوم، أم تريد تحديد حصة في هذا اليوم؟','أيّهما تقصد: توفر عام في هذا اليوم، أم طلب موعد محدد؟'],TIME_ONLY:['هل تسأل عن توفر حصص حول هذا الوقت، أم تريد هذا الوقت تحديدًا للحصة؟','أيّهما تقصد: توفر عام في هذا الوقت، أم طلب وقت محدد؟'],AFFIRMATION:['ما الذي تريد تأكيده؟','ما الذي تؤكده تحديدًا؟'],NEGATION:['ما الذي تريد تصحيحه أو رفضه؟','ما الذي تقول له لا تحديدًا؟'],DEFAULT:['هل يمكنك توضيح ما الذي تقصده؟','أي جزء تريد المساعدة فيه؟'],FALLBACK:'ما زلت غير متأكد مما تقصده. يمكنك كتابة الموضوع بكلمات قليلة أو طلب التحدث مع فريقنا.'},
 fr:{SUBJECT_ONLY:['Demandez-vous si nous proposons cette matière, ou indiquez-vous la matière pour laquelle vous cherchez du tutorat ?','Que voulez-vous dire : disponibilité de cette matière, ou tutorat pour un élève ?'],GRADE_ONLY:['Demandez-vous si nous accompagnons ce niveau, ou indiquez-vous le niveau scolaire de l’élève ?','Que voulez-vous dire : admissibilité du niveau, ou niveau scolaire de l’élève pour le tutorat ?'],DAY_ONLY:['Demandez-vous si nous proposons des cours ce jour-là, ou voulez-vous planifier un cours ce jour-là ?','Que voulez-vous dire : disponibilité générale ce jour-là, ou demande d’horaire précise ?'],TIME_ONLY:['Demandez-vous la disponibilité autour de cette heure, ou voulez-vous cette heure précise pour un cours ?','Que voulez-vous dire : disponibilité générale, ou heure précise pour le cours ?'],AFFIRMATION:['Que souhaitez-vous confirmer ?','Que confirmez-vous exactement ?'],NEGATION:['Que souhaitez-vous corriger ou refuser ?','À quoi dites-vous non exactement ?'],DEFAULT:['Pouvez-vous préciser ce que vous voulez dire ?','Sur quel point souhaitez-vous de l’aide ?'],FALLBACK:'Je ne suis toujours pas certain de ce que vous voulez dire. Vous pouvez indiquer le sujet en quelques mots ou demander à parler avec notre équipe.'}
};
const sha=s=>{let h=2166136261;for(const ch of String(s)){h^=ch.codePointAt(0);h=Math.imul(h,16777619);}const a=(h>>>0).toString(16).padStart(8,'0');return (a+a+a+a+a+a+a+a).slice(0,64);};
const emptyState=()=>({schema:'SPM_WU104_CLARIFICATION_STATE_V1',active:false,clarification_key:null,attempt:0,reason_code:'NONE',language:lang,expected_response_type:'NONE',last_intent:null,updated_at:null,raw_message_logged:false,raw_session_logged:false,secret_values_logged:false});
let decision={schema:'SPM_WU104_SHORT_QUERY_DECISION_V1',short_query_detected:short,normalized_length_bucket:bucket,short_query_type:shortType,context_available:Boolean(awaitedRaw),awaited_entity:awaitedRaw,context_binding_status:'NOT_NEEDED',binding_source:'NONE',resolved_intent:intent||null,resolved_entity_type:'NONE',clarification_required:false,clarification_reason:'NONE',clarification_key:null,clarification_attempt:0,clarification_language:lang,safe_action:'CONTINUE',irreversible_action_allowed:false,raw_message_logged:false,raw_session_logged:false,secret_values_logged:false};
let nextClar=emptyState();
let answer=null;
function clarify(reason){
 const key=sha([reason,shortType,awaitedType||'NONE',intent||'NONE'].join('|'));
 const same=Boolean(previous.active)&&previous.clarification_key===key;
 const prevAttempt=same?Math.max(0,Math.min(2,Number(previous.attempt)||0)):0;
 if(same&&prevAttempt>=2){
  decision={...decision,context_binding_status:decision.context_binding_status==='NOT_NEEDED'?'NEEDS_CLARIFICATION':decision.context_binding_status,clarification_required:false,clarification_reason:'LOOP_CAP_REACHED',clarification_key:key,clarification_attempt:2,safe_action:'SAFE_FALLBACK_OR_HUMAN_HELP'};
  nextClar=emptyState();answer=texts[lang].FALLBACK;return;
 }
 const attempt=prevAttempt+1;
 decision={...decision,context_binding_status:decision.context_binding_status==='NOT_NEEDED'?'NEEDS_CLARIFICATION':decision.context_binding_status,clarification_required:true,clarification_reason:reason,clarification_key:key,clarification_attempt:attempt,safe_action:'ASK_ONE_CLARIFYING_QUESTION'};
 nextClar={schema:'SPM_WU104_CLARIFICATION_STATE_V1',active:true,clarification_key:key,attempt,reason_code:reason,language:lang,expected_response_type:({GRADE_ONLY:'grade',SUBJECT_ONLY:'subject',LOCATION_ONLY:'location',DAY_ONLY:'day',TIME_ONLY:'time',AFFIRMATION:'yes_no',NEGATION:'yes_no'})[shortType]||'intent_disambiguation',last_intent:intent||null,updated_at:new Date().toISOString(),raw_message_logged:false,raw_session_logged:false,secret_values_logged:false};
 const pair=texts[lang][shortType]||texts[lang].DEFAULT;answer=pair[Math.min(1,attempt-1)];
}
if(correction){
 if(direct){decision.binding_source='CLASSIFIER_DIRECT';nextClar=emptyState();}
 else clarify(c.ambiguous===true?'CLASSIFIER_AMBIGUOUS':'CLASSIFIER_BELOW_THRESHOLD');
}else if(['AFFIRMATION','NEGATION'].includes(shortType)){
 if(registrationGuard){decision={...decision,context_binding_status:'BOUND_DETERMINISTIC',binding_source:'REGISTRATION_CONFIRMATION_GUARD',resolved_entity_type:'confirmation'};nextClar=emptyState();}
 else{decision.context_binding_status='UNSAFE_TO_BIND';clarify('UNSAFE_YES_NO');}
}else if(['GRADE_ONLY','SUBJECT_ONLY','LOCATION_ONLY','DAY_ONLY','TIME_ONLY'].includes(shortType)){
 const expected=expectedByType[shortType];
 if(expected&&awaitedType===expected){decision={...decision,context_binding_status:'BOUND_DETERMINISTIC',binding_source:'AWAITED_ENTITY',resolved_entity_type:entityByType[shortType]};nextClar=emptyState();}
 else if(awaitedRaw&&!awaitedType){decision.context_binding_status='UNSAFE_TO_BIND';clarify('UNKNOWN_AWAITED_ENTITY');}
 else{decision.context_binding_status='NEEDS_CLARIFICATION';clarify('BARE_FRAGMENT_NO_CONTEXT');}
}else if(direct){decision.binding_source='CLASSIFIER_DIRECT';nextClar=emptyState();}
else clarify(c.ambiguous===true?'CLASSIFIER_AMBIGUOUS':'CLASSIFIER_BELOW_THRESHOLD');
const newState={...state,clarification:nextClar};
let route=j.classifier_route;
let customerClarification=j.customer_clarification_required;
let safeAction=j.classifier_safe_action;
if(decision.safe_action==='ASK_ONE_CLARIFYING_QUESTION'){route='clarify';customerClarification=true;safeAction='ASK_ONE_CLARIFYING_QUESTION';}
else if(decision.safe_action==='SAFE_FALLBACK_OR_HUMAN_HELP'){route='fallback';customerClarification=false;safeAction='SAFE_FALLBACK_OR_HUMAN_HELP';}
return [{json:{...j,sales_state:newState,classifier_route:route,customer_clarification_required:Boolean(customerClarification),irreversible_action_allowed:false,classifier_safe_action:safeAction,wu104_short_query_decision:decision,wu104_clarification_text:answer,wu104_release:'WU104_STAGING_SHORT_QUERY_V1'}}];"""
    decision_node = {
        'id': '10400000-0000-4000-8000-000000000101',
        'name': decision_name,
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': [-80832, 6064],
        'parameters': {'jsCode': decision_js},
    }

    response_name = 'Apply WU104 Clarification Response Override'
    response_js = r"""const j=$input.first().json||{};
const d=j.wu104_short_query_decision||{};
const text=String(j.wu104_clarification_text||'').trim();
if(!text||!['ASK_ONE_CLARIFYING_QUESTION','SAFE_FALLBACK_OR_HUMAN_HELP'].includes(String(d.safe_action||'')))return [{json:j}];
const current=(j.sales_agent_output&&typeof j.sales_agent_output==='object')?j.sales_agent_output:{};
const output={...current,answer_text:text,wu104_response_override:true,wu104_safe_action:d.safe_action};
return [{json:{...j,sales_agent_output:output}}];"""
    response_node = {
        'id': '10400000-0000-4000-8000-000000000102',
        'name': response_name,
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': [-79296, 5536],
        'parameters': {'jsCode': response_js},
    }

    wf['nodes'].extend([decision_node, response_node])

    # All classifier outcomes converge through WU-104 before WU89 entity processing.
    for upstream in [
        'Mark Direct Classification',
        'Mark Clarification Required',
        'Mark Classifier Fallback',
        'Build Catalog Failure Classification',
    ]:
        existing = wf['connections'].get(upstream, {}).get('main', [])
        if existing != [[{'node': 'Capture WU89 Classifier Context', 'type': 'main', 'index': 0}]]:
            raise RuntimeError(f'unexpected classifier convergence for {upstream}: {existing!r}')
        wf['connections'][upstream] = {'main': [[{'node': decision_name, 'type': 'main', 'index': 0}]]}
    wf['connections'][decision_name] = {'main': [[{'node': 'Capture WU89 Classifier Context', 'type': 'main', 'index': 0}]]}

    # Deterministic UX text override occurs after business/telemetry construction but before
    # WU97 redaction and AI-memory persistence. Route/action gating was already forced safe above.
    telemetry = 'Build Telemetry Envelope'
    redact = 'Redact WU97 Observability Telemetry'
    existing = wf['connections'].get(telemetry, {}).get('main', [])
    if existing != [[{'node': redact, 'type': 'main', 'index': 0}]]:
        raise RuntimeError(f'unexpected telemetry/redaction connection: {existing!r}')
    wf['connections'][telemetry] = {'main': [[{'node': response_name, 'type': 'main', 'index': 0}]]}
    wf['connections'][response_name] = {'main': [[{'node': redact, 'type': 'main', 'index': 0}]]}

    return wf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--baseline', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    wf = build(args.baseline)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(wf, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({
        'output': str(out),
        'sha256': sha256(out),
        'node_count': len(wf['nodes']),
        'connection_sources': len(wf['connections']),
        'workflow_name': wf['name'],
        'workflow_active': wf.get('active'),
        'release': 'WU104_STAGING_SHORT_QUERY_V1',
    }, indent=2))


if __name__ == '__main__':
    main()
