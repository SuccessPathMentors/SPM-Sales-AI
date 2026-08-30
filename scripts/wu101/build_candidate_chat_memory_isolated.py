#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from build_candidate import build as build_base, sha256

SESSION_KEY_EXPR = "={{ 'spm:staging:chat:' + $json.sessionId }}"


def node_by_name(wf, name):
    matches = [n for n in wf['nodes'] if n.get('name') == name]
    if len(matches) != 1:
        raise RuntimeError(f'expected exactly one node {name!r}, found {len(matches)}')
    return matches[0]


def build(baseline_path):
    wf = build_base(baseline_path)
    memory = node_by_name(wf, 'Redis Chat Memory')
    memory.setdefault('parameters', {})['sessionKey'] = SESSION_KEY_EXPR
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
        'node_count': len(wf['nodes']),
        'connection_sources': len(wf['connections']),
        'chat_memory_session_key': SESSION_KEY_EXPR,
    }, indent=2))


if __name__ == '__main__':
    main()
