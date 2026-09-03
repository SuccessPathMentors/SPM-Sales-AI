#!/usr/bin/env python3
"""Read-only, privacy-safe WU-106 runtime diagnostic.

Fetches recent n8n executions for the WU-106 STAGING workflow and emits only
control/state metadata required to diagnose GJ-04. It intentionally excludes
raw customer messages, names, contact details, extracted entity values, model
answers, prompts, and credentials.
"""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

BASE = os.environ.get("N8N_API_BASE_URL", "").strip().rstrip("/")
KEY = os.environ.get("N8N_API_KEY", "").strip()
WORKFLOW_ID = os.environ.get("N8N_TARGET_WORKFLOW_ID", "vvHvidUHVxM5wTVT").strip()
OUT = Path(os.environ.get("WU106_DIAGNOSTIC_OUT", "wu106-runtime-diagnostic.json"))
LIMIT = max(1, min(20, int(os.environ.get("WU106_DIAGNOSTIC_LIMIT", "12"))))

if not BASE or not KEY:
    raise SystemExit("missing n8n read-only diagnostic environment")
if WORKFLOW_ID != "vvHvidUHVxM5wTVT":
    raise SystemExit("diagnostic is hard-scoped to WU-106 STAGING")


def get(path: str) -> dict[str, Any]:
    req = urllib.request.Request(
        BASE + "/" + path.lstrip("/"),
        headers={"accept": "application/json", "X-N8N-API-KEY": KEY},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        raw = resp.read()
    obj = json.loads(raw.decode("utf-8")) if raw else {}
    if not isinstance(obj, dict):
        raise RuntimeError(f"unexpected response shape for {path}")
    return obj


def last_json(run_data: dict[str, Any], node: str) -> dict[str, Any] | None:
    runs = run_data.get(node)
    if not isinstance(runs, list) or not runs:
        return None
    for run in reversed(runs):
        if not isinstance(run, dict):
            continue
        data = run.get("data")
        if not isinstance(data, dict):
            continue
        main = data.get("main")
        if not isinstance(main, list):
            continue
        for branch in reversed(main):
            if not isinstance(branch, list):
                continue
            for item in reversed(branch):
                if isinstance(item, dict) and isinstance(item.get("json"), dict):
                    return item["json"]
    return None


def node_executed(run_data: dict[str, Any], node: str) -> bool:
    return isinstance(run_data.get(node), list) and len(run_data.get(node) or []) > 0


def safe_conversion(j: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(j, dict):
        return None
    state = j.get("sales_state")
    if not isinstance(state, dict):
        return None
    conv = state.get("conversion")
    if not isinstance(conv, dict):
        return None
    return {
        "registration_active": bool(conv.get("registration_active")),
        "registration_status": conv.get("registration_status"),
        "awaiting_field": conv.get("awaiting_field"),
        "pending_confirmation": bool(conv.get("pending_confirmation")),
        "lead_write_status": conv.get("lead_write_status"),
    }


def safe_classification(j: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(j, dict):
        return None
    c = j.get("classification")
    if not isinstance(c, dict):
        return None
    return {
        "spm_intent": c.get("spm_intent"),
        "confidence": c.get("confidence"),
        "threshold": c.get("threshold"),
        "ambiguous": c.get("ambiguous"),
        "rationale_code": c.get("rationale_code"),
    }


def safe_wu104(j: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(j, dict):
        return None
    d = j.get("wu104_short_query_decision")
    if not isinstance(d, dict):
        return None
    return {
        "short_query_type": d.get("short_query_type"),
        "context_available": d.get("context_available"),
        "awaited_entity": d.get("awaited_entity"),
        "context_binding_status": d.get("context_binding_status"),
        "binding_source": d.get("binding_source"),
        "resolved_intent": d.get("resolved_intent"),
        "resolved_entity_type": d.get("resolved_entity_type"),
        "clarification_required": d.get("clarification_required"),
        "safe_action": d.get("safe_action"),
    }


def safe_cr(j: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(j, dict):
        return None
    r = j.get("wu106_cr10601_recovery")
    if not isinstance(r, dict):
        return None
    return {
        "applied": r.get("applied"),
        "reason": r.get("reason"),
        "awaiting_field": r.get("awaiting_field"),
        "registration_active": r.get("registration_active"),
        "explicit_availability_pattern": r.get("explicit_availability_pattern"),
        "original_intent": r.get("original_intent"),
        "result_intent": r.get("result_intent"),
    }


def safe_validation(j: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(j, dict):
        return None
    v = j.get("wu95_lead_validation")
    if not isinstance(v, dict):
        return None
    return {
        "mode": v.get("mode"),
        "flow": v.get("flow"),
        "valid": v.get("valid"),
        "missing_fields": v.get("missing_fields"),
        "registration_status": v.get("registration_status"),
        "awaiting_field": v.get("awaiting_field"),
        "write_allowed_by_validation": v.get("write_allowed_by_validation"),
    }


def safe_serialized_conversion(j: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(j, dict):
        return None
    raw = j.get("wu95_sales_state_text")
    if not isinstance(raw, str):
        return None
    try:
        state = json.loads(raw)
    except Exception:
        return {"parse_error": True}
    conv = state.get("conversion") if isinstance(state, dict) else None
    if not isinstance(conv, dict):
        return None
    return {
        "registration_active": bool(conv.get("registration_active")),
        "registration_status": conv.get("registration_status"),
        "awaiting_field": conv.get("awaiting_field"),
        "pending_confirmation": bool(conv.get("pending_confirmation")),
        "lead_write_status": conv.get("lead_write_status"),
    }


params = urllib.parse.urlencode({"workflowId": WORKFLOW_ID, "limit": LIMIT})
listing = get("executions?" + params)
items = listing.get("data")
if not isinstance(items, list):
    items = []

records: list[dict[str, Any]] = []
for item in items:
    if not isinstance(item, dict) or item.get("id") is None:
        continue
    eid = str(item["id"])
    detail = get(f"executions/{urllib.parse.quote(eid)}?includeData=true")
    data = detail.get("data") if isinstance(detail.get("data"), dict) else {}
    result_data = data.get("resultData") if isinstance(data.get("resultData"), dict) else {}
    run_data = result_data.get("runData") if isinstance(result_data.get("runData"), dict) else {}
    workflow_data = detail.get("workflowData") if isinstance(detail.get("workflowData"), dict) else {}

    init = last_json(run_data, "Initialize + Merge Sales State Contract")
    classifier = last_json(run_data, "Validate SPM V2 Classifier Output")
    wu104 = last_json(run_data, "Build WU104 Short Query Decision")
    cr = last_json(run_data, "Apply WU106 Journey Transition Recovery [CR-106-01]")
    validation = last_json(run_data, "Validate WU95 Lead Contract")
    serialized = last_json(run_data, "Serialize WU95 STAGING Sales State")

    records.append({
        "execution_id": eid,
        "status": detail.get("status") or item.get("status"),
        "mode": detail.get("mode") or item.get("mode"),
        "started_at": detail.get("startedAt") or item.get("startedAt"),
        "stopped_at": detail.get("stoppedAt") or item.get("stoppedAt"),
        "workflow_version_id": workflow_data.get("versionId"),
        "workflow_node_count": len(workflow_data.get("nodes") or []) if isinstance(workflow_data.get("nodes"), list) else None,
        "cr10601_node_in_execution_workflow": any(
            isinstance(n, dict) and n.get("name") == "Apply WU106 Journey Transition Recovery [CR-106-01]"
            for n in (workflow_data.get("nodes") or [])
        ) if isinstance(workflow_data.get("nodes"), list) else None,
        "loaded_conversion": safe_conversion(init),
        "classifier": safe_classification(classifier),
        "classifier_route_after_validation": classifier.get("classifier_route") if isinstance(classifier, dict) else None,
        "wu104": safe_wu104(wu104),
        "cr10601": safe_cr(cr),
        "wu95_validation": safe_validation(validation),
        "conversion_after_wu95_validation": safe_conversion(validation),
        "serialized_conversion": safe_serialized_conversion(serialized),
        "redis_save_success_path_executed": node_executed(run_data, "Restore Context After WU95 Redis Save"),
        "redis_save_failure_path_executed": node_executed(run_data, "Build WU95 Redis Save Failure Context"),
        "final_response_executed": node_executed(run_data, "RC3 Chat Response"),
    })

report = {
    "schema": "SPM_WU106_RUNTIME_DIAGNOSTIC_V1",
    "workflow_id": WORKFLOW_ID,
    "privacy": {
        "raw_messages_logged": False,
        "pii_values_logged": False,
        "model_answers_logged": False,
        "credentials_logged": False,
    },
    "execution_count": len(records),
    "executions": records,
}
OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))
