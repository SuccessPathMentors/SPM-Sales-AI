#!/usr/bin/env python3
import hashlib
import re
import unicodedata
from datetime import datetime, timezone

SHORT_CHAR_LIMIT = 48
SHORT_TOKEN_LIMIT = 5
VERY_SHORT_CHAR_LIMIT = 12

AFFIRMATION = {
    'yes','y','yeah','yep','ok','okay','sure','correct','نعم','ايوه','أيوه','اه','آه','تمام','صح','oui','ouais','daccord','d’accord'
}
NEGATION = {
    'no','n','nope','not','لا','كلا','مش','non','pas'
}
DAYS = {
    'monday','tuesday','wednesday','thursday','friday','saturday','sunday','today','tomorrow',
    'الاثنين','الإثنين','الثلاثاء','الأربعاء','الاربعاء','الخميس','الجمعة','السبت','الأحد','الاحد','اليوم','غدا','غداً','بكرة',
    'lundi','mardi','mercredi','jeudi','vendredi','samedi','dimanche','aujourd’hui','aujourdhui','demain'
}
SUBJECT_INTENTS = {'subject_inquiry','learning_goal','teacher_availability'}
LOCATION_INTENTS = {'timezone','schedule_request','availability','registration'}

SEMANTIC_PATTERNS = [
    r'\b(?:price|cost|pricing|how much|refund|discount|human|agent|person|login|register|registration|cancel|reschedule|payment)\b',
    r'(?:سعر|السعر|كم\s+السعر|استرجاع|استرداد|خصم|موظف|موظفة|شخص|إنسان|انسان|تسجيل|دفع|إلغاء|الغاء|تغيير\s+موعد)',
    r'\b(?:prix|coût|cout|remboursement|réduction|reduction|agent|humain|conseiller|connexion|inscription|paiement|annuler)\b',
    r'\b(?:tutor|tutoring|lesson|lessons|course|courses|cours|soutien)\b',
    r'(?:مدرس|مدرسة|معلم|معلمة|دروس|حصص|حصة)'
]
CORRECTION_PATTERNS = [
    r'\b(?:actually|correction|correcting|not\s+.+\s+but|instead)\b',
    r'(?:تصحيح|بالعكس|مش\s+.+\s+بل|لا،|لا،\s*)',
    r'\b(?:correction|en fait|plutôt|plutot|pas\s+.+\s+mais)\b'
]


def normalize_text(text):
    text = unicodedata.normalize('NFKC', str(text or '')).strip().lower()
    text = re.sub(r'\s+', ' ', text)
    return text


def lexical_tokens(text):
    return re.findall(r"[\wÀ-ÿء-ي]+", normalize_text(text), flags=re.UNICODE)


def language3(value):
    s = normalize_text(value)
    if s.startswith('ar'):
        return 'ar'
    if s.startswith('fr'):
        return 'fr'
    return 'en'


def length_bucket(text):
    s = normalize_text(text)
    if not s:
        return 'EMPTY'
    if len(s) <= VERY_SHORT_CHAR_LIMIT:
        return 'VERY_SHORT'
    if len(s) <= SHORT_CHAR_LIMIT and len(lexical_tokens(s)) <= SHORT_TOKEN_LIMIT:
        return 'SHORT'
    return 'NOT_SHORT'


def is_short(text):
    s = normalize_text(text)
    return bool(s) and len(s) <= SHORT_CHAR_LIMIT and len(lexical_tokens(s)) <= SHORT_TOKEN_LIMIT


def compact_key(value):
    return re.sub(r'[^\wء-ي]+', '', normalize_text(value), flags=re.UNICODE)


def is_affirmation(text):
    return compact_key(text) in {compact_key(x) for x in AFFIRMATION}


def is_negation(text):
    return compact_key(text) in {compact_key(x) for x in NEGATION}


