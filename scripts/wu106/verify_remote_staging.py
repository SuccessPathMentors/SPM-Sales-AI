#!/usr/bin/env python3
import json
import os
import sys
import urllib.request

TARGET = os.getenv("N8N_TARGET_WORKFLOW_ID", "").strip()
BASE = os.getenv("N8N_API_BASE_URL", "").strip().rstrip("/")
KEY = os.getenv("N8N_API_KEY", "").strip()

EXPECTED_NAME = "[STAGING] SPM_WU106_END_TO_END_JOURNEYS_V1"
EXPECTED_NODE_COUNT = 133
WU106_NODE = "Build WU106 Journey Orchestration Envelope"
WU106_CR_NODE = "Apply WU106 Journey Transition Recovery [CR-106-01]"
WU104_DECISION = "Build WU104 Short Query Decision"
WU104_TRIAL_GUARD = "Apply WU104 Short Trial Inquiry Guard"
SOURCE_NODE = "Apply WU105 Golden Intent Prompt Overlay"
TARGET_NODE = "Generate WU92 Sales Agent Response"
EXPECTED_WU106_ID = "vvHvidUHVxM5wTVT"
PROTECTED_IDS = {
    "CMBMpxX5AqqK2UTn",
    "mMZVFxJIxE7a9SSW",
    "1kaRBBFVJYbPxvQG",
    "5COEoxXjk8AvuGBa",
    "Bt3PvOIbFzU0O9gk",
    "KXfalaYSCLdgmf4X",
}

if not TARGET or not BASE or not KEY:
    raise SystemExit("missing required n8n readback environment")
if TARGET != EXPECTED_WU106_ID:
    raise SystemExit(f"unexpected WU-106 target ID: {TARGET}")
if TARGET in PROTECTED_IDS:
    raise SystemExit("protected workflow ID denied")

req = urllib.request.Request(
    f"{BASE}/workflows/{TARGET}",
    headers={"accept": "application/json", "X-N8N-API-KEY": KEY},
    method="GET",
)
with urllib.request.urlopen(req, timeout=45) as resp:
    wf = json.loads(resp.read().decode("utf-8"))

errors = []
nodes = {n.get("name"): n for n in wf.get("nodes", [])}
connections = wf.get("connections", {})


def one_target(name):
    main = connections.get(name, {}).get("main")
    if not isinstance(main, list) or len(main) != 1 or len(main[0]) != 1:
        return None
    return main[0][0].get("node")


if str(wf.get("id")) != EXPECTED_WU106_ID:
    errors.append(f"workflow ID mismatch: {wf.get('id')!r}")
if wf.get("name") != EXPECTED_NAME:
    errors.append(f"name mismatch: {wf.get('name')!r}")
if wf.get("active") is True:
    errors.append("workflow unexpectedly active")
if len(wf.get("nodes", [])) != EXPECTED_NODE_COUNT:
    errors.append(f"node count mismatch: {len(wf.get('nodes', []))}")

required_nodes = [
    WU106_NODE,
    WU106_CR_NODE,
    WU104_DECISION,
    WU104_TRIAL_GUARD,
    SOURCE_NODE,
    TARGET_NODE,
    "Apply WU105 Availability Answer-First Guard",
    "Apply WU105 Explicit Free Trial Action Guard",
    "Apply WU105 Refund Policy Answer-First Guard",
    "Load POLICIES [WU91 READ ONLY]",
    "Upsert WU102 Unanswered [STAGING]",
    "Redis Chat Memory",
]
for name in required_nodes:
    if name not in nodes:
        errors.append(f"missing required node: {name}")

if one_target(SOURCE_NODE) != WU106_NODE:
    errors.append(f"WU105 overlay does not feed WU106 envelope: {one_target(SOURCE_NODE)!r}")
if one_target(WU106_NODE) != TARGET_NODE:
    errors.append(f"WU106 envelope does not return to generator: {one_target(WU106_NODE)!r}")
if one_target(WU104_DECISION) != WU106_CR_NODE:
    errors.append(f"WU104 decision does not feed CR-106-01: {one_target(WU104_DECISION)!r}")
if one_target(WU106_CR_NODE) != WU104_TRIAL_GUARD:
    errors.append(f"CR-106-01 does not return to locked short-trial guard: {one_target(WU106_CR_NODE)!r}")

