#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / 'evidence' / 'wu103' / 'chg-wu103-runtime-block-001.regression.json'


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def sha256_text(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


e = json.loads(EVIDENCE.read_text(encoding='utf-8'))
assert e['schema'] == 'SPM_WU103_REGRESSION_EVIDENCE_V1'
assert e['change_id'] == 'chg-wu103-runtime-block-001'
assert e['source_queue_event_id'] == 'uq-mthio2u5-14vfybrnbiu-d8skcnpdvis-1'
assert e['target_family'] == 'FALLBACKS'
assert e['intent_mapping'] == ['out_of_scope']
assert e['overall_result'] == 'PASS'

payload = e['candidate_payload_json']
payload_sha = sha256_text(canonical_json(payload))
assert payload_sha == e['candidate_payload_sha256']
assert payload_sha == 'eb4d4088bc2f3de8db060a036e2cefa868eba9f26d2d2e44b80ef6bf720aac8b'
assert payload['scenario'] == 'out_of_scope'
assert payload['next_action'] == 'redirect_to_spm_scope'
assert payload['status'] == 'ACTIVE'
message = str(payload['message'])
assert 'Success Path Mentors' in message
assert 'tutoring' in message.lower()
for forbidden_phrase in ['not currently available', 'refer your request']:
    assert forbidden_phrase not in message.lower()

cases = e['cases']
assert len(cases) >= 2
ids = [c['case_id'] for c in cases]
assert len(ids) == len(set(ids))
assert all(c['result'] == 'PASS' for c in cases)

positive = next(c for c in cases if c['type'] == 'positive_originating_gap')
assert positive['source_ref'] == 'WU102_UNANSWERED_STAGING:uq-mthio2u5-14vfybrnbiu-d8skcnpdvis-1'
assert positive['observed_intent'] == 'out_of_scope'
assert positive['expected_candidate_selected'] is True
assert positive['observed_intent'] in e['intent_mapping']
assert all(positive['assertions'].values())

negative = next(c for c in cases if c['type'] == 'negative_neighbor')
assert negative['source_ref'] == 'SPM_INTENTS_V2:SPM-002'
assert negative['observed_intent'] == 'subject_inquiry'
assert negative['expected_candidate_selected'] is False
assert negative['observed_intent'] not in e['intent_mapping']
assert all(negative['assertions'].values())

# Privacy boundary: evidence may contain the curated candidate payload and test text,
# but never raw customer/session/contact identifiers or secrets.
raw = canonical_json(e).lower()
for forbidden_key in ['queue_session_key', 'session_id', 'correlation_id', 'email', 'phone', 'api_key', 'password', 'credential']:
    assert f'\"{forbidden_key}\"' not in raw

regression_evidence_sha256 = sha256_text(canonical_json(e))
print('WU103_REGRESSION_EVIDENCE_PASS')
print(json.dumps({
    'change_id': e['change_id'],
    'candidate_payload_sha256': payload_sha,
    'regression_evidence_sha256': regression_evidence_sha256,
    'case_ids': ids,
    'overall_result': e['overall_result'],
}, indent=2))
