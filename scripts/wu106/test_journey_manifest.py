#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "contracts" / "WU106_GOLDEN_JOURNEYS_V1.json"
LOCK = ROOT / "work-units" / "WU-105.lock.md"
SPEC = ROOT / "work-units" / "WU-106.md"

EXPECTED_SHA = "42ba2b9de1f52c0db1fc32e59974dc40ebce80b787677ac6b0d4418a6315bca1"
EXPECTED_STATES = {
    "TRUSTED_KNOWN",
    "CURRENT_MESSAGE",
    "AWAITED_FIELD",
    "ACTION_PENDING",
    "ACTION_SUCCESS",
    "SUSPENDED_CONTEXT",
    "STALE_HISTORY",
}
EXPECTED_IDS = {f"GJ-{i:02d}" for i in range(1, 13)}
TRUE_RULES = {
    "reuse_trusted_context",
    "do_not_reask_known_fields",
    "current_message_overrides_stale_context",
    "explicit_correction_overrides_prior_value",
    "action_pending_is_not_action_success",
    "availability_requires_live_source",
    "booking_success_requires_action_success",
    "registration_success_requires_action_success",
    "refund_success_requires_action_success",
    "handoff_success_requires_action_success",
    "support_complaint_handoff_can_interrupt_sales",
    "child_context_switch_requires_boundary",
    "wu104_rules_authoritative",
    "wu105_rules_authoritative",
}
FALSE_RULES = {
    "new_taxonomy_intents_allowed",
    "second_wu106_agent_allowed",
    "production_mutation_allowed",
    "irreversible_action_allowed",
}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    lock = LOCK.read_text(encoding="utf-8")
    spec = SPEC.read_text(encoding="utf-8")

    require(data["schema"] == "SPM_WU106_GOLDEN_JOURNEYS_V1", "wrong schema")
    require(data["version"] == "1.0", "wrong version")
    require(data["taxonomy"] == "SPM_V2_62_INTENTS", "taxonomy drift")
    require(data["journey_count"] == 12, "journey_count must be 12")
    require(len(data["journeys"]) == 12, "exactly 12 journeys required")

    dep = data["depends_on"]
    require(dep["wu105_lock"] is True, "WU-105 lock dependency missing")
    require(dep["wu105_final_cr"] == "CR-105-04", "wrong WU-105 final CR")
    require(dep["wu105_candidate_sha256"] == EXPECTED_SHA, "wrong WU-105 candidate SHA")

    require("Status: LOCKED" in lock, "WU-105 lock file is not LOCKED")
    require("locked final CR: `CR-105-04`" in lock, "WU-105 lock CR mismatch")
    require(EXPECTED_SHA in lock, "WU-105 locked candidate SHA not found in lock record")

    rules = data["global_rules"]
    for name in TRUE_RULES:
        require(rules.get(name) is True, f"global rule must remain true: {name}")
    for name in FALSE_RULES:
        require(rules.get(name) is False, f"global rule must remain false: {name}")

    require(set(data["state_classes"]) == EXPECTED_STATES, "state class set drift")

    ids = [j["id"] for j in data["journeys"]]
    require(len(ids) == len(set(ids)), "duplicate journey IDs")
    require(set(ids) == EXPECTED_IDS, "journey ID set must be GJ-01 through GJ-12")

    by_id = {j["id"]: j for j in data["journeys"]}
    for journey in data["journeys"]:
        require(len(journey["turn_intents"]) >= 2, f"{journey['id']} needs at least two turns")
        require(len(journey["must_not"]) >= 2, f"{journey['id']} needs explicit forbidden behavior")
        require(journey["live_priority"] in {"HIGH", "CRITICAL"}, f"bad live priority: {journey['id']}")
        require(len(journey["transition_contract"]) >= 20, f"transition contract too weak: {journey['id']}")

    require("student_identity_or_relation_switch" in by_id["GJ-07"].get("must_create_boundary", []), "GJ-07 must enforce child boundary")
    require("sales_progression" in by_id["GJ-09"].get("must_suspend", []), "GJ-09 must suspend sales")
    require(set(by_id["GJ-12"].get("required_language_paths", [])) == {"EN_TO_AR", "AR_TO_EN", "FR_CONTINUITY", "SAME_LANGUAGE_MULTI_TURN"}, "GJ-12 language paths incomplete")
    require(by_id["GJ-07"]["live_priority"] == "CRITICAL", "child context switch must remain critical")
    require(by_id["GJ-09"]["live_priority"] == "CRITICAL", "support interruption must remain critical")
    require(by_id["GJ-11"]["live_priority"] == "CRITICAL", "stale-context override must remain critical")

    # Guard against accidental authorization language in the frozen spec.
    require("Production activation/deployment is not authorized" in spec, "Production hard-stop missing from spec")
    require("12 Golden Journeys" in spec, "frozen Golden Journey count missing from spec")
    require(re.search(r"P0-08.*Production boundary", spec, re.S), "P0 Production boundary missing")

    print("WU106_GOLDEN_JOURNEY_MANIFEST_PASS")
    print(f"journeys={len(data['journeys'])}")
    print(f"upstream_wu105_sha={EXPECTED_SHA}")
    print("production_mutation_allowed=false")


if __name__ == "__main__":
    main()
