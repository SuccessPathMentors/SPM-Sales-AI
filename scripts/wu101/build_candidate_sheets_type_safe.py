#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from build_candidate_chat_memory_isolated import build as build_base
from build_candidate import sha256

NUMERIC_FIELDS = ('turn_index', 'confidence', 'duration_ms')
BOOLEAN_FIELDS = (
    'clarification_used',
    'fallback_used',
    'human_requested',
    'lead_id_present',
    'opt_out',
    'degraded',
    'pii_redacted',
    'raw_message_logged',
    'raw_session_logged',
    'correlation_id_logged',
    'secret_values_logged',
)


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
    # Google Sheets call. Keep numeric event fields numeric and explicitly
    # coerce them at the sink.
    columns['attemptToConvertTypes'] = True
    columns['value']['turn_index'] = "={{ Number($json.wu101_analytics_event.turn_index ?? 1) }}"
    columns['value']['confidence'] = "={{ $json.wu101_analytics_event.confidence == null ? null : Number($json.wu101_analytics_event.confidence) }}"
    columns['value']['duration_ms'] = "={{ Number($json.wu101_analytics_event.duration_ms ?? 0) }}"

    # Runtime Test #1 then showed n8n rejecting the first boolean field
    # (clarification_used) at the same cached-schema validation boundary.
    # Preserve booleans in the analytics event contract, but encode every
    # boolean as canonical lower-case text at the Google Sheets sink. This
    # avoids a field-by-field failure chain while keeping the storage format
    # deterministic and trivially parseable downstream.
    schema = {f.get('id'): f for f in columns.get('schema', []) if isinstance(f, dict)}
    for field in BOOLEAN_FIELDS:
        if field not in columns['value'] or field not in schema:
            raise RuntimeError(f'missing WU-101 boolean analytics field: {field}')
        columns['value'][field] = (
            f"={{ $json.wu101_analytics_event.{field} === true ? 'true' : 'false' }}"
        )
        schema[field]['type'] = 'string'

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
        'boolean_sink_fields': list(BOOLEAN_FIELDS),
        'boolean_sink_encoding': 'canonical_string_true_false',
    }, indent=2))


if __name__ == '__main__':
    main()
