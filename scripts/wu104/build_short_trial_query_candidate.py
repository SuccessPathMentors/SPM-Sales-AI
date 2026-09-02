#!/usr/bin/env python3
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_WRAPPER = ROOT / 'scripts' / 'wu104' / 'build_known_slot_candidate.py'


def load_base_wrapper():
    spec = importlib.util.spec_from_file_location('wu104_known_slot_for_short_trial_fix', BASE_WRAPPER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def node_by_name(wf, name):
    matches = [n for n in wf['nodes'] if n.get('name') == name]
    if len(matches) != 1:
        raise RuntimeError(f'expected exactly one node {name!r}, found {len(matches)}')
    return matches[0]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(baseline_path):
    base = load_base_wrapper()
    wf = copy.deepcopy(base.build(baseline_path))

    guard_name = 'Apply WU104 Short Trial Inquiry Guard'
    guard_js = r"""const j=$input.first().json||{};
const c=(j.classification&&typeof j.classification==='object')?j.classification:{};
const raw=String(j.message?.raw??'').normalize('NFKC').trim();
const norm=raw.toLowerCase().replace(/\s+/g,' ');
const intent=String(c.spm_intent||'');
const direct=String(j.classifier_route||'')==='direct'&&c.ambiguous!==true;
const terseTrialInfoQuestion=[
 /^free\s+trial\s*\?$/iu,
 /^trial\s+lesson\s*\?$/iu,
 /^(?:حصة\s+(?:تجريبية|مجانية)|تجربة\s+مجانية)\s*[؟?]$/u,
 /^(?:essai\s+gratuit|cours\s+d['’]?essai)\s*\?$/iu
].some(r=>r.test(norm));
const catalog=Array.isArray(j.intent_catalog)?j.intent_catalog:[];
const target=catalog.find(r=>String(r?.spm_intent||'')==='trial_details')||null;
let classification=c;
let decision=(j.wu104_short_query_decision&&typeof j.wu104_short_query_decision==='object')?{...j.wu104_short_query_decision}:{};
let status='NO_OVERRIDE';
let applied=false;
if(intent==='free_trial'&&direct&&terseTrialInfoQuestion&&target){
 const targetThreshold=Number.isFinite(Number(target.min_confidence))?Number(target.min_confidence):0.85;
 classification={
  ...c,
  spm_intent:'trial_details',
  secondary_spm_intent:'',
  confidence:Math.max(Number(c.confidence||0),0.99),
  threshold:targetThreshold,
  ambiguous:false,
  required_entities:Array.isArray(target.required_entities)?target.required_entities:[],
  source_gate:String(target.source_gate||c.source_gate||''),
  risk_tier:String(target.risk_tier||c.risk_tier||''),
  sales_stage:String(target.sales_stage||c.sales_stage||''),
  rationale_code:'WU104_SHORT_TRIAL_INFO_QUESTION'
 };
 decision={...decision,resolved_intent:'trial_details',binding_source:'WU104_SHORT_SEMANTIC_GUARD'};
 status='REMAP_FREE_TRIAL_QUESTION_TO_TRIAL_DETAILS';
 applied=true;
}else if(intent==='free_trial'&&direct&&terseTrialInfoQuestion&&!target){
 status='TARGET_INTENT_MISSING_FAIL_CLOSED';
}
const evidence={
 schema:'SPM_WU104_SHORT_SEMANTIC_GUARD_V1',
 status,
 applied,
 source_intent:intent||null,
 target_intent:applied?'trial_details':null,
 classifier_route:String(j.classifier_route||''),
 raw_message_logged:false,
 raw_session_logged:false,
 secret_values_logged:false
};
return [{json:{...j,classification,wu104_short_query_decision:decision,wu104_short_semantic_guard:evidence}}];"""

    guard_node = {
        'id': '10400000-0000-4000-8000-000000000105',
        'name': guard_name,
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': [-80720, 5472],
        'parameters': {'jsCode': guard_js},
    }
    wf['nodes'].append(guard_node)

    upstream = 'Build WU104 Short Query Decision'
    downstream = 'Capture WU89 Classifier Context'
    existing = wf['connections'].get(upstream, {}).get('main', [])
    if existing != [[{'node': downstream, 'type': 'main', 'index': 0}]]:
        raise RuntimeError(f'unexpected WU104 decision connection: {existing!r}')
    wf['connections'][upstream] = {'main': [[{'node': guard_name, 'type': 'main', 'index': 0}]]}
    wf['connections'][guard_name] = {'main': [[{'node': downstream, 'type': 'main', 'index': 0}]]}

    return wf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--baseline', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    wf = build(args.baseline)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(wf, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({
        'output': str(out),
        'sha256': sha256(out),
        'node_count': len(wf['nodes']),
        'connection_sources': len(wf['connections']),
        'cr': 'CR-104-05',
        'guard': 'SHORT_TRIAL_INFO_QUESTION_ONLY',
        'production_modified': False,
    }, indent=2))


if __name__ == '__main__':
    main()
