#!/usr/bin/env python3
from core import (
    build_decision,
    clarification_text,
    detect_short_type,
    empty_clarification_state,
    is_short,
    question_count,
)


def cls(intent, *, confidence=0.98, ambiguous=False, language='en', threshold=0.85):
    return {
        'spm_intent': intent,
        'confidence': confidence,
        'ambiguous': ambiguous,
        'language': language,
        'threshold': threshold,
    }


def decide(text, intent, *, route='direct', state=None, lang='en', previous=None, ambiguous=False, confidence=0.98, reg=False, yesno=False):
    return build_decision(
        text,
        cls(intent, confidence=confidence, ambiguous=ambiguous, language=lang),
        route,
        state or {},
        language=lang,
        registration_confirmation_guard=reg,
        yes_no_guard_authorized=yesno,
        previous_clarification=previous,
    )

# Shortness is a feature, never a reason by itself to clarify.
for text, intent, lang in [
    ('price?', 'pricing', 'en'),
    ('السعر؟', 'pricing', 'ar'),
    ('prix ?', 'pricing', 'fr'),
    ('human?', 'human_handoff', 'en'),
    ('موظف؟', 'human_handoff', 'ar'),
    ('agent humain ?', 'human_handoff', 'fr'),
    ('refund?', 'refund_policy', 'en'),
]:
    d, s = decide(text, intent, lang=lang)
    assert d['short_query_detected'] is True, (text, d)
    assert d['safe_action'] == 'CONTINUE', (text, d)
    assert d['clarification_required'] is False
    assert d['binding_source'] == 'CLASSIFIER_DIRECT'
    assert d['resolved_intent'] == intent
    assert d['irreversible_action_allowed'] is False
    assert s['active'] is False

assert is_short('This is a much longer customer sentence asking a detailed question about tutoring availability next week') is False

# Bare subject fragment in fresh session must not silently turn into a student goal/action.
d1, s1 = decide('Math', 'subject_inquiry')
assert d1['short_query_type'] == 'SUBJECT_ONLY'
assert d1['context_binding_status'] == 'NEEDS_CLARIFICATION'
assert d1['clarification_reason'] == 'BARE_FRAGMENT_NO_CONTEXT'
assert d1['safe_action'] == 'ASK_ONE_CLARIFYING_QUESTION'
assert d1['clarification_attempt'] == 1
assert question_count(clarification_text(d1)) == 1
assert s1['active'] is True

# Awaiting subject allows deterministic binding.
d, s = decide('Math', 'subject_inquiry', state={'conversion': {'awaiting_field': 'subject'}})
assert d['short_query_type'] == 'SUBJECT_ONLY'
assert d['context_binding_status'] == 'BOUND_DETERMINISTIC'
assert d['binding_source'] == 'AWAITED_ENTITY'
assert d['resolved_entity_type'] == 'subject'
assert d['clarification_required'] is False
assert s['active'] is False

# Grade fragment: fresh session clarifies; awaited grade binds.
d, _ = decide('Grade 10', 'grade_inquiry')
assert d['short_query_type'] == 'GRADE_ONLY'
assert d['clarification_required'] is True

d, _ = decide('Grade 10', 'grade_inquiry', state={'journey': {'awaiting_entity': 'grade_level'}})
assert d['context_binding_status'] == 'BOUND_DETERMINISTIC'
assert d['resolved_entity_type'] == 'grade'

# Day fragment: never invent booking without context; binds only to scheduling day/date.
d, _ = decide('Saturday', 'schedule_request')
assert d['short_query_type'] == 'DAY_ONLY'
assert d['clarification_required'] is True
assert d['context_binding_status'] == 'NEEDS_CLARIFICATION'

d, _ = decide('Saturday', 'schedule_request', state={'conversion': {'awaiting_field': 'scheduling_day'}})
assert d['context_binding_status'] == 'BOUND_DETERMINISTIC'
assert d['resolved_entity_type'] == 'day'

# Time fragment same behavior.
d, _ = decide('6 PM', 'schedule_request')
assert d['short_query_type'] == 'TIME_ONLY'
assert d['clarification_required'] is True

d, _ = decide('6 PM', 'schedule_request', state={'conversion': {'awaiting_field': 'time_window'}})
assert d['context_binding_status'] == 'BOUND_DETERMINISTIC'
assert d['resolved_entity_type'] == 'time'

# Location fragment can bind when explicitly awaited.
d, _ = decide('Toronto', 'timezone', state={'conversion': {'awaiting_field': 'city'}})
assert d['short_query_type'] == 'LOCATION_ONLY'
assert d['context_binding_status'] == 'BOUND_DETERMINISTIC'
assert d['resolved_entity_type'] == 'location'

# Fresh yes/no is unsafe. Locked registration confirmation guard permits contextual binding,
# but WU-104 still never grants irreversible permission.
for answer, kind in [('yes','AFFIRMATION'), ('no','NEGATION'), ('نعم','AFFIRMATION'), ('non','NEGATION')]:
    d, _ = decide(answer, 'registration', lang='ar' if answer == 'نعم' else ('fr' if answer == 'non' else 'en'))
    assert d['short_query_type'] == kind
    assert d['context_binding_status'] == 'UNSAFE_TO_BIND'
    assert d['clarification_required'] is True
    assert d['clarification_reason'] == 'UNSAFE_YES_NO'

