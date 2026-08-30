#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from build_candidate import sha256
from build_candidate_sheets_type_safe import build as build_normal, node_by_name

FAIL_DOCUMENT_ID = 'WU101_FORCED_FAILURE_NO_SUCH_SPREADSHEET'
FAIL_WORKFLOW_NAME = 'SPM WU101 Analytics Failure Injection Candidate'
LOGGER_NAME = 'Upsert WU101 Analytics [STAGING]'


def build(baseline_path):
    wf = build_normal(baseline_path)
    wf['name'] = FAIL_WORKFLOW_NAME
    wf['active'] = False

    logger = node_by_name(wf, LOGGER_NAME)
    logger['parameters']['documentId'] = {
        '__rl': True,
        'value': FAIL_DOCUMENT_ID,
        'mode': 'id',
    }
    logger['onError'] = 'continueRegularOutput'
    logger['notesInFlow'] = True
    logger['notes'] = (
        'WU101 TEST-ONLY failure injection: this deliberately targets a non-existent '
        'Google spreadsheet so the analytics sink fails while the customer response '
        'must continue through the existing fail-open restore path. Never publish.'
    )
    return wf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--baseline', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    wf = build(args.baseline)
    Path(args.output).write_text(
        json.dumps(wf, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
    )
    print(json.dumps({
        'output': args.output,
        'sha256': sha256(args.output),
        'workflow_name': wf['name'],
        'active': wf.get('active'),
        'failure_document_id': FAIL_DOCUMENT_ID,
        'failure_scope': 'ANALYTICS_SINK_ONLY',
    }, indent=2))


if __name__ == '__main__':
    main()
