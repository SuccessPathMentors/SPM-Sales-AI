#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path

CR_NODE = "Apply WU106 Journey Transition Recovery [CR-106-01]"
SOURCE_NODE = "Build WU104 Short Query Decision"
TARGET_NODE = "Capture WU89 Classifier Context"


def require(cond, msg):
    if not cond:
        raise AssertionError(msg)


def target_of(wf, source):
    main = wf.get("connections", {}).get(source, {}).get("main")
    require(isinstance(main, list) and len(main) == 1 and len(main[0]) == 1, f"unexpected topology from {source}")
    return main[0][0].get("node")


def run_js(js, payload):
    script = "const input=" + json.dumps(payload, ensure_ascii=False) + ";\n"
    script += "const $input={first:()=>({json:input})};\n"
    script += "const fn=()=>{\n" + js + "\n};\n"
    script += "const result=fn(); console.log(JSON.stringify(result[0].json));\n"
    p = subprocess.run(["node", "-e", script], text=True, capture_output=True, check=True)
    return json.loads(p.stdout.strip())


def base_payload(raw, awaited, intent="unknown_intent", confidence=0.4, ambiguous=True, route="clarify"):
    return {
        "message": {"raw": raw},
        "classification": {
            "spm_intent": intent,
            "confidence": confidence,
            "threshold": 0.85,
            "ambiguous": ambiguous,
            "language": "en",
        },
        "sales_state": {
            "conversion": {
                "registration_active": True,
                "registration_status": "collecting",
                "awaiting_field": awaited,
            },
            "journey": {"awaiting_entity": awaited},
            "clarification": {
                "schema": "SPM_WU104_CLARIFICATION_STATE_V1",
                "active": True,
                "clarification_key": "x",
                "attempt": 1,
                "reason_code": "CLASSIFIER_AMBIGUOUS",
                "language": "en",
            },
        },
        "classifier_route": route,
        "customer_clarification_required": route == "clarify",
        "classifier_safe_action": "ASK_ONE_CLARIFYING_QUESTION" if route == "clarify" else "CONTINUE",
        "wu104_short_query_decision": {
            "safe_action": "ASK_ONE_CLARIFYING_QUESTION" if route == "clarify" else "CONTINUE",
            "clarification_required": route == "clarify",
            "clarification_reason": "CLASSIFIER_AMBIGUOUS" if route == "clarify" else "NONE",
            "clarification_key": "x" if route == "clarify" else None,
            "clarification_attempt": 1 if route == "clarify" else 0,
            "clarification_language": "en",
            "context_binding_status": "NEEDS_CLARIFICATION" if route == "clarify" else "NOT_NEEDED",
            "binding_source": "NONE",
            "resolved_intent": intent,
            "resolved_entity_type": "NONE",
        },
        "wu104_clarification_text": "Could you tell me what you mean by that?" if route == "clarify" else None,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--candidate", required=True, type=Path)
    args = p.parse_args()
    wf = json.loads(args.candidate.read_text(encoding="utf-8"))
    require(len(wf.get("nodes", [])) == 133, "CR-106-01 candidate must contain 133 nodes")
    require(wf.get("active") is False, "CR-106-01 candidate must remain inactive")
    names = [n.get("name") for n in wf.get("nodes", [])]
    require(names.count(CR_NODE) == 1, "CR-106-01 node must exist exactly once")
    require(target_of(wf, SOURCE_NODE) == CR_NODE, "CR-106-01 must be directly after WU104 short-query decision")
    require(target_of(wf, CR_NODE) == TARGET_NODE, "CR-106-01 must return to WU89 capture")
    node = next(n for n in wf["nodes"] if n.get("name") == CR_NODE)
    require(node.get("type") == "n8n-nodes-base.code", "CR-106-01 must be deterministic Code node")
    js = str(node.get("parameters", {}).get("jsCode", ""))
    for marker in [
        "SPM_WU106_CR10601_JOURNEY_TRANSITION_RECOVERY_V1",
        "WU106_REGISTRATION_AWAITED_FIELD",
        "WU106_EXPLICIT_AVAILABILITY_PATTERN",
        "action_permission_mutated:false",
        "irreversible_action_allowed:false",
        "production_mutation_allowed:false",
        "raw_message_logged:false",
        "raw_session_logged:false",
        "secret_values_logged:false",
    ]:
        require(marker in js, f"missing CR-106-01 safety/identity marker: {marker}")
    for forbidden in ["httpRequest", "googleSheets", "redis", "executeWorkflow", "booking_id=", "lead_upsert"]:
        require(forbidden not in js, f"CR-106-01 introduced forbidden action surface: {forbidden}")

    # GJ-04 defect #1: a plausible name must bind to the active registration awaiting_field.
    r = run_js(js, base_payload("Ahmed", "parent_name"))
    ev = r["wu106_cr10601_recovery"]
    require(ev["applied"] is True and ev["reason"] == "REGISTRATION_AWAITED_FIELD_RECOVERED", "parent_name recovery did not apply")
    require(r["classifier_route"] == "direct", "recovered parent_name must continue downstream")
    require(r["customer_clarification_required"] is False, "recovered parent_name must clear clarification")
    require(r["sales_state"]["conversion"]["awaiting_field"] == "parent_name", "guard must not pre-consume authoritative awaiting_field")
    require(r["sales_state"]["clarification"]["active"] is False, "guard must clear stale clarification state")
    require(r["classification"]["spm_intent"] == "unknown_intent", "registration field recovery must not invent an intent")

    # Random conversational text must not be mistaken for a person's name.
    r = run_js(js, base_payload("Maybe later", "parent_name"))
    require(r["wu106_cr10601_recovery"]["applied"] is False, "conversational phrase must not bind as parent_name")
    require(r["classifier_route"] == "clarify", "unsafe free text must remain fail-closed")

    # GJ-04 defect #2: explicit day availability must override stale registration clarification.
    r = run_js(js, base_payload("Is Saturday available?", "student_name"))
    ev = r["wu106_cr10601_recovery"]
    require(ev["applied"] is True and ev["reason"] == "EXPLICIT_AVAILABILITY_CURRENT_MESSAGE_OVERRIDE", "explicit availability recovery did not apply")
    require(r["classification"]["spm_intent"] == "availability", "explicit availability must route as availability")
    require(r["classification"]["ambiguous"] is False, "explicit availability must clear ambiguity")
    require(r["classifier_route"] == "direct", "explicit availability must continue downstream")
    require(r["sales_state"]["conversion"]["awaiting_field"] == "student_name", "availability interrupt must preserve registration awaiting state")
    require(r["customer_clarification_required"] is False, "availability override must clear stale clarification")

    # A clear human-handoff intent remains authoritative and is never bound to a registration field.
    r = run_js(js, base_payload("I want to speak with a person", "parent_name", intent="human_handoff", confidence=0.99, ambiguous=False, route="direct"))
    require(r["wu106_cr10601_recovery"]["applied"] is False, "human_handoff must not be overridden")
    require(r["classification"]["spm_intent"] == "human_handoff", "human_handoff intent changed")

    # A clear schedule request is not silently rewritten as an availability inquiry.
    r = run_js(js, base_payload("Please schedule it for Saturday at 6 PM.", "student_name", intent="schedule_request", confidence=0.99, ambiguous=False, route="direct"))
    require(r["wu106_cr10601_recovery"]["applied"] is False, "schedule request must not be rewritten")
    require(r["classification"]["spm_intent"] == "schedule_request", "schedule request intent changed")

    print("WU106_CR10601_EXECUTABLE_PASS")
    print(json.dumps({
        "parent_name_context_binding": True,
        "unsafe_free_text_fail_closed": True,
        "explicit_availability_current_message_override": True,
        "handoff_precedence_preserved": True,
        "schedule_request_distinction_preserved": True,
        "production_mutation": False,
    }, indent=2))


if __name__ == "__main__":
    main()