def is_grade_only(text):
    s = normalize_text(text)
    patterns = [
        r'^(?:grade|gr|g)\s*([1-9]|1[0-2])$',
        r'^([1-9]|1[0-2])(?:st|nd|rd|th)?\s*grade$',
        r'^(?:صف|الصف)\s*(?:ال)?(?:[1-9]|1[0-2]|أول|اول|ثاني|ثالث|رابع|خامس|سادس|سابع|ثامن|تاسع|عاشر|حادي\s*عشر|ثاني\s*عشر)$',
        r'^(?:classe|niveau)\s*(?:[1-9]|1[0-2])$'
    ]
    return any(re.match(p, s, flags=re.IGNORECASE | re.UNICODE) for p in patterns)


def is_time_only(text):
    s = normalize_text(text).replace('٫', ':')
    return bool(re.match(r'^(?:[01]?\d|2[0-3])(?::[0-5]\d)?\s*(?:am|pm|a\.m\.|p\.m\.)?$', s, flags=re.IGNORECASE))


def is_day_only(text):
    return normalize_text(text) in {normalize_text(x) for x in DAYS}


def has_explicit_semantic_language(text):
    s = normalize_text(text)
    return any(re.search(p, s, flags=re.IGNORECASE | re.UNICODE) for p in SEMANTIC_PATTERNS)


def is_correction(text):
    s = normalize_text(text)
    return any(re.search(p, s, flags=re.IGNORECASE | re.UNICODE) for p in CORRECTION_PATTERNS)


def normalize_awaited_entity(value):
    s = normalize_text(value).replace('-', '_').replace(' ', '_')
    aliases = {
        'grade_level':'grade','grade':'grade','student_grade':'grade',
        'subject':'subject','student_subject':'subject',
        'city':'location','location':'location','student_city':'location','parent_city':'location',
        'day':'day','date':'day','lesson_day':'day','schedule_day':'day','scheduling_day':'day','scheduling_date':'day',
        'time':'time','lesson_time':'time','schedule_time':'time','scheduling_time':'time','time_window':'time','scheduling_time_window':'time',
        'consent_to_contact':'confirmation','final_confirmation':'confirmation'
    }
    return aliases.get(s)


def detect_short_type(text, *, classifier_intent=None, awaited_entity=None):
    if not is_short(text):
        return 'NONE'
    if is_affirmation(text):
        return 'AFFIRMATION'
    if is_negation(text):
        return 'NEGATION'
    if is_grade_only(text):
        return 'GRADE_ONLY'
    if is_day_only(text):
        return 'DAY_ONLY'
    if is_time_only(text):
        return 'TIME_ONLY'
    if has_explicit_semantic_language(text):
        return 'SEMANTIC_FRAGMENT'

    intent = str(classifier_intent or '')
    tokens = lexical_tokens(text)
    awaited = normalize_awaited_entity(awaited_entity)
    if awaited == 'subject' or (intent in SUBJECT_INTENTS and 1 <= len(tokens) <= 3):
        return 'SUBJECT_ONLY'
    if awaited == 'location' or (intent in LOCATION_INTENTS and 1 <= len(tokens) <= 3):
        return 'LOCATION_ONLY'
    return 'OTHER_SHORT'


def compatible_entity(short_type, awaited_entity):
    awaited = normalize_awaited_entity(awaited_entity)
    expected = {
        'GRADE_ONLY':'grade',
        'SUBJECT_ONLY':'subject',
        'LOCATION_ONLY':'location',
        'DAY_ONLY':'day',
        'TIME_ONLY':'time'
    }.get(short_type)
    return expected is not None and awaited == expected


def entity_type_for(short_type):
    return {
        'GRADE_ONLY':'grade','SUBJECT_ONLY':'subject','LOCATION_ONLY':'location',
        'DAY_ONLY':'day','TIME_ONLY':'time','AFFIRMATION':'confirmation','NEGATION':'confirmation'
    }.get(short_type, 'NONE')


def expected_response_type(short_type):
    return {
        'GRADE_ONLY':'grade','SUBJECT_ONLY':'subject','LOCATION_ONLY':'location',
        'DAY_ONLY':'day','TIME_ONLY':'time','AFFIRMATION':'yes_no','NEGATION':'yes_no'
    }.get(short_type, 'intent_disambiguation')


