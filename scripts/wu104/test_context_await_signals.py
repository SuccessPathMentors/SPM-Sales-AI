#!/usr/bin/env python3
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / 'n8n' / 'workflows' / 'production' / 'SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json'
WRAPPER = ROOT / 'scripts' / 'wu104' / 'build_context_await_candidate.py'

spec = importlib.util.spec_from_file_location('wu104_context_exec_test', WRAPPER)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
wf = mod.build(BASELINE)
early_node = next(n for n in wf['nodes'] if n.get('name') == 'Persist WU104 Awaited Context Hint')
final_node = next(n for n in wf['nodes'] if n.get('name') == 'Persist WU104 Final Asked Field')
early_js = early_node['parameters']['jsCode']
final_js = final_node['parameters']['jsCode']


def run_js(js, payload):
    script = "const input=" + json.dumps(payload, ensure_ascii=False) + ";\n"
    script += "const $input={first:()=>({json:input})};\n"
    script += "const fn=()=>{\n" + js + "\n};\n"
    script += "const result=fn(); console.log(JSON.stringify(result[0].json));\n"
    proc = subprocess.run(['node', '-e', script], text=True, capture_output=True, check=True)
    return json.loads(proc.stdout.strip())


# Early discovery: WU90 asks subject next -> persist subject for the next short reply.
r = run_js(early_js, {
    'sales_state': {'journey': {}, 'conversion': {}},
    'journey_decision': {'required_missing_fields': ['subject', 'learning_goal']},
})
assert r['sales_state']['journey']['awaiting_entity'] == 'subject'
assert r['wu104_await_context_write']['status'] == 'PERSISTED'
assert r['wu104_await_context_write']['source'] == 'WU90_REQUIRED_MISSING_FIELDS'

# Registration remains authoritative even if WU90 also has a discovery missing field.
r = run_js(early_js, {
    'sales_state': {'journey': {'awaiting_entity': 'subject'}, 'conversion': {'awaiting_field': 'consent_to_contact'}},
    'journey_decision': {'required_missing_fields': ['subject']},
})
assert r['sales_state']['journey']['awaiting_entity'] == 'consent_to_contact'
assert r['wu104_await_context_write']['status'] == 'REGISTRATION_AWAITING_FIELD_AUTHORITATIVE'

# Final rendered question can deterministically identify subject even when intake next_field is absent.
r = run_js(final_js, {
    'sales_state': {'journey': {}, 'conversion': {}},
    'journey_decision': {'required_missing_fields': []},
    'intake_question_candidate': None,
    'sales_agent_output': {
        'answer_text': 'We offer online one-to-one tutoring in Mathematics and English for Grade 8 students. Could you please specify which subject your son needs help with?',
        'purposeful_question': None,
    },
    'wu104_short_query_decision': {'clarification_required': False, 'safe_action': 'CONTINUE'},
})
assert r['sales_state']['journey']['awaiting_entity'] == 'subject'
assert r['wu104_final_asked_field_write']['status'] == 'PERSISTED_FROM_FINAL_QUESTION'
assert r['wu104_final_asked_field_write']['source'] == 'FINAL_RESPONSE_QUESTION_PATTERN'
assert r['wu104_final_asked_field_write']['final_question_field_detected'] is True

# WU104 ambiguity clarification must never be converted into a slot-binding instruction.
r = run_js(final_js, {
    'sales_state': {'journey': {'awaiting_entity': 'subject'}, 'conversion': {}},
    'journey_decision': {'required_missing_fields': []},
    'intake_question_candidate': {'next_field': 'subject'},
    'sales_agent_output': {
        'answer_text': 'Are you asking whether we offer this subject, or are you giving me the subject you need tutoring in?',
        'purposeful_question': None,
    },
    'wu104_short_query_decision': {'clarification_required': True, 'safe_action': 'ASK_ONE_CLARIFYING_QUESTION'},
})
assert r['sales_state']['journey']['awaiting_entity'] is None
assert r['wu104_final_asked_field_write']['status'] == 'WU104_CLARIFICATION_NOT_SLOT_BINDABLE'
assert r['wu104_final_asked_field_write']['wu104_clarification_guard'] is True

# Intake next_field still works when the final question is explicit and safe.
r = run_js(final_js, {
    'sales_state': {'journey': {}, 'conversion': {}},
    'journey_decision': {'required_missing_fields': []},
    'intake_question_candidate': {'next_field': 'grade'},
    'sales_agent_output': {'answer_text': 'What is the student grade?', 'purposeful_question': None},
    'wu104_short_query_decision': {'clarification_required': False, 'safe_action': 'CONTINUE'},
})
assert r['sales_state']['journey']['awaiting_entity'] == 'grade'

# Registration precedence also applies at final write.
r = run_js(final_js, {
    'sales_state': {'journey': {'awaiting_entity': 'subject'}, 'conversion': {'awaiting_field': 'consent_to_contact'}},
    'journey_decision': {'required_missing_fields': ['subject']},
    'intake_question_candidate': {'next_field': 'subject'},
    'sales_agent_output': {'answer_text': 'Which subject does the student need help with?', 'purposeful_question': None},
    'wu104_short_query_decision': {'clarification_required': False, 'safe_action': 'CONTINUE'},
})
assert r['sales_state']['journey']['awaiting_entity'] == 'consent_to_contact'
assert r['wu104_final_asked_field_write']['status'] == 'REGISTRATION_AWAITING_FIELD_AUTHORITATIVE'

# When no supported final question remains, stale discovery context is cleared.
r = run_js(final_js, {
    'sales_state': {'journey': {'awaiting_entity': 'subject'}, 'conversion': {}},
    'journey_decision': {'required_missing_fields': []},
    'intake_question_candidate': None,
    'sales_agent_output': {'answer_text': 'We can help with tutoring.', 'purposeful_question': None},
    'wu104_short_query_decision': {'clarification_required': False, 'safe_action': 'CONTINUE'},
})
assert r['sales_state']['journey']['awaiting_entity'] is None

# Evidence stays privacy-safe and stores no customer text/session identity.
for ev_name in ['wu104_final_asked_field_write']:
    ev = r[ev_name]
    assert ev['raw_message_logged'] is False
    assert ev['raw_session_logged'] is False
    assert ev['secret_values_logged'] is False
    for forbidden in ['raw_message', 'message', 'session_id', 'correlation_id', 'phone', 'email', 'contact']:
        assert forbidden not in ev

print('WU104_CONTEXT_AWAIT_EXECUTABLE_SIGNALS_PASS')
print(json.dumps({
    'early_subject_persisted': True,
    'final_subject_question_detected': True,
    'wu104_ambiguity_guarded': True,
    'registration_precedence': True,
    'stale_context_cleared': True,
    'privacy_safe': True,
}, indent=2))
