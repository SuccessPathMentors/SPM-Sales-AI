#!/usr/bin/env python3
"""
Safe GitHub -> n8n non-production workflow deployer.

Safety properties:
- DEV/STAGING only.
- Production workflow IDs are hard-denied.
- Existing published/active workflows are never updated.
- No publish/activate/deactivate endpoint is called.
- PUT uses publishIfActive=false as defense in depth.
- Source JSON is reduced to the n8n Public API writable workflow schema.
- Apply mode requires an exact SHA-256 and an explicit non-production confirmation token.
- API keys are read only from environment variables and never printed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ALLOWED_ENVIRONMENTS = {"dev", "staging"}
PROTECTED_PRODUCTION_WORKFLOW_IDS = {
    "CMBMpxX5AqqK2UTn",  # RC4.3.3 live production
}
CONFIRM_TOKEN = "SPM_NONPROD_ONLY"

WRITABLE_TOP_LEVEL = {
    "name",
    "description",
    "nodes",
    "connections",
    "nodeGroups",
    "settings",
    "staticData",
    "pinData",
}
WRITABLE_SETTINGS = {
    "saveExecutionProgress",
    "saveManualExecutions",
    "saveDataErrorExecution",
    "saveDataSuccessExecution",
    "executionTimeout",
    "errorWorkflow",
    "timezone",
    "executionOrder",
    "callerPolicy",
    "callerIds",
    "timeSavedMode",
    "timeSavedPerExecution",
    "redactionPolicy",
    "availableInMCP",
    "customTelemetryTags",
}
INTERNAL_SETTINGS_DROPPED = {"binaryMode", "credentialResolverId"}


class SafetyError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json_bytes(path: Path) -> tuple[bytes, dict[str, Any]]:
    raw = path.read_bytes()
    try:
        obj = json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise SafetyError(f"Artifact is not UTF-8 JSON: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SafetyError(f"Artifact is invalid JSON: {path}: {exc}") from exc
    if not isinstance(obj, dict):
        raise SafetyError("Workflow artifact root must be a JSON object")
    return raw, obj


def validate_graph(workflow: dict[str, Any]) -> dict[str, Any]:
    for required in ("name", "nodes", "connections", "settings"):
        if required not in workflow:
            raise SafetyError(f"Missing required workflow field: {required}")

    if not isinstance(workflow["name"], str) or not workflow["name"].strip():
        raise SafetyError("Workflow name must be a non-empty string")
    if not isinstance(workflow["nodes"], list) or not workflow["nodes"]:
        raise SafetyError("Workflow nodes must be a non-empty array")
    if not isinstance(workflow["connections"], dict):
        raise SafetyError("Workflow connections must be an object")
    if not isinstance(workflow["settings"], dict):
        raise SafetyError("Workflow settings must be an object")

    node_names: list[str] = []
    node_ids: list[str] = []
    credential_refs: list[dict[str, str]] = []

    for idx, node in enumerate(workflow["nodes"]):
        if not isinstance(node, dict):
            raise SafetyError(f"Node #{idx} is not an object")
        for field in ("name", "type", "parameters", "position"):
            if field not in node:
                raise SafetyError(f"Node #{idx} missing field: {field}")
        name = node.get("name")
        if not isinstance(name, str) or not name.strip():
            raise SafetyError(f"Node #{idx} has invalid name")
        node_names.append(name)
        node_id = node.get("id")
        if isinstance(node_id, str) and node_id:
            node_ids.append(node_id)

        creds = node.get("credentials")
        if isinstance(creds, dict):
            for cred_type, ref in creds.items():
                if isinstance(ref, dict):
                    cred_id = ref.get("id")
                    cred_name = ref.get("name")
                    credential_refs.append(
                        {
                            "node": name,
                            "type": str(cred_type),
                            "id": str(cred_id) if cred_id is not None else "",
                            "name": str(cred_name) if cred_name is not None else "",
                        }
                    )

    if len(node_names) != len(set(node_names)):
        raise SafetyError("Duplicate node names found")
    nonempty_ids = [x for x in node_ids if x]
    if len(nonempty_ids) != len(set(nonempty_ids)):
        raise SafetyError("Duplicate non-empty node IDs found")

    names = set(node_names)
    unknown_sources = sorted(k for k in workflow["connections"] if k not in names)
    if unknown_sources:
        raise SafetyError(
            "Connections reference unknown source node(s): " + ", ".join(unknown_sources)
        )

    unknown_targets: set[str] = set()

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            target = value.get("node")
            if isinstance(target, str) and target not in names:
                unknown_targets.add(target)
            for v in value.values():
                walk(v)
        elif isinstance(value, list):
            for v in value:
                walk(v)

    walk(workflow["connections"])
    if unknown_targets:
        raise SafetyError(
            "Connections reference unknown target node(s): "
            + ", ".join(sorted(unknown_targets))
        )

    return {
        "node_count": len(node_names),
        "connection_source_count": len(workflow["connections"]),
        "credential_reference_count": len(credential_refs),
        "credential_references": credential_refs,
    }


def sanitize_workflow(workflow: dict[str, Any], environment: str) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key in WRITABLE_TOP_LEVEL:
        if key in workflow:
            value = workflow[key]
            if value is not None:
                payload[key] = value

    payload.setdefault("settings", {})
    payload["settings"] = {
        key: value
        for key, value in payload["settings"].items()
        if key in WRITABLE_SETTINGS and key not in INTERNAL_SETTINGS_DROPPED
    }

    prefix = f"[{environment.upper()}] "
    original_name = str(payload["name"]).strip()
    if not original_name.startswith(prefix):
        payload["name"] = prefix + original_name

    # Never make a non-production copy callable through MCP by default.
    if payload["settings"].get("availableInMCP") is True:
        payload["settings"]["availableInMCP"] = False

    for required in ("name", "nodes", "connections", "settings"):
        if required not in payload:
            raise SafetyError(f"Sanitized payload missing required field: {required}")

    return payload


def api_request(
    base_url: str,
    api_key: str,
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    url = base_url.rstrip("/") + "/" + path.lstrip("/")
    data = None
    headers = {
        "accept": "application/json",
        "X-N8N-API-KEY": api_key,
    }
    if body is not None:
        data = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:2000]
        raise SafetyError(f"n8n API {method} {path} failed: HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise SafetyError(f"n8n API {method} {path} connection failed: {exc.reason}") from exc

    if not raw:
        return {}
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise SafetyError(f"n8n API {method} {path} returned non-JSON") from exc
    if not isinstance(parsed, dict):
        raise SafetyError(f"n8n API {method} {path} returned unexpected JSON shape")
    return parsed


def assert_safe_target(target: dict[str, Any], target_id: str, environment: str) -> None:
    if target_id in PROTECTED_PRODUCTION_WORKFLOW_IDS:
        raise SafetyError(f"Protected production workflow ID is denied: {target_id}")
    if target.get("active") is True:
        raise SafetyError(
            f"Target workflow {target_id} is published/active; MIG-003 refuses to update it"
        )
    expected_prefix = f"[{environment.upper()}] "
    remote_name = target.get("name")
    if not isinstance(remote_name, str) or not remote_name.startswith(expected_prefix):
        raise SafetyError(
            f"Target workflow name must start with {expected_prefix!r}; got {remote_name!r}"
        )


def write_result(path: Path, result: dict[str, Any]) -> None:
    safe = dict(result)
    for key in list(safe):
        if any(token in key.lower() for token in ("api_key", "password", "secret", "token")):
            safe.pop(key, None)
    path.write_text(
        json.dumps(safe, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--environment", required=True, choices=sorted(ALLOWED_ENVIRONMENTS))
    parser.add_argument("--expected-sha256")
    parser.add_argument("--target-workflow-id")
    parser.add_argument("--mode", choices=("dry-run", "apply"), default="dry-run")
    parser.add_argument("--allow-create", action="store_true", help="Explicitly permit one-time creation when no target ID is configured")
    parser.add_argument("--result-file", default="deployment-result.json")
    args = parser.parse_args()

    artifact = Path(args.artifact)
    if not artifact.is_file():
        raise SafetyError(f"Artifact not found: {artifact}")

    raw, source = load_json_bytes(artifact)
    digest = sha256_bytes(raw)
    graph = validate_graph(source)
    payload = sanitize_workflow(source, args.environment)

    source_id = source.get("id")
    source_is_production_export = (
        isinstance(source_id, str) and source_id in PROTECTED_PRODUCTION_WORKFLOW_IDS
    )

    if args.expected_sha256:
        expected = args.expected_sha256.strip().lower()
        if digest != expected:
            raise SafetyError(f"SHA-256 mismatch: expected {expected}, actual {digest}")
    elif args.mode == "apply":
        raise SafetyError("--expected-sha256 is mandatory in apply mode")

    target_id = (args.target_workflow_id or os.getenv("N8N_TARGET_WORKFLOW_ID") or "").strip()
    if target_id in PROTECTED_PRODUCTION_WORKFLOW_IDS:
        raise SafetyError(f"Protected production workflow ID is denied: {target_id}")

    base_result = {
        "schema": "SPM_N8N_NONPROD_DEPLOY_RESULT_V1",
        "timestamp_epoch": int(time.time()),
        "mode": args.mode,
        "environment": args.environment,
        "artifact": str(artifact),
        "artifact_sha256": digest,
        "source_workflow_name": source.get("name"),
        "source_workflow_id": source_id,
        "source_is_production_export": source_is_production_export,
        "sanitized_workflow_name": payload.get("name"),
        "node_count": graph["node_count"],
        "connection_source_count": graph["connection_source_count"],
        "credential_reference_count": graph["credential_reference_count"],
        "target_workflow_id": target_id or None,
        "protected_production_ids_checked": sorted(PROTECTED_PRODUCTION_WORKFLOW_IDS),
        "published_or_activated": False,
    }

    if args.mode == "dry-run":
        base_result["status"] = "PASS_DRY_RUN"
        base_result["operation"] = "NONE"
        write_result(Path(args.result_file), base_result)
        print(json.dumps(base_result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    if os.getenv("SPM_DEPLOY_CONFIRM") != CONFIRM_TOKEN:
        raise SafetyError(f"Apply mode requires SPM_DEPLOY_CONFIRM={CONFIRM_TOKEN}")

    base_url = (os.getenv("N8N_API_BASE_URL") or "").strip()
    api_key = (os.getenv("N8N_API_KEY") or "").strip()
    if not base_url or not api_key:
        raise SafetyError("Apply mode requires N8N_API_BASE_URL and N8N_API_KEY")

    parsed_url = urllib.parse.urlparse(base_url)
    if parsed_url.scheme != "https":
        raise SafetyError("N8N_API_BASE_URL must use HTTPS")
    if not base_url.rstrip("/").endswith("/api/v1"):
        raise SafetyError("N8N_API_BASE_URL must end with /api/v1")

    if target_id:
        current = api_request(base_url, api_key, "GET", f"workflows/{target_id}")
        assert_safe_target(current, target_id, args.environment)
        updated = api_request(
            base_url,
            api_key,
            "PUT",
            f"workflows/{target_id}?publishIfActive=false",
            payload,
        )
        returned_id = str(updated.get("id") or target_id)
        if returned_id != target_id:
            raise SafetyError(f"n8n returned unexpected workflow ID: {returned_id} != {target_id}")
        verified = api_request(base_url, api_key, "GET", f"workflows/{target_id}")
        assert_safe_target(verified, target_id, args.environment)
        operation = "UPDATE_INACTIVE_NONPROD"
        final_id = target_id
    else:
        if not args.allow_create:
            raise SafetyError(
                "No N8N_TARGET_WORKFLOW_ID configured. Refusing implicit create; "
                "use --allow-create for a deliberate one-time non-production creation."
            )
        created = api_request(base_url, api_key, "POST", "workflows", payload)
        final_id = str(created.get("id") or "").strip()
        if not final_id:
            raise SafetyError("n8n create response did not return workflow ID")
        if final_id in PROTECTED_PRODUCTION_WORKFLOW_IDS:
            raise SafetyError("n8n unexpectedly returned a protected production workflow ID")
        verified = api_request(base_url, api_key, "GET", f"workflows/{final_id}")
        assert_safe_target(verified, final_id, args.environment)
        operation = "CREATE_INACTIVE_NONPROD"

    base_result.update(
        {
            "status": "PASS_APPLY",
            "operation": operation,
            "target_workflow_id": final_id,
            "remote_active_after": bool(verified.get("active")),
            "remote_name_after": verified.get("name"),
            "remote_version_id_after": verified.get("versionId"),
        }
    )
    write_result(Path(args.result_file), base_result)
    print(json.dumps(base_result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SafetyError as exc:
        print(f"SAFETY_STOP: {exc}", file=sys.stderr)
        raise SystemExit(2)
