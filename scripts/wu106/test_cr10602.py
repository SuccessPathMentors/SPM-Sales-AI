#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path

LOAD_CTRL = "Load WU106 Registration Control [CR-106-02]"
MERGE_CTRL = "Merge WU106 Durable Registration Control [CR-106-02]"
ROOT = "Apply WU106 Root Journey Recovery [CR-106-02]"
BUILD_CTRL = "Build WU106 Registration Control Snapshot [CR-106-02]"
SAVE_CTRL = "Save WU106 Registration Control [CR-106-02]"
RESTORE_CTRL = "Restore After WU106 Registration Control Save [CR-106-02]"


def require(cond, msg):
    if not cond:
        raise AssertionError(msg)


def node(wf, name):
    xs = [n for n in wf.get("nodes", []) if n.get("name") == name]
    require(len(xs) == 1, f"expected one node: {name}")
    return xs[0]


def target(wf, source, output=0):
    main = wf.get("connections", {}).get(source, {}).get("main")
    require(isinstance(main, list) and len(main) > output and len(main[output]) == 1, f"unexpected topology from {source}[{output}]")
    return main[output][0].get("node")


def run_js(js, payload, named=None):
    named = named or {}
    script = "const input=" + json.dumps(payload, ensure_ascii=False) + ";\n"
    script += "const named=" + json.dumps(named, ensure_ascii=False) + ";\n"
    script += "const $input={first:()=>({json:input})};\n"
    script += "const $=(name)=>({first:()=>({json:named[name]||{}})});\n"
    script += "const fn=()=>{\n" + js + "\n};\n"
    script += "const result=fn(); console.log(JSON.stringify(result[0].json));\n"
    p = subprocess.run(["node", "-e", script], text=True, capture_output=True, check=True)
    return json.loads(p.stdout.strip())


def base_state(active=False, awaiting=None):
    return {
        "conversion": {
            "registration_active": active,
            "registration_status": "collecting" if active else "not_started",
            "awaiting_field": awaiting,
            "request_type": "ENROLLMENT" if active else None,
            "pending_confirmation": False,
        },
        "journey": {"awaiting_entity": awaiting},
        "clarification": {"active": True, "attempt": 1, "clarification_key": "old"},
    }


