#!/usr/bin/env python3
import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path

EXPECTED_WU104_BASELINE_SHA256 = "32721cae2b09531d8f4860373c37911ace9e95b6818babdca880fa08ef1b7bc9"
EXPECTED_WU104_NODE_COUNT = 126
PROMPT_NODE = "Build WU96-Aware Sales Agent Prompt"
GENERATOR_NODE = "Generate WU92 Sales Agent Response"
OVERLAY_NODE = "Apply WU105 Golden Intent Prompt Overlay"
SCHEDULING_GUARD_NODE = "Apply WU94 Scheduling Truth Guard"
CONVERSION_NODE = "Resolve WU95 Conversion Mode"
AVAILABILITY_GUARD_NODE = "Apply WU105 Availability Answer-First Guard"
REQUIRED_WU104_NODES = {
    "Build WU104 Short Query Decision",
    "Apply WU104 Short Trial Inquiry Guard",
    "Persist WU104 Awaited Context Hint",
    "Persist WU104 Final Asked Field",
    "Apply WU104 Clarification Response Override",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact_contract(row):
    return {
        "direct_answer_requirement": row["direct_answer_requirement"],
        "authoritative_sources": row["authoritative_sources"],
        "do_not_reask": row["do_not_reask"],
        "preferred_next_best_action": row["preferred_next_best_action"],
        "smallest_optional_qualifier": row["smallest_optional_qualifier"],
        "stop_overrides": row["stop_overrides"],
        "forbidden": row["forbidden"],
        "confusion_pairs": row["confusion_pairs"],
        "wu104_compatibility": row["wu104_compatibility"],
    }


def make_overlay_node(manifest, position):
    guidance = {row["intent"]: compact_contract(row) for row in manifest["intents"]}
    guidance_js = json.dumps(guidance, ensure_ascii=False, separators=(",", ":"))
    js_code = f"""const j=$input.first().json||{{}};
const intent=String(j.classification?.spm_intent||'');
const goldenMap={guidance_js};
const contract=goldenMap[intent]||null;
const meta={{
  schema:'SPM_WU105_GOLDEN_INTENT_RUNTIME_V1',
  manifest_version:'1.0',
  active:Boolean(contract),
  intent:contract?intent:null,
  answer_first:true,
  max_followup_questions:1,
  wu104_authoritative:true,
  source_action_gates_authoritative:true,
  irreversible_action_allowed:false,
  raw_message_logged:false,
  raw_session_logged:false,
  secret_values_logged:false
}};
if(!contract) return [{{json:{{...j,wu105_golden:meta}}}}];
const overlay=`\n\nWU105 GOLDEN INTENT OPTIMIZATION — CONTRACTUAL OVERLAY\nCURRENT GOLDEN INTENT: ${{intent}}\nDIRECT ANSWER REQUIREMENT: ${{contract.direct_answer_requirement}}\nAUTHORITATIVE SOURCES: ${{JSON.stringify(contract.authoritative_sources)}}\nDO NOT RE-ASK WHEN ALREADY KNOWN: ${{JSON.stringify(contract.do_not_reask)}}\nPREFERRED NEXT-BEST-ACTION: ${{contract.preferred_next_best_action}}\nSMALLEST OPTIONAL QUALIFIER: ${{contract.smallest_optional_qualifier}}\nSTOP / OVERRIDE CONDITIONS: ${{JSON.stringify(contract.stop_overrides)}}\nFORBIDDEN: ${{JSON.stringify(contract.forbidden)}}\nNEAREST CONFUSION PAIRS: ${{JSON.stringify(contract.confusion_pairs)}}\nWU104 COMPATIBILITY: ${{contract.wu104_compatibility}}\n\nWU105 EXECUTION RULES:\n- Answer the customer's current question before qualification unless a locked support/safety rule overrides.\n- Reuse trusted known context and never ask a known relevant field again.\n- Ask at most one smallest relevant question, and only when useful.\n- Do not change classifier intent, source truth, business truth, or action permission.\n- If required truth is live/unavailable, state that confirmation is required; do not invent it.\n- Never claim booking, registration, refund, discount, handoff, payment, tutor assignment, or other business action succeeded without the existing deterministic gateway/tool success.\n- WU-104 ambiguity and short-query behavior remains authoritative.\n- proposed_action is only a proposal; deterministic downstream gates remain authoritative.\n`;
return [{{json:{{...j,sales_agent_prompt:String(j.sales_agent_prompt||'')+overlay,wu105_golden:meta}}}}];"""
    return {
        "parameters": {"jsCode": js_code},
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": position,
        "id": "wu105-golden-intent-overlay-v1",
        "name": OVERLAY_NODE,
        "notesInFlow": True,
        "notes": "WU-105 STAGING-only prompt overlay. Inherits locked WU-104 CR-104-05 candidate exactly; no classifier/source/action permission changes. Production remains read-only."
    }


def make_availability_guard_node(position):
    js_code = """const j=$input.first().json||{};
const intent=String(j.classification?.spm_intent||'');
const lang=(j.classification?.language||j.language_hint||'en').toLowerCase();
const o={...(j.sales_agent_output||{})};
const availabilityVerified=Boolean(j.scheduling_context?.availability_verified);
const wu92SafetyRewrite=Boolean(o.safety_rewrite_applied);
const wu94Violations=Array.isArray(j.wu94_scheduling_guard?.violations)?j.wu94_scheduling_guard.violations:[];
const schedulingRewrite=wu94Violations.includes('UNVERIFIED_AVAILABILITY_CLAIM_REWRITTEN')||wu94Violations.includes('UNVERIFIED_BOOKING_CLAIM_REWRITTEN');
let applied=false;

if(intent==='availability' && !availabilityVerified && (wu92SafetyRewrite || schedulingRewrite)){
  if(lang==='ar'){
    o.answer_text='أحتاج إلى التحقق من جدول المواعيد المباشر قبل أن أخبرك إن كان اليوم أو الوقت المطلوب يحتوي على موعد مفتوح للدروس.';
  }else if(lang==='fr'){
    o.answer_text="Je dois vérifier le planning en direct avant de pouvoir vous dire si le jour ou l’heure demandés disposent d’un créneau de tutorat libre.";
  }else{
    o.answer_text='I need to check the live schedule before I can tell you whether your requested day or time has an open tutoring slot.';
  }
  applied=true;
}

const guard={
  schema:'SPM_WU105_AVAILABILITY_ANSWER_FIRST_GUARD_V1',
  applied,
  intent,
  availability_verified:availabilityVerified,
  source_action_gates_authoritative:true,
  action_mutated:false,
  purposeful_question_mutated:false,
  irreversible_action_allowed:false,
  raw_message_logged:false,
  raw_session_logged:false,
  secret_values_logged:false
};
return [{json:{...j,sales_agent_output:o,wu105_availability_guard:guard}}];"""
    return {
        "parameters": {"jsCode": js_code},
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": position,
        "id": "wu105-availability-answer-first-guard-v1",
        "name": AVAILABILITY_GUARD_NODE,
        "notesInFlow": True,
        "notes": "CR-105-01 STAGING-only UX guard. Restores availability-specific answer-first wording after inherited safety rewrites without changing classifier, live truth, action permission, or Production."
    }


def build(baseline: Path, manifest_path: Path, output: Path):
    actual = sha256(baseline)
    if actual != EXPECTED_WU104_BASELINE_SHA256:
        raise SystemExit(f"WU-104 locked upstream baseline SHA mismatch: {actual}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "SPM_WU105_GOLDEN_INTENTS_V1":
        raise SystemExit("Unexpected WU-105 manifest schema")
    if not 8 <= len(manifest.get("intents", [])) <= 15:
        raise SystemExit("WU-105 golden manifest must contain 8-15 intents")

    workflow = json.loads(baseline.read_text(encoding="utf-8"))
    if len(workflow.get("nodes", [])) != EXPECTED_WU104_NODE_COUNT:
        raise SystemExit(f"WU-104 locked upstream node count mismatch: {len(workflow.get('nodes', []))}")

    candidate = deepcopy(workflow)
    candidate["name"] = "[STAGING] SPM_WU105_GOLDEN_INTENTS_V1"
    candidate["active"] = False

    names = [n.get("name") for n in candidate.get("nodes", [])]
    missing_wu104 = sorted(REQUIRED_WU104_NODES - set(names))
    if missing_wu104:
        raise SystemExit("WU-105 refuses a baseline without locked WU-104 controls: " + ", ".join(missing_wu104))
    if OVERLAY_NODE in names or AVAILABILITY_GUARD_NODE in names:
        raise SystemExit("WU-105 owned node already exists")
    for required in [PROMPT_NODE, GENERATOR_NODE, SCHEDULING_GUARD_NODE, CONVERSION_NODE]:
        if names.count(required) != 1:
            raise SystemExit(f"Required locked node identity not found exactly once: {required}")

    prompt_node = next(n for n in candidate["nodes"] if n.get("name") == PROMPT_NODE)
    x, y = prompt_node.get("position", [0, 0])
    overlay = make_overlay_node(manifest, [x + 320, y + 176])
    candidate["nodes"].append(overlay)

    scheduling_node = next(n for n in candidate["nodes"] if n.get("name") == SCHEDULING_GUARD_NODE)
    sx, sy = scheduling_node.get("position", [0, 0])
    availability_guard = make_availability_guard_node([sx + 320, sy + 160])
    candidate["nodes"].append(availability_guard)

    connections = candidate.setdefault("connections", {})

    prompt_connections = deepcopy(connections.get(PROMPT_NODE))
    if not prompt_connections or "main" not in prompt_connections:
        raise SystemExit("Locked prompt node has no main connection")
    main = prompt_connections["main"]
    if len(main) != 1 or len(main[0]) != 1 or main[0][0].get("node") != GENERATOR_NODE:
        raise SystemExit("Unexpected prompt-to-generator topology; refusing broad graph rewrite")
    original_target = deepcopy(main[0][0])
    connections[PROMPT_NODE] = {**prompt_connections, "main": [[{"node": OVERLAY_NODE, "type": "main", "index": 0}]]}
    connections[OVERLAY_NODE] = {"main": [[original_target]]}

    scheduling_connections = deepcopy(connections.get(SCHEDULING_GUARD_NODE))
    if not scheduling_connections or "main" not in scheduling_connections:
        raise SystemExit("Locked scheduling guard has no main connection")
    smain = scheduling_connections["main"]
    if len(smain) != 1 or len(smain[0]) != 1 or smain[0][0].get("node") != CONVERSION_NODE:
        raise SystemExit("Unexpected scheduling-guard-to-conversion topology; refusing broad graph rewrite")
    scheduling_target = deepcopy(smain[0][0])
    connections[SCHEDULING_GUARD_NODE] = {**scheduling_connections, "main": [[{"node": AVAILABILITY_GUARD_NODE, "type": "main", "index": 0}]]}
    connections[AVAILABILITY_GUARD_NODE] = {"main": [[scheduling_target]]}

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"WU105_UPSTREAM_WU104_SHA256={actual}")
    print(f"WU105_CANDIDATE={output}")
    print(f"WU105_CANDIDATE_SHA256={sha256(output)}")
    print(f"WU105_NODE_COUNT={len(candidate.get('nodes', []))}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", required=True, type=Path, help="Locked WU-104 CR-104-05 staging candidate artifact, never Production")
    parser.add_argument("--manifest", default=Path("contracts/WU105_GOLDEN_INTENTS_V1.json"), type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    build(args.baseline, args.manifest, args.output)


if __name__ == "__main__":
    main()
