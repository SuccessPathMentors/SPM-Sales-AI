#!/usr/bin/env python3
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "contracts" / "WU105_GOLDEN_INTENTS_V1.json"
PRODUCTION = ROOT / "n8n" / "workflows" / "production" / "SPM_RC4_3_3_PRODUCTION_FINAL_2026-08-28.json"
EXPECTED_PRODUCTION_SHA256 = "680496f2b68b13dd7105e72fd132a2066d70ec969e6e0675f138ebb1fb16fe39"
EXPECTED_GOLDEN = {
    "subject_inquiry",
    "pricing",
    "package_comparison",
    "price_objection",
    "free_trial",
    "trial_details",
    "teacher_quality",
    "availability",
    "schedule_request",
    "registration",
    "ready_to_register",
    "human_handoff",
    "refund_policy",
}


def all_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from all_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from all_strings(item)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(manifest["schema"] == "SPM_WU105_GOLDEN_INTENTS_V1", "wrong manifest schema")
    require(manifest["version"] == "1.0", "wrong manifest version")
    require(manifest["taxonomy"] == "SPM_V2_62_INTENTS", "taxonomy identifier changed")
    require(8 <= manifest["count"] <= 15, "golden set must remain bounded to 8-15 intents")
    require(manifest["count"] == len(manifest["intents"]), "manifest count does not match intent rows")

    rules = manifest["global_rules"]
    require(rules["answer_current_question_first"] is True, "answer-first rule must remain enabled")
    require(rules["reuse_trusted_context"] is True, "trusted-context reuse must remain enabled")
    require(rules["max_followup_questions"] == 1, "golden response may ask at most one follow-up question")
    require(rules["do_not_reask_known_fields"] is True, "no-reask rule must remain enabled")
    require(rules["wu104_ambiguity_rules_authoritative"] is True, "WU-104 must remain authoritative")
    require(rules["source_and_action_gates_authoritative"] is True, "source/action gates must remain authoritative")
    require(rules["new_business_permissions"] is False, "WU-105 may not grant business permissions")
    require(rules["production_mutation_allowed"] is False, "WU-105 may not mutate Production")

    names = [row["intent"] for row in manifest["intents"]]
    require(len(names) == len(set(names)), "duplicate golden intent")
    require(set(names) == EXPECTED_GOLDEN, "V1 golden selection changed without an explicit contract update")
    require("out_of_scope" not in names, "out_of_scope must not be optimized as a generic uncertainty route")

    prod_bytes = PRODUCTION.read_bytes()
    actual_sha = hashlib.sha256(prod_bytes).hexdigest()
    require(actual_sha == EXPECTED_PRODUCTION_SHA256, f"Production baseline SHA changed: {actual_sha}")
    production = json.loads(prod_bytes.decode("utf-8"))
    classifier_text = "\n".join(all_strings(production))

    for row in manifest["intents"]:
        intent = row["intent"]
        require(re.fullmatch(r"[a-z0-9_]+", intent) is not None, f"invalid intent name: {intent}")
        heading = f"------------------------------ {intent} ------------------------------"
        require(heading in classifier_text, f"golden intent is not defined in the locked Production classifier: {intent}")
        require(row["selection_reasons"], f"selection reason missing: {intent}")
        require(row["authoritative_sources"], f"authoritative source missing: {intent}")
        require(len(row["direct_answer_requirement"].strip()) >= 20, f"direct-answer contract too weak: {intent}")
        require(row["preferred_next_best_action"].strip(), f"NBA missing: {intent}")
        require(row["smallest_optional_qualifier"].strip(), f"smallest qualifier contract missing: {intent}")
        require(row["forbidden"], f"forbidden behavior list missing: {intent}")
        require(row["confusion_pairs"], f"confusion pairs missing: {intent}")
        require(intent not in row["confusion_pairs"], f"intent cannot be its own confusion pair: {intent}")
        require(row["irreversible_action_allowed"] is False, f"WU-105 cannot authorize irreversible action: {intent}")
        require(len(row["wu104_compatibility"].strip()) >= 20, f"WU-104 compatibility rule missing: {intent}")
        for neighbor in row["confusion_pairs"]:
            neighbor_heading = f"------------------------------ {neighbor} ------------------------------"
            require(neighbor_heading in classifier_text, f"unknown confusion-pair intent {neighbor} for {intent}")

    print(f"PASS WU-105 golden manifest: {len(names)} intents")
    print(f"PASS Production baseline SHA256: {actual_sha}")
    print("PASS selected intents and confusion neighbors exist in locked classifier definitions")
    print("PASS answer-first/no-reask/WU-104/source-action hard stops")


if __name__ == "__main__":
    main()
