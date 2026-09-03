#!/usr/bin/env python3
import json
import os
import sys
import urllib.request

TARGET = os.getenv("N8N_TARGET_WORKFLOW_ID", "").strip()
BASE = os.getenv("N8N_API_BASE_URL", "").strip().rstrip("/")
KEY = os.getenv("N8N_API_KEY", "").strip()

EXPECTED_NAME = "[STAGING] SPM_WU105_GOLDEN_INTENTS_V1"
EXPECTED_NODE_COUNT = 130
REFUND_GUARD = "Apply WU105 Refund Policy Answer-First Guard"
VALIDATOR = "Validate + Guard WU92 Sales Agent Output"
POLICY_GUARD = "Apply WU92 Sales Agent Policy Guard"
FREE_TRIAL_GUARD = "Apply WU105 Explicit Free Trial Action Guard"
WU104_TRIAL_GUARD = "Apply WU104 Short Trial Inquiry Guard"
WU89_CONTEXT = "Capture WU89 Classifier Context"
AVAILABILITY_GUARD = "Apply WU105 Availability Answer-First Guard"
SCHEDULING_GUARD = "Apply WU94 Scheduling Truth Guard"
CONVERSION_NODE = "Resolve WU95 Conversion Mode"
PROTECTED_IDS = {
    "CMBMpxX5AqqK2UTn",
    "mMZVFxJIxE7a9SSW",
    "1kaRBBFVJYbPxvQG",
    "5COEoxXjk8AvuGBa",
    "Bt3PvOIbFzU0O9gk",
}

if not TARGET or not BASE or not KEY:
    raise SystemExit("missing required n8n readback environment")
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

def targets(name):
    return [[c.get("node") for c in group] for group in connections.get(name, {}).get("main", [])]

if wf.get("name") != EXPECTED_NAME:
    errors.append(f"name mismatch: {wf.get('name')!r}")
if wf.get("active") is True:
    errors.append("workflow unexpectedly active")
if len(wf.get("nodes", [])) != EXPECTED_NODE_COUNT:
    errors.append(f"node count mismatch: {len(wf.get('nodes', []))}")

required = [
    REFUND_GUARD, VALIDATOR, POLICY_GUARD,
    FREE_TRIAL_GUARD, WU104_TRIAL_GUARD, WU89_CONTEXT,
    AVAILABILITY_GUARD, SCHEDULING_GUARD, CONVERSION_NODE,
    "Persist WU104 Awaited Context Hint",
    "Apply WU104 Clarification Response Override",
]
for name in required:
    if name not in nodes:
        errors.append(f"missing required node: {name}")

refund_code = nodes.get(REFUND_GUARD, {}).get("parameters", {}).get("jsCode", "")
if REFUND_GUARD in nodes:
    n = nodes[REFUND_GUARD]
    if n.get("type") != "n8n-nodes-base.code":
        errors.append("CR-105-03 guard is not deterministic Code node")
    if n.get("credentials"):
        errors.append("CR-105-03 guard unexpectedly has credentials")
    for token in [
        "SPM_WU105_REFUND_POLICY_ANSWER_FIRST_GUARD_V1",
        "refund_policy",
        "SOURCE_UNAVAILABLE_PRESERVE_FAIL_CLOSED",
        "EXPLICIT_REFUND_ACTION_PRESERVE_GATEWAY",
        "RESTORED_SOURCE_BACKED_POLICY_EXPLANATION",
        "source_gate_authoritative:true",
        "explicit_action_gateway_preserved:true",
        "action_permission_mutated:false",
        "irreversible_action_allowed:false",
        "raw_message_logged:false",
        "raw_session_logged:false",
        "secret_values_logged:false",
    ]:
        if token not in refund_code:
            errors.append(f"CR-105-03 token missing: {token}")

if targets(VALIDATOR) != [[REFUND_GUARD]]:
    errors.append(f"WU92 validator must feed CR-105-03 guard: {targets(VALIDATOR)!r}")