def ambiguity_key(reason, short_type, awaited_entity, resolved_intent):
    # Deliberately excludes raw customer text and language, so language switching
    # cannot create an unlimited clarification loop for the same business ambiguity.
    raw = '|'.join([
        str(reason or 'NONE'), str(short_type or 'NONE'),
        str(normalize_awaited_entity(awaited_entity) or 'NONE'),
        str(resolved_intent or 'NONE')
    ])
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def empty_clarification_state(language='en'):
    return {
        'schema':'SPM_WU104_CLARIFICATION_STATE_V1',
        'active':False,
        'clarification_key':None,
        'attempt':0,
        'reason_code':'NONE',
        'language':language3(language),
        'expected_response_type':'NONE',
        'last_intent':None,
        'updated_at':None,
        'raw_message_logged':False,
        'raw_session_logged':False,
        'secret_values_logged':False,
    }


def next_clarification_state(previous, *, key, reason, short_type, language, last_intent):
    previous = previous if isinstance(previous, dict) else {}
    same = bool(previous.get('active')) and previous.get('clarification_key') == key
    prev_attempt = int(previous.get('attempt') or 0) if same else 0
    if same and prev_attempt >= 2:
        return empty_clarification_state(language), 'SAFE_FALLBACK_OR_HUMAN_HELP', 2, 'LOOP_CAP_REACHED'

    attempt = prev_attempt + 1
    state = {
        'schema':'SPM_WU104_CLARIFICATION_STATE_V1',
        'active':True,
        'clarification_key':key,
        'attempt':attempt,
        'reason_code':reason,
        'language':language3(language),
        'expected_response_type':expected_response_type(short_type),
        'last_intent':last_intent or None,
        'updated_at':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'raw_message_logged':False,
        'raw_session_logged':False,
        'secret_values_logged':False,
    }
    return state, 'ASK_ONE_CLARIFYING_QUESTION', attempt, reason


def classifier_is_direct(classification, route):
    c = classification or {}
    confidence = float(c.get('confidence') or 0)
    threshold = float(c.get('threshold') or 0.85)
    return route == 'direct' and c.get('ambiguous') is not True and confidence >= threshold


def resolve_awaited_entity(sales_state):
    s = sales_state if isinstance(sales_state, dict) else {}
    conv = s.get('conversion') if isinstance(s.get('conversion'), dict) else {}
    journey = s.get('journey') if isinstance(s.get('journey'), dict) else {}
    return conv.get('awaiting_field') or journey.get('awaiting_entity') or None