envelope_code = nodes.get(WU106_NODE, {}).get("parameters", {}).get("jsCode", "")
for marker in [
    "SPM_WU106_ORCHESTRATION_ENVELOPE_V1",
    "OBSERVE_ONLY_BASELINE",
    "state_mutated:false",
    "prompt_mutated:false",
    "action_permission_mutated:false",
    "irreversible_action_allowed:false",
    "wu104_authoritative:true",
    "wu105_authoritative:true",
    "raw_message_logged:false",
    "raw_session_logged:false",
    "secret_values_logged:false",
]:
    if marker not in envelope_code:
        errors.append(f"WU106 envelope marker missing: {marker}")

cr_code = nodes.get(WU106_CR_NODE, {}).get("parameters", {}).get("jsCode", "")
for marker in [
    "SPM_WU106_CR10601_JOURNEY_TRANSITION_RECOVERY_V1",
    "WU106_REGISTRATION_AWAITED_FIELD",
    "WU106_EXPLICIT_AVAILABILITY_PATTERN",
    "action_permission_mutated:false",
    "irreversible_action_allowed:false",
    "production_mutation_allowed:false",
    "raw_message_logged:false",
    "raw_session_logged:false",
    "secret_values_logged:false",
]:
    if marker not in cr_code:
        errors.append(f"CR-106-01 marker missing: {marker}")
for forbidden in ["httpRequest", "googleSheets", "redis", "executeWorkflow", "booking_id=", "lead_upsert"]:
    if forbidden in cr_code:
        errors.append(f"CR-106-01 forbidden action surface present: {forbidden}")

avail_code = nodes.get("Apply WU105 Availability Answer-First Guard", {}).get("parameters", {}).get("jsCode", "")
refund_code = nodes.get("Apply WU105 Refund Policy Answer-First Guard", {}).get("parameters", {}).get("jsCode", "")
if "SPM_WU105_AVAILABILITY_ANSWER_FIRST_GUARD_V1" not in avail_code:
    errors.append("CR-105-01 signature missing")
if "SPM_WU105_REFUND_POLICY_ANSWER_FIRST_GUARD_V1" not in refund_code:
    errors.append("CR-105-03 signature missing")

q = nodes.get("Upsert WU102 Unanswered [STAGING]", {})
qcols = q.get("parameters", {}).get("columns", {})
if q.get("parameters", {}).get("operation") != "appendOrUpdate":
    errors.append("WU102 queue operation changed")
if qcols.get("matchingColumns") != ["queue_event_id"]:
    errors.append("WU102 queue idempotency changed")

memory_key = nodes.get("Redis Chat Memory", {}).get("parameters", {}).get("sessionKey")
if memory_key != "={{ 'spm:staging:chat:' + $json.sessionId }}":
    errors.append("STAGING Redis isolation changed")

if nodes.get(WU106_NODE, {}).get("type") != "n8n-nodes-base.code":
    errors.append("WU106 envelope is not deterministic Code node")
if nodes.get(WU106_CR_NODE, {}).get("type") != "n8n-nodes-base.code":
    errors.append("CR-106-01 is not deterministic Code node")

observed = {
    "workflow_id": wf.get("id"),
    "workflow_name": wf.get("name"),
    "active": wf.get("active"),
    "versionId": wf.get("versionId"),
    "node_count": len(wf.get("nodes", [])),
    "wu106_envelope_present": WU106_NODE in nodes,
    "cr10601_present": WU106_CR_NODE in nodes,
    "cr10601_signature_present": "SPM_WU106_CR10601_JOURNEY_TRANSITION_RECOVERY_V1" in cr_code,
    "wu104_decision_target": one_target(WU104_DECISION),
    "cr10601_target": one_target(WU106_CR_NODE),
    "wu105_overlay_target": one_target(SOURCE_NODE),
    "wu106_envelope_target": one_target(WU106_NODE),
    "cr10501_present": "SPM_WU105_AVAILABILITY_ANSWER_FIRST_GUARD_V1" in avail_code,
    "cr10502_present": "Apply WU105 Explicit Free Trial Action Guard" in nodes,
    "cr10503_present": "SPM_WU105_REFUND_POLICY_ANSWER_FIRST_GUARD_V1" in refund_code,
    "cr10504_policies_loader_present": "Load POLICIES [WU91 READ ONLY]" in nodes,
    "wu102_queue_operation": q.get("parameters", {}).get("operation"),
    "wu102_queue_matching_columns": qcols.get("matchingColumns"),
    "chat_memory_session_key": memory_key,
    "production_write_performed": False,
}
print(json.dumps(observed, indent=2, ensure_ascii=False))
if errors:
    print("WU106_CR10601_REMOTE_FAIL: " + "; ".join(errors), file=sys.stderr)
    raise SystemExit(1)
print("WU106_CR10601_REMOTE_PASS")
