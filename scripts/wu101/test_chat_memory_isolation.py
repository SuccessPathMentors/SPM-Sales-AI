#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

from build_candidate import build as build_base
from build_candidate_chat_memory_isolated import SESSION_KEY_EXPR, build

BASE = Path('n8n/workflows/production/SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json')
EXPECTED_CANDIDATE_SHA256 = '23d30ebb215205b1fdfc299302e86d98f2ff7f94ec2ad2339f988cbe3e6a49ed'


def node(wf, name):
    matches = [n for n in wf['nodes'] if n.get('name') == name]
    assert len(matches) == 1, (name, len(matches))
    return matches[0]


old = build_base(BASE)
wf = build(BASE)
wf2 = build(BASE)

memory = node(wf, 'Redis Chat Memory')
assert memory['parameters']['sessionKey'] == SESSION_KEY_EXPR
assert 'spm:staging:chat:' in memory['parameters']['sessionKey']
assert 'spm:prod:' not in memory['parameters']['sessionKey']
assert '$json.sessionId' in memory['parameters']['sessionKey']
assert memory['parameters']['sessionTTL'] == 2592000
assert memory['parameters']['contextWindowLength'] == 50

# Prove the isolation patch changes only the Redis Chat Memory sessionKey.
old_copy = json.loads(json.dumps(old))
new_copy = json.loads(json.dumps(wf))
node(new_copy, 'Redis Chat Memory')['parameters'].pop('sessionKey', None)
assert old_copy == new_copy

serialized = json.dumps(wf, ensure_ascii=False, indent=2) + '\n'
serialized2 = json.dumps(wf2, ensure_ascii=False, indent=2) + '\n'
digest = hashlib.sha256(serialized.encode('utf-8')).hexdigest()
assert digest == hashlib.sha256(serialized2.encode('utf-8')).hexdigest()
assert digest == EXPECTED_CANDIDATE_SHA256, digest

assert wf.get('active') is False
assert 'id' not in wf
assert len(wf['nodes']) == 117
assert not [n['name'] for n in wf['nodes'] if n.get('disabled') is True]

print('WU101_CHAT_MEMORY_ISOLATION_PASS')
print(json.dumps({
    'candidate_sha256': digest,
    'session_key': SESSION_KEY_EXPR,
    'active': wf.get('active'),
}, indent=2))