for answer in ['yes', 'no']:
    d, _ = decide(answer, 'registration', state={'conversion': {'awaiting_field': 'final_confirmation'}}, reg=True)
    assert d['context_binding_status'] == 'BOUND_DETERMINISTIC'
    assert d['binding_source'] == 'REGISTRATION_CONFIRMATION_GUARD'
    assert d['resolved_entity_type'] == 'confirmation'
    assert d['clarification_required'] is False
    assert d['irreversible_action_allowed'] is False

# Unknown awaiting field is explicitly unsafe, never fuzzy-bound.
d, _ = decide('Math', 'subject_inquiry', state={'conversion': {'awaiting_field': 'custom_unknown_field'}})
assert d['context_binding_status'] == 'UNSAFE_TO_BIND'
assert d['clarification_reason'] == 'UNKNOWN_AWAITED_ENTITY'

# Explicit current meaning outranks stale awaited entity.
d, _ = decide('price?', 'pricing', state={'conversion': {'awaiting_field': 'grade'}})
assert d['safe_action'] == 'CONTINUE'
assert d['binding_source'] == 'CLASSIFIER_DIRECT'
assert d['resolved_intent'] == 'pricing'
assert d['resolved_entity_type'] == 'NONE'

# Current correction wins; do not consume it as a generic awaited slot.
d, _ = decide('Actually Grade 11', 'grade_inquiry', state={'conversion': {'awaiting_field': 'grade'}})
assert d['safe_action'] == 'CONTINUE'
assert d['binding_source'] == 'CLASSIFIER_DIRECT'
assert d['context_binding_status'] == 'NOT_NEEDED'

# Clear unrelated current support intent wins over stale prior commercial state.
d, _ = decide("I can't log in", 'account_login', state={'journey': {'last_intent': 'pricing'}})
assert d['safe_action'] == 'CONTINUE'
assert d['resolved_intent'] == 'account_login'

# Long-form direct classification remains direct; WU-104 doesn't force short behavior.
long_text = 'How do you make sure your tutors are qualified and experienced for Grade 10 students?'
d, _ = decide(long_text, 'teacher_quality')
assert d['short_query_detected'] is False
assert d['short_query_type'] == 'NONE'
assert d['safe_action'] == 'CONTINUE'

# Existing classifier ambiguity / below-threshold remains observable and safe.
d, _ = decide('I need help with tutoring options', 'learning_goal', route='clarify', ambiguous=True, confidence=0.62)
assert d['clarification_required'] is True
assert d['clarification_reason'] == 'CLASSIFIER_AMBIGUOUS'
assert d['safe_action'] == 'ASK_ONE_CLARIFYING_QUESTION'
assert d['irreversible_action_allowed'] is False

# Clarification loop: ask #1, ask #2 with materially different text, then no third question.
d1, s1 = decide('Math', 'subject_inquiry')
q1 = clarification_text(d1)
d2, s2 = decide('Math', 'subject_inquiry', previous=s1)
q2 = clarification_text(d2)
d3, s3 = decide('Math', 'subject_inquiry', previous=s2)
q3 = clarification_text(d3)
assert d1['clarification_attempt'] == 1 and d1['safe_action'] == 'ASK_ONE_CLARIFYING_QUESTION'
assert d2['clarification_attempt'] == 2 and d2['safe_action'] == 'ASK_ONE_CLARIFYING_QUESTION'
assert q1 != q2
assert question_count(q1) == 1 and question_count(q2) == 1
assert d3['clarification_attempt'] == 2
assert d3['safe_action'] == 'SAFE_FALLBACK_OR_HUMAN_HELP'
assert d3['clarification_required'] is False
assert d3['clarification_reason'] == 'LOOP_CAP_REACHED'
assert question_count(q3) == 0
assert s3['active'] is False and s3['attempt'] == 0

# Language change does not create a new ambiguity key / unlimited loop.
d1, s1 = decide('Math', 'subject_inquiry', lang='en')
d2, s2 = decide('Math', 'subject_inquiry', lang='fr', previous=s1)
assert d1['clarification_key'] == d2['clarification_key']
assert d2['clarification_attempt'] == 2
assert d2['clarification_language'] == 'fr'

# Direct resolution resets stale clarification state.
d_resolved, s_resolved = decide('price?', 'pricing', previous=s1)
assert d_resolved['safe_action'] == 'CONTINUE'
assert s_resolved == empty_clarification_state('en')

# EN/AR/FR clarification text parity: exactly one question for attempt 1/2.
for text, intent, lang in [('Math','subject_inquiry','en'), ('رياضيات','subject_inquiry','ar'), ('Mathématiques','subject_inquiry','fr')]:
    d1, st1 = decide(text, intent, lang=lang)
    d2, _ = decide(text, intent, lang=lang, previous=st1)
    assert d1['clarification_language'] == lang
    assert d2['clarification_language'] == lang
    assert question_count(clarification_text(d1)) == 1
    assert question_count(clarification_text(d2)) == 1

# Basic detector sanity.
assert detect_short_type('Grade 10', classifier_intent='grade_inquiry') == 'GRADE_ONLY'
assert detect_short_type('Saturday', classifier_intent='schedule_request') == 'DAY_ONLY'
assert detect_short_type('6 PM', classifier_intent='schedule_request') == 'TIME_ONLY'

print('WU104_CORE_TESTS_PASS')
print({
    'short_semantics_direct': True,
    'bare_fragment_guard': True,
    'awaited_entity_binding': True,
    'yes_no_guard_parity': True,
    'clarification_loop_cap': True,
    'en_ar_fr_question_parity': True,
})
