#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "contracts" / "WU106_JOURNEY_STATE_V1.json"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    d = json.loads(STATE.read_text(encoding="utf-8"))
    require(d["schema"] == "SPM_WU106_JOURNEY_STATE_V1", "state schema mismatch")
    require(d["version"] == "1.0", "state version mismatch")

    bindings = d["existing_state_bindings"]
    require(bindings["current_intent"] == "classification.spm_intent", "current intent binding drift")
    require(bindings["primary_awaited_field"] == "sales_state.conversion.awaiting_field", "primary awaited binding drift")
    require(bindings["secondary_awaited_entity"] == "sales_state.journey.awaiting_entity", "secondary awaited binding drift")
    require(bindings["wu104_correction_precedence"] is True, "WU104 correction precedence must remain authoritative")
    require(bindings["wu104_yes_no_guard_authoritative"] is True, "WU104 yes/no guard must remain authoritative")
    require(bindings["wu105_golden_contract_authoritative"] is True, "WU105 contract must remain authoritative")

    precedence = d["precedence_order"]
    expected_prefix = [
        "LOCKED_SAFETY_SUPPORT_OPT_OUT_OVERRIDES",
        "EXPLICIT_CURRENT_STUDENT_CONTEXT_SWITCH",
        "EXPLICIT_CURRENT_CORRECTION",
        "CURRENT_CLEAR_SEMANTIC_INTENT",
        "LOCKED_WU104_AWAITED_FIELD_BINDING",
    ]
    require(precedence[:5] == expected_prefix, "precedence order drift")
    require(precedence[-1] == "STALE_HISTORY", "stale history must remain lowest precedence")

    fields = d["derived_metadata"]["fields"]
    require("student_context_epoch" in fields, "student context epoch missing")
    require(fields["action_state"]["enum"][-3:] == ["ACTION_PENDING", "ACTION_SUCCESS", "ACTION_FAILED"], "action state contract drift")
    require("ACTION_SUCCESS may only be set from an authoritative downstream tool/gateway success signal." in fields["action_state"]["description"], "authoritative success rule missing")

    scopes = d["context_scopes"]
    require("grade" in scopes["student_scoped"] and "subject" in scopes["student_scoped"], "student scoped fields incomplete")
    require("student_name" not in scopes["parent_shared"], "student identity leaked into parent-shared scope")
    require("increment student_context_epoch" in scopes["student_switch_rule"], "student switch boundary missing")

    transitions = {x["id"]: x for x in d["transition_rules"]}
    require(set(transitions) == {f"TR-{i:02d}" for i in range(1, 11)}, "transition rule IDs must be TR-01..TR-10")
    require("preserve compatible fields" in transitions["TR-02"]["then"], "correction preservation rule missing")
    require("increment student_context_epoch" in transitions["TR-04"]["then"], "child boundary transition missing")
    require("stop sales progression" in transitions["TR-05"]["then"], "support override must stop sales")
    require("do not auto-resume" in transitions["TR-06"]["then"], "policy interrupt auto-resume guard missing")
    require("never ACTION_SUCCESS" in transitions["TR-09"]["then"], "availability success guard missing")
    require("ACTION_SUCCESS requires authoritative tool success" in transitions["TR-10"]["then"], "action success gateway missing")

    resume = d["resume_rules"]
    require(resume["automatic_resume_allowed"] is False, "automatic resume must remain false")
    require(resume["customer_signal_required"] is True, "resume requires customer signal")
    require(resume["consent_inferred_from_prior_turn"] is False, "consent inference must remain false")

    privacy = d["privacy_rules"]
    for key in ["duplicate_raw_message", "duplicate_raw_session", "store_secret_values", "store_payment_credentials", "store_student_identity_in_wu106_meta"]:
        require(privacy[key] is False, f"privacy rule must remain false: {key}")

    prod = d["production_rules"]
    require(prod["production_mutation_allowed"] is False, "Production mutation must remain false")
    require(prod["production_activation_allowed"] is False, "Production activation must remain false")
    require(prod["staging_candidate_must_start_inactive"] is True, "STAGING candidate must start inactive")

    print("WU106_JOURNEY_STATE_CONTRACT_PASS")
    print(f"transitions={len(transitions)}")
    print("production_mutation_allowed=false")
    print("automatic_resume_allowed=false")


if __name__ == "__main__":
    main()
