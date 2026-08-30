#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from build_candidate_chat_memory_isolated import build as build_base
from build_candidate import FIELDS, sha256

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


def field_expr(field):
    # Build n8n expression syntax without Python f-string brace collapsing.
    return '={{ $json.wu101_analytics_event.' + field + ' }}'


def boolean_text_expr(field):
    # Preserve boolean semantics in the event, encode canonical text only at Sheets sink.
    return '={{ $json.wu101_analytics_event.' + field + " === true ? 'true' : 'false' }}"


def build(baseline_path):
    wf = build_base(baseline_path)
    logger = node_by_name(wf, 'Upsert WU101 Analytics [STAGING]')
    columns = logger['parameters']['columns']

    # Runtime Finding #4: build_candidate.py originally used an f-string such
    # as f"={{ ... }}". Python collapses doubled braces inside f-strings, so
    # the generated n8n value became "={ ... }" and Sheets stored the
    # expression source literally. Rebuild every ordinary mapping with the
    # exact n8n expression delimiter "={{ ... }}" here.
    for field in FIELDS:
        if field in NUMERIC_FIELDS or field in BOOLEAN_FIELDS or field == 'error_codes':
            continue
        columns['value'][field] = field_expr(field)

    # n8n validates mapped values against the cached column schema before the
    # Google Sheets call. Keep numeric event fields numeric and explicitly
    # coerce them at the sink.
    columns['attemptToConvertTypes'] = True
    columns['value']['turn_index'] = "={{ Number($json.wu101_analytics_event.turn_index ?? 1) }}"
    columns['value']['confidence'] = "={{ $json.wu101_analytics_event.confidence == null ? null : Number($json.wu101_analytics_event.confidence) }}"
    columns['value']['duration_ms'] = "={{ Number($json.wu101_analytics_event.duration_ms ?? 0) }}"

    # Runtime Finding #3: n8n rejected native booleans against the cached
    # Google Sheets schema. Keep booleans in the analytics event contract, but
    # encode every boolean as canonical lower-case text at the sink.
    schema = {f.get('id'): f for f in columns.get('schema', []) if isinstance(f, dict)}
    for field in BOOLEAN_FIELDS:
        if field not in columns['value'] or field not in schema:
            raise RuntimeError(f'missing WU-101 boolean analytics field: {field}')
        columns['value'][field] = boolean_text_expr(field)
        schema[field]['type'] = 'string'

    # error_codes was already built as a normal string (not an f-string) in
    # the base builder and therefore already has correct n8n expression braces.
    if columns['value'].get('error_codes') != "={{ JSON.stringify($json.wu101_analytics_event.error_codes || []) }}":
        raise RuntimeError('WU-101 error_codes expression is malformed')

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
        'expression_escaping': 'n8n_double_brace_verified',
    }, indent=2))


if __name__ == '__main__':
    main()
