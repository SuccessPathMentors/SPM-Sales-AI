#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

EXPECTED_INPUT_SHA256 = "e40610b13ec61a781acf44842b74955a88a11286e83baa7e121aee349cc9dcf0"
EXPECTED_INPUT_NODE_COUNT = 128
EXPECTED_OUTPUT_NODE_COUNT = 129
SOURCE_NODE = "Apply WU104 Short Trial Inquiry Guard"
TARGET_NODE = "Capture WU89 Classifier Context"
GUARD_NODE = "Apply WU105 Explicit Free Trial Action Guard"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def explicit_action_py(text: str) -> bool:
    t = " ".join(text.strip().lower().split())
    patterns = [
        r"\b(?:i|we)\s+(?:want|would\s+like|need|wish)\s+(?:to\s+)?(?:start|book|arrange|request|schedule|get|try|have)\b.{0,80}\b(?:a\s+)?free\s+trial\b",
        r"\b(?:please\s+)?(?:start|book|arrange|request|schedule)\b.{0,80}\b(?:a\s+)?free\s+trial\b",
        r"\bcan\s+(?:i|we|you)\b.{0,35}\b(?:get|book|start|arrange|request|schedule|have)\b.{0,70}\b(?:a\s+)?free\s+trial\b",
        r"(?:أريد|اريد|بدي|عايز|عاوز|أبغى|ابغى).{0,45}(?:أبدأ|ابدأ|احجز|أحجز|اطلب|أطلب|اجرب|أجرب|احصل|أحصل).{0,45}(?:حصة\s+(?:تجريبية|مجانية)|تجربة\s+مجانية)",
        r"\b(?:je|nous)\s+(?:veux|voudrais|souhaite|souhaitons)\b.{0,55}\b(?:commencer|réserver|reserver|demander|obtenir|faire)\b.{0,70}\b(?:un\s+)?(?:essai\s+gratuit|cours\s+d['’]?essai)\b",
    ]
    return any(re.search(p, t, re.I | re.U) for p in patterns)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--script", default=Path("scripts/wu105/apply_cr10502.py"), type=Path)
    args = parser.parse_args()

    require(args.input.exists(), f"missing CR-105-02 input candidate: {args.input}")
    require(sha256(args.input) == EXPECTED_INPUT_SHA256, "CR-105-02 input SHA mismatch")
    base = json.loads(args.input.read_text(encoding="utf-8"))
    require(len(base.get("nodes", [])) == EXPECTED_INPUT_NODE_COUNT, "CR-105-02 input node count mismatch")

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "cr10502.json"
        subprocess.run(["python", str(args.script), "--input", str(args.input), "--output", str(out)], check=True)
        cand = json.loads(out.read_text(encoding="utf-8"))
        print(f"CR10502_TEST_OUTPUT_SHA256={sha256(out)}")

    require(cand.get("active") is False, "CR-105-02 output must remain inactive")
    require(len(cand.get("nodes", [])) == EXPECTED_OUTPUT_NODE_COUNT, "CR-105-02 output must contain 129 nodes")

    base_nodes = {n.get("name"): n for n in base.get("nodes", [])}
    cand_nodes = {n.get("name"): n for n in cand.get("nodes", [])}
    require(GUARD_NODE not in base_nodes and GUARD_NODE in cand_nodes, "CR-105-02 guard node identity mismatch")
    for name, node in base_nodes.items():
        require(cand_nodes.get(name) == node, f"CR-105-02 modified existing node: {name}")

    guard = cand_nodes[GUARD_NODE]
    require(guard.get("type") == "n8n-nodes-base.code", "CR-105-02 guard must be deterministic Code node")
    require(not guard.get("credentials"), "CR-105-02 guard must not contain credentials")
    code = guard.get("parameters", {}).get("jsCode", "")
    for token in [
        "SPM_WU105_EXPLICIT_FREE_TRIAL_ACTION_GUARD_V1",
        "WU105_EXPLICIT_FREE_TRIAL_ACTION",
        "free_trial",
        "trial_details",
        "human_handoff",
        "complaint",
        "not_interested",
        "wu104_authoritative:true",
        "support_override_preserved:true",
        "action_permission_mutated:false",
        "irreversible_action_allowed:false",
        "raw_message_logged:false",
        "raw_session_logged:false",
        "secret_values_logged:false",
    ]:
        require(token in code, f"missing CR-105-02 invariant/token: {token}")

    def targets(workflow, name):
        return [[c.get("node") for c in group] for group in workflow.get("connections", {}).get(name, {}).get("main", [])]

    require(targets(base, SOURCE_NODE) == [[TARGET_NODE]], "CR-105-02 expected input topology mismatch")
    require(targets(cand, SOURCE_NODE) == [[GUARD_NODE]], "WU-104 short-trial node must feed CR-105-02 guard")
    require(targets(cand, GUARD_NODE) == [[TARGET_NODE]], "CR-105-02 guard must feed WU89 classifier context")

    for name, conn in base.get("connections", {}).items():
        if name == SOURCE_NODE:
            continue
        require(cand.get("connections", {}).get(name) == conn, f"CR-105-02 changed unrelated connection: {name}")

    positive = [
        "I want to start a free trial for my son in Grade 8 Math.",
        "We would like to book a free trial for Grade 6 English.",
        "Can I get a free trial for my daughter?",
        "أريد أبدأ حصة تجريبية مجانية لابني.",
        "Je voudrais réserver un essai gratuit pour ma fille.",
    ]
    negative = [
        "free trial?",
        "How does the free trial work?",
        "What is included in the free trial?",
        "حصة تجريبية؟",
        "Comment fonctionne l'essai gratuit ?",
        "I want to know how the free trial works.",
    ]
    for sample in positive:
        require(explicit_action_py(sample), f"positive CR-105-02 semantic fixture not detected: {sample}")
    for sample in negative:
        require(not explicit_action_py(sample), f"informational trial fixture incorrectly detected as action: {sample}")

    print("PASS CR-105-02 adds exactly one deterministic semantic guard")
    print("PASS explicit free-trial action EN/AR/FR fixtures")
    print("PASS informational trial questions remain outside CR-105-02 action guard")
    print("PASS support/opt-out precedence tokens and no-action-permission invariants")


if __name__ == "__main__":
    main()
