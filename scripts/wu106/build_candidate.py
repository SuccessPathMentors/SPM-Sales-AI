#!/usr/bin/env python3
import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path

EXPECTED_WU105_SHA256 = "42ba2b9de1f52c0db1fc32e59974dc40ebce80b787677ac6b0d4418a6315bca1"
EXPECTED_WU105_NODE_COUNT = 131
SOURCE_NODE = "Apply WU105 Golden Intent Prompt Overlay"
TARGET_NODE = "Generate WU92 Sales Agent Response"
WU106_NODE = "Build WU106 Journey Orchestration Envelope"
REQUIRED_LOCKED_NODES = {
    "Build WU104 Short Query Decision",
    "Apply WU104 Short Trial Inquiry Guard",
    "Apply WU105 Golden Intent Prompt Overlay",
    "Apply WU105 Availability Answer-First Guard",
    "Apply WU105 Explicit Free Trial Action Guard",
    "Apply WU105 Refund Policy Answer-First Guard",
    "Load POLICIES [WU91 READ ONLY]",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_node(position):
    js_code = r"""const j=$input.first().json||{};
const c=(j.classification&&typeof j.classification==='object')?j.classification:{};
const s=(j.sales_state&&typeof j.sales_state==='object')?j.sales_state:{};
const conv=(s.conversion&&typeof s.conversion==='object')?s.conversion:{};
const journey=(s.journey&&typeof s.journey==='object')?s.journey:{};
const intent=String(c.spm_intent||'');
const awaited=conv.awaiting_field??journey.awaiting_entity??null;
const lang=String(c.language||j.language_hint||'en').toLowerCase();
const language=lang.startsWith('ar')?'ar':(lang.startsWith('fr')?'fr':'en');
const supportOverride=new Set(['human_handoff','complaint','technical_issue','technical_support','account_login','payment_problem','not_interested','do_not_contact']).has(intent);
const actionSensitive=new Set(['availability','schedule_request','registration','ready_to_register','free_trial','human_handoff','refund_policy']).has(intent);
const meta={
 schema:'SPM_WU106_ORCHESTRATION_ENVELOPE_V1',
 mode:'OBSERVE_ONLY_BASELINE',
 active_objective_intent:intent||null,
 last_clear_intent:(String(j.classifier_route||'')==='direct'&&c.ambiguous!==true)?(intent||null):null,
 primary_awaited_field:conv.awaiting_field??null,
 secondary_awaited_entity:journey.awaiting_entity??null,
 resolved_awaited_entity:awaited,
 current_language:language,
 support_override_active:supportOverride,
 action_sensitive_intent:actionSensitive,
 action_state:'NONE',
 student_context_epoch:Number.isFinite(Number(journey.wu106_student_context_epoch))?Number(journey.wu106_student_context_epoch):0,
 state_mutated:false,
 prompt_mutated:false,
 action_permission_mutated:false,
 irreversible_action_allowed:false,
 wu104_authoritative:true,
 wu105_authoritative:true,
 raw_message_logged:false,
 raw_session_logged:false,
 raw_contact_logged:false,
 secret_values_logged:false
};
return [{json:{...j,wu106_orchestration:meta}}];"""
    return {
        "parameters": {"jsCode": js_code},
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": position,
        "id": "wu106-journey-orchestration-envelope-v1",
        "name": WU106_NODE,
        "notesInFlow": True,
        "notes": (
            "WU-106 baseline STAGING-only observability envelope. Derives privacy-safe journey metadata from the existing "
            "classification and sales_state, including the locked WU-104 awaited-field precedence. It does not mutate "
            "sales_state, prompts, source truth, action permission, or Production. Functional journey changes require a CR-106."
        ),
    }


def build(baseline: Path, output: Path):
    actual = sha256(baseline)
    if actual != EXPECTED_WU105_SHA256:
        raise SystemExit(f"WU-106 refuses non-locked WU-105 baseline SHA: {actual}")

    workflow = json.loads(baseline.read_text(encoding="utf-8"))
    if len(workflow.get("nodes", [])) != EXPECTED_WU105_NODE_COUNT:
        raise SystemExit(f"WU-106 locked WU-105 node count mismatch: {len(workflow.get('nodes', []))}")

    candidate = deepcopy(workflow)
    candidate["name"] = "[STAGING] SPM_WU106_END_TO_END_JOURNEYS_V1"
    candidate["active"] = False

    names = [n.get("name") for n in candidate.get("nodes", [])]
    missing = sorted(REQUIRED_LOCKED_NODES - set(names))
    if missing:
        raise SystemExit("WU-106 refuses baseline missing locked controls: " + ", ".join(missing))
    if WU106_NODE in names:
        raise SystemExit("WU-106 envelope already exists")
    if names.count(SOURCE_NODE) != 1 or names.count(TARGET_NODE) != 1:
        raise SystemExit("WU-106 required insertion topology identity mismatch")

    source = next(n for n in candidate["nodes"] if n.get("name") == SOURCE_NODE)
    x, y = source.get("position", [0, 0])
    candidate["nodes"].append(make_node([x + 160, y + 96]))

    connections = candidate.setdefault("connections", {})
    source_connections = deepcopy(connections.get(SOURCE_NODE))
    if not source_connections or "main" not in source_connections:
        raise SystemExit("WU-106 source node has no main connection")
    main = source_connections["main"]
    if len(main) != 1 or len(main[0]) != 1 or main[0][0].get("node") != TARGET_NODE:
        raise SystemExit("WU-106 unexpected WU-105 overlay-to-generator topology")

    original_target = deepcopy(main[0][0])
    connections[SOURCE_NODE] = {**source_connections, "main": [[{"node": WU106_NODE, "type": "main", "index": 0}]]}
    connections[WU106_NODE] = {"main": [[original_target]]}

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"WU106_INPUT_WU105_SHA256={actual}")
    print(f"WU106_CANDIDATE={output}")
    print(f"WU106_CANDIDATE_SHA256={sha256(output)}")
    print(f"WU106_NODE_COUNT={len(candidate.get('nodes', []))}")
    print("WU106_MODE=OBSERVE_ONLY_BASELINE")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    build(args.baseline, args.output)


if __name__ == "__main__":
    main()
