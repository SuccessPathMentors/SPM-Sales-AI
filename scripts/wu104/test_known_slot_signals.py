#!/usr/bin/env python3
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / 'n8n' / 'workflows' / 'production' / 'SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json'
BUILDER = ROOT / 'scripts' / 'wu104' / 'build_known_slot_candidate.py'

spec = importlib.util.spec_from_file_location('wu104_known_slot_exec_test', BUILDER)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
wf = mod.build(BASELINE)
node = next(n for n in wf['nodes'] if n.get('name') == 'Persist WU104 Awaited Context Hint')
js = node['parameters']['jsCode']


def run_case(payload):
    script = "const input=" + json.dumps(payload, ensure_ascii=False) + ";\n"
    script += "const $input={first:()=>({json:input})};\n"
    script += "const fn=()=>{\n" + js + "\n};\n"
    script += "const result=fn(); console.log(JSON.stringify(result[0].json));\n"
    proc = subprocess.run(['node', '-e', script], text=True, capture_output=True, check=True)
    return json.loads(proc.stdout.strip())


# Reproduce the runtime failure shape: one student profile has Grade 8 while the
# validated current-turn subject exists only in entity records. Math must become
# durable state so a later grade correction cannot trigger a subject re-ask.
r = run_case({
    'sales_state': {
        'journey': {}, 'conversion': {},
        'entities': {'global': {}, 'students': [{'student_ref': 'child_1', 'grade': 'Grade 8'}]},
    },
    'entity_extraction': {
        'records': [
            {'entity': 'grade', 'canonical': 'Grade 8', 'status': 'valid'},
            {'entity': 'subject', 'canonical': 'Math', 'status': 'valid'},
        ],
        'student_profiles': [{'student_ref': 'child_1', 'grade': 'Grade 8'}],
    },
    'journey_decision': {'required_missing_fields': []},
})
student = r['sales_state']['entities']['students'][0]
assert student['grade'] == 'Grade 8'
assert student['subjects'] == ['Math']
assert r['wu104_known_slot_reconcile']['subject_reconciled'] is True
assert r['wu104_known_slot_reconcile']['grade_reconciled'] is True

# Current-message grade correction overrides the old grade while preserving the
# already-known Math subject.
r = run_case({
    'sales_state': {
        'journey': {}, 'conversion': {},
        'entities': {'global': {}, 'students': [{'student_ref': 'child_1', 'grade': 'Grade 8', 'subjects': ['Math']}]},
    },
    'entity_extraction': {
        'records': [{'entity': 'grade', 'canonical': 'Grade 9', 'status': 'valid', 'is_correction': True}],
        'student_profiles': [{'student_ref': 'child_1', 'grade': 'Grade 9'}],
        'correction_detected': True,
    },
    'journey_decision': {'required_missing_fields': []},
})
student = r['sales_state']['entities']['students'][0]
assert student['grade'] == 'Grade 9'
assert student['subjects'] == ['Math']
assert r['wu104_known_slot_reconcile']['grade_reconciled'] is True
assert r['wu104_known_slot_reconcile']['subject_reconciled'] is False

# A direct subject correction is authoritative for the sole student.
r = run_case({
    'sales_state': {
        'journey': {}, 'conversion': {},
        'entities': {'global': {}, 'students': [{'student_ref': 'child_1', 'grade': 'Grade 9', 'subjects': ['Math']}]},
    },
    'entity_extraction': {
        'records': [{'entity': 'subject', 'canonical': 'English', 'status': 'valid', 'is_correction': True}],
        'student_profiles': [{'student_ref': 'child_1'}],
        'correction_detected': True,
    },
    'journey_decision': {'required_missing_fields': []},
})
student = r['sales_state']['entities']['students'][0]
assert student['grade'] == 'Grade 9'
assert student['subjects'] == ['English']

# Never guess which child owns an academic slot in multi-student state.
r = run_case({
    'sales_state': {
        'journey': {}, 'conversion': {},
        'entities': {'global': {}, 'students': [
            {'student_ref': 'child_1', 'grade': 'Grade 8', 'subjects': ['Math']},
            {'student_ref': 'child_2', 'grade': 'Grade 6', 'subjects': ['English']},
        ]},
    },
    'entity_extraction': {
        'records': [{'entity': 'grade', 'canonical': 'Grade 9', 'status': 'valid'}],
        'student_profiles': [],
    },
    'journey_decision': {'required_missing_fields': []},
})
assert r['sales_state']['entities']['students'][0]['grade'] == 'Grade 8'
assert r['sales_state']['entities']['students'][1]['grade'] == 'Grade 6'
assert r['wu104_known_slot_reconcile']['skipped_multi_student'] is True

# Needs-validation/rejected academic values are never promoted into durable state.
r = run_case({
    'sales_state': {
        'journey': {}, 'conversion': {},
        'entities': {'global': {}, 'students': [{'student_ref': 'child_1', 'grade': 'Grade 8', 'subjects': ['Math']}]},
    },
    'entity_extraction': {
        'records': [
            {'entity': 'subject', 'canonical': 'UnknownSubject', 'status': 'needs_validation'},
            {'entity': 'grade', 'canonical': 'Grade 99', 'status': 'rejected'},
        ],
        'student_profiles': [{'student_ref': 'child_1'}],
    },
    'journey_decision': {'required_missing_fields': []},
})
student = r['sales_state']['entities']['students'][0]
assert student['grade'] == 'Grade 8'
assert student['subjects'] == ['Math']
assert r['wu104_known_slot_reconcile']['subject_reconciled'] is False
assert r['wu104_known_slot_reconcile']['grade_reconciled'] is False

# Evidence is structural only: no customer text, session identity, or secret values.
ev = r['wu104_known_slot_reconcile']
assert ev['raw_message_logged'] is False
assert ev['raw_session_logged'] is False
assert ev['secret_values_logged'] is False
for forbidden in ['raw_message', 'message', 'session_id', 'correlation_id', 'phone', 'email', 'contact', 'canonical', 'value']:
    assert forbidden not in ev

assert len(wf['nodes']) == 125
assert wf.get('active') is False
print('WU104_KNOWN_SLOT_EXECUTABLE_SIGNALS_PASS')
print(json.dumps({
    'subject_record_promoted_for_single_student': True,
    'grade_correction_preserves_subject': True,
    'subject_correction_authoritative': True,
    'multi_student_guard': True,
    'unvalidated_values_blocked': True,
    'privacy_safe_evidence': True,
}, indent=2))
