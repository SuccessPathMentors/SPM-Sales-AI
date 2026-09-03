#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "contracts" / "WU106_RUNTIME_MATRIX_V1.json"
MANIFEST = ROOT / "contracts" / "WU106_GOLDEN_JOURNEYS_V1.json"
STATE = ROOT / "contracts" / "WU106_JOURNEY_STATE_V1.json"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    state = json.loads(STATE.read_text(encoding="utf-8"))

    require(matrix["schema"] == "SPM_WU106_RUNTIME_MATRIX_V1", "matrix schema mismatch")
    require(matrix["journey_count"] == 12, "matrix journey count must be 12")
    require(matrix["variants_per_journey"] == 4, "matrix requires four variants per journey")
    require(matrix["planned_scenario_count"] == 48, "matrix planned scenario count must be 48")

    expected_variants = {
        "V1_BASE_CONTINUITY",
        "V2_KNOWN_CONTEXT_NO_REASK",
        "V3_OVERRIDE_OR_ACTION_SAFETY",
        "V4_EDGE_LANGUAGE_OR_STALE_CONTEXT",
    }
    require(set(matrix["variant_definitions"]) == expected_variants, "variant definition set drift")

    manifest_ids = {j["id"] for j in manifest["journeys"]}
    matrix_ids = {j["journey_id"] for j in matrix["journey_matrix"]}
    require(manifest_ids == matrix_ids, "runtime matrix must cover every Golden Journey exactly")
    require(len(matrix["journey_matrix"]) == 12, "runtime matrix journey rows must be 12")

    expanded = []
    for row in matrix["journey_matrix"]:
        require(set(row["variants"]) == expected_variants, f"{row['journey_id']} must define all four variants")
        for variant, description in row["variants"].items():
            require(isinstance(description, str) and len(description) >= 30, f"weak scenario definition: {row['journey_id']} {variant}")
            expanded.append((row["journey_id"], variant))
    require(len(expanded) == 48, "expanded deterministic scenario count must be 48")
    require(len(expanded) == len(set(expanded)), "duplicate journey/variant scenario pair")

    assertions = set(matrix["global_assertions"])
    for required in {
        "wu104_ambiguity_and_awaited_binding_authoritative",
        "wu105_golden_intent_contract_authoritative",
        "production_mutation_allowed_false",
        "action_pending_not_equal_action_success",
        "no_raw_secret_or_payment_credential_persistence",
    }:
        require(required in assertions, f"missing global assertion: {required}")

    require(state["resume_rules"]["automatic_resume_allowed"] is False, "matrix assumes locked no-auto-resume state contract")
    require(state["production_rules"]["production_mutation_allowed"] is False, "matrix must inherit Production hard-stop")
    require(manifest["global_rules"]["current_message_overrides_stale_context"] is True, "matrix must inherit current-message precedence")

    # High-risk journey coverage guards.
    by_id = {row["journey_id"]: row for row in matrix["journey_matrix"]}
    require("daughter Grade 10 Physics" in by_id["GJ-07"]["variants"]["V1_BASE_CONTINUITY"], "child-switch base case missing")
    require("stops conversion pressure" in by_id["GJ-09"]["variants"]["V3_OVERRIDE_OR_ACTION_SAFETY"], "support override safety case missing")
    require("new Grade 10 Physics" in by_id["GJ-11"]["variants"]["V4_EDGE_LANGUAGE_OR_STALE_CONTEXT"], "stale-context critical edge missing")
    require("EN -> AR" in by_id["GJ-12"]["variants"]["V2_KNOWN_CONTEXT_NO_REASK"], "EN->AR case missing")
    require("AR -> EN" in by_id["GJ-12"]["variants"]["V3_OVERRIDE_OR_ACTION_SAFETY"], "AR->EN case missing")
    require("French" in by_id["GJ-12"]["variants"]["V4_EDGE_LANGUAGE_OR_STALE_CONTEXT"], "French case missing")

    print("WU106_RUNTIME_MATRIX_PASS")
    print(f"journeys={len(matrix['journey_matrix'])}")
    print(f"expanded_scenarios={len(expanded)}")
    print("manual_live_tests_target=10_to_15")


if __name__ == "__main__":
    main()
