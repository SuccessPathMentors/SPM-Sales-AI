#!/usr/bin/env python3
import copy
import json
from pathlib import Path

from build_candidate_sheets_type_safe import build as build_normal, node_by_name
from build_failure_injection_candidate import (
    FAIL_DOCUMENT_ID,
    FAIL_WORKFLOW_NAME,
    LOGGER_NAME,
    build as build_failure,
)

BASE = Path('n8n/workflows/production/SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json')

normal = build_normal(BASE)
failure = build_failure(BASE)

assert failure.get('active') is False
assert failure['name'] == FAIL_WORKFLOW_NAME
logger = node_by_name(failure, LOGGER_NAME)
assert logger.get('onError') == 'continueRegularOutput'
assert logger['parameters']['documentId']['value'] == FAIL_DOCUMENT_ID
assert logger['parameters']['documentId']['mode'] == 'id'
assert failure['connections'][LOGGER_NAME]['main'][0][0]['node'] == 'Restore Customer Context After WU101 Analytics'

# Prove the failure-injection artifact is the validated normal WU-101 candidate
# with exactly one behavioral mutation: the analytics Google Sheets document
# target is intentionally invalid. Workflow name and node note are metadata only.
normalized = copy.deepcopy(failure)
normalized['name'] = normal['name']
f_logger = node_by_name(normalized, LOGGER_NAME)
n_logger = node_by_name(normal, LOGGER_NAME)
f_logger['parameters']['documentId'] = copy.deepcopy(n_logger['parameters']['documentId'])
f_logger.pop('notes', None)
f_logger.pop('notesInFlow', None)
assert normalized == normal

blob = json.dumps(failure, ensure_ascii=False)
assert 'spm:prod:sales:' not in blob
assert 'WU101_LEADS_STAGING' in blob
assert 'WU101_ANALYTICS_STAGING' in blob
assert FAIL_DOCUMENT_ID in blob
assert 'CMBMpxX5AqqK2UTn' not in blob

print('WU101_FAILURE_INJECTION_STATIC_PASS')
print(json.dumps({
    'workflow_name': failure['name'],
    'active': failure.get('active'),
    'failure_scope': 'ANALYTICS_SINK_ONLY',
    'on_error': logger.get('onError'),
    'restore_node': failure['connections'][LOGGER_NAME]['main'][0][0]['node'],
}, indent=2))
