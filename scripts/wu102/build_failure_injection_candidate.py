#!/usr/bin/env python3
import argparse
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('wu102_build_candidate', HERE / 'build_candidate.py')
assert spec and spec.loader
wu102 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wu102)

build_normal = wu102.build
node_by_name = wu102.node_by_name
sha256 = wu102.sha256

FAILURE_DOCUMENT_ID = 'WU102_FAILURE_INJECTION_NONEXISTENT_SPREADSHEET'
LOGGER = 'Upsert WU102 Unanswered [STAGING]'


def build(baseline_path):
    wf = build_normal(baseline_path)
    logger = node_by_name(wf, LOGGER)
    doc = logger['parameters']['documentId']
    if not isinstance(doc, dict) or not doc.get('__rl'):
        raise RuntimeError('unexpected WU-102 queue documentId shape')
    logger['parameters']['documentId'] = {
        '__rl': True,
        'value': FAILURE_DOCUMENT_ID,
        'mode': 'id',
    }
    if logger.get('onError') != 'continueRegularOutput':
        raise RuntimeError('WU-102 queue logger is not configured fail-open')
    return wf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--baseline', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    wf = build(args.baseline)
    Path(args.output).write_text(json.dumps(wf, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({
        'output': args.output,
        'sha256': sha256(args.output),
        'failure_injection': 'queue_document_not_found',
        'failure_document_id': FAILURE_DOCUMENT_ID,
        'workflow_active': wf.get('active'),
        'logger_on_error': node_by_name(wf, LOGGER).get('onError'),
    }, indent=2))


if __name__ == '__main__':
    main()
