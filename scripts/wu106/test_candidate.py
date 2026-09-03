#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_WU105_SHA256 = "42ba2b9de1f52c0db1fc32e59974dc40ebce80b787677ac6b0d4418a6315bca1"
EXPECTED_WU105_NODE_COUNT = 131
EXPECTED_WU106_NODE_COUNT = 132
SOURCE_NODE = "Apply WU105 Golden Intent Prompt Overlay"
TARGET_NODE = "Generate WU92 Sales Agent Response"
WU106_NODE = "Build WU106 Journey Orchestration Envelope"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def target_of(workflow, source):
    main = workflow.get("connections", {}).get(source, {}).get("main")
    require(isinstance(main, list) and len(main) == 1 and len(main[0]) == 1, f"unexpected topology from {source}")
    return main[0][0].get("node")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    args = parser.parse_args()

    require(sha256(args.baseline) == EXPECTED_WU105_SHA256, "baseline is not exact locked WU-105 final candidate")
    base = json.loads(args.baseline.read_text(encoding="utf-8"))
    cand = json.loads(args.candidate.read_text(encoding="utf-8"))

    require(len(base["nodes"]) == EXPECTED_WU105_NODE_COUNT, "WU-105 baseline node count drift")
    require(len(cand["nodes"]) == EXPECTED_WU106_NODE_COUNT, "WU-106 candidate must add exactly one node")
    require(cand.get("active") is False, "WU-106 candidate must remain inactive")
    require(cand.get("name") == "[STAGING] SPM_WU106_END_TO_END_JOURNEYS_V1", "candidate name mismatch")

    base_names = [n.get("name") for n in base["nodes"]]
    cand_names = [n.get("name") for n in cand["nodes"]]
    require(WU106_NODE not in base_names, "WU-106 node unexpectedly exists in locked WU-105")
    require(cand_names.count(WU106_NODE) == 1, "WU-106 envelope must exist exactly once")
    require(set(base_names).issubset(set(cand_names)), "locked upstream node removed")
    require(len(set(cand_names) - set(base_names)) == 1, "WU-106 baseline may add only one node")

    require(target_of(base, SOURCE_NODE) == TARGET_NODE, "locked WU-105 source topology drift")
    require(target_of(cand, SOURCE_NODE) == WU106_NODE, "WU-106 node not inserted after WU-105 overlay")
    require(target_of(cand, WU106_NODE) == TARGET_NODE, "WU-106 node must return to original generator")

    # All original nodes must be byte-equivalent as JSON objects.
    base_by_name = {n["name"]: n for n in base["nodes"]}
    cand_by_name = {n["name"]: n for n in cand["nodes"] if n["name"] in base_by_name}
    for name, original in base_by_name.items():
        require(cand_by_name[name] == original, f"locked upstream node mutated: {name}")

    node = next(n for n in cand["nodes"] if n.get("name") == WU106_NODE)
    require(node.get("type") == "n8n-nodes-base.code", "WU-106 baseline node must be deterministic Code node")
    js = str(node.get("parameters", {}).get("jsCode", ""))
    for required in [
        "OBSERVE_ONLY_BASELINE",
        "state_mutated:false",
        "prompt_mutated:false",
        "action_permission_mutated:false",
        "irreversible_action_allowed:false",
        "raw_message_logged:false",
        "raw_session_logged:false",
        "secret_values_logged:false",
        "sales_state.conversion.awaiting_field" if False else "conv.awaiting_field",
        "journey.awaiting_entity",
    ]:
        require(required in js, f"WU-106 baseline safety marker missing: {required}")

    # Fail if the new node appears to create an external write/action surface.
    forbidden_fragments = [
        "httpRequest",
        "googleSheets",
        "redis",
        "executeWorkflow",
        "ACTION_SUCCESS'",  # observe-only baseline must not emit success
        "sales_state:",     # must not replace/write the authoritative state object
        "sales_agent_prompt:",
        "proposed_action:",
    ]
    for fragment in forbidden_fragments:
        require(fragment not in js, f"observe-only baseline contains forbidden mutation/action fragment: {fragment}")

    # Existing node-type inventory must change only by one deterministic Code node.
    def counts(workflow):
        out = {}
        for n in workflow["nodes"]:
            out[n.get("type")] = out.get(n.get("type"), 0) + 1
        return out
    bc = counts(base)
    cc = counts(cand)
    for node_type, count in bc.items():
        expected = count + (1 if node_type == "n8n-nodes-base.code" else 0)
        require(cc.get(node_type) == expected, f"node type inventory changed unexpectedly: {node_type}")
    require(set(cc) == set(bc), "new external node type introduced")

    print("WU106_CANDIDATE_STATIC_PASS")
    print(f"candidate_sha256={sha256(args.candidate)}")
    print(f"node_count={len(cand['nodes'])}")
    print("mode=OBSERVE_ONLY_BASELINE")
    print("production_mutation_allowed=false")


if __name__ == "__main__":
    main()
