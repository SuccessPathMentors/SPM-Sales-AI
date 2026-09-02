#!/usr/bin/env python3
import json
import os
import sys
import urllib.request

TARGET = os.getenv("N8N_TARGET_WORKFLOW_ID", "").strip()
BASE = os.getenv("N8N_API_BASE_URL", "").strip().rstrip("/")
KEY = os.getenv("N8N_API_KEY", "").strip()

EXPECTED_NAME = "[STAGING] SPM_WU105_GOLDEN_INTENTS_V1"
EXPECTED_NODE_COUNT = 131
ROUTE_NODE = "Route WU91 Source Family"
POLICY_NODE = "Load POLICIES [WU91 READ ONLY]"
TEMPLATE_NODE = "Load FAQ [WU91 READ ONLY]"
RANK_NODE = "Rank + Compact WU91 Source Evidence"
ERROR_NODE = "Build WU91 Live-or-Blocked Source Evidence"
KB_DOCUMENT_ID = "1JJu6eNurnNbBdikOnOe1u7OvUjcTS8Q14TPHjUiT3lM"
POLICY_SHEET_ID = 1408992606
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

for name in [ROUTE_NODE, POLICY_NODE, TEMPLATE_NODE, RANK_NODE, ERROR_NODE,
             "Apply WU105 Availability Answer-First Guard",
             "Apply WU105 Explicit Free Trial Action Guard",
             "Apply WU105 Refund Policy Answer-First Guard",
             "Persist WU104 Awaited Context Hint",
             "Apply WU104 Short Trial Inquiry Guard"]:
    if name not in nodes:
        errors.append(f"missing required node: {name}")

if POLICY_NODE in nodes and TEMPLATE_NODE in nodes:
    pnode = nodes[POLICY_NODE]
    tnode = nodes[TEMPLATE_NODE]
    p = pnode.get("parameters", {})
    if pnode.get("type") != "n8n-nodes-base.googleSheets":
        errors.append("POLICIES loader is not Google Sheets")
    if pnode.get("credentials") != tnode.get("credentials"):
        errors.append("POLICIES loader credential differs from proven WU91 read loader")
    if str((p.get("documentId") or {}).get("value", "")) != KB_DOCUMENT_ID:
        errors.append("POLICIES loader KB document mismatch")
    if (p.get("sheetName") or {}).get("value") != POLICY_SHEET_ID:
        errors.append("POLICIES loader sheet ID mismatch")
    if (p.get("sheetName") or {}).get("cachedResultName") != "POLICIES":
        errors.append("POLICIES loader sheet name mismatch")
    if ((p.get("filtersUI") or {}).get("values")) != [{"lookupColumn": "status", "lookupValue": "ACTIVE"}]:
        errors.append("POLICIES loader ACTIVE filter mismatch")

route_main = connections.get(ROUTE_NODE, {}).get("main", [])
if len(route_main) < 2 or [x.get("node") for x in route_main[1]] != [POLICY_NODE]:
    errors.append(f"WU91 policies route mismatch: {route_main[1] if len(route_main)>1 else None!r}")
if targets(POLICY_NODE) != targets(TEMPLATE_NODE):
    errors.append("POLICIES loader success/error topology differs from proven template loader")
if targets(POLICY_NODE) and (not targets(POLICY_NODE)[0] or targets(POLICY_NODE)[0][0] != RANK_NODE):
    errors.append("POLICIES loader does not feed source ranker")

rank_code = nodes.get(RANK_NODE, {}).get("parameters", {}).get("jsCode", "")
for token in ["plan.source_family==='policies'", "policy_type:r.policy_type", "rule:r.rule", "customer_answer:r.customer_answer"]:
    if token not in rank_code:
        errors.append(f"policy compaction token missing: {token}")

refund_code = nodes.get("Apply WU105 Refund Policy Answer-First Guard", {}).get("parameters", {}).get("jsCode", "")
if "SPM_WU105_REFUND_POLICY_ANSWER_FIRST_GUARD_V1" not in refund_code:
    errors.append("CR-105-03 signature missing")
avail_code = nodes.get("Apply WU105 Availability Answer-First Guard", {}).get("parameters", {}).get("jsCode", "")
if "SPM_WU105_AVAILABILITY_ANSWER_FIRST_GUARD_V1" not in avail_code:
    errors.append("CR-105-01 signature missing")

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
    "policies_loader_present": POLICY_NODE in nodes,
    "policies_route": route_main[1] if len(route_main) > 1 else None,
    "policies_sheet_id": (nodes.get(POLICY_NODE, {}).get("parameters", {}).get("sheetName") or {}).get("value"),
    "cr10501_present": "SPM_WU105_AVAILABILITY_ANSWER_FIRST_GUARD_V1" in avail_code,
    "cr10502_present": "Apply WU105 Explicit Free Trial Action Guard" in nodes,
    "cr10503_present": "SPM_WU105_REFUND_POLICY_ANSWER_FIRST_GUARD_V1" in refund_code,
    "wu102_queue_operation": q.get("parameters", {}).get("operation"),
    "wu102_queue_matching_columns": qcols.get("matchingColumns"),
    "chat_memory_session_key": memory_key,
}
print(json.dumps(observed, indent=2, ensure_ascii=False))
if errors:
    print("WU105_CR10504_REMOTE_FAIL: " + "; ".join(errors), file=sys.stderr)
    raise SystemExit(1)
print("WU105_CR10504_REMOTE_PASS")