def payload(raw, state, intent="unknown_intent", confidence=0.2, ambiguous=True, route="clarify"):
    return {
        "session_id": "session-cr10602-test",
        "message": {"raw": raw},
        "sales_state": state,
        "classification": {
            "spm_intent": intent,
            "secondary_spm_intent": "",
            "confidence": confidence,
            "threshold": 0.85,
            "ambiguous": ambiguous,
            "language": "en",
        },
        "classifier_route": route,
        "customer_clarification_required": route != "direct",
        "classifier_safe_action": "ASK_ONE_CLARIFYING_QUESTION" if route != "direct" else "CONTINUE",
        "wu104_short_query_decision": {
            "safe_action": "ASK_ONE_CLARIFYING_QUESTION" if route != "direct" else "CONTINUE",
            "clarification_required": route != "direct",
            "clarification_reason": "CLASSIFIER_AMBIGUOUS" if route != "direct" else "NONE",
            "context_binding_status": "NEEDS_CLARIFICATION" if route != "direct" else "NOT_NEEDED",
            "binding_source": "NONE",
            "resolved_intent": intent,
            "resolved_entity_type": "NONE",
        },
        "wu104_clarification_text": "Could you tell me what you mean by that?",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--candidate", required=True, type=Path)
    a = p.parse_args()
    wf = json.loads(a.candidate.read_text(encoding="utf-8"))

    require(len(wf.get("nodes", [])) == 139, "CR-106-02 candidate must contain 139 nodes")
    require(wf.get("active") is False, "candidate must remain inactive")
    for name in [LOAD_CTRL, MERGE_CTRL, ROOT, BUILD_CTRL, SAVE_CTRL, RESTORE_CTRL]:
        node(wf, name)

    require(target(wf, "Initialize + Merge Sales State Contract") == LOAD_CTRL, "control load must happen immediately after canonical state initialization")
    require(target(wf, LOAD_CTRL, 0) == MERGE_CTRL and target(wf, LOAD_CTRL, 1) == MERGE_CTRL, "control load success/failure must converge safely")
    require(target(wf, MERGE_CTRL) == "Load SPM V2 62 Intent Catalog", "classifier must see merged durable control state")
    require(target(wf, "Apply WU106 Journey Transition Recovery [CR-106-01]") == ROOT, "CR-106-02 root recovery must supersede CR-106-01 downstream")
    require(target(wf, ROOT) == "Apply WU104 Short Trial Inquiry Guard", "locked WU104 short-trial guard must remain downstream")
    require(target(wf, "Persist WU104 Final Asked Field") == BUILD_CTRL, "control snapshot must be built from final canonical state")
    require(target(wf, BUILD_CTRL) == SAVE_CTRL, "control snapshot must persist")
    require(target(wf, SAVE_CTRL, 0) == RESTORE_CTRL and target(wf, SAVE_CTRL, 1) == RESTORE_CTRL, "control save success/failure must converge")
    require(target(wf, RESTORE_CTRL) == "Serialize WU95 STAGING Sales State", "canonical WU95 persistence must remain authoritative and downstream")

    load = node(wf, LOAD_CTRL)
    save = node(wf, SAVE_CTRL)
    require(load.get("type") == "n8n-nodes-base.redis" and save.get("type") == "n8n-nodes-base.redis", "control persistence must use Redis")
    require(load.get("credentials") == node(wf, "Load Sales State [STAGING NAMESPACE]").get("credentials"), "control load must reuse certified STAGING Redis credential")
    require(save.get("credentials") == node(wf, "Save WU95 Sales State [STAGING NAMESPACE]").get("credentials"), "control save must reuse certified STAGING Redis credential")
    require("spm:staging:regctrl:" in str(load.get("parameters", {}).get("key", "")), "control load must use isolated STAGING namespace")
    require("spm:staging:regctrl:" in str(node(wf, BUILD_CTRL).get("parameters", {}).get("jsCode", "")), "control snapshot must use isolated STAGING namespace")

    merge_js = node(wf, MERGE_CTRL)["parameters"]["jsCode"]
    ctrl = {
        "schema": "SPM_WU106_REGISTRATION_CONTROL_V1",
        "active": True,
        "registration_status": "collecting",
        "awaiting_field": "parent_name",
        "request_type": "ENROLLMENT",
        "pending_confirmation": False,
    }
    base = {"session_id": "session-cr10602-test", "sales_state": base_state(False, None)}
    merged = run_js(merge_js, {"wu106_registration_control_raw": json.dumps(ctrl)}, {"Initialize + Merge Sales State Contract": base})
    require(merged["sales_state"]["conversion"]["registration_active"] is True, "durable control must restore active registration")
    require(merged["sales_state"]["conversion"]["awaiting_field"] == "parent_name", "durable control must restore parent_name awaiting field")
    require(merged["sales_state"]["journey"]["awaiting_entity"] == "parent_name", "durable control must restore journey awaiting entity")
    require(merged["wu106_cr10602_control_merge"]["applied"] is True, "control merge evidence must show applied")

    root_js = node(wf, ROOT)["parameters"]["jsCode"]
    # Strong but wrong classifier must not defeat an active awaited registration slot.
    r = run_js(root_js, payload("Ahmed", merged["sales_state"], intent="subject_inquiry", confidence=0.99, ambiguous=False, route="direct"))
    require(r["wu106_cr10602_root_recovery"]["reason"] == "DURABLE_REGISTRATION_FIELD_BOUND", "Ahmed must bind through durable registration control")
    require(r["classification"]["spm_intent"] == "registration", "awaited registration value must force registration continuation")
    require(r["classifier_route"] == "direct" and r["customer_clarification_required"] is False, "awaited registration value must clear clarification")
    require(r["sales_state"]["conversion"]["awaiting_field"] == "parent_name", "root recovery must not pre-consume awaited field before WU89")

    # Explicit availability must win even if classifier is wrong/strong and stale registration is active.
    state2 = base_state(True, "student_name")
    r = run_js(root_js, payload("Is Saturday available?", state2, intent="registration", confidence=0.99, ambiguous=False, route="direct"))
    require(r["wu106_cr10602_root_recovery"]["reason"] == "EXPLICIT_AVAILABILITY_ROOT_OVERRIDE", "explicit availability root override must apply")
    require(r["classification"]["spm_intent"] == "availability", "explicit availability must route as availability")
    require(r["sales_state"]["conversion"]["awaiting_field"] == "student_name", "availability interrupt must preserve registration continuation")
    require(r["customer_clarification_required"] is False, "availability must not become clarification")

    # Human/support request remains higher priority than registration slot binding.
    r = run_js(root_js, payload("I want to speak with a person", base_state(True, "parent_name"), intent="human_handoff", confidence=0.99, ambiguous=False, route="direct"))
    require(r["wu106_cr10602_root_recovery"]["applied"] is False, "human handoff must not be overwritten")
    require(r["classification"]["spm_intent"] == "human_handoff", "human handoff intent must remain")

    build_js = node(wf, BUILD_CTRL)["parameters"]["jsCode"]
    snap = run_js(build_js, {"session_id": "session-cr10602-test", "message": {"raw": "SECRET NAME"}, "sales_state": base_state(True, "parent_name")})
    stored = json.loads(snap["wu106_registration_control_text"])
    require(stored["active"] is True and stored["awaiting_field"] == "parent_name", "control snapshot must capture control state")
    require("SECRET NAME" not in snap["wu106_registration_control_text"], "control snapshot must not store raw customer text")
    require(stored.get("pii_values_stored") is False and stored.get("raw_message_stored") is False, "control snapshot privacy markers must be false")

    # Mini multi-turn simulation: turn-1 control -> turn-2 merge/bind -> turn-3 explicit availability.
    turn1_ctrl = snap["wu106_registration_control_text"]
    turn2 = run_js(merge_js, {"wu106_registration_control_raw": turn1_ctrl}, {"Initialize + Merge Sales State Contract": base})
    turn2r = run_js(root_js, payload("Ahmed", turn2["sales_state"], intent="unknown_intent", confidence=0.2, ambiguous=True, route="clarify"))
    require(turn2r["classification"]["spm_intent"] == "registration" and turn2r["customer_clarification_required"] is False, "turn-2 parent-name continuation failed")
    simulated_after_wu95 = base_state(True, "student_name")
    turn3r = run_js(root_js, payload("Is Saturday available?", simulated_after_wu95, intent="registration", confidence=0.99, ambiguous=False, route="direct"))
    require(turn3r["classification"]["spm_intent"] == "availability" and turn3r["customer_clarification_required"] is False, "turn-3 availability interrupt failed")

    for n in [node(wf, MERGE_CTRL), node(wf, ROOT), node(wf, BUILD_CTRL), node(wf, RESTORE_CTRL)]:
        js = str(n.get("parameters", {}).get("jsCode", ""))
        require("production_mutation_allowed:false" in js or "production_mutation_allowed" not in js, f"production mutation marker invalid in {n['name']}")
        for forbidden in ["booking_create", "payment_action", "lead_upsert", "human_handoff_create"]:
            require(forbidden not in js, f"forbidden action surface in {n['name']}: {forbidden}")

    print("WU106_CR10602_ROOT_CAUSE_EXECUTABLE_PASS")
    print(json.dumps({
        "durable_registration_control_restore": True,
        "strong_classifier_cannot_break_awaited_slot": True,
        "explicit_availability_current_message_priority": True,
        "human_handoff_precedence": True,
        "pii_free_control_snapshot": True,
        "multi_turn_simulation": True,
        "canonical_wu95_persistence_preserved": True,
        "production_mutation": False,
    }, indent=2))


if __name__ == "__main__":
    main()
