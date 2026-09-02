#!/usr/bin/env python3
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / 'scripts' / 'wu104' / 'build_short_trial_query_candidate.py'
BASELINE = ROOT / 'n8n' / 'workflows' / 'production' / 'SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json'

spec = importlib.util.spec_from_file_location('wu104_cr10405_builder', BUILDER)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
wf = mod.build(BASELINE)
assert len(wf['nodes']) == 126, len(wf['nodes'])
node = next(n for n in wf['nodes'] if n.get('name') == 'Apply WU104 Short Trial Inquiry Guard')
js = node['parameters']['jsCode']


def run_case(message, intent='free_trial', *, target=True, route='direct', ambiguous=False):
    catalog = []
    if target:
        catalog.append({
            'spm_intent': 'trial_details',
            'required_entities': [],
            'source_gate': 'APPROVED_KB_OR_LOGIC',
            'risk_tier': 'A',
            'sales_stage': 'discovery',
            'min_confidence': 0.88,
        })
    payload = {
        'message': {'raw': message},
        'classifier_route': route,
        'classification': {
            'schema': 'SPM_CLASSIFIER_OUTPUT_V2',
            'spm_intent': intent,
            'secondary_spm_intent': '',
            'confidence': 0.97,
            'threshold': 0.85,
            'ambiguous': ambiguous,
            'required_entities': ['parent_name'],
            'source_gate': 'ORIGINAL',
            'risk_tier': 'B',
            'sales_stage': 'conversion',
            'language': 'en',
            'rationale_code': 'CLEAR_SEMANTIC_MATCH',
        },
        'intent_catalog': catalog,
        'wu104_short_query_decision': {
            'schema': 'SPM_WU104_SHORT_QUERY_DECISION_V1',
            'resolved_intent': intent,
            'binding_source': 'CLASSIFIER_DIRECT',
            'safe_action': 'CONTINUE',
        },
    }
    wrapper = f"""
const PAYLOAD={json.dumps(payload, ensure_ascii=False)};
const $input={{first:()=>({{json:PAYLOAD}})}};
function run(){{
{js}
}}
const out=run();
process.stdout.write(JSON.stringify(out));
"""
    proc = subprocess.run(['node', '-e', wrapper], check=True, capture_output=True, text=True)
    return json.loads(proc.stdout)[0]['json']


for text in ['free trial?', 'trial lesson?', 'حصة مجانية؟', 'حصة تجريبية؟', 'تجربة مجانية؟', 'essai gratuit ?', "cours d'essai ?"]:
    out = run_case(text)
    c = out['classification']
    e = out['wu104_short_semantic_guard']
    d = out['wu104_short_query_decision']
    assert c['spm_intent'] == 'trial_details', (text, c)
    assert c['secondary_spm_intent'] == ''
    assert c['ambiguous'] is False
    assert c['required_entities'] == []
    assert c['source_gate'] == 'APPROVED_KB_OR_LOGIC'
    assert c['risk_tier'] == 'A'
    assert c['sales_stage'] == 'discovery'
    assert c['threshold'] == 0.88
    assert c['confidence'] >= 0.99
    assert c['rationale_code'] == 'WU104_SHORT_TRIAL_INFO_QUESTION'
    assert d['resolved_intent'] == 'trial_details'
    assert d['binding_source'] == 'WU104_SHORT_SEMANTIC_GUARD'
    assert e['status'] == 'REMAP_FREE_TRIAL_QUESTION_TO_TRIAL_DETAILS'
    assert e['applied'] is True
    assert e['raw_message_logged'] is False
    assert e['raw_session_logged'] is False
    assert e['secret_values_logged'] is False

for text in ['I want a free trial.', 'Can I book a free trial?', 'Please start a free trial.', 'I would like a free trial']:
    out = run_case(text)
    assert out['classification']['spm_intent'] == 'free_trial', text
    assert out['wu104_short_semantic_guard']['status'] == 'NO_OVERRIDE', text
    assert out['wu104_short_semantic_guard']['applied'] is False

out = run_case('price?', intent='pricing')
assert out['classification']['spm_intent'] == 'pricing'
assert out['wu104_short_semantic_guard']['status'] == 'NO_OVERRIDE'

out = run_case('free trial?', target=False)
assert out['classification']['spm_intent'] == 'free_trial'
assert out['wu104_short_semantic_guard']['status'] == 'TARGET_INTENT_MISSING_FAIL_CLOSED'
assert out['wu104_short_semantic_guard']['applied'] is False

out = run_case('free trial?', route='clarify', ambiguous=True)
assert out['classification']['spm_intent'] == 'free_trial'
assert out['wu104_short_semantic_guard']['status'] == 'NO_OVERRIDE'

connections = wf['connections']
assert connections['Build WU104 Short Query Decision']['main'] == [[{'node': 'Apply WU104 Short Trial Inquiry Guard', 'type': 'main', 'index': 0}]]
assert connections['Apply WU104 Short Trial Inquiry Guard']['main'] == [[{'node': 'Capture WU89 Classifier Context', 'type': 'main', 'index': 0}]]

print('WU104_CR10405_SHORT_TRIAL_EXECUTABLE_SIGNALS_PASS')
print(json.dumps({
    'node_count': len(wf['nodes']),
    'terse_trial_question_remapped': True,
    'explicit_trial_request_preserved': True,
    'missing_target_fail_closed': True,
    'other_intents_unchanged': True,
    'production_modified': False,
}, indent=2))
