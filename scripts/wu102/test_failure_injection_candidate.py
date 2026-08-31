#!/usr/bin/env python3
import copy
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

normal_spec = importlib.util.spec_from_file_location('wu102_build_candidate', HERE / 'build_candidate.py')
assert normal_spec and normal_spec.loader
normal_mod = importlib.util.module_from_spec(normal_spec)
normal_spec.loader.exec_module(normal_mod)

failure_spec = importlib.util.spec_from_file_location('wu102_failure_candidate', HERE / 'build_failure_injection_candidate.py')
assert failure_spec and failure_spec.loader
failure_mod = importlib.util.module_from_spec(failure_spec)
failure_spec.loader.exec_module(failure_mod)

build_normal = normal_mod.build
node_by_name = normal_mod.node_by_name
build_failure = failure_mod.build
FAILURE_DOCUMENT_ID = failure_mod.FAILURE_DOCUMENT_ID
LOGGER = failure_mod.LOGGER

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

# Prove the failure candidate differs from the approved WU-102 candidate only
# at the queue logger documentId. No routing, business logic, credentials,
# Redis namespace, analytics, lead adapter, or response node may change.
normal_copy = copy.deepcopy(normal)
fi_copy = copy.deepcopy(fi)
node_by_name(normal_copy, LOGGER)['parameters']['documentId'] = {'__normalized__': True}
node_by_name(fi_copy, LOGGER)['parameters']['documentId'] = {'__normalized__': True}
assert normal_copy == fi_copy, 'failure-injection candidate changed more than WU-102 queue documentId'

serialized = json.dumps(fi, ensure_ascii=False)
assert 'spm:staging:sales:' in serialized
assert 'spm:prod:sales:' not in serialized
assert "workflow_release:'WU102_STAGING_UNANSWERED_V1'" in node_by_name(fi, 'Build Canonical Session Envelope')['parameters']['jsCode']

sheet = fi_logger['parameters']['sheetName']
assert isinstance(sheet, dict)
assert sheet.get('cachedResultName') == 'WU102_UNANSWERED_STAGING'
assert str(sheet.get('value')) == '2026102001'
assert fi_logger['parameters']['columns']['matchingColumns'] == ['queue_event_id']

print('WU102_FAILURE_INJECTION_STATIC_PASS')
print(json.dumps({
    'failure_mode': 'queue_document_not_found',
    'logger_on_error': fi_logger.get('onError'),
    'workflow_active': fi.get('active'),
    'queue_sheet': sheet.get('cachedResultName'),
    'matching_column': 'queue_event_id',
    'only_diff': 'Upsert WU102 Unanswered [STAGING].parameters.documentId',
}, indent=2))
