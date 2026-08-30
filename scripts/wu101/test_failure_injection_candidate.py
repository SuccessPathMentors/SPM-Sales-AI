#!/usr/bin/env python3
import copy
import json
from pathlib import Path

from build_candidate_sheets_type_safe import build as build_normal, node_by_name
from build_failure_injection_candidate import build as build_failure, FAILURE_DOCUMENT_ID, LOGGER

BASE = Path('n8n/workflows/production/SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json')

normal = build_normal(BASE)
fi = build_failure(BASE)

assert normal.get('active') is False
assert fi.get('active') is False

normal_logger = node_by_name(normal, LOGGER)
fi_logger = node_by_name(fi, LOGGER)
assert fi_logger.get('onError') == 'continueRegularOutput'
assert fi_logger['parameters']['documentId']['value'] == FAILURE_DOCUMENT_ID
assert normal_logger['parameters']['documentId']['value'] != FAILURE_DOCUMENT_ID

# Prove the failure candidate differs from the approved WU-101 candidate only
# at the analytics logger documentId. No routing, business logic, credentials,
# Redis namespace, lead adapter or response node may change.
normal_copy = copy.deepcopy(normal)
fi_copy = copy.deepcopy(fi)
node_by_name(normal_copy, LOGGER)['parameters']['documentId'] = {'__normalized__': True}
node_by_name(fi_copy, LOGGER)['parameters']['documentId'] = {'__normalized__': True}
assert normal_copy == fi_copy, 'failure-injection candidate changed more than analytics documentId'

# Explicit hard-stop checks.
serialized = json.dumps(fi, ensure_ascii=False)
assert 'spm:staging:sales:' in serialized
assert 'spm:prod:sales:' not in serialized
assert 'WU101_LEADS_STAGING' in serialized
assert 'LEADS_TEMPLATE' not in serialized
assert 'CMBMpxX5AqqK2UTn' not in serialized

print('WU101_FAILURE_INJECTION_STATIC_PASS')
print(json.dumps({
    'failure_mode': 'analytics_document_not_found',
    'logger_on_error': fi_logger.get('onError'),
    'workflow_active': fi.get('active'),
    'only_diff': 'Upsert WU101 Analytics [STAGING].parameters.documentId',
}, indent=2))
