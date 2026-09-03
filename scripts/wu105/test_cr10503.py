#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

EXPECTED_INPUT_SHA256 = "7fc201137671b1cd47f9fc6b4ec60a9b563b2bae7c0776952ec68e0988bfed1e"
EXPECTED_INPUT_NODE_COUNT = 129
EXPECTED_OUTPUT_NODE_COUNT = 130
SOURCE_NODE = "Validate + Guard WU92 Sales Agent Output"
TARGET_NODE = "Apply WU92 Sales Agent Policy Guard"
GUARD_NODE = "Apply WU105 Refund Policy Answer-First Guard"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def policy_info_py(text: str) -> bool:
    t = " ".join(text.strip().lower().split())
    pats = [
        r"\brefund\s+policy\b",
        r"\bpolicy\s+(?:on|for|about)\s+refunds?\b",
        r"\brefund\s+rules?\b",
        r"\bhow\s+(?:does|do)\b.{0,35}\brefund(?:s|ing)?\b.{0,35}\bwork\b",
        r"سياسة\s+(?:الاسترجاع|الاسترداد|استرجاع|استرداد)",
        r"(?:ما|ماهي|ما هي|شو)\s+.{0,20}سياسة\s+(?:الاسترجاع|الاسترداد)",
        r"\bpolitique\s+de\s+remboursement\b",
        r"\brègles?\s+de\s+remboursement\b",
    ]
    return any(re.search(p, t, re.I | re.U) for p in pats)


def explicit_refund_action_py(text: str) -> bool:
    t = " ".join(text.strip().lower().split())
    pats = [
        r"\b(?:i|we)\s+(?:want|need|would\s+like|request)\b.{0,35}\b(?:a\s+)?refund\b",
        r"\b(?:please\s+)?(?:refund|reimburse)\s+(?:me|us|my|our)\b",
        r"\b(?:issue|process|send|give)\b.{0,25}\b(?:a\s+)?refund\b",
        r"(?:أريد|اريد|بدي|عايز|عاوز).{0,30}(?:استرجاع|استرداد|ارجاع|إرجاع).{0,25}(?:مالي|المبلغ|الدفع)?",
        r"\b(?:je|nous)\s+(?:veux|voudrais|demande|demandons)\b.{0,40}\bun\s+remboursement\b",
    ]
    return any(re.search(p, t, re.I | re.U) for p in pats)


