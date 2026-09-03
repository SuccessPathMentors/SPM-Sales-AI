#!/usr/bin/env python3
import argparse
import json
import tempfile
from pathlib import Path

from apply_cr10504 import (
    EXPECTED_INPUT_NODE_COUNT,
    KB_DOCUMENT_ID,
    POLICY_NODE,
    POLICY_SHEET_ID,
    POLICY_SHEET_NAME,
    RANK_NODE,
    ROUTE_NODE,
    TEMPLATE_NODE,
    apply,
    sha256,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    args = parser.parse_args()

    base = json.loads(args.input.read_text(encoding="utf-8"))
    base_connections = base.get("connections", {})
    base_route_main = base_connections[ROUTE_NODE]["main"]
    assert base_route_main[1][0]["node"] == RANK_NODE, "fixture must prove the missing-loader defect"
    assert POLICY_NODE not in {n.get("name") for n in base.get("nodes", [])}

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "candidate.json"
        apply(args.input, out)
        candidate = json.loads(out.read_text(encoding="utf-8"))

    nodes = {n.get("name"): n for n in candidate.get("nodes", [])}
    assert len(candidate.get("nodes", [])) == EXPECTED_INPUT_NODE_COUNT + 1
    assert candidate.get("active") is False
    assert POLICY_NODE in nodes

    loader = nodes[POLICY_NODE]
    template = nodes[TEMPLATE_NODE]
    assert loader.get("type") == "n8n-nodes-base.googleSheets"
    assert loader.get("typeVersion") == template.get("typeVersion")
    assert loader.get("credentials") == template.get("credentials"), "must reuse existing read credential only"

    p = loader.get("parameters", {})
    assert str((p.get("documentId") or {}).get("value")) == KB_DOCUMENT_ID
    assert (p.get("sheetName") or {}).get("value") == POLICY_SHEET_ID
    assert (p.get("sheetName") or {}).get("cachedResultName") == POLICY_SHEET_NAME
    assert ((p.get("filtersUI") or {}).get("values")) == [
        {"lookupColumn": "status", "lookupValue": "ACTIVE"}
    ]
    assert p.get("operation") in (None, "read", "getAll"), "loader must not be a write operation"

    con = candidate.get("connections", {})
    route_main = con[ROUTE_NODE]["main"]
    assert route_main[1] == [{"node": POLICY_NODE, "type": "main", "index": 0}]
    assert con[POLICY_NODE] == con[TEMPLATE_NODE], "policy loader must inherit the proven WU91 read/error topology"
    assert con[POLICY_NODE]["main"][0][0]["node"] == RANK_NODE

    # All non-policy switch outputs must remain byte-equivalent structurally.
    for idx, branch in enumerate(base_route_main):
        if idx != 1:
            assert route_main[idx] == branch, f"unrelated WU91 switch output {idx} changed"

    rank_code = nodes[RANK_NODE].get("parameters", {}).get("jsCode", "")
    for token in [
        "plan.source_family==='policies'",
        "policy_type:r.policy_type",
        "rule:r.rule",
        "customer_answer:r.customer_answer",
    ]:
        assert token in rank_code, f"existing policy compaction contract missing: {token}"

    # Existing WU-105 repairs must remain in the candidate.
    assert "Apply WU105 Availability Answer-First Guard" in nodes
    assert "Apply WU105 Explicit Free Trial Action Guard" in nodes
    assert "Apply WU105 Refund Policy Answer-First Guard" in nodes
    refund_code = nodes["Apply WU105 Refund Policy Answer-First Guard"].get("parameters", {}).get("jsCode", "")
    assert "SPM_WU105_REFUND_POLICY_ANSWER_FIRST_GUARD_V1" in refund_code

    print(f"CR10504_TEST_OUTPUT_SHA256={sha256(out) if out.exists() else 'temp_removed'}")
    print("PASS missing policies branch is repaired with one ACTIVE-only read loader")
    print("PASS approved KB document and POLICIES sheet identity are exact")
    print("PASS existing OAuth credential is reused with no write operation")
    print("PASS unrelated WU91 source-family routes remain unchanged")
    print("PASS policy evidence compaction feeds rule/customer_answer to source gate")
    print("PASS CR-105-01/02/03 remain present")


if __name__ == "__main__":
    main()
