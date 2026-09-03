#!/usr/bin/env python3
import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path

EXPECTED_INPUT_SHA256 = "aaaa139faa67815f4196fb9779232471c4c8b051a26f0ba0a3be4c56231d4653"
EXPECTED_INPUT_NODE_COUNT = 130
ROUTE_NODE = "Route WU91 Source Family"
RANK_NODE = "Rank + Compact WU91 Source Evidence"
ERROR_NODE = "Build WU91 Live-or-Blocked Source Evidence"
TEMPLATE_NODE = "Load FAQ [WU91 READ ONLY]"
POLICY_NODE = "Load POLICIES [WU91 READ ONLY]"
POLICY_SHEET_ID = 1408992606
POLICY_SHEET_NAME = "POLICIES"
KB_DOCUMENT_ID = "1JJu6eNurnNbBdikOnOe1u7OvUjcTS8Q14TPHjUiT3lM"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def apply(input_path: Path, output_path: Path):
    actual = sha256(input_path)
    if actual != EXPECTED_INPUT_SHA256:
        raise SystemExit(f"CR-105-04 input candidate SHA mismatch: {actual}")

    workflow = json.loads(input_path.read_text(encoding="utf-8"))
    if len(workflow.get("nodes", [])) != EXPECTED_INPUT_NODE_COUNT:
        raise SystemExit(f"CR-105-04 input node count mismatch: {len(workflow.get('nodes', []))}")

    candidate = deepcopy(workflow)
    candidate["active"] = False
    names = [n.get("name") for n in candidate.get("nodes", [])]
    if POLICY_NODE in names:
        raise SystemExit("CR-105-04 policy loader already exists")
    for name in [ROUTE_NODE, RANK_NODE, ERROR_NODE, TEMPLATE_NODE]:
        if names.count(name) != 1:
            raise SystemExit(f"CR-105-04 required node identity mismatch: {name}")

    template = next(n for n in candidate["nodes"] if n.get("name") == TEMPLATE_NODE)
    loader = deepcopy(template)
    loader["name"] = POLICY_NODE
    loader["id"] = "wu105-wu91-policies-read-only-loader-v1"
    tx, ty = template.get("position", [0, 0])
    loader["position"] = [tx, ty + 320]
    loader["notesInFlow"] = True
    loader["notes"] = (
        "CR-105-04 STAGING-only WU91 source-wiring repair. Reads ACTIVE rows from the existing "
        "POLICIES tab in the approved SPM KB using the same read-only Google Sheets credential pattern "
        "as the other WU91 source loaders. No policy content is hard-coded and no write permission is added."
    )

    params = loader.setdefault("parameters", {})
    document = params.get("documentId") or {}
    if str(document.get("value", "")) != KB_DOCUMENT_ID:
        raise SystemExit("CR-105-04 template KB document identity mismatch")
    sheet = params.get("sheetName") or {}
    sheet["value"] = POLICY_SHEET_ID
    sheet["mode"] = "list"
    sheet["cachedResultName"] = POLICY_SHEET_NAME
    sheet["cachedResultUrl"] = (
        f"https://docs.google.com/spreadsheets/d/{KB_DOCUMENT_ID}/edit#gid={POLICY_SHEET_ID}"
    )
    params["sheetName"] = sheet

    filters = (((params.get("filtersUI") or {}).get("values")) or [])
    if filters != [{"lookupColumn": "status", "lookupValue": "ACTIVE"}]:
        raise SystemExit("CR-105-04 template ACTIVE-only filter mismatch")

    candidate["nodes"].append(loader)

    connections = candidate.setdefault("connections", {})
    route = deepcopy(connections.get(ROUTE_NODE) or {})
    main = route.get("main")
    if not isinstance(main, list) or len(main) < 2:
        raise SystemExit("CR-105-04 WU91 route outputs missing")
    policy_branch = main[1]
    if len(policy_branch) != 1 or policy_branch[0].get("node") != RANK_NODE:
        raise SystemExit(f"CR-105-04 unexpected existing policies branch: {policy_branch!r}")

    # Preserve every other route output exactly; only the policies output is repaired.
    original_edge = deepcopy(policy_branch[0])
    main[1] = [{"node": POLICY_NODE, "type": "main", "index": 0}]
    route["main"] = main
    connections[ROUTE_NODE] = route

    template_connections = deepcopy(connections.get(TEMPLATE_NODE) or {})
    template_main = template_connections.get("main")
    if (
        not isinstance(template_main, list)
        or len(template_main) < 1
        or not template_main[0]
        or template_main[0][0].get("node") != RANK_NODE
    ):
        raise SystemExit("CR-105-04 template loader success topology mismatch")
    connections[POLICY_NODE] = template_connections

    # The original direct edge target must still be the downstream success target.
    if original_edge.get("node") != RANK_NODE:
        raise SystemExit("CR-105-04 original policy target changed unexpectedly")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"CR10504_INPUT_SHA256={actual}")
    print(f"CR10504_OUTPUT={output_path}")
    print(f"CR10504_OUTPUT_SHA256={sha256(output_path)}")
    print(f"CR10504_NODE_COUNT={len(candidate.get('nodes', []))}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    apply(args.input, args.output)


if __name__ == "__main__":
    main()
