#!/usr/bin/env python3
from copy import deepcopy
from core import (
    allocate_logical_id,
    automation_may_write_approval_field,
    business_truth_gate,
    candidate_key,
    payload_hash,
    publish_gate,
    resolve_staging_base,
    row_fingerprint,
    stale_base,
    transition_allowed,
    validate_family_payload,
)

# Candidate key: deterministic, scoped to exact queue/family/type/target.
k1 = candidate_key('uq-test-1', 'FAQ', 'UPDATE', 'FAQ-001')
k2 = candidate_key('uq-test-1', 'FAQ', 'UPDATE', 'FAQ-001')
assert k1 == k2 and len(k1) == 64
assert k1 != candidate_key('uq-test-1', 'FAQ', 'UPDATE', 'FAQ-002')
assert k1 != candidate_key('uq-test-1', 'FAQ', 'ADD', None)

# Family allowlist / unknown-field rejection.
faq = {
    'record_id':'FAQ-001','category':'trial','language':'en','question':'Q?',
    'answer':'A.','keywords':'trial','priority':'1','status':'ACTIVE','last_reviewed':'2026-08-06'
}
validate_family_payload('FAQ', faq)
try:
    validate_family_payload('FAQ', {**faq, 'evil_field':'x'})
    raise AssertionError('unknown field accepted')
except ValueError as e:
    assert str(e).startswith('UNKNOWN_PAYLOAD_FIELDS')

# Hashes deterministic; operational last_reviewed does not create a stale content fingerprint.
f1 = row_fingerprint('FAQ', faq)
f2 = row_fingerprint('FAQ', {**faq, 'last_reviewed':'2026-08-31'})
assert f1 == f2
assert payload_hash('FAQ', faq) == payload_hash('FAQ', deepcopy(faq))

# State machine cannot skip human/test/release gates.
assert transition_allowed('DRAFT', 'HUMAN_APPROVED')
assert not transition_allowed('DRAFT', 'TEST_PASSED')
assert not transition_allowed('DRAFT', 'PUBLISHED')
assert transition_allowed('HUMAN_APPROVED', 'TEST_PASSED')
assert transition_allowed('TEST_PASSED', 'RELEASE_APPROVED')
assert transition_allowed('RELEASE_APPROVED', 'PUBLISHED')

# Automation cannot authoritatively write approval fields.
for field in ['review_decision','business_truth_approval','release_approval_status']:
    assert automation_may_write_approval_field(field) is False
assert automation_may_write_approval_field('regression_status') is True

# Business truth gates.
assert business_truth_gate('FAQ', False, 'WEBSITE', 'SRC-01')[0] is True
assert business_truth_gate('PACKAGES', False, 'OWNER_DECISION', 'SRC-009')[0] is False
assert business_truth_gate('PACKAGES', True, 'WEBSITE', 'SRC-01')[0] is False
assert business_truth_gate('PACKAGES', True, 'OWNER_DECISION', 'SRC-009')[0] is True
assert business_truth_gate('POLICIES', True, 'INTERNAL_APPROVED_SOURCE', 'approved-policy-1')[0] is True

# Base resolution: canonical legacy first, then ACTIVE shadow takes precedence.
canonical = [faq]
base_legacy = resolve_staging_base('FAQ', 'FAQ-001', canonical, [])
assert base_legacy['base_source'] == 'CANONICAL_LEGACY'
assert base_legacy['base_revision'] == 'LEGACY_UNVERSIONED'
assert base_legacy['base_fingerprint_sha256'] == f1
assert stale_base(f1, base_legacy) is False
assert stale_base('0' * 64, base_legacy) is True

shadow = [{
    'target_family':'FAQ','logical_record_id':'FAQ-001','revision':'v1','change_id':'chg-one',
    'source_queue_event_id':'uq-test-1','payload_json':'{}','payload_sha256':'a' * 64,
    'base_fingerprint_sha256':f1,'record_status':'ACTIVE','published_at':'2026-08-31T00:00:00Z',
    'supersedes_revision':None
}]
base_shadow = resolve_staging_base('FAQ', 'FAQ-001', canonical, shadow)
assert base_shadow['base_source'] == 'SHADOW'
assert base_shadow['base_revision'] == 'v1'
assert base_shadow['base_fingerprint_sha256'] == 'a' * 64

try:
    resolve_staging_base('FAQ', 'FAQ-001', canonical, shadow + [dict(shadow[0], change_id='chg-two')])
    raise AssertionError('non-unique shadow base accepted')
except ValueError as e:
    assert str(e) == 'BASE_RECORD_NOT_UNIQUE'

# ADD ID allocation is deterministic/collision-checkable.
id1 = allocate_logical_id('FAQ', 'chg-test-one')
id2 = allocate_logical_id('FAQ', 'chg-test-one')
assert id1 == id2 and id1.startswith('FAQ-WU103-')

# Publish gate binds regression evidence to the exact payload hash.
change = {
    'change_state':'RELEASE_APPROVED',
    'review_decision':'APPROVED',
    'regression_status':'PASS',
    'release_approval_status':'APPROVED',
    'pii_reviewed':True,
    'candidate_payload_sha256':'b' * 64,
    'target_family':'FAQ',
    'business_truth_approval':False,
    'source_type':'WEBSITE',
    'source_reference':'SRC-01'
}
assert publish_gate(change, regression_bound_payload_sha256='b' * 64) == (True, 'PASS')
assert publish_gate(change, regression_bound_payload_sha256='c' * 64)[0] is False
assert publish_gate({**change, 'change_state':'TEST_PASSED'}, regression_bound_payload_sha256='b' * 64)[0] is False

print('WU103_CORE_TESTS_PASS')
print({
    'candidate_key': k1,
    'legacy_fingerprint': f1,
    'shadow_precedence': True,
    'business_truth_gate': True,
    'approval_skip_blocked': True,
})
