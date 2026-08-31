#!/usr/bin/env python3
import json
from copy import deepcopy
from core import (
    allocate_logical_id, automation_may_write_approval_field, business_truth_gate,
    candidate_key, candidate_payload_hash, canonical_candidate_payload,
    parse_candidate_payload, payload_hash, publish_gate, regression_evidence_gate,
    resolve_staging_base, row_fingerprint, sheet_safe_text, stale_base,
    transition_allowed, validate_family_payload,
)

k1 = candidate_key('uq-test-1', 'FAQ', 'UPDATE', 'FAQ-001')
k2 = candidate_key('uq-test-1', 'FAQ', 'UPDATE', 'FAQ-001')
assert k1 == k2 and len(k1) == 64
assert k1 != candidate_key('uq-test-1', 'FAQ', 'UPDATE', 'FAQ-002')
assert k1 != candidate_key('uq-test-1', 'FAQ', 'ADD', None)

faq = {'record_id':'FAQ-001','category':'trial','language':'en','question':'Q?','answer':'A.','keywords':'trial','priority':'1','status':'ACTIVE','last_reviewed':'2026-08-06'}
validate_family_payload('FAQ', faq)
try:
    validate_family_payload('FAQ', {**faq, 'evil_field':'x'})
    raise AssertionError('unknown field accepted')
except ValueError as e:
    assert str(e).startswith('UNKNOWN_PAYLOAD_FIELDS')

payload_json = json.dumps(faq, ensure_ascii=False)
parsed = parse_candidate_payload('FAQ', payload_json)
assert parsed == faq
canonical = canonical_candidate_payload('FAQ', payload_json)
assert json.loads(canonical) == faq
candidate_hash_1 = candidate_payload_hash('FAQ', payload_json)
assert candidate_hash_1 == payload_hash('FAQ', faq)
edited = {**faq, 'answer':'A revised human-curated answer.'}
candidate_hash_2 = candidate_payload_hash('FAQ', json.dumps(edited))
assert candidate_hash_2 != candidate_hash_1

try:
    parse_candidate_payload('FAQ', '{bad json')
    raise AssertionError('invalid JSON accepted')
except ValueError as e:
    assert str(e) == 'CANDIDATE_PAYLOAD_JSON_INVALID'
try:
    parse_candidate_payload('FAQ', json.dumps({**faq, 'raw_question':'customer text'}))
    raise AssertionError('queue/raw field accepted as knowledge payload')
except ValueError as e:
    assert str(e).startswith('UNKNOWN_PAYLOAD_FIELDS')

faq_add = {k:v for k,v in faq.items() if k != 'record_id'}
parse_candidate_payload('FAQ', json.dumps(faq_add), allow_missing_id=True)
try:
    parse_candidate_payload('FAQ', json.dumps(faq_add), allow_missing_id=False)
    raise AssertionError('UPDATE payload without target id accepted')
except ValueError as e:
    assert str(e) == 'MISSING_TARGET_ID_FIELD'

assert sheet_safe_text('=IMPORTXML("x","y")').startswith("'=")
assert sheet_safe_text('normal text') == 'normal text'
f1 = row_fingerprint('FAQ', faq)
f2 = row_fingerprint('FAQ', {**faq, 'last_reviewed':'2026-08-31'})
assert f1 == f2
assert payload_hash('FAQ', faq) == payload_hash('FAQ', deepcopy(faq))

assert transition_allowed('DRAFT', 'HUMAN_APPROVED')
assert not transition_allowed('DRAFT', 'TEST_PASSED')
assert not transition_allowed('DRAFT', 'PUBLISHED')
assert transition_allowed('HUMAN_APPROVED', 'TEST_PASSED')
assert transition_allowed('TEST_PASSED', 'RELEASE_APPROVED')
assert transition_allowed('RELEASE_APPROVED', 'PUBLISHED')
for field in ['review_decision','business_truth_approval','release_approval_status']:
    assert automation_may_write_approval_field(field) is False
assert automation_may_write_approval_field('regression_status') is True

