#!/usr/bin/env python3
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADAPTERS_PATH = ROOT / 'contracts' / 'WU103_FAMILY_ADAPTERS_V1.json'
SHA256_RE = re.compile(r'^[a-f0-9]{64}$')
SOURCE_TYPES = {'WEBSITE','ATTACHMENT','QUALITY_NOTE','OWNER_DECISION','INTERNAL_APPROVED_SOURCE'}


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def sha256_text(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def sha256_json(value):
    return sha256_text(canonical_json(value))


def load_adapters():
    data = json.loads(ADAPTERS_PATH.read_text(encoding='utf-8'))
    assert data['schema'] == 'SPM_WU103_FAMILY_ADAPTERS_V1'
    return data['families']


def candidate_key(source_queue_event_id, target_family, change_type, target_record_id=None):
    target = target_record_id or 'NEW'
    raw = f'{source_queue_event_id}|{target_family}|{change_type}|{target}'
    return sha256_text(raw)


def validate_family_payload(target_family, payload, *, allow_missing_id=False):
    adapters = load_adapters()
    if target_family not in adapters:
        raise ValueError('UNKNOWN_TARGET_FAMILY')
    adapter = adapters[target_family]
    if not isinstance(payload, dict):
        raise ValueError('PAYLOAD_NOT_OBJECT')
    unknown = sorted(set(payload) - set(adapter['fields']))
    if unknown:
        raise ValueError(f'UNKNOWN_PAYLOAD_FIELDS:{",".join(unknown)}')
    id_field = adapter['id_field']
    if not allow_missing_id and not str(payload.get(id_field, '')).strip():
        raise ValueError('MISSING_TARGET_ID_FIELD')
    if 'status' in payload and str(payload['status']).upper() != 'ACTIVE':
        raise ValueError('NON_ACTIVE_CANDIDATE_STATUS')
    return adapter


def parse_candidate_payload(target_family, candidate_payload_json, *, allow_missing_id=False):
    if not isinstance(candidate_payload_json, str) or not candidate_payload_json.strip():
        raise ValueError('CANDIDATE_PAYLOAD_JSON_REQUIRED')
    try:
        payload = json.loads(candidate_payload_json)
    except json.JSONDecodeError as exc:
        raise ValueError('CANDIDATE_PAYLOAD_JSON_INVALID') from exc
    validate_family_payload(target_family, payload, allow_missing_id=allow_missing_id)
    return payload


def canonical_candidate_payload(target_family, candidate_payload_json, *, allow_missing_id=False):
    payload = parse_candidate_payload(target_family, candidate_payload_json, allow_missing_id=allow_missing_id)
    adapter = load_adapters()[target_family]
    normalized = {field: payload.get(field) for field in adapter['fields'] if field in payload}
    return canonical_json(normalized)


def candidate_payload_hash(target_family, candidate_payload_json, *, allow_missing_id=False):
    return sha256_text(canonical_candidate_payload(target_family, candidate_payload_json, allow_missing_id=allow_missing_id))


def normalized_authoritative_row(target_family, row):
    adapter = validate_family_payload(target_family, row, allow_missing_id=False)
    fields = [f for f in adapter['fields'] if f != 'last_reviewed']
    return {field: row.get(field) for field in fields}


def row_fingerprint(target_family, row):
    return sha256_json(normalized_authoritative_row(target_family, row))


def payload_hash(target_family, payload):
    adapter = validate_family_payload(target_family, payload, allow_missing_id=True)
    normalized = {field: payload.get(field) for field in adapter['fields'] if field in payload}
    return sha256_json(normalized)


def sheet_safe_text(value):
    text = '' if value is None else str(value)
    return "'" + text if text.startswith(('=', '+', '-', '@')) else text


def allocate_logical_id(target_family, change_id):
    adapters = load_adapters()
    if target_family not in adapters:
        raise ValueError('UNKNOWN_TARGET_FAMILY')
    suffix = sha256_text(change_id)[:12].upper()
    return adapters[target_family]['id_prefix'] + suffix


FORWARD_TRANSITIONS = {
    'DRAFT': {'HUMAN_APPROVED', 'REJECTED', 'BLOCKED'},
    'HUMAN_APPROVED': {'TEST_PASSED', 'REJECTED', 'BLOCKED', 'SUPERSEDED'},
    'TEST_PASSED': {'RELEASE_APPROVED', 'BLOCKED', 'SUPERSEDED'},
    'RELEASE_APPROVED': {'PUBLISHED', 'BLOCKED', 'SUPERSEDED'},
    'PUBLISHED': {'SUPERSEDED'},
    'REJECTED': set(),
    'SUPERSEDED': set(),
    'BLOCKED': set(),
}


def transition_allowed(current_state, next_state):
    return next_state in FORWARD_TRANSITIONS.get(current_state, set())


def automation_may_write_approval_field(field):
    return field not in {'review_decision','business_truth_approval','release_approval_status'}


def business_truth_gate(target_family, business_truth_approval, source_type, source_reference):
    adapters = load_adapters()
    if target_family not in adapters:
        return False, 'UNKNOWN_TARGET_FAMILY'
    if source_type not in SOURCE_TYPES:
        return False, 'SOURCE_TYPE_REQUIRED'
    if not str(source_reference or '').strip():
        return False, 'SOURCE_REFERENCE_REQUIRED'
    if not adapters[target_family]['business_truth_required']:
        return True, 'NOT_REQUIRED'
    if business_truth_approval is not True:
        return False, 'BUSINESS_TRUTH_APPROVAL_REQUIRED'
    if source_type not in {'OWNER_DECISION', 'INTERNAL_APPROVED_SOURCE'}:
        return False, 'APPROVED_BUSINESS_SOURCE_REQUIRED'
    return True, 'PASS'


def resolve_staging_base(target_family, target_record_id, canonical_rows, shadow_rows):
    adapters = load_adapters()
    if target_family not in adapters:
        raise ValueError('UNKNOWN_TARGET_FAMILY')
    id_field = adapters[target_family]['id_field']
    active_shadow = [r for r in shadow_rows if r.get('target_family') == target_family and r.get('logical_record_id') == target_record_id and r.get('record_status') == 'ACTIVE']
    if len(active_shadow) > 1:
        raise ValueError('BASE_RECORD_NOT_UNIQUE')
    if len(active_shadow) == 1:
        row = active_shadow[0]
        return {'base_source':'SHADOW','base_revision':row['revision'],'base_fingerprint_sha256':row['payload_sha256'],'base_row':row}
    canonical = [r for r in canonical_rows if str(r.get(id_field, '')).strip() == str(target_record_id).strip() and str(r.get('status', '')).upper() == 'ACTIVE']
    if len(canonical) != 1:
        raise ValueError('BASE_RECORD_NOT_UNIQUE')
    row = canonical[0]
    return {'base_source':'CANONICAL_LEGACY','base_revision':'LEGACY_UNVERSIONED','base_fingerprint_sha256':row_fingerprint(target_family,row),'base_row':row}


def stale_base(expected_fingerprint, resolved_base):
    return expected_fingerprint != resolved_base['base_fingerprint_sha256']


def payload_regression_is_current(change):
    return change.get('regression_status') == 'PASS' and change.get('regression_payload_sha256') == change.get('candidate_payload_sha256')


def regression_evidence_gate(change):
    evidence = change.get('regression_evidence_sha256')
    if not isinstance(evidence, str) or not SHA256_RE.fullmatch(evidence):
        return False, 'REGRESSION_EVIDENCE_REQUIRED'
    cases = change.get('regression_case_ids')
    if not isinstance(cases, list) or len(set(cases)) < 2 or any(not str(x).strip() for x in cases):
        return False, 'REGRESSION_CASES_INCOMPLETE'
    if not payload_regression_is_current(change):
        return False, 'REGRESSION_PAYLOAD_HASH_MISMATCH'
    return True, 'PASS'


def publish_gate(change):
    if change.get('change_state') != 'RELEASE_APPROVED':
        return False, 'RELEASE_STATE_REQUIRED'
    if change.get('review_decision') != 'APPROVED':
        return False, 'HUMAN_APPROVAL_REQUIRED'
    if change.get('regression_status') != 'PASS':
        return False, 'REGRESSION_PASS_REQUIRED'
    if change.get('release_approval_status') != 'APPROVED':
        return False, 'RELEASE_APPROVAL_REQUIRED'
    if change.get('pii_reviewed') is not True:
        return False, 'PII_REVIEW_REQUIRED'
    ok, reason = regression_evidence_gate(change)
    if not ok:
        return False, reason
    ok, reason = business_truth_gate(change.get('target_family'), change.get('business_truth_approval'), change.get('source_type'), change.get('source_reference'))
    if not ok:
        return False, reason
    return True, 'PASS'
