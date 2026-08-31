#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / 'evidence' / 'wu103' / 'chg-wu103-runtime-legacy-004.regression.json'

def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

def sha256_text(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

e = json.loads(PATH.read_text(encoding='utf-8'))
assert e['schema'] == 'SPM_WU103_REGRESSION_EVIDENCE_V1'
assert e['change_id'] == 'chg-wu103-runtime-legacy-004'
assert e['change_type'] == 'UPDATE'
assert e['source_queue_event_id'] == 'uq-mthio2u5-14vfybrnbiu-d8skcnpdvis-1'
assert e['target_family'] == 'FALLBACKS'
assert e['target_record_id'] == 'FB-003'
assert e['base_revision'] == 'LEGACY_UNVERSIONED'
assert e['candidate_revision'] == 'v1'
assert e['base_fingerprint_sha256'] == '2b440d9609f77b23e6759f7ba03e3553ced3925a538dcb69646846491400f8de'
assert e['supersedes_change_id'] is None
assert e['intent_mapping'] == ['out_of_scope']
assert e['overall_result'] == 'PASS'

payload = e['candidate_payload_json']
payload_sha = sha256_text(canonical_json(payload))
assert payload_sha == e['candidate_payload_sha256']
assert payload_sha == '502062d5301f724effdc3d4ab8599e79bcfb3e06d53193eae70d05a6b465518b'
assert payload == {
    'language': 'en',
    'message': 'I can help with questions related to Success Path Mentors tutoring services. Please ask me about tutoring, subjects, trials, scheduling, or support.',
    'next_action': 'redirect_to_spm_scope',
    'record_id': 'FB-003',
    'scenario': 'no_answer',
    'status': 'ACTIVE',
}
for forbidden_phrase in ['not currently available', 'refer your request']:
    assert forbidden_phrase not in payload['message'].lower()

cases = e['cases']
ids = [c['case_id'] for c in cases]
assert len(ids) >= 3 and len(ids) == len(set(ids))
assert all(c['result'] == 'PASS' for c in cases)

positive = next(c for c in cases if c['type'] == 'positive_originating_gap')
assert positive['source_ref'] == 'WU102_UNANSWERED_STAGING:uq-mthio2u5-14vfybrnbiu-d8skcnpdvis-1'
assert positive['observed_intent'] == 'out_of_scope'
assert positive['expected_candidate_selected'] is True
assert all(positive['assertions'].values())

negative = next(c for c in cases if c['type'] == 'negative_neighbor')
assert negative['source_ref'] == 'SPM_INTENTS_V2:SPM-002'
assert negative['observed_intent'] == 'subject_inquiry'
assert negative['expected_candidate_selected'] is False
assert all(negative['assertions'].values())

base = next(c for c in cases if c['type'] == 'legacy_base_lineage')
assert base['source_ref'] == 'FALLBACKS:FB-003'
assert base['expected_candidate_selected'] is True
assert all(base['assertions'].values())

raw = canonical_json(e).lower()
for forbidden_key in ['queue_session_key','session_id','correlation_id','email','phone','api_key','password','credential']:
    assert f'\"{forbidden_key}\"' not in raw

evidence_sha = sha256_text(canonical_json(e))
print('WU103_LEGACY_REGRESSION_EVIDENCE_READY')
print(json.dumps({
    'change_id': e['change_id'],
    'candidate_payload_sha256': payload_sha,
    'regression_evidence_sha256': evidence_sha,
    'case_ids': ids,
    'overall_result': e['overall_result'],
    'base_revision': e['base_revision'],
    'candidate_revision': e['candidate_revision'],
    'base_fingerprint_sha256': e['base_fingerprint_sha256'],
}, indent=2))
