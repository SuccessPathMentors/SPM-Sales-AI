#!/usr/bin/env python3
import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path

EXPECTED_INPUT_SHA256 = "7fc201137671b1cd47f9fc6b4ec60a9b563b2bae7c0776952ec68e0988bfed1e"
EXPECTED_INPUT_NODE_COUNT = 129
SOURCE_NODE = "Validate + Guard WU92 Sales Agent Output"
TARGET_NODE = "Apply WU92 Sales Agent Policy Guard"
GENERATOR_NODE = "Generate WU92 Sales Agent Response"
GUARD_NODE = "Apply WU105 Refund Policy Answer-First Guard"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_guard_node(position):
    js_code = r"""const j=$input.first().json||{};
const intent=String(j.classification?.spm_intent||'');
const msg=String(j.message?.raw||'').normalize('NFKC').trim();
const norm=msg.toLowerCase().replace(/\s+/g,' ');
const out={...(j.sales_agent_output||{})};
const lang=String(j.classification?.language||j.language_hint||'en').toLowerCase();

function parse(v){
  if(v&&typeof v==='object'&&!Array.isArray(v)) return v;
  let t=String(v??'').trim().replace(/^```(?:json)?\s*/i,'').replace(/\s*```$/,'').trim();
  try{return JSON.parse(t)}catch{}
  const a=t.indexOf('{'), b=t.lastIndexOf('}');
  if(a>=0&&b>a){try{return JSON.parse(t.slice(a,b+1))}catch{}}
  return {};
}

// Read the original model answer only for false-positive recovery. This does
// not bypass source truth: recovery is allowed only when the existing source
// gate already says the factual answer is supportable.
const generated=$('Generate WU92 Sales Agent Response').first().json||{};
const raw=parse(generated.output??generated.text??generated.response??generated);
const rawAnswer=String(raw.answer_text||'').trim();

const policyInfo=[
  /\brefund\s+policy\b/iu,
  /\bpolicy\s+(?:on|for|about)\s+refunds?\b/iu,
  /\brefund\s+rules?\b/iu,
  /\bhow\s+(?:does|do)\b.{0,35}\brefund(?:s|ing)?\b.{0,35}\bwork\b/iu,
  /سياسة\s+(?:الاسترجاع|الاسترداد|استرجاع|استرداد)/u,
  /(?:ما|ماهي|ما هي|شو)\s+.{0,20}سياسة\s+(?:الاسترجاع|الاسترداد)/u,
  /\bpolitique\s+de\s+remboursement\b/iu,
  /\brègles?\s+de\s+remboursement\b/iu
].some(r=>r.test(norm));

// Explicit customer-specific execution requests remain under the original
// safety/action gateway and are never restored by this guard.
const explicitRefundAction=[
  /\b(?:i|we)\s+(?:want|need|would\s+like|request)\b.{0,35}\b(?:a\s+)?refund\b/iu,
  /\b(?:please\s+)?(?:refund|reimburse)\s+(?:me|us|my|our)\b/iu,
  /\b(?:issue|process|send|give)\b.{0,25}\b(?:a\s+)?refund\b/iu,
  /(?:أريد|اريد|بدي|عايز|عاوز).{0,30}(?:استرجاع|استرداد|ارجاع|إرجاع).{0,25}(?:مالي|المبلغ|الدفع)?/u,
  /\b(?:je|nous)\s+(?:veux|voudrais|demande|demandons)\b.{0,40}\bun\s+remboursement\b/iu
].some(r=>r.test(norm));

const sourceCanAnswer=Boolean(j.source_gate_decision?.can_answer);
const hadSafetyRewrite=Boolean(out.safety_rewrite_applied);
const forbidden=/\b(booked|confirmed|saved|registered|refunded|discount approved|tutor assigned)\b/i;
const unrelatedForbidden=/\b(booked|saved|registered|discount approved|tutor assigned)\b/i;
const customerSpecificExecution=/\b(?:your|you have|you've|we have|we've|already)\b.{0,60}\b(?:refunded|refund\s+(?:was|has been)|confirmed)\b/i;

let applied=false;
let status='NO_RESTORE';
let restoredAnswer=String(out.answer_text||'');

if(intent==='refund_policy' && policyInfo && !explicitRefundAction && sourceCanAnswer && hadSafetyRewrite && rawAnswer){
  if(!forbidden.test(rawAnswer)){
    status='NO_FALSE_POSITIVE_TOKEN';
  }else if(unrelatedForbidden.test(rawAnswer)){
    status='BLOCK_UNRELATED_EXECUTION_TOKEN';
  }else if(customerSpecificExecution.test(rawAnswer)){
    status='BLOCK_CUSTOMER_SPECIFIC_EXECUTION_CLAIM';
  }else{
    // Narrowly neutralize vocabulary that the locked WU92 validator treats as
    // executed action while preserving the source-backed policy explanation.
    restoredAnswer=rawAnswer
      .replace(/\b(?:will|shall|can|may|could)\s+be\s+refunded\b/gi,'may be eligible for a refund under the applicable policy')
      .replace(/\b(?:has|have|had)\s+been\s+refunded\b/gi,'may be eligible for a refund under the applicable policy')
      .replace(/\b(?:is|are|was|were)\s+refunded\b/gi,'may be eligible for a refund under the applicable policy')
      .replace(/\brefunded\b/gi,'eligible for refund review')
      .replace(/\bconfirmed\b/gi,'verified');

    // If an execution-like token somehow remains, fail closed and retain the
    // original validator rewrite instead of weakening the action boundary.
    if(forbidden.test(restoredAnswer)){
      status='SANITIZATION_INCOMPLETE_FAIL_CLOSED';
      restoredAnswer=String(out.answer_text||'');
    }else{
      out.answer_text=restoredAnswer;
      out.proposed_action='none';
      out.action_requires_gateway=false;
      applied=true;
      status='RESTORED_SOURCE_BACKED_POLICY_EXPLANATION';
    }
  }
}else if(intent==='refund_policy' && explicitRefundAction){
  status='EXPLICIT_REFUND_ACTION_PRESERVE_GATEWAY';
}else if(intent==='refund_policy' && policyInfo && !sourceCanAnswer){
  status='SOURCE_UNAVAILABLE_PRESERVE_FAIL_CLOSED';
}

const evidence={
  schema:'SPM_WU105_REFUND_POLICY_ANSWER_FIRST_GUARD_V1',
  status,
  applied,
  intent,
  policy_information_request:Boolean(policyInfo),
  explicit_refund_action:Boolean(explicitRefundAction),
  source_can_answer:sourceCanAnswer,
  upstream_safety_rewrite:Boolean(hadSafetyRewrite),
  original_model_answer_present:Boolean(rawAnswer),
  action_permission_mutated:false,
  irreversible_action_allowed:false,
  source_gate_authoritative:true,
  explicit_action_gateway_preserved:true,
  raw_message_logged:false,
  raw_session_logged:false,
  secret_values_logged:false
};
return [{json:{...j,sales_agent_output:out,wu105_refund_policy_guard:evidence}}];"""
    return {
        "parameters": {"jsCode": js_code},
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": position,
        "id": "wu105-refund-policy-answer-first-guard-v1",
        "name": GUARD_NODE,
        "notesInFlow": True,
        "notes": "CR-105-03 STAGING-only deterministic guard. Recovers a source-backed general refund-policy explanation only when locked WU92 falsely treats policy wording such as 'refunded' as an executed action. Explicit refund requests and source-unavailable cases remain fail-closed."
    }