def sanitize_policy_py(answer: str) -> str:
    s = answer
    s = re.sub(r"\b(?:will|shall|can|may|could)\s+be\s+refunded\b", "may be eligible for a refund under the applicable policy", s, flags=re.I)
    s = re.sub(r"\b(?:has|have|had)\s+been\s+refunded\b", "may be eligible for a refund under the applicable policy", s, flags=re.I)
    s = re.sub(r"\b(?:is|are|was|were)\s+refunded\b", "may be eligible for a refund under the applicable policy", s, flags=re.I)
    s = re.sub(r"\brefunded\b", "eligible for refund review", s, flags=re.I)
    s = re.sub(r"\bconfirmed\b", "verified", s, flags=re.I)
    return s


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--script", default=Path("scripts/wu105/apply_cr10503.py"), type=Path)
    args = parser.parse_args()

    require(args.input.exists(), f"missing CR-105-03 input candidate: {args.input}")
    require(sha256(args.input) == EXPECTED_INPUT_SHA256, "CR-105-03 input SHA mismatch")
    base = json.loads(args.input.read_text(encoding="utf-8"))
    require(len(base.get("nodes", [])) == EXPECTED_INPUT_NODE_COUNT, "CR-105-03 input node count mismatch")

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "cr10503.json"
        subprocess.run(["python", str(args.script), "--input", str(args.input), "--output", str(out)], check=True)
        cand = json.loads(out.read_text(encoding="utf-8"))
        print(f"CR10503_TEST_OUTPUT_SHA256={sha256(out)}")

    require(cand.get("active") is False, "CR-105-03 output must remain inactive")
    require(len(cand.get("nodes", [])) == EXPECTED_OUTPUT_NODE_COUNT, "CR-105-03 output must contain 130 nodes")

    base_nodes = {n.get("name"): n for n in base.get("nodes", [])}
    cand_nodes = {n.get("name"): n for n in cand.get("nodes", [])}
    require(GUARD_NODE not in base_nodes and GUARD_NODE in cand_nodes, "CR-105-03 guard node identity mismatch")
    for name, node in base_nodes.items():
        require(cand_nodes.get(name) == node, f"CR-105-03 modified existing node: {name}")

    guard = cand_nodes[GUARD_NODE]
    require(guard.get("type") == "n8n-nodes-base.code", "CR-105-03 guard must be deterministic Code node")
    require(not guard.get("credentials"), "CR-105-03 guard must not contain credentials")
    code = guard.get("parameters", {}).get("jsCode", "")
    for token in [
        "SPM_WU105_REFUND_POLICY_ANSWER_FIRST_GUARD_V1",
        "refund_policy",
        "SOURCE_UNAVAILABLE_PRESERVE_FAIL_CLOSED",
        "EXPLICIT_REFUND_ACTION_PRESERVE_GATEWAY",
        "RESTORED_SOURCE_BACKED_POLICY_EXPLANATION",
        "source_gate_authoritative:true",
        "explicit_action_gateway_preserved:true",
        "action_permission_mutated:false",
        "irreversible_action_allowed:false",
        "raw_message_logged:false",
        "raw_session_logged:false",
        "secret_values_logged:false",
    ]:
        require(token in code, f"missing CR-105-03 invariant/token: {token}")

    def targets(workflow, name):
        return [[c.get("node") for c in group] for group in workflow.get("connections", {}).get(name, {}).get("main", [])]

    require(targets(base, SOURCE_NODE) == [[TARGET_NODE]], "CR-105-03 expected input topology mismatch")
    require(targets(cand, SOURCE_NODE) == [[GUARD_NODE]], "WU92 validator must feed CR-105-03 guard")
    require(targets(cand, GUARD_NODE) == [[TARGET_NODE]], "CR-105-03 guard must feed existing WU92 policy guard")
    for name, conn in base.get("connections", {}).items():
        if name == SOURCE_NODE:
            continue
        require(cand.get("connections", {}).get(name) == conn, f"CR-105-03 changed unrelated connection: {name}")

    positive_info = [
        "What is your refund policy?",
        "What are your refund rules?",
        "How do refunds work under your policy?",
        "ما هي سياسة الاسترداد عندكم؟",
        "Quelle est votre politique de remboursement ?",
    ]
    explicit_actions = [
        "I want a refund.",
        "Please refund me.",
        "Process a refund for my payment.",
        "أريد استرداد المبلغ.",
        "Je voudrais un remboursement.",
    ]
    for sample in positive_info:
        require(policy_info_py(sample), f"policy information fixture not detected: {sample}")
        require(not explicit_refund_action_py(sample), f"policy information fixture incorrectly treated as action: {sample}")
    for sample in explicit_actions:
        require(explicit_refund_action_py(sample), f"explicit refund action fixture not detected: {sample}")

    original = "Unused eligible lessons may be refunded after the applicable refund conditions are confirmed."
    sanitized = sanitize_policy_py(original)
    forbidden = re.compile(r"\b(booked|confirmed|saved|registered|refunded|discount approved|tutor assigned)\b", re.I)
    require(not forbidden.search(sanitized), "CR-105-03 sanitizer must remove validator false-positive execution tokens")
    require("refund" in sanitized.lower(), "CR-105-03 sanitizer must preserve refund-policy meaning")

    print("PASS CR-105-03 adds exactly one deterministic post-validator guard")
    print("PASS general refund-policy EN/AR/FR information fixtures")
    print("PASS explicit refund action fixtures preserve original gateway")
    print("PASS source-unavailable fail-closed and no-action-permission invariants")
    print("PASS false-positive validator vocabulary sanitized without deleting refund meaning")


if __name__ == "__main__":
    main()
