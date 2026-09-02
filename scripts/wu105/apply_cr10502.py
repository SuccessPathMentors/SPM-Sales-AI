#!/usr/bin/env python3
import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path

EXPECTED_INPUT_SHA256 = "e40610b13ec61a781acf44842b74955a88a11286e83baa7e121aee349cc9dcf0"
EXPECTED_INPUT_NODE_COUNT = 128
SOURCE_NODE = "Apply WU104 Short Trial Inquiry Guard"
TARGET_NODE = "Capture WU89 Classifier Context"
GUARD_NODE = "Apply WU105 Explicit Free Trial Action Guard"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_guard_node(position):
    js_code = r"""const j=$input.first().json||{};
const c=(j.classification&&typeof j.classification==='object')?j.classification:{};
const raw=String(j.message?.raw??'').normalize('NFKC').trim();
const norm=raw.toLowerCase().replace(/\s+/g,' ');
const intent=String(c.spm_intent||'');
const direct=String(j.classifier_route||'')==='direct'&&c.ambiguous!==true;

// CR-105-02 only repairs unmistakable ACTION wording. Informational questions
// such as "free trial?" or "How does the free trial work?" remain governed by
// locked WU-104 / trial_details behavior.
const explicitFreeTrialAction=[
 /\b(?:i|we)\s+(?:want|would\s+like|need|wish)\s+(?:to\s+)?(?:start|book|arrange|request|schedule|get|try|have)\b.{0,80}\b(?:a\s+)?free\s+trial\b/iu,
 /\b(?:please\s+)?(?:start|book|arrange|request|schedule)\b.{0,80}\b(?:a\s+)?free\s+trial\b/iu,
 /\bcan\s+(?:i|we|you)\b.{0,35}\b(?:get|book|start|arrange|request|schedule|have)\b.{0,70}\b(?:a\s+)?free\s+trial\b/iu,
 /(?:أريد|اريد|بدي|عايز|عاوز|أبغى|ابغى).{0,45}(?:أبدأ|ابدأ|احجز|أحجز|اطلب|أطلب|اجرب|أجرب|احصل|أحصل).{0,45}(?:حصة\s+(?:تجريبية|مجانية)|تجربة\s+مجانية)/u,
 /\b(?:je|nous)\s+(?:veux|voudrais|souhaite|souhaitons)\b.{0,55}\b(?:commencer|réserver|reserver|demander|obtenir|faire)\b.{0,70}\b(?:un\s+)?(?:essai\s+gratuit|cours\s+d['’]?essai)\b/iu
].some(r=>r.test(norm));

// Fail-safe scope: only repair common semantic confusions for an explicit trial
// action. Never override support, opt-out, complaint, payment, or other user
// override intents.
const allowedSourceIntents=new Set([
 'free_trial','subject_inquiry','grade_inquiry','learning_goal','trial_details',
 'registration','ready_to_register','unknown_intent'
]);
const blockedIntents=new Set([
 'human_handoff','complaint','technical_issue','account_login','payment_problem',
 'payment_methods','not_interested','refund_policy','cancellation_policy','security'
]);

const catalog=Array.isArray(j.intent_catalog)?j.intent_catalog:[];
const target=catalog.find(r=>String(r?.spm_intent||'')==='free_trial')||null;
let classification=c;
let status='NO_OVERRIDE';
let applied=false;

if(direct&&explicitFreeTrialAction&&!blockedIntents.has(intent)&&allowedSourceIntents.has(intent)&&target){
 const targetThreshold=Number.isFinite(Number(target.min_confidence))?Number(target.min_confidence):0.85;
 classification={
  ...c,
  spm_intent:'free_trial',
  secondary_spm_intent:intent&&intent!=='free_trial'?intent:'',
  confidence:Math.max(Number(c.confidence||0),0.99),
  threshold:targetThreshold,
  ambiguous:false,
  required_entities:Array.isArray(target.required_entities)?target.required_entities:[],
  source_gate:String(target.source_gate||c.source_gate||''),
  risk_tier:String(target.risk_tier||c.risk_tier||''),
  sales_stage:String(target.sales_stage||c.sales_stage||''),
  rationale_code:'WU105_EXPLICIT_FREE_TRIAL_ACTION'
 };
 status=intent==='free_trial'?'CONFIRM_FREE_TRIAL_ACTION':'REMAP_EXPLICIT_FREE_TRIAL_ACTION';
 applied=intent!=='free_trial';
}else if(direct&&explicitFreeTrialAction&&!blockedIntents.has(intent)&&allowedSourceIntents.has(intent)&&!target){
 status='TARGET_INTENT_MISSING_FAIL_CLOSED';
}else if(explicitFreeTrialAction&&blockedIntents.has(intent)){
 status='BLOCKED_BY_HIGHER_PRIORITY_INTENT';
}else if(explicitFreeTrialAction&&!allowedSourceIntents.has(intent)){
 status='OUTSIDE_NARROW_REMAP_SCOPE';
}

const evidence={
 schema:'SPM_WU105_EXPLICIT_FREE_TRIAL_ACTION_GUARD_V1',
 status,
 applied,
 source_intent:intent||null,
 resolved_intent:String(classification.spm_intent||intent||''),
 explicit_action_detected:Boolean(explicitFreeTrialAction),
 classifier_route:String(j.classifier_route||''),
 wu104_authoritative:true,
 support_override_preserved:true,
 action_permission_mutated:false,
 irreversible_action_allowed:false,
 raw_message_logged:false,
 raw_session_logged:false,
 secret_values_logged:false
};
return [{json:{...j,classification,wu105_free_trial_action_guard:evidence}}];"""
    return {
        "parameters": {"jsCode": js_code},
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": position,
        "id": "wu105-explicit-free-trial-action-guard-v1",
        "name": GUARD_NODE,
        "notesInFlow": True,
        "notes": "CR-105-02 STAGING-only deterministic semantic guard. Repairs unmistakable explicit free-trial action requests without overriding WU-104 informational-trial handling, support precedence, source truth, consent gates, or Production."
    }


