#!/usr/bin/env python3
import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WU101_DIR = HERE.parent / 'wu101'
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(WU101_DIR))

import build_candidate as wu102  # noqa: E402
from build_candidate_sheets_type_safe import build as build_wu101  # noqa: E402

BASE = Path('n8n/workflows/production/SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json')
base = build_wu101(BASE)
candidate = wu102.build(BASE)

WU102_NODES = {
    'Build WU102 Unanswered Queue Decision',
    'Is WU102 Queue Write Required?',
    'Upsert WU102 Unanswered [STAGING]',
    'Restore Customer Context After WU102 Queue',
}

assert len(base['nodes']) == 117
assert len(candidate['nodes']) == 121
assert WU102_NODES.issubset({n['name'] for n in candidate['nodes']})

normalized = copy.deepcopy(candidate)
normalized['name'] = base['name']
normalized['nodes'] = [n for n in normalized['nodes'] if n.get('name') not in WU102_NODES]
for name in WU102_NODES:
    normalized['connections'].pop(name, None)

# Restore the one approved insertion edge.
normalized['connections']['Restore Customer Context After WU101 Analytics'] = {
    'main': [[{'node': 'Save AI Message to Chat History', 'type': 'main', 'index': 0}]]
}

# Canonical envelope differs only by the staged release label.
def node(wf, name):
    matches = [n for n in wf['nodes'] if n.get('name') == name]
    assert len(matches) == 1, (name, len(matches))
    return matches[0]

n = node(normalized, 'Build Canonical Session Envelope')
n['parameters']['jsCode'] = n['parameters']['jsCode'].replace(
    "workflow_release:'WU102_STAGING_UNANSWERED_V1'",
    "workflow_release:'WU101_STAGING_ANALYTICS_V1'",
)

# WU-102 shifts only the final response nodes to make room on the canvas.
for name in ['Save AI Message to Chat History', 'Restore Final Response Payload', 'RC3 Chat Response']:
    node(normalized, name)['position'] = copy.deepcopy(node(base, name)['position'])

assert normalized == base, 'WU-102 changed content outside its approved insertion/release-label path'

# Critical business nodes are byte-identical even before normalization.
critical = [
    'Validate SPM V2 Classifier Output',
    'Route Classifier Confidence',
    'Resolve WU91 Source Plan',
    'Build WU91 Source Gate Decision',
    'Build WU92 Response Rule Context',
    'Apply WU95 Lead Truth Guard',
    'Deterministic Action Gateway [RC3 SCOPE LOCK]',
    'Redact WU97 Observability Telemetry',
]
for name in critical:
    assert node(candidate, name) == node(base, name), name

print('WU102_WU101_REGRESSION_PARITY_PASS')
print(json.dumps({
    'wu101_nodes': len(base['nodes']),
    'wu102_nodes': len(candidate['nodes']),
    'new_wu102_nodes': len(WU102_NODES),
    'normalized_exact_match': True,
    'critical_business_nodes_unchanged': True,
}, indent=2))
