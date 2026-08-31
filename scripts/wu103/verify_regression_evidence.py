#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / 'evidence' / 'wu103'


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def sha256_text(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def verify_common(path, expected_change_id, expected_payload_sha):
    e = json.loads(path.read_text(encoding='utf-8'))
    assert e['schema'] == 'SPM_WU103_REGRESSION_EVIDENCE_V1'
    assert e['change_id'] == expected_change_id
    assert e['source_queue_event_id'] == 'uq-mthio2u5-14vfybrnbiu-d8skcnpdvis-1'
    assert e['target_family'] == 'FALLBACKS'
    assert e['intent_mapping'] == ['out_of_scope']
    assert e['overall_result'] == 'PASS'

    payload = e['candidate_payload_json']
    payload_sha = sha256_text(canonical_json(payload))
    assert payload_sha == e['candidate_payload_sha256']
    assert payload_sha == expected_payload_sha
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

    # Evidence can contain curated candidate/test text, but never customer/session/contact identity or secrets.
    raw = canonical_json(e).lower()
    for forbidden_key in [
        'queue_session_key', 'session_id', 'correlation_id', 'email', 'phone',
        'api_key', 'password', 'credential'
    ]:
        assert f'\"{forbidden_key}\"' not in raw

    return e, payload_sha, ids, sha256_text(canonical_json(e))


v1_path = EVIDENCE_DIR / 'chg-wu103-runtime-block-001.regression.json'
v1, v1_payload_sha, v1_ids, v1_evidence_sha = verify_common(
    v1_path,
    'chg-wu103-runtime-block-001',
    'eb4d4088bc2f3de8db060a036e2cefa868eba9f26d2d2e44b80ef6bf720aac8b',
)
assert v1.get('change_type') in (None, 'ADD')
assert 'record_id' not in v1['candidate_payload_json']

v2_path = EVIDENCE_DIR / 'chg-wu103-runtime-update-002.regression.json'
v2, v2_payload_sha, v2_ids, v2_evidence_sha = verify_common(
    v2_path,
    'chg-wu103-runtime-update-002',
    'd0f48f467a9465de5d2ba5e5b830b913d2955f6d5384eb23cad7210ae0bc0389',
)
assert v2['change_type'] == 'UPDATE'
assert v2['target_record_id'] == 'FB-WU103-3BDF51AC9F7B'
assert v2['candidate_payload_json']['record_id'] == v2['target_record_id']
assert v2['base_revision'] == 'v1'
assert v2['candidate_revision'] == 'v2'
assert v2['base_fingerprint_sha256'] == 'eb4d4088bc2f3de8db060a036e2cefa868eba9f26d2d2e44b80ef6bf720aac8b'
assert v2['supersedes_change_id'] == 'chg-wu103-runtime-block-001'
lineage = next(c for c in v2['cases'] if c['type'] == 'update_lineage')
assert lineage['source_ref'] == 'WU103_KB_SHADOW_STAGING:FB-WU103-3BDF51AC9F7B:v1'
assert lineage['expected_candidate_selected'] is True
assert all(lineage['assertions'].values())

print('WU103_REGRESSION_EVIDENCE_PASS')
print(json.dumps({
    'verified_changes': [
        {
            'change_id': v1['change_id'],
            'candidate_payload_sha256': v1_payload_sha,
            'regression_evidence_sha256': v1_evidence_sha,
            'case_ids': v1_ids,
            'overall_result': v1['overall_result'],
        },
        {
            'change_id': v2['change_id'],
            'candidate_payload_sha256': v2_payload_sha,
            'regression_evidence_sha256': v2_evidence_sha,
            'case_ids': v2_ids,
            'overall_result': v2['overall_result'],
            'base_revision': v2['base_revision'],
            'candidate_revision': v2['candidate_revision'],
            'base_fingerprint_sha256': v2['base_fingerprint_sha256'],
        },
    ]
}, indent=2))
