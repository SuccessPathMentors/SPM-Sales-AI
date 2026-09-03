#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path

WU89 = "Validate + Normalize WU89 Entities"
ROOT = "Apply WU106 Root Journey Recovery [CR-106-02]"
SHORT_TRIAL = "Apply WU104 Short Trial Inquiry Guard"
ALT = "Apply WU106 Alternative Slot Recovery [CR-106-03]"
AVAIL_GUARD = "Apply WU105 Availability Answer-First Guard"
CONVERSION = "Resolve WU95 Conversion Mode"
ALT_RESPONSE = "Apply WU106 Alternative Availability Response Guard [CR-106-03]"


def one_target(conns, name):
    main = conns.get(name, {}).get("main")
    if not isinstance(main, list) or len(main) != 1 or len(main[0]) != 1:
        return None
    return main[0][0].get("node")


def run_code(code, payload, *, dollar_context=None):
    wrapper = []
    if dollar_context is not None:
        wrapper.append("const __ctx=" + json.dumps(dollar_context, ensure_ascii=False) + ";")
        wrapper.append("function $(name){return {first:()=>({json:__ctx})};}")
        wrapper.append("const $json={};")
    else:
        wrapper.append("const $input={first:()=>({json:" + json.dumps(payload, ensure_ascii=False) + "})};")
    wrapper.append("function __run(){")
    wrapper.append(code)
    wrapper.append("}")
    wrapper.append("console.log(JSON.stringify(__run()));")
    cp = subprocess.run(["node", "-e", "\n".join(wrapper)], text=True, capture_output=True)
    if cp.returncode != 0:
        raise AssertionError(cp.stderr)
    return json.loads(cp.stdout)[0]["json"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True, type=Path)
    args = ap.parse_args()
    d = json.loads(args.candidate.read_text(encoding="utf-8"))
    assert len(d["nodes"]) == 141
    nodes = {n["name"]: n for n in d["nodes"]}
    conns = d["connections"]

    for name in [WU89, ROOT, SHORT_TRIAL, ALT, AVAIL_GUARD, ALT_RESPONSE, CONVERSION]:
        assert name in nodes, name

    assert one_target(conns, ROOT) == ALT
    assert one_target(conns, ALT) == SHORT_TRIAL
    assert one_target(conns, AVAIL_GUARD) == ALT_RESPONSE
    assert one_target(conns, ALT_RESPONSE) == CONVERSION

    wu89_code = nodes[WU89]["parameters"]["jsCode"]
    assert "SPM_WU106_CR10603_SCHEDULING_NORMALIZATION_V1" in wu89_code
    ctx = {
        "entity_schema": [
            {"entity_name": "city", "data_type": "string", "sensitivity": "Low", "validation_rule": "", "usage": ""},
            {"entity_name": "timezone", "data_type": "string", "sensitivity": "Low", "validation_rule": "", "usage": ""},
            {"entity_name": "preferred_day", "data_type": "string", "sensitivity": "Low", "validation_rule": "", "usage": ""},
            {"entity_name": "preferred_time", "data_type": "string", "sensitivity": "Low", "validation_rule": "", "usage": ""},
        ],
        "message": {"raw": "My son is in Grade 8 and needs Math tutoring. Is Saturday at 6 PM Toronto time available?"},
        "sales_state": {"conversion": {}, "journey": {}},
    }
    out = run_code(wu89_code, {}, dollar_context=ctx)
    ge = out["entity_extraction"]["global_entities"]
    assert ge["city"] == "Toronto"
    assert ge["timezone"] == "America/Toronto"
    assert ge["preferred_day"] == "Saturday"
    assert ge["preferred_time"] == "6 PM"
    rec = {r["entity"]: r for r in out["entity_extraction"]["records"]}
    assert rec["timezone"]["status"] == "valid"
    assert rec["timezone"]["source"] == "customer_deterministic_city_time_alias"

    alt_code = nodes[ALT]["parameters"]["jsCode"]
    payload = {
        "message": {"raw": "If 6 PM is not available, what other time could work?"},
        "classification": {"spm_intent": "schedule_request", "confidence": 0.98, "threshold": 0.85, "ambiguous": False, "language": "en"},
        "sales_state": {
            "entities": {"global": {"timezone": "America/Toronto", "preferred_day": "Saturday", "preferred_time": "6 PM"}},
            "clarification": {"active": False},
        },
        "wu104_short_query_decision": {"clarification_required": False, "safe_action": "CONTINUE"},
        "classifier_route": "direct",
    }
    out = run_code(alt_code, payload)
    assert out["classification"]["spm_intent"] == "availability"
    assert out["wu106_cr10603_alternative_recovery"]["applied"] is True
    assert out["sales_state"]["entities"]["global"]["preferred_time"] == "6 PM"
    assert out["sales_state"]["entities"]["global"]["preferred_day"] == "Saturday"
    assert out["sales_state"]["entities"]["global"]["timezone"] == "America/Toronto"

    handoff_payload = dict(payload)
    handoff_payload["message"] = {"raw": "I want a human person, not another time."}
    handoff_payload["classification"] = {"spm_intent": "human_handoff", "confidence": 0.99, "threshold": 0.85, "ambiguous": False, "language": "en"}
    out_h = run_code(alt_code, handoff_payload)
    assert out_h["classification"]["spm_intent"] == "human_handoff"
    assert out_h["wu106_cr10603_alternative_recovery"]["applied"] is False

    response_code = nodes[ALT_RESPONSE]["parameters"]["jsCode"]
    response_payload = {
        "classification": {"language": "en"},
        "sales_agent_output": {
            "answer_text": "We can proceed with that step, but it is only confirmed after the required system check or action succeeds.",
            "purposeful_question": "What other time?",
            "proposed_action": "ask_clarification",
            "action_requires_gateway": False,
        },
        "wu106_cr10603_alternative_recovery": {"applied": True},
        "scheduling_context": {"availability_verified": False, "request": {"preferred_day": "Saturday", "preferred_time": "6 PM", "timezone": "America/Toronto"}},
    }
    out_r = run_code(response_code, response_payload)
    ans = out_r["sales_agent_output"]["answer_text"]
    assert "live schedule" in ans.lower()
    assert "other available times" in ans.lower()
    assert out_r["sales_agent_output"]["purposeful_question"] is None
    assert out_r["sales_agent_output"]["proposed_action"] == "request_live_check"
    assert out_r["sales_agent_output"]["action_requires_gateway"] is True
    assert out_r["wu106_cr10603_alternative_response_guard"]["slot_invented"] is False
    assert out_r["wu106_cr10603_alternative_response_guard"]["booking_claimed"] is False

    for node_name in [ALT, ALT_RESPONSE]:
        code = nodes[node_name]["parameters"]["jsCode"]
        for forbidden in ["booking_success=true", "availability_verified=true", "httpRequest", "executeWorkflow", "lead_upsert"]:
            assert forbidden not in code

    print("WU106_CR10603_GJ05_ROOT_FIX_EXECUTABLE_PASS")
    print(json.dumps({
        "toronto_time_normalized": True,
        "day_time_preference_normalized": True,
        "alternative_slot_becomes_availability": True,
        "existing_requested_preference_preserved": True,
        "human_handoff_precedence_preserved": True,
        "no_slot_invented": True,
        "no_booking_claim": True,
        "production_mutation": False
    }, indent=2))


if __name__ == "__main__":
    main()
