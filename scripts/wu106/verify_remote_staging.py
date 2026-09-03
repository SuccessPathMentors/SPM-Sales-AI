#!/usr/bin/env python3
import json
import os
import sys
import urllib.request

TARGET = os.getenv("N8N_TARGET_WORKFLOW_ID", "").strip()
BASE = os.getenv("N8N_API_BASE_URL", "").strip().rstrip("/")
KEY = os.getenv("N8N_API_KEY", "").strip()

EXPECTED_NAME = "[STAGING] SPM_WU106_END_TO_END_JOURNEYS_V1"
EXPECTED_NODE_COUNT = 139
EXPECTED_WU106_ID = "vvHvidUHVxM5wTVT"
PROTECTED_IDS = {
    "CMBMpxX5AqqK2UTn",
    "mMZVFxJIxE7a9SSW",
    "1kaRBBFVJYbPxvQG",
    "5COEoxXjk8AvuGBa",
    "Bt3PvOIbFzU0O9gk",
    "KXfalaYSCLdgmf4X",
}

WU106_ENVELOPE = "Build WU106 Journey Orchestration Envelope"
CR10601 = "Apply WU106 Journey Transition Recovery [CR-106-01]"
LOAD_CTRL = "Load WU106 Registration Control [CR-106-02]"
MERGE_CTRL = "Merge WU106 Durable Registration Control [CR-106-02]"
ROOT_RECOVERY = "Apply WU106 Root Journey Recovery [CR-106-02]"
BUILD_CTRL = "Build WU106 Registration Control Snapshot [CR-106-02]"
SAVE_CTRL = "Save WU106 Registration Control [CR-106-02]"
RESTORE_CTRL = "Restore After WU106 Registration Control Save [CR-106-02]"
INIT = "Initialize + Merge Sales State Contract"
CATALOG = "Load SPM V2 62 Intent Catalog"
WU104_DECISION = "Build WU104 Short Query Decision"
WU104_TRIAL = "Apply WU104 Short Trial Inquiry Guard"
PERSIST_FINAL = "Persist WU104 Final Asked Field"
SERIALIZE_WU95 = "Serialize WU95 STAGING Sales State"
SOURCE_NODE = "Apply WU105 Golden Intent Prompt Overlay"
TARGET_NODE = "Generate WU92 Sales Agent Response"
CANON_LOAD = "Load Sales State [STAGING NAMESPACE]"
CANON_SAVE = "Save WU95 Sales State [STAGING NAMESPACE]"

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


def target(name, output=0):
    main = connections.get(name, {}).get("main")
    if not isinstance(main, list) or len(main) <= output:
        return None
    branch = main[output]
    if not isinstance(branch, list) or len(branch) != 1:
        return None
    return branch[0].get("node")


def require_target(source, expected, output=0):
    got = target(source, output)
    if got != expected:
        errors.append(f"topology mismatch {source}[{output}] -> {got!r}, expected {expected!r}")


if str(wf.get("id")) != EXPECTED_WU106_ID:
    errors.append(f"workflow ID mismatch: {wf.get('id')!r}")
if wf.get("name") != EXPECTED_NAME:
    errors.append(f"name mismatch: {wf.get('name')!r}")
if wf.get("active") is True:
    errors.append("workflow unexpectedly active")
if len(wf.get("nodes", [])) != EXPECTED_NODE_COUNT:
    errors.append(f"node count mismatch: {len(wf.get('nodes', []))}")