def apply(input_path: Path, output_path: Path):
    actual = sha256(input_path)
    if actual != EXPECTED_INPUT_SHA256:
        raise SystemExit(f"CR-105-03 input candidate SHA mismatch: {actual}")

    workflow = json.loads(input_path.read_text(encoding="utf-8"))
    if len(workflow.get("nodes", [])) != EXPECTED_INPUT_NODE_COUNT:
        raise SystemExit(f"CR-105-03 input node count mismatch: {len(workflow.get('nodes', []))}")

    candidate = deepcopy(workflow)
    candidate["active"] = False
    names = [n.get("name") for n in candidate.get("nodes", [])]
    if GUARD_NODE in names:
        raise SystemExit("CR-105-03 guard already exists")
    for name in [SOURCE_NODE, TARGET_NODE, GENERATOR_NODE]:
        if names.count(name) != 1:
            raise SystemExit(f"CR-105-03 required node identity mismatch: {name}")

    source = next(n for n in candidate["nodes"] if n.get("name") == SOURCE_NODE)
    x, y = source.get("position", [0, 0])
    candidate["nodes"].append(make_guard_node([x + 320, y + 144]))

    connections = candidate.setdefault("connections", {})
    source_connections = deepcopy(connections.get(SOURCE_NODE))
    if not source_connections or "main" not in source_connections:
        raise SystemExit("CR-105-03 source node has no main connection")
    main = source_connections["main"]
    if len(main) != 1 or len(main[0]) != 1 or main[0][0].get("node") != TARGET_NODE:
        raise SystemExit("CR-105-03 unexpected WU92 validator topology")
    original_target = deepcopy(main[0][0])
    connections[SOURCE_NODE] = {**source_connections, "main": [[{"node": GUARD_NODE, "type": "main", "index": 0}]]}
    connections[GUARD_NODE] = {"main": [[original_target]]}

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"CR10503_INPUT_SHA256={actual}")
    print(f"CR10503_OUTPUT={output_path}")
    print(f"CR10503_OUTPUT_SHA256={sha256(output_path)}")
    print(f"CR10503_NODE_COUNT={len(candidate.get('nodes', []))}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    apply(args.input, args.output)


if __name__ == "__main__":
    main()
