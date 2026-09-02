#!/usr/bin/env python3
import json
import subprocess
import tempfile
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "n8n" / "workflows" / "production" / "SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json"
MANIFEST = ROOT / "contracts" / "WU105_GOLDEN_INTENTS_V1.json"
BUILDER = ROOT / "scripts" / "wu105" / "build_candidate.py"
PROMPT_NODE = "Build WU96-Aware Sales Agent Prompt"
GENERATOR_NODE = "Generate WU92 Sales Agent Response"
OVERLAY_NODE = "Apply WU105 Golden Intent Prompt Overlay"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as td:
        output = Path(td) / "candidate.json"
        subprocess.run([
            "python", str(BUILDER),
            "--baseline", str(BASELINE),
            "--manifest", str(MANIFEST),
            "--output", str(output),
        ], check=True)
        candidate = json.loads(output.read_text(encoding="utf-8"))

    require(candidate.get("active") is False, "WU-105 candidate must remain inactive")
    require(candidate.get("name") == "[STAGING] SPM_WU105_GOLDEN_INTENTS_V1", "unexpected candidate name")
    require(len(candidate["nodes"]) == len(baseline["nodes"]) + 1, "WU-105 may add exactly one runtime node in V1")

    base_nodes = {n["name"]: n for n in baseline["nodes"]}
    cand_nodes = {n["name"]: n for n in candidate["nodes"]}
    require(OVERLAY_NODE not in base_nodes and OVERLAY_NODE in cand_nodes, "overlay node identity mismatch")
    for name, node in base_nodes.items():
        require(name in cand_nodes, f"locked baseline node removed: {name}")
        require(cand_nodes[name] == node, f"locked baseline node modified: {name}")

    overlay = cand_nodes[OVERLAY_NODE]
    require(overlay["type"] == "n8n-nodes-base.code", "overlay must be deterministic Code node")
    require("credentials" not in overlay, "overlay must not add credentials")
    code = overlay.get("parameters", {}).get("jsCode", "")
    for row in manifest["intents"]:
        require(row["intent"] in code, f"golden intent missing from embedded overlay: {row['intent']}")
    for invariant in [
        "answer_first:true",
        "max_followup_questions:1",
        "wu104_authoritative:true",
        "source_action_gates_authoritative:true",
        "irreversible_action_allowed:false",
        "raw_message_logged:false",
        "raw_session_logged:false",
        "secret_values_logged:false",
    ]:
        require(invariant in code, f"missing overlay invariant: {invariant}")

    base_connections = deepcopy(baseline["connections"])
    cand_connections = deepcopy(candidate["connections"])
    original_prompt = base_connections[PROMPT_NODE]
    require(original_prompt["main"][0][0]["node"] == GENERATOR_NODE, "locked baseline prompt topology unexpected")

    expected_prompt = deepcopy(original_prompt)
    expected_prompt["main"] = [[{"node": OVERLAY_NODE, "type": "main", "index": 0}]]
    require(cand_connections[PROMPT_NODE] == expected_prompt, "prompt node must be rewired only to WU-105 overlay")
    require(cand_connections[OVERLAY_NODE] == {"main": [[{"node": GENERATOR_NODE, "type": "main", "index": 0}]]}, "overlay must feed the existing generator")

    for name, conn in base_connections.items():
        if name == PROMPT_NODE:
            continue
        require(cand_connections.get(name) == conn, f"unrelated connection modified: {name}")

    # No second classifier/model or external execution node is introduced.
    base_types = [n.get("type") for n in baseline["nodes"]]
    cand_types = [n.get("type") for n in candidate["nodes"]]
    for model_type in ["@n8n/n8n-nodes-langchain.lmChatOpenAi", "@n8n/n8n-nodes-langchain.chainLlm"]:
        require(cand_types.count(model_type) == base_types.count(model_type), f"WU-105 may not add model node type {model_type}")
    require(cand_types.count("n8n-nodes-base.code") == base_types.count("n8n-nodes-base.code") + 1, "only one deterministic Code node may be added")

    print("PASS WU-105 candidate adds exactly one deterministic prompt-overlay node")
    print("PASS all locked baseline nodes remain byte-equivalent as parsed JSON")
    print("PASS only prompt->generator main topology is interposed")
    print("PASS no new model, credentials, or external execution node")


if __name__ == "__main__":
    main()