def apply(input_path: Path, output_path: Path):
    actual = sha256(input_path)
    if actual != EXPECTED_INPUT_SHA256:
        raise SystemExit(f"CR-105-02 input candidate SHA mismatch: {actual}")

    workflow = json.loads(input_path.read_text(encoding="utf-8"))
    if len(workflow.get("nodes", [])) != EXPECTED_INPUT_NODE_COUNT:
        raise SystemExit(f"CR-105-02 input node count mismatch: {len(workflow.get('nodes', []))}")

    candidate = deepcopy(workflow)
    candidate["active"] = False
    names = [n.get("name") for n in candidate.get("nodes", [])]
    if GUARD_NODE in names:
        raise SystemExit("CR-105-02 guard already exists")
    if names.count(SOURCE_NODE) != 1 or names.count(TARGET_NODE) != 1:
        raise SystemExit("CR-105-02 required topology node identity mismatch")

    source = next(n for n in candidate["nodes"] if n.get("name") == SOURCE_NODE)
    x, y = source.get("position", [0, 0])
    candidate["nodes"].append(make_guard_node([x + 320, y + 144]))

    connections = candidate.setdefault("connections", {})
    source_connections = deepcopy(connections.get(SOURCE_NODE))
    if not source_connections or "main" not in source_connections:
        raise SystemExit("CR-105-02 source node has no main connection")
    main = source_connections["main"]
    if len(main) != 1 or len(main[0]) != 1 or main[0][0].get("node") != TARGET_NODE:
        raise SystemExit("CR-105-02 unexpected locked WU-104 short-trial topology")
    original_target = deepcopy(main[0][0])
    connections[SOURCE_NODE] = {**source_connections, "main": [[{"node": GUARD_NODE, "type": "main", "index": 0}]]}
    connections[GUARD_NODE] = {"main": [[original_target]]}

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"CR10502_INPUT_SHA256={actual}")
    print(f"CR10502_OUTPUT={output_path}")
    print(f"CR10502_OUTPUT_SHA256={sha256(output_path)}")
    print(f"CR10502_NODE_COUNT={len(candidate.get('nodes', []))}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    apply(args.input, args.output)


if __name__ == "__main__":
    main()
