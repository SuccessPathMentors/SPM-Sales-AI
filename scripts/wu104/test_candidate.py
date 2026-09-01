#!/usr/bin/env python3
import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / 'n8n' / 'workflows' / 'production' / 'SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json'
BUILDER = ROOT / 'scripts' / 'wu104' / 'build_candidate.py'

spec = importlib.util.spec_from_file_location('wu104_candidate_builder_test', BUILDER)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
wf = mod.build(BASELINE)


def node(name):
    matches = [n for n in wf['nodes'] if n.get('name') == name]
    assert len(matches) == 1, (name, len(matches))
    return matches[0]

assert wf['name'] == 'SPM WU104 Short Query + Ambiguity UX Candidate'
assert wf.get('active') is False
assert len(wf['nodes']) == 123, len(wf['nodes'])
assert len(wf['connections']) == 121, len(wf['connections'])

canonical = node('Build Canonical Session Envelope')['parameters']['jsCode']
assert "workflow_release:'WU104_STAGING_SHORT_QUERY_V1'" in canonical
assert 'PRODUCTION_ACTIVE' not in canonical or 'workflow_mode' in canonical

# Exactly two WU-104 nodes, both deterministic Code nodes.
wu104_nodes = [n for n in wf['nodes'] if 'WU104' in n.get('name','')]
assert [n['name'] for n in wu104_nodes] == [
    'Build WU104 Short Query Decision',
    'Apply WU104 Clarification Response Override',
]
assert all(n['type'] == 'n8n-nodes-base.code' for n in wu104_nodes)

builder = node('Build WU104 Short Query Decision')
js = builder['parameters']['jsCode']
for required in [
    'short_query_detected',
    "safe_action:'CONTINUE'",
    'BOUND_DETERMINISTIC',
    'BARE_FRAGMENT_NO_CONTEXT',
    'UNSAFE_YES_NO',
    'UNKNOWN_AWAITED_ENTITY',
    'LOOP_CAP_REACHED',
    'ASK_ONE_CLARIFYING_QUESTION',
    'SAFE_FALLBACK_OR_HUMAN_HELP',
    'REGISTRATION_CONFIRMATION_GUARD',
    'irreversible_action_allowed:false',
    'raw_message_logged:false',
    'raw_session_logged:false',
    'secret_values_logged:false',
    'sales_state:newState',
]:
    assert required in js, required

# No raw customer/session/contact values are persisted inside clarification state.
clarification_state_fragment = js[js.index("const emptyState"):]
for forbidden_state_field in [
    'session_id:', 'correlation_id:', 'phone:', 'email:', 'parent_name:',
    'student_name:', 'contact:', 'api_key:', 'password:', 'secret:'
]:
    assert forbidden_state_field not in clarification_state_fragment, forbidden_state_field

# All existing classifier outcome branches now converge through WU-104 once.
for upstream in [
    'Mark Direct Classification',
    'Mark Clarification Required',
    'Mark Classifier Fallback',
    'Build Catalog Failure Classification',
]:
    assert wf['connections'][upstream]['main'] == [[{
        'node':'Build WU104 Short Query Decision','type':'main','index':0
    }]], upstream
assert wf['connections']['Build WU104 Short Query Decision']['main'] == [[{
    'node':'Capture WU89 Classifier Context','type':'main','index':0
}]]

# Deterministic response override is placed after telemetry construction and before redaction/memory.
assert wf['connections']['Build Telemetry Envelope']['main'] == [[{
    'node':'Apply WU104 Clarification Response Override','type':'main','index':0
}]]
assert wf['connections']['Apply WU104 Clarification Response Override']['main'] == [[{
    'node':'Redact WU97 Observability Telemetry','type':'main','index':0
}]]
override_js = node('Apply WU104 Clarification Response Override')['parameters']['jsCode']
assert 'sales_agent_output' in override_js
assert 'answer_text:text' in override_js
assert "ASK_ONE_CLARIFYING_QUESTION" in override_js
assert "SAFE_FALLBACK_OR_HUMAN_HELP" in override_js

# Save AI memory still consumes redacted sales_agent_output.answer_text, so the override
# is included in memory without bypassing WU97 redaction.
memory = node('Save AI Message to Chat History')
memory_blob = json.dumps(memory, ensure_ascii=False)
assert 'Redact WU97 Observability Telemetry' in memory_blob
assert 'sales_agent_output.answer_text' in memory_blob

# No second LLM/classifier layer is introduced by WU-104.
llm_types = {
    '@n8n/n8n-nodes-langchain.lmChatOpenAi',
    '@n8n/n8n-nodes-langchain.agent',
}
base_wu102 = mod.load_wu102_builder().build(BASELINE)
base_llm = [(n.get('name'), n.get('type')) for n in base_wu102['nodes'] if n.get('type') in llm_types]
wu104_llm = [(n.get('name'), n.get('type')) for n in wf['nodes'] if n.get('type') in llm_types]
assert wu104_llm == base_llm

# Locked upstream sinks and production namespace behavior are not rewritten by WU-104.
for critical in [
    'Upsert WU102 Unanswered [STAGING]',
    'Upsert WU101 Analytics [STAGING]',
    'Save WU95 Sales State [STAGING NAMESPACE]',
]:
    # WU102 builder may rename production namespace nodes to STAGING; if a particular
    # name changes in the upstream implementation, compare by normalized base parity below.
    pass

# Normalize the two intentional WU-104 insertions + release/name and prove exact WU-102 parity.
def normalized(candidate):
    x = json.loads(json.dumps(candidate))
    x['name'] = base_wu102['name']
    x['nodes'] = [n for n in x['nodes'] if n.get('name') not in {
        'Build WU104 Short Query Decision',
        'Apply WU104 Clarification Response Override',
    }]
    canon = next(n for n in x['nodes'] if n.get('name') == 'Build Canonical Session Envelope')
    canon['parameters']['jsCode'] = canon['parameters']['jsCode'].replace(
        "workflow_release:'WU104_STAGING_SHORT_QUERY_V1'",
        "workflow_release:'WU102_STAGING_UNANSWERED_V1'",
    )
    for upstream in [
        'Mark Direct Classification','Mark Clarification Required','Mark Classifier Fallback','Build Catalog Failure Classification'
    ]:
        x['connections'][upstream] = {'main': [[{'node':'Capture WU89 Classifier Context','type':'main','index':0}]]}
    x['connections'].pop('Build WU104 Short Query Decision', None)
    x['connections']['Build Telemetry Envelope'] = {'main': [[{'node':'Redact WU97 Observability Telemetry','type':'main','index':0}]]}
    x['connections'].pop('Apply WU104 Clarification Response Override', None)
    return x

assert normalized(wf) == base_wu102

# Production workflow ID must never appear as a target instruction in the artifact itself.
artifact_text = json.dumps(wf, ensure_ascii=False)
assert 'CMBMpxX5AqqK2UTn' not in artifact_text

with tempfile.TemporaryDirectory() as td:
    p = Path(td) / 'candidate.json'
    p.write_text(json.dumps(wf, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('WU104_CANDIDATE_SHA256=' + mod.sha256(p))

print('WU104_CANDIDATE_TESTS_PASS')
print(json.dumps({
    'nodes': len(wf['nodes']),
    'connection_sources': len(wf['connections']),
    'new_nodes': 2,
    'normalized_wu102_parity': True,
    'second_llm_added': False,
    'production_artifact_targeted': False,
}, indent=2))
