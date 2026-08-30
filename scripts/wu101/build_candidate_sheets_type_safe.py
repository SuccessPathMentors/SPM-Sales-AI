#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from build_candidate_chat_memory_isolated import build as build_base
from build_candidate import sha256

NUMERIC_FIELDS = ('turn_index', 'confidence', 'duration_ms')


def node_by_name(wf, name):
    matches = [n for n in wf['nodes'] if n.get('name') == name]
    if len(matches) != 1:
        raise RuntimeError(f'expected exactly one node {name!r}, found {len(matches)}')
    return matches[0]


def build(baseline_path):
    wf = build_base(baseline_path)
    logger = node_by_name(wf, 'Upsert WU101 Analytics [STAGING]')
    columns = logger['parameters']['columns']

    # n8n validates mapped values against the cached column schema before the
    # Google Sheets call. Runtime Test #1 showed turn_index being rejected at
    # this boundary. Keep the analytics event numeric, explicitly coerce the
    # three numeric mappings, and permit n8n's schema conversion at the sink.
    columns['attemptToConvertTypes'] = True
    columns['value']['turn_index'] = "={{ Number($json.wu101_analytics_event.turn_index ?? 1) }}"
    columns['value']['confidence'] = "={{ $json.wu101_analytics_event.confidence == null ? null : Number($json.wu101_analytics_event.confidence) }}"
    columns['value']['duration_ms'] = "={{ Number($json.wu101_analytics_event.duration_ms ?? 0) }}"
    return wf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--baseline', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    wf = build(args.baseline)
    Path(args.output).write_text(json.dumps(wf, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    logger = node_by_name(wf, 'Upsert WU101 Analytics [STAGING]')
    print(json.dumps({
        'output': args.output,
        'sha256': sha256(args.output),
        'node_count': len(wf['nodes']),
        'connection_sources': len(wf['connections']),
        'attempt_to_convert_types': logger['parameters']['columns'].get('attemptToConvertTypes'),
        'numeric_fields': list(NUMERIC_FIELDS),
    }, indent=2))


if __name__ == '__main__':
    main()