assert business_truth_gate('FAQ', False, 'WEBSITE', 'SRC-01')[0] is True
assert business_truth_gate('FAQ', False, 'WEBSITE', '') == (False, 'SOURCE_REFERENCE_REQUIRED')
assert business_truth_gate('FAQ', False, 'BAD_SOURCE', 'SRC') == (False, 'SOURCE_TYPE_REQUIRED')
assert business_truth_gate('PACKAGES', False, 'OWNER_DECISION', 'SRC-009')[0] is False
assert business_truth_gate('PACKAGES', True, 'WEBSITE', 'SRC-01')[0] is False
assert business_truth_gate('PACKAGES', True, 'OWNER_DECISION', 'SRC-009')[0] is True
assert business_truth_gate('POLICIES', True, 'INTERNAL_APPROVED_SOURCE', 'approved-policy-1')[0] is True

canonical_rows = [faq]
base_legacy = resolve_staging_base('FAQ', 'FAQ-001', canonical_rows, [])
assert base_legacy['base_source'] == 'CANONICAL_LEGACY'
assert base_legacy['base_revision'] == 'LEGACY_UNVERSIONED'
assert base_legacy['base_fingerprint_sha256'] == f1
assert stale_base(f1, base_legacy) is False
assert stale_base('0' * 64, base_legacy) is True
shadow = [{'target_family':'FAQ','logical_record_id':'FAQ-001','revision':'v1','change_id':'chg-one','source_queue_event_id':'uq-test-1','payload_json':'{}','payload_sha256':'a' * 64,'base_fingerprint_sha256':f1,'record_status':'ACTIVE','published_at':'2026-08-31T00:00:00Z','supersedes_revision':None}]
base_shadow = resolve_staging_base('FAQ', 'FAQ-001', canonical_rows, shadow)
assert base_shadow['base_source'] == 'SHADOW'
assert base_shadow['base_revision'] == 'v1'
assert base_shadow['base_fingerprint_sha256'] == 'a' * 64
try:
    resolve_staging_base('FAQ', 'FAQ-001', canonical_rows, shadow + [dict(shadow[0], change_id='chg-two')])
    raise AssertionError('non-unique shadow base accepted')
except ValueError as e:
    assert str(e) == 'BASE_RECORD_NOT_UNIQUE'

id1 = allocate_logical_id('FAQ', 'chg-test-one')
id2 = allocate_logical_id('FAQ', 'chg-test-one')
assert id1 == id2 and id1.startswith('FAQ-WU103-')

evidence_hash='e'*64
change = {
    'change_state':'RELEASE_APPROVED','review_decision':'APPROVED','regression_status':'PASS',
    'regression_payload_sha256':candidate_hash_1,'regression_evidence_sha256':evidence_hash,
    'regression_case_ids':['positive-origin-gap','negative-neighbor'],
    'release_approval_status':'APPROVED','pii_reviewed':True,'candidate_payload_sha256':candidate_hash_1,
    'target_family':'FAQ','business_truth_approval':False,'source_type':'WEBSITE','source_reference':'SRC-01'
}
assert regression_evidence_gate(change) == (True, 'PASS')
assert publish_gate(change) == (True, 'PASS')
assert publish_gate({**change, 'regression_payload_sha256':candidate_hash_2}) == (False, 'REGRESSION_PAYLOAD_HASH_MISMATCH')
assert publish_gate({**change, 'candidate_payload_sha256':candidate_hash_2}) == (False, 'REGRESSION_PAYLOAD_HASH_MISMATCH')
assert publish_gate({**change, 'regression_payload_sha256':None}) == (False, 'REGRESSION_PAYLOAD_HASH_MISMATCH')
assert publish_gate({**change, 'regression_evidence_sha256':None}) == (False, 'REGRESSION_EVIDENCE_REQUIRED')
assert publish_gate({**change, 'regression_case_ids':['positive-only']}) == (False, 'REGRESSION_CASES_INCOMPLETE')
assert publish_gate({**change, 'source_reference':''}) == (False, 'SOURCE_REFERENCE_REQUIRED')
assert publish_gate({**change, 'change_state':'TEST_PASSED'})[0] is False

print('WU103_CORE_TESTS_PASS')
print({'candidate_key':k1,'candidate_payload_hash':candidate_hash_1,'payload_edit_invalidates_hash':True,'regression_payload_binding':True,'regression_evidence_required':True,'minimum_regression_cases':2,'legacy_fingerprint':f1,'shadow_precedence':True,'business_truth_gate':True,'approval_skip_blocked':True})