if targets(REFUND_GUARD) != [[POLICY_GUARD]]:
    errors.append(f"CR-105-03 guard must feed WU92 policy guard: {targets(REFUND_GUARD)!r}")

# Prior WU-105 CRs must remain intact.
if targets(WU104_TRIAL_GUARD) != [[FREE_TRIAL_GUARD]]:
    errors.append("CR-105-02 upstream topology changed")
if targets(FREE_TRIAL_GUARD) != [[WU89_CONTEXT]]:
    errors.append("CR-105-02 downstream topology changed")
if targets(SCHEDULING_GUARD) != [[AVAILABILITY_GUARD]]:
    errors.append("CR-105-01 scheduling topology changed")
if targets(AVAILABILITY_GUARD) != [[CONVERSION_NODE]]:
    errors.append("CR-105-01 downstream topology changed")

persist_code = nodes.get("Persist WU104 Awaited Context Hint", {}).get("parameters", {}).get("jsCode", "")
short_code = nodes.get(WU104_TRIAL_GUARD, {}).get("parameters", {}).get("jsCode", "")
avail_code = nodes.get(AVAILABILITY_GUARD, {}).get("parameters", {}).get("jsCode", "")
free_trial_code = nodes.get(FREE_TRIAL_GUARD, {}).get("parameters", {}).get("jsCode", "")
if "SPM_WU104_KNOWN_SLOT_RECONCILE_V1" not in persist_code:
    errors.append("CR-104-04 signature missing")
if "SPM_WU104_SHORT_SEMANTIC_GUARD_V1" not in short_code:
    errors.append("CR-104-05 signature missing")
if "SPM_WU105_AVAILABILITY_ANSWER_FIRST_GUARD_V1" not in avail_code:
    errors.append("CR-105-01 signature missing")
if "SPM_WU105_EXPLICIT_FREE_TRIAL_ACTION_GUARD_V1" not in free_trial_code:
    errors.append("CR-105-02 signature missing")

# Locked WU-102 / STAGING isolation invariants.
q = nodes.get("Upsert WU102 Unanswered [STAGING]", {})
qcols = q.get("parameters", {}).get("columns", {})
if q.get("parameters", {}).get("operation") != "appendOrUpdate":
    errors.append("WU102 queue operation changed")
if qcols.get("matchingColumns") != ["queue_event_id"]:
    errors.append("WU102 queue idempotency changed")
memory_key = nodes.get("Redis Chat Memory", {}).get("parameters", {}).get("sessionKey")
if memory_key != "={{ 'spm:staging:chat:' + $json.sessionId }}":
    errors.append("STAGING Redis isolation changed")

observed = {
    "workflow_id": wf.get("id"),
    "workflow_name": wf.get("name"),
    "active": wf.get("active"),
    "versionId": wf.get("versionId"),
    "node_count": len(wf.get("nodes", [])),
    "cr10501_present": "SPM_WU105_AVAILABILITY_ANSWER_FIRST_GUARD_V1" in avail_code,
    "cr10502_present": "SPM_WU105_EXPLICIT_FREE_TRIAL_ACTION_GUARD_V1" in free_trial_code,
    "cr10503_present": "SPM_WU105_REFUND_POLICY_ANSWER_FIRST_GUARD_V1" in refund_code,
    "cr10404_present": "SPM_WU104_KNOWN_SLOT_RECONCILE_V1" in persist_code,
    "cr10405_present": "SPM_WU104_SHORT_SEMANTIC_GUARD_V1" in short_code,
    "wu102_queue_operation": q.get("parameters", {}).get("operation"),
    "wu102_queue_matching_columns": qcols.get("matchingColumns"),
    "chat_memory_session_key": memory_key,
}
print(json.dumps(observed, indent=2, ensure_ascii=False))
if errors:
    print("WU105_CR10503_REMOTE_FAIL: " + "; ".join(errors), file=sys.stderr)
    raise SystemExit(1)
print("WU105_CR10503_REMOTE_PASS")
