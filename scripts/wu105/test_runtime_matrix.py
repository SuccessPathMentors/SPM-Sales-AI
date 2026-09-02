#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = json.loads((ROOT / "contracts" / "WU105_GOLDEN_INTENTS_V1.json").read_text(encoding="utf-8"))
MATRIX = json.loads((ROOT / "contracts" / "WU105_RUNTIME_MATRIX_V1.json").read_text(encoding="utf-8"))
EXPECTED_CANDIDATE_SHA = "43ac3b2be6ae51b99b16f4e3166e0c9e0e055ccbc0b67d48871346d594415eed"
REQUIRED_CASES = {
    "fresh_direct",
    "context_no_reask",
    "stale_context_override",
    "wu104_case",
    "confusion_case",
    "source_unavailable",
}


def require(value, message):
    if not value:
        raise AssertionError(message)


def main():
    require(MATRIX["schema"] == "SPM_WU105_RUNTIME_MATRIX_V1", "wrong matrix schema")
    require(MATRIX["version"] == "1.0", "wrong matrix version")
    require(MATRIX["candidate_sha256"] == EXPECTED_CANDIDATE_SHA, "runtime matrix bound to wrong candidate SHA")

    global_assertions = MATRIX["global_assertions"]
    for field in [
        "answer_current_question_first",
        "no_reask_known_fields",
        "wu104_authoritative",
        "zero_unauthorized_business_writes",
        "source_action_gates_authoritative",
        "production_untouched",
    ]:
        require(global_assertions.get(field) is True, f"global assertion not frozen true: {field}")
    require(global_assertions.get("max_followup_questions") == 1, "question cap must remain 1")

    manifest_names = {row["intent"] for row in MANIFEST["intents"]}
    rows = MATRIX["intents"]
    matrix_names = [row["intent"] for row in rows]
    require(len(matrix_names) == len(set(matrix_names)), "duplicate intent in runtime matrix")
    require(set(matrix_names) == manifest_names, "runtime matrix must cover every and only V1 Golden intent")

    total_scenarios = 0
    multilingual_prompts = 0
    for row in rows:
        intent = row["intent"]
        require(REQUIRED_CASES.issubset(row), f"missing required runtime case for {intent}")
        fresh = row["fresh_direct"]
        for lang in ("en", "ar", "fr"):
            require(isinstance(fresh.get(lang), str) and fresh[lang].strip(), f"missing {lang} direct prompt for {intent}")
            multilingual_prompts += 1
        context = row["context_no_reask"]
        require(context.get("trusted_context"), f"trusted context fixture missing for {intent}")
        require(context.get("must_not_ask"), f"no-reask assertion missing for {intent}")
        stale = row["stale_context_override"]
        require(stale.get("stale_intent") and stale.get("expected_intent"), f"stale-context assertion missing for {intent}")
        wu104 = row["wu104_case"]
        require(wu104.get("message") and wu104.get("expected"), f"WU-104 compatibility fixture missing for {intent}")
        confusion = row["confusion_case"]
        require(confusion.get("neighbor") and confusion.get("expected_intent"), f"confusion-pair assertion missing for {intent}")
        require(confusion["neighbor"] in next(x for x in MANIFEST["intents"] if x["intent"] == intent)["confusion_pairs"], f"runtime confusion neighbor is not frozen in manifest for {intent}")
        unavailable = row["source_unavailable"]
        require(unavailable.get("expected"), f"source-unavailable safe outcome missing for {intent}")
        total_scenarios += 8  # EN/AR/FR direct + five specialized cases

    require(multilingual_prompts == len(rows) * 3, "multilingual direct prompt coverage mismatch")
    require(total_scenarios == len(rows) * 8, "scenario count mismatch")
    print(f"PASS WU-105 runtime matrix intents: {len(rows)}")
    print(f"PASS multilingual direct prompts: {multilingual_prompts}")
    print(f"PASS planned runtime scenarios: {total_scenarios}")
    print(f"PASS matrix bound to candidate SHA256: {EXPECTED_CANDIDATE_SHA}")


if __name__ == "__main__":
    main()
