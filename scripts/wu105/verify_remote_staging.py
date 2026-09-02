#!/usr/bin/env python3
import json
import os
import sys
import urllib.request

TARGET = os.getenv("N8N_TARGET_WORKFLOW_ID", "").strip()
BASE = os.getenv("N8N_API_BASE_URL", "").strip().rstrip("/")
KEY = os.getenv("N8N_API_KEY", "").strip()

PROTECTED_IDS = {
    "CMBMpxX5AqqK2UTn": "Production RC4.3.3",
    "mMZVFxJIxE7a9SSW": "WU-101 STAGING",
    "1kaRBBFVJYbPxvQG": "WU-102 STAGING",
    "5COEoxXjk8AvuGBa": "WU-103 STAGING",
    "Bt3PvOIbFzU0O9gk": "WU-104 STAGING",
}
EXPECTED_NAME = "[STAGING] SPM_WU105_GOLDEN_INTENTS_V1"
EXPECTED_NODE_COUNT = 125
OVERLAY = "Apply WU105 Golden Intent Prompt Overlay"
PROMPT = "Build WU96-Aware Sales Agent Prompt"
GENERATOR = "Generate WU92 Sales Agent Response"
REQUIRED_WU104 = [
    "Build WU104 Short Query Decision",
    "Persist WU104 Awaited Context Hint",
    "Apply WU104 Clarification Response Override",
]

if not TARGET or not BASE or not KEY:
    raise SystemExit("missing required n8n readback environment")
if TARGET in PROTECTED_IDS:
    raise SystemExit(f"protected workflow ID denied: {PROTECTED_IDS[TARGET]}")

req = urllib.request.Request(
    f"{BASE}/workflows/{TARGET}",
    headers={"accept": "application/json", "X-N8N-API-KEY": KEY},
    method="GET",
)
with urllib.request.urlopen(req, timeout=45) as resp:
    wf = json.loads(resp.read().decode("utf-8"))

errors = []
nodes = {n.get("name"): n for n in wf.get("nodes", [])}

if wf.get("active") is True:
    errors.append("remote WU-105 workflow unexpectedly active")
if wf.get("name") != EXPECTED_NAME:
    errors.append(f"remote workflow name mismatch: {wf.get('name')!r}")
if len(wf.get("nodes", [])) != EXPECTED_NODE_COUNT:
    errors.append(f"remote node count mismatch: {len(wf.get('nodes', []))}")
for name in REQUIRED_WU104 + [OVERLAY, PROMPT, GENERATOR]:
    if name not in nodes:
        errors.append(f"required inherited/owned node missing: {name}")

if OVERLAY in nodes:
    overlay = nodes[OVERLAY]
    if overlay.get("type") != "n8n-nodes-base.code":
        errors.append("WU-105 overlay is not deterministic Code node")
    if overlay.get("credentials"):
        errors.append("WU-105 overlay unexpectedly contains credentials")
    code = overlay.get("parameters", {}).get("jsCode", "")
    for token in [
        "SPM_WU105_GOLDEN_INTENT_RUNTIME_V1",
        "answer_first:true",
        "max_followup_questions:1",
        "wu104_authoritative:true",
        "source_action_gates_authoritative:true",
        "irreversible_action_allowed:false",
        "raw_message_logged:false",
        "raw_session_logged:false",
        "secret_values_logged:false",
        "subject_inquiry",
        "pricing",
        "package_comparison",
        "price_objection",
        "free_trial",
        "trial_details",
        "teacher_quality",
        "availability",
        "schedule_request",
        "registration",
        "ready_to_register",
        "human_handoff",
        "refund_policy",
    ]:
        if token not in code:
            errors.append(f"WU-105 overlay token missing: {token}")

for n in wf.get("nodes", []):
    if "WU105" in n.get("name", "") and n.get("type") in {
        "@n8n/n8n-nodes-langchain.lmChatOpenAi",
        "@n8n/n8n-nodes-langchain.chainLlm",
        "@n8n/n8n-nodes-langchain.agent",
    }:
        errors.append("WU-105 second LLM/classifier/agent node detected")

connections = wf.get("connections", {})
def targets(name):
    return [[c.get("node") for c in group] for group in connections.get(name, {}).get("main", [])]

if targets(PROMPT) != [[OVERLAY]]:
    errors.append("prompt must feed WU-105 overlay exactly once")
if targets(OVERLAY) != [[GENERATOR]]:
    errors.append("WU-105 overlay must feed existing response generator")

# Critical inherited WU-104 topology remains intact.
if targets("Merge Durable Sales State + Decide Journey [WU90]") != [["Persist WU104 Awaited Context Hint"]]:
    errors.append("WU-104 awaited-context upstream topology changed")
if targets("Persist WU104 Awaited Context Hint") != [["Serialize WU90 Production Sales State"]]:
    errors.append("WU-104 awaited-context downstream topology changed")
if targets("Build Telemetry Envelope") != [["Apply WU104 Clarification Response Override"]]:
    errors.append("WU-104 clarification response override upstream changed")
if targets("Apply WU104 Clarification Response Override") != [["Redact WU97 Observability Telemetry"]]:
    errors.append("WU-104 clarification response override downstream changed")

# WU-102 queue and STAGING memory isolation remain inherited.
q = nodes.get("Upsert WU102 Unanswered [STAGING]", {})
qcols = q.get("parameters", {}).get("columns", {})
if q.get("parameters", {}).get("operation") != "appendOrUpdate":
    errors.append("WU-102 queue operation changed")
if qcols.get("matchingColumns") != ["queue_event_id"]:
    errors.append("WU-102 queue idempotency key changed")
if q.get("onError") != "continueRegularOutput":
    errors.append("WU-102 queue fail-open changed")

memory_key = nodes.get("Redis Chat Memory", {}).get("parameters", {}).get("sessionKey")
if memory_key != "={{ 'spm:staging:chat:' + $json.sessionId }}":
    errors.append("Redis Chat Memory STAGING isolation mismatch")

observed = {
    "workflow_id": wf.get("id"),
    "workflow_name": wf.get("name"),
    "active": wf.get("active"),
    "versionId": wf.get("versionId"),
    "node_count": len(wf.get("nodes", [])),
    "wu104_nodes_present": [x for x in REQUIRED_WU104 if x in nodes],
    "wu105_overlay_present": OVERLAY in nodes,
    "wu102_queue_operation": q.get("parameters", {}).get("operation"),
    "wu102_queue_matching_columns": qcols.get("matchingColumns"),
    "chat_memory_session_key": memory_key,
}
print(json.dumps(observed, indent=2, ensure_ascii=False))

if errors:
    print("WU105_REMOTE_READBACK_FAIL: " + "; ".join(errors), file=sys.stderr)
    raise SystemExit(1)
print("WU105_REMOTE_READBACK_PASS")
