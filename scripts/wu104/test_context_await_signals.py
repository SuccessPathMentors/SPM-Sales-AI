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
node = next(n for n in wf['nodes'] if n.get('name') == 'Persist WU104 Awaited Context Hint')
js = node['parameters']['jsCode']


def run_case(payload):
    script = "const input=" + json.dumps(payload, ensure_ascii=False) + ";\n"
    script += "const $input={first:()=>({json:input})};\n"
    script += "const fn=()=>{\n" + js + "\n};\n"
    script += "const result=fn(); console.log(JSON.stringify(result[0].json));\n"
    proc = subprocess.run(['node', '-e', script], text=True, capture_output=True, check=True)
    return json.loads(proc.stdout.strip())


# Discovery: WU90 asks subject next -> persist subject for the next short reply.
r = run_case({
    'sales_state': {'journey': {}, 'conversion': {}},
    'journey_decision': {'required_missing_fields': ['subject', 'learning_goal']},
})
assert r['sales_state']['journey']['awaiting_entity'] == 'subject'
assert r['wu104_await_context_write']['status'] == 'PERSISTED'
assert r['wu104_await_context_write']['source'] == 'WU90_REQUIRED_MISSING_FIELDS'

# Registration remains authoritative even if WU90 also has a discovery missing field.
r = run_case({
    'sales_state': {'journey': {'awaiting_entity': 'subject'}, 'conversion': {'awaiting_field': 'consent_to_contact'}},
    'journey_decision': {'required_missing_fields': ['subject']},
})
assert r['sales_state']['journey']['awaiting_entity'] == 'consent_to_contact'
assert r['wu104_await_context_write']['status'] == 'REGISTRATION_AWAITING_FIELD_AUTHORITATIVE'
assert r['wu104_await_context_write']['source'] == 'CONVERSION_AWAITING_FIELD'

# Supported aliases normalize to the contextual slot family.
r = run_case({
    'sales_state': {'journey': {}, 'conversion': {}},
    'journey_decision': {'required_missing_fields': ['student_city']},
})
assert r['sales_state']['journey']['awaiting_entity'] == 'location'

# When no supported field remains, stale discovery context is cleared.
r = run_case({
    'sales_state': {'journey': {'awaiting_entity': 'subject'}, 'conversion': {}},
    'journey_decision': {'required_missing_fields': []},
})
assert r['sales_state']['journey']['awaiting_entity'] is None
assert r['wu104_await_context_write']['status'] == 'CLEARED_NO_SUPPORTED_MISSING'

# Evidence stays privacy-safe and stores no customer text/session identity.
ev = r['wu104_await_context_write']
assert ev['raw_message_logged'] is False
assert ev['raw_session_logged'] is False
assert ev['secret_values_logged'] is False
for forbidden in ['raw_message', 'message', 'session_id', 'correlation_id', 'phone', 'email', 'contact']:
    assert forbidden not in ev

print('WU104_CONTEXT_AWAIT_EXECUTABLE_SIGNALS_PASS')
print(json.dumps({
    'subject_persisted': True,
    'registration_precedence': True,
    'location_alias': True,
    'stale_context_cleared': True,
    'privacy_safe': True,
}, indent=2))