def build_decision(
    text,
    classification,
    classifier_route,
    sales_state=None,
    *,
    language='en',
    registration_confirmation_guard=False,
    yes_no_guard_authorized=False,
    previous_clarification=None,
):
    classification = classification if isinstance(classification, dict) else {}
    resolved_intent = classification.get('spm_intent') or None
    awaited_entity = resolve_awaited_entity(sales_state)
    short = is_short(text)
    short_type = detect_short_type(text, classifier_intent=resolved_intent, awaited_entity=awaited_entity)
    direct = classifier_is_direct(classification, classifier_route)
    lang = language3(classification.get('language') or language)
    correction = is_correction(text)

    decision = {
        'schema':'SPM_WU104_SHORT_QUERY_DECISION_V1',
        'short_query_detected':short,
        'normalized_length_bucket':length_bucket(text),
        'short_query_type':short_type,
        'context_available':bool(awaited_entity),
        'awaited_entity':awaited_entity,
        'context_binding_status':'NOT_NEEDED',
        'binding_source':'NONE',
        'resolved_intent':resolved_intent,
        'resolved_entity_type':'NONE',
        'clarification_required':False,
        'clarification_reason':'NONE',
        'clarification_key':None,
        'clarification_attempt':0,
        'clarification_language':lang,
        'safe_action':'CONTINUE',
        'irreversible_action_allowed':False,
        'raw_message_logged':False,
        'raw_session_logged':False,
        'secret_values_logged':False,
    }

    # Explicit current correction/semantic meaning outranks stale context.
    if correction:
        if direct:
            decision['binding_source'] = 'CLASSIFIER_DIRECT'
            return decision, empty_clarification_state(lang)
        reason = 'CLASSIFIER_AMBIGUOUS' if classification.get('ambiguous') is True else 'CLASSIFIER_BELOW_THRESHOLD'
        return _clarify(decision, previous_clarification, reason, lang)

    # Existing locked registration confirmation/consent guard remains authoritative.
    if short_type in {'AFFIRMATION','NEGATION'}:
        if registration_confirmation_guard or yes_no_guard_authorized:
            decision.update({
                'context_binding_status':'BOUND_DETERMINISTIC',
                'binding_source':'REGISTRATION_CONFIRMATION_GUARD' if registration_confirmation_guard else 'AWAITED_ENTITY',
                'resolved_entity_type':'confirmation',
            })
            return decision, empty_clarification_state(lang)
        decision['context_binding_status'] = 'UNSAFE_TO_BIND'
        return _clarify(decision, previous_clarification, 'UNSAFE_YES_NO', lang)

    bare_types = {'GRADE_ONLY','SUBJECT_ONLY','LOCATION_ONLY','DAY_ONLY','TIME_ONLY'}
    if short_type in bare_types:
        if compatible_entity(short_type, awaited_entity):
            decision.update({
                'context_binding_status':'BOUND_DETERMINISTIC',
                'binding_source':'AWAITED_ENTITY',
                'resolved_entity_type':entity_type_for(short_type),
            })
            return decision, empty_clarification_state(lang)
        if awaited_entity and normalize_awaited_entity(awaited_entity) is None:
            decision['context_binding_status'] = 'UNSAFE_TO_BIND'
            return _clarify(decision, previous_clarification, 'UNKNOWN_AWAITED_ENTITY', lang)
        decision['context_binding_status'] = 'NEEDS_CLARIFICATION'
        return _clarify(decision, previous_clarification, 'BARE_FRAGMENT_NO_CONTEXT', lang)

    # Short explicit semantic request may remain direct. Shortness never forces ambiguity.
    if direct:
        decision['binding_source'] = 'CLASSIFIER_DIRECT'
        return decision, empty_clarification_state(lang)

    # Preserve classifier ambiguity for non-bare short/long inputs.
    if classification.get('ambiguous') is True:
        return _clarify(decision, previous_clarification, 'CLASSIFIER_AMBIGUOUS', lang)
    return _clarify(decision, previous_clarification, 'CLASSIFIER_BELOW_THRESHOLD', lang)


def _clarify(decision, previous_clarification, reason, lang):
    key = ambiguity_key(reason, decision['short_query_type'], decision.get('awaited_entity'), decision.get('resolved_intent'))
    state, safe_action, attempt, final_reason = next_clarification_state(
        previous_clarification,
        key=key,
        reason=reason,
        short_type=decision['short_query_type'],
        language=lang,
        last_intent=decision.get('resolved_intent'),
    )
    decision.update({
        'clarification_required': safe_action == 'ASK_ONE_CLARIFYING_QUESTION',
        'clarification_reason': final_reason,
        'clarification_key':key,
        'clarification_attempt':attempt,
        'safe_action':safe_action,
    })
    if decision['context_binding_status'] == 'NOT_NEEDED':
        decision['context_binding_status'] = 'NEEDS_CLARIFICATION'
    return decision, state