required_nodes = [
    WU106_ENVELOPE, CR10601, LOAD_CTRL, MERGE_CTRL, ROOT_RECOVERY, BUILD_CTRL,
    SAVE_CTRL, RESTORE_CTRL, INIT, CATALOG, WU104_DECISION, WU104_TRIAL,
    PERSIST_FINAL, SERIALIZE_WU95, SOURCE_NODE, TARGET_NODE, CANON_LOAD, CANON_SAVE,
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

# Locked/upstream paths remain present.
require_target(WU104_DECISION, CR10601)
require_target(CR10601, ROOT_RECOVERY)
require_target(ROOT_RECOVERY, WU104_TRIAL)
require_target(SOURCE_NODE, WU106_ENVELOPE)
require_target(WU106_ENVELOPE, TARGET_NODE)

# CR-106-02 durable control must run before classifier/catalog.
require_target(INIT, LOAD_CTRL)
require_target(LOAD_CTRL, MERGE_CTRL, 0)
require_target(LOAD_CTRL, MERGE_CTRL, 1)
require_target(MERGE_CTRL, CATALOG)

# CR-106-02 control snapshot must be based on final WU95/WU104 asked-field state,
# then converge back to canonical WU95 serialization regardless of redundant save outcome.
require_target(PERSIST_FINAL, BUILD_CTRL)
require_target(BUILD_CTRL, SAVE_CTRL)
require_target(SAVE_CTRL, RESTORE_CTRL, 0)
require_target(SAVE_CTRL, RESTORE_CTRL, 1)
require_target(RESTORE_CTRL, SERIALIZE_WU95)

# Redis isolation and credential reuse.
load_ctrl = nodes.get(LOAD_CTRL, {})
save_ctrl = nodes.get(SAVE_CTRL, {})
canon_load = nodes.get(CANON_LOAD, {})
canon_save = nodes.get(CANON_SAVE, {})
if load_ctrl.get("type") != "n8n-nodes-base.redis" or save_ctrl.get("type") != "n8n-nodes-base.redis":
    errors.append("CR-106-02 control persistence is not Redis")
if load_ctrl.get("credentials") != canon_load.get("credentials"):
    errors.append("CR-106-02 control load credential differs from canonical STAGING Redis")
if save_ctrl.get("credentials") != canon_save.get("credentials"):
    errors.append("CR-106-02 control save credential differs from canonical STAGING Redis")
if "spm:staging:regctrl:" not in str(load_ctrl.get("parameters", {}).get("key", "")):
    errors.append("CR-106-02 control load namespace is not isolated STAGING regctrl")
if "spm:staging:regctrl:" not in str(nodes.get(BUILD_CTRL, {}).get("parameters", {}).get("jsCode", "")):
    errors.append("CR-106-02 control snapshot namespace marker missing")

root_code = str(nodes.get(ROOT_RECOVERY, {}).get("parameters", {}).get("jsCode", ""))
merge_code = str(nodes.get(MERGE_CTRL, {}).get("parameters", {}).get("jsCode", ""))
build_code = str(nodes.get(BUILD_CTRL, {}).get("parameters", {}).get("jsCode", ""))
for marker in [
    "SPM_WU106_CR10602_ROOT_RECOVERY_V1",
    "DURABLE_REGISTRATION_FIELD_BOUND",
    "EXPLICIT_AVAILABILITY_ROOT_OVERRIDE",
    "production_mutation_allowed:false",
    "pii_values_logged:false",
]:
    if marker not in root_code:
        errors.append(f"CR-106-02 root marker missing: {marker}")
for marker in ["SPM_WU106_CR10602_CONTROL_MERGE_V1", "pii_values_loaded:false", "production_mutation_allowed:false"]:
    if marker not in merge_code:
        errors.append(f"CR-106-02 merge marker missing: {marker}")
for marker in ["SPM_WU106_REGISTRATION_CONTROL_V1", "pii_values_stored:false", "raw_message_stored:false", "production_namespace:false"]:
    if marker not in build_code:
        errors.append(f"CR-106-02 snapshot marker missing: {marker}")

# Upstream WU-105/WU-102 safety invariants.
avail_code = str(nodes.get("Apply WU105 Availability Answer-First Guard", {}).get("parameters", {}).get("jsCode", ""))
refund_code = str(nodes.get("Apply WU105 Refund Policy Answer-First Guard", {}).get("parameters", {}).get("jsCode", ""))
if "SPM_WU105_AVAILABILITY_ANSWER_FIRST_GUARD_V1" not in avail_code:
    errors.append("CR-105-01 signature missing")
if "Apply WU105 Explicit Free Trial Action Guard" not in nodes:
    errors.append("CR-105-02 node missing")
if "SPM_WU105_REFUND_POLICY_ANSWER_FIRST_GUARD_V1" not in refund_code:
    errors.append("CR-105-03 signature missing")
if "Load POLICIES [WU91 READ ONLY]" not in nodes:
    errors.append("CR-105-04 policies loader missing")

q = nodes.get("Upsert WU102 Unanswered [STAGING]", {})
qcols = q.get("parameters", {}).get("columns", {})
if q.get("parameters", {}).get("operation") != "appendOrUpdate":
    errors.append("WU102 queue operation changed")
if qcols.get("matchingColumns") != ["queue_event_id"]:
    errors.append("WU102 queue idempotency changed")
memory_key = nodes.get("Redis Chat Memory", {}).get("parameters", {}).get("sessionKey")
if memory_key != "={{ 'spm:staging:chat:' + $json.sessionId }}":
    errors.append("STAGING Redis chat-memory isolation changed")

observed = {
    "workflow_id": wf.get("id"),
    "workflow_name": wf.get("name"),
    "active": wf.get("active"),
    "versionId": wf.get("versionId"),
    "node_count": len(wf.get("nodes", [])),
    "cr10601_present": CR10601 in nodes,
    "cr10602_nodes_present": all(x in nodes for x in [LOAD_CTRL, MERGE_CTRL, ROOT_RECOVERY, BUILD_CTRL, SAVE_CTRL, RESTORE_CTRL]),
    "init_target": target(INIT),
    "control_load_success_target": target(LOAD_CTRL, 0),
    "control_load_failure_target": target(LOAD_CTRL, 1),
    "control_merge_target": target(MERGE_CTRL),
    "cr10601_target": target(CR10601),
    "root_recovery_target": target(ROOT_RECOVERY),
    "persist_final_target": target(PERSIST_FINAL),
    "control_save_success_target": target(SAVE_CTRL, 0),
    "control_save_failure_target": target(SAVE_CTRL, 1),
    "control_restore_target": target(RESTORE_CTRL),
    "registration_control_namespace_isolated": "spm:staging:regctrl:" in str(load_ctrl.get("parameters", {}).get("key", "")),
    "registration_control_reuses_canonical_redis_credentials": load_ctrl.get("credentials") == canon_load.get("credentials") and save_ctrl.get("credentials") == canon_save.get("credentials"),
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
    print("WU106_CR10602_REMOTE_FAIL: " + "; ".join(errors), file=sys.stderr)
    raise SystemExit(1)
print("WU106_CR10602_REMOTE_PASS")
