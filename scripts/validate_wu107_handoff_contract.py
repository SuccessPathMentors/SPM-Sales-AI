#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
contract = json.loads((ROOT / 'contracts' / 'wu107-handoff-contract.json').read_text())
scenarios = json.loads((ROOT / 'contracts' / 'wu107-handoff-scenarios.json').read_text())

errors = []

required_states = {'NONE','REQUESTED','QUEUED','ACCEPTED','FAILED','CANCELLED'}
if set(contract.get('states', [])) != required_states:
    errors.append('State set mismatch')

allowed = contract.get('allowed_transitions', {})
expected_allowed = {
    'NONE': {'REQUESTED'},
    'REQUESTED': {'QUEUED','FAILED','CANCELLED'},
    'QUEUED': {'ACCEPTED','FAILED','CANCELLED'},
    'ACCEPTED': set(), 'FAILED': set(), 'CANCELLED': set()
}
for state, targets in expected_allowed.items():
    if set(allowed.get(state, [])) != targets:
        errors.append(f'Illegal transition contract for {state}')

truth = contract.get('truth_rules', {})
for state in ['REQUESTED','QUEUED','FAILED','CANCELLED']:
    if truth.get(state, {}).get('may_claim_human_received') is not False:
        errors.append(f'{state} must not permit human-received claim')
if truth.get('ACCEPTED', {}).get('may_claim_human_received') is not True:
    errors.append('ACCEPTED must be the only state permitting human-received claim')
if truth.get('QUEUED', {}).get('queue_receipt_required') is not True:
    errors.append('QUEUED requires queue receipt')
if truth.get('ACCEPTED', {}).get('human_acceptance_required') is not True:
    errors.append('ACCEPTED requires human acceptance evidence')

retry = contract.get('retry_policy', {})
if retry.get('idempotency_required') is not True:
    errors.append('Idempotency must be required')
if retry.get('max_attempts') != 3:
    errors.append('Expected bounded retry max_attempts=3')

forbidden = set(contract.get('forbidden_default_fields', []))
required_forbidden = {'password','api_key','token','secret','card_number','bank_account','raw_conversation','raw_session_id'}
if not required_forbidden.issubset(forbidden):
    errors.append('Privacy forbidden-field baseline incomplete')

provider = contract.get('provider_contract', {})
if provider.get('queue_receipt_is_not_human_acceptance') is not True:
    errors.append('Provider contract must separate queue receipt from human acceptance')
if provider.get('whatsapp_notification_is_out_of_scope_for_wu107') is not True:
    errors.append('WU-108 notification channel must remain out of WU-107 core')

items = scenarios.get('scenarios', [])
ids = [x.get('id') for x in items]
if len(items) < 24:
    errors.append('Scenario matrix must contain at least 24 deterministic scenarios')
if len(ids) != len(set(ids)):
    errors.append('Scenario IDs must be unique')

required_names = {
    'explicit human request','technical support escalation','complaint escalation',
    'verified queue receipt','verified human acceptance','retry exhaustion',
    'duplicate logical handoff retry','classifier alone cannot queue',
    'generated text alone cannot accept','Arabic request parity','French request parity',
    'secret negative field test','raw conversation negative field test'
}
found_names = {x.get('name') for x in items}
if not required_names.issubset(found_names):
    errors.append('Scenario matrix missing required coverage')

# P0 semantic checks on fixtures
for s in items:
    if s.get('expected_state') in {'REQUESTED','QUEUED'} and s.get('may_claim_acceptance') is True:
        errors.append(f"{s.get('id')}: premature acceptance claim")
    if s.get('duplicate_idempotency_key') and s.get('expected_duplicate_case_count') != 0:
        errors.append(f"{s.get('id')}: duplicate case creation permitted")
    if s.get('classifier_says_success') and s.get('expected_state') not in {'NONE','REQUESTED'}:
        errors.append(f"{s.get('id')}: classifier improperly creates execution truth")

if errors:
    print('WU107_HANDOFF_CONTRACT_FAIL')
    for err in errors:
        print('-', err)
    raise SystemExit(1)

print('WU107_HANDOFF_CONTRACT_PASS')
print(f"states={len(required_states)} scenarios={len(items)} max_attempts={retry.get('max_attempts')}")