CLARIFY_TEXT = {
    'en': {
        'SUBJECT_ONLY': (
            'Are you asking whether we offer this subject, or are you giving me the subject you need tutoring in?',
            'Which do you mean: subject availability, or tutoring for a student?'
        ),
        'GRADE_ONLY': (
            'Are you asking whether we support this grade, or are you giving me the student’s grade?',
            'Which do you mean: grade eligibility, or the student’s grade for tutoring?'
        ),
        'DAY_ONLY': (
            'Are you asking whether we offer lessons that day, or do you want to schedule a lesson for that day?',
            'Which do you mean: general availability that day, or a specific scheduling request?'
        ),
        'TIME_ONLY': (
            'Are you asking about lessons around that time, or do you want that specific lesson time?',
            'Which do you mean: general time availability, or a specific time request?'
        ),
        'AFFIRMATION': ('What would you like to confirm?', 'What exactly are you confirming?'),
        'NEGATION': ('What would you like to correct or decline?', 'What exactly are you saying no to?'),
        'DEFAULT': ('Could you tell me what you mean by that?', 'Which part would you like help with?'),
        'FALLBACK': 'I’m still not sure what you mean. You can tell me the topic in a few words, or ask to speak with our team.'
    },
    'ar': {
        'SUBJECT_ONLY': (
            'هل تسأل إذا كنا ندرّس هذه المادة، أم أنك تحدد المادة التي تحتاج فيها إلى دروس؟',
            'أيّهما تقصد: توفر تدريس المادة، أم دروس لطالب في هذه المادة؟'
        ),
        'GRADE_ONLY': (
            'هل تسأل إذا كنا ندعم هذا الصف، أم أنك تخبرني بصف الطالب؟',
            'أيّهما تقصد: هل الصف مدعوم، أم أن هذا هو صف الطالب للدروس؟'
        ),
        'DAY_ONLY': (
            'هل تسأل إذا كانت لدينا حصص في هذا اليوم، أم تريد تحديد حصة في هذا اليوم؟',
            'أيّهما تقصد: توفر عام في هذا اليوم، أم طلب موعد محدد؟'
        ),
        'TIME_ONLY': (
            'هل تسأل عن توفر حصص حول هذا الوقت، أم تريد هذا الوقت تحديدًا للحصة؟',
            'أيّهما تقصد: توفر عام في هذا الوقت، أم طلب وقت محدد؟'
        ),
        'AFFIRMATION': ('ما الذي تريد تأكيده؟', 'ما الذي تؤكده تحديدًا؟'),
        'NEGATION': ('ما الذي تريد تصحيحه أو رفضه؟', 'ما الذي تقول له لا تحديدًا؟'),
        'DEFAULT': ('هل يمكنك توضيح ما الذي تقصده؟', 'أي جزء تريد المساعدة فيه؟'),
        'FALLBACK': 'ما زلت غير متأكد مما تقصده. يمكنك كتابة الموضوع بكلمات قليلة أو طلب التحدث مع فريقنا.'
    },
    'fr': {
        'SUBJECT_ONLY': (
            'Demandez-vous si nous proposons cette matière, ou indiquez-vous la matière pour laquelle vous cherchez du tutorat ?',
            'Que voulez-vous dire : disponibilité de cette matière, ou tutorat pour un élève ?'
        ),
        'GRADE_ONLY': (
            'Demandez-vous si nous accompagnons ce niveau, ou indiquez-vous le niveau scolaire de l’élève ?',
            'Que voulez-vous dire : admissibilité du niveau, ou niveau scolaire de l’élève pour le tutorat ?'
        ),
        'DAY_ONLY': (
            'Demandez-vous si nous proposons des cours ce jour-là, ou voulez-vous planifier un cours ce jour-là ?',
            'Que voulez-vous dire : disponibilité générale ce jour-là, ou demande d’horaire précise ?'
        ),
        'TIME_ONLY': (
            'Demandez-vous la disponibilité autour de cette heure, ou voulez-vous cette heure précise pour un cours ?',
            'Que voulez-vous dire : disponibilité générale, ou heure précise pour le cours ?'
        ),
        'AFFIRMATION': ('Que souhaitez-vous confirmer ?', 'Que confirmez-vous exactement ?'),
        'NEGATION': ('Que souhaitez-vous corriger ou refuser ?', 'À quoi dites-vous non exactement ?'),
        'DEFAULT': ('Pouvez-vous préciser ce que vous voulez dire ?', 'Sur quel point souhaitez-vous de l’aide ?'),
        'FALLBACK': 'Je ne suis toujours pas certain de ce que vous voulez dire. Vous pouvez indiquer le sujet en quelques mots ou demander à parler avec notre équipe.'
    }
}


def clarification_text(decision):
    lang = language3(decision.get('clarification_language'))
    table = CLARIFY_TEXT[lang]
    if decision.get('safe_action') == 'SAFE_FALLBACK_OR_HUMAN_HELP':
        return table['FALLBACK']
    kind = decision.get('short_query_type')
    options = table.get(kind, table['DEFAULT'])
    attempt = max(1, min(2, int(decision.get('clarification_attempt') or 1)))
    return options[attempt - 1]


def question_count(text):
    return str(text or '').count('?') + str(text or '').count('؟')
