#!/usr/bin/env python3
import hashlib
import json
import subprocess
import tempfile
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRODUCTION = ROOT / "n8n" / "workflows" / "production" / "SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json"
MANIFEST = ROOT / "contracts" / "WU105_GOLDEN_INTENTS_V1.json"
WU104_BUILDER = ROOT / "scripts" / "wu104" / "build_context_await_candidate.py"
WU105_BUILDER = ROOT / "scripts" / "wu105" / "build_candidate.py"
EXPECTED_WU104_SHA256 = "d0c2ad10c3455b435868a8b7d4c874d31d27ae35e64844d62713d1a5ba74e45f"
PROMPT_NODE = "Build WU96-Aware Sales Agent Prompt"
GENERATOR_NODE = "Generate WU92 Sales Agent Response"
OVERLAY_NODE = "Apply WU105 Golden Intent Prompt Overlay"
REQUIRED_WU104_NODES = {
    "Build WU104 Short Query Decision",
    "Persist WU104 Awaited Context Hint",
    "Apply WU104 Clarification Response Override",
}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        wu104_path = td / "wu104.json"
        output = td / "wu105.json"
        subprocess.run([
            "python", str(WU104_BUILDER),
            "--baseline", str(PRODUCTION),
            "--output", str(wu104_path),
        ], check=True)
        require(sha256(wu104_path) == EXPECTED_WU104_SHA256, "current deterministic WU-104 upstream SHA mismatch")
        subprocess.run([
            "python", str(WU105_BUILDER),
            "--baseline", str(wu104_path),
            "--manifest", str(MANIFEST),
            "--output", str(output),
        ], check=True)
        baseline = json.loads(wu104_path.read_text(encoding="utf-8"))
        candidate = json.loads(output.read_text(encoding="utf-8"))

    require(candidate.get("active") is False, "WU-105 candidate must remain inactive")
    require(candidate.get("name") == "[STAGING] SPM_WU105_GOLDEN_INTENTS_V1", "unexpected candidate name")
    require(len(baseline["nodes"]) == 124, f"expected current WU-104 upstream to contain 124 nodes, got {len(baseline['nodes'])}")
    require(len(candidate["nodes"]) == 125, f"expected WU-105 candidate to contain 125 nodes, got {len(candidate['nodes'])}")
    require(len(candidate["nodes"]) == len(baseline["nodes"]) + 1, "WU-105 may add exactly one runtime node in V1")

    base_nodes = {n["name"]: n for n in baseline["nodes"]}
    cand_nodes = {n["name"]: n for n in candidate["nodes"]}
    require(REQUIRED_WU104_NODES.issubset(base_nodes), "current WU-104 controls missing from upstream baseline")
    require(REQUIRED_WU104_NODES.issubset(cand_nodes), "WU-105 candidate dropped current WU-104 controls")
    require(OVERLAY_NODE not in base_nodes and OVERLAY_NODE in cand_nodes, "overlay node identity mismatch")

    for name, node in base_nodes.items():
        require(name in cand_nodes, f"WU-104 upstream node removed: {name}")
        require(cand_nodes[name] == node, f"WU-104 upstream node modified: {name}")

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
    require(original_prompt["main"][0][0]["node"] == GENERATOR_NODE, "WU-104 upstream prompt topology unexpected")

    expected_prompt = deepcopy(original_prompt)
    expected_prompt["main"] = [[{"node": OVERLAY_NODE, "type": "main", "index": 0}]]
    require(cand_connections[PROMPT_NODE] == expected_prompt, "prompt node must be rewired only to WU-105 overlay")
    require(cand_connections[OVERLAY_NODE] == {"main": [[{"node": GENERATOR_NODE, "type": "main", "index": 0}]]}, "overlay must feed the existing generator")

    for name, conn in base_connections.items():
        if name == PROMPT_NODE:
            continue
        require(cand_connections.get(name) == conn, f"unrelated WU-104 upstream connection modified: {name}")

    base_types = [n.get("type") for n in baseline["nodes"]]
    cand_types = [n.get("type") for n in candidate["nodes"]]
    for model_type in ["@n8n/n8n-nodes-langchain.lmChatOpenAi", "@n8n/n8n-nodes-langchain.chainLlm"]:
        require(cand_types.count(model_type) == base_types.count(model_type), f"WU-105 may not add model node type {model_type}")
    require(cand_types.count("n8n-nodes-base.code") == base_types.count("n8n-nodes-base.code") + 1, "only one deterministic Code node may be added")

    print(f"PASS inherited current WU-104 candidate SHA256: {EXPECTED_WU104_SHA256}")
    print("PASS WU-105 candidate preserves all 124 WU-104 upstream nodes and adds exactly one deterministic overlay")
    print("PASS only prompt->generator main topology is interposed")
    print("PASS no new model, credentials, or external execution node")


if __name__ == "__main__":
    main()
