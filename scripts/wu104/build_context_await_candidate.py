#!/usr/bin/env python3
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_BUILDER = ROOT / 'scripts' / 'wu104' / 'build_candidate.py'


def load_base_builder():
    spec = importlib.util.spec_from_file_location('wu104_base_builder_for_context_fix', BASE_BUILDER)
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
    base = load_base_builder()
    wf = copy.deepcopy(base.build(baseline_path))

    # Early deterministic hint from WU90 required entities. This remains useful when
    # the journey contract already knows the next required field before response planning.
    persist_name = 'Persist WU104 Awaited Context Hint'
    persist_js = r"""const j=$input.first().json||{};
const state=(j.sales_state&&typeof j.sales_state==='object')?JSON.parse(JSON.stringify(j.sales_state)):{};
state.journey=(state.journey&&typeof state.journey==='object')?state.journey:{};
const conv=(state.conversion&&typeof state.conversion==='object')?state.conversion:{};
const registrationAwait=String(conv.awaiting_field||'').trim();
const missing=Array.isArray(j.journey_decision?.required_missing_fields)?j.journey_decision.required_missing_fields:[];
const rawFirst=String(missing[0]||'').trim().toLowerCase().replace(/[-\s]+/g,'_');
const aliases={
 grade:'grade',grade_level:'grade',student_grade:'grade',
 subject:'subject',student_subject:'subject',subjects:'subject',
 city:'location',location:'location',student_city:'location',parent_city:'location',
 day:'day',date:'day',lesson_day:'day',schedule_day:'day',scheduling_day:'day',scheduling_date:'day',
 time:'time',lesson_time:'time',schedule_time:'time',scheduling_time:'time',time_window:'time',scheduling_time_window:'time'
};
const safe=aliases[rawFirst]||null;
let status='CLEARED_NO_SUPPORTED_MISSING';
let persisted=null;
let source='WU90_REQUIRED_MISSING_FIELDS';
if(registrationAwait){
 status='REGISTRATION_AWAITING_FIELD_AUTHORITATIVE';
 persisted=registrationAwait;
 source='CONVERSION_AWAITING_FIELD';
 state.journey.awaiting_entity=registrationAwait;
}else if(safe){
 status='PERSISTED';
 persisted=safe;
 state.journey.awaiting_entity=safe;
}else{
 state.journey.awaiting_entity=null;
}
state.updated_at=new Date().toISOString();
const evidence={
 schema:'SPM_WU104_AWAIT_CONTEXT_WRITE_V1',
 status,
 persisted_entity:persisted,
 source,
 required_missing_count:missing.length,
 raw_message_logged:false,
 raw_session_logged:false,
 secret_values_logged:false
};
return [{json:{...j,sales_state:state,wu104_await_context_write:evidence}}];"""
    persist_node = {
        'id': '10400000-0000-4000-8000-000000000103',
        'name': persist_name,
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': [-79856, 6064],
        'parameters': {'jsCode': persist_js},
    }
    wf['nodes'].append(persist_node)

    upstream = 'Merge Durable Sales State + Decide Journey [WU90]'
    downstream = 'Serialize WU90 Production Sales State'
    existing = wf['connections'].get(upstream, {}).get('main', [])
    if existing != [[{'node': downstream, 'type': 'main', 'index': 0}]]:
        raise RuntimeError(f'unexpected WU90 serialization connection: {existing!r}')
    wf['connections'][upstream] = {'main': [[{'node': persist_name, 'type': 'main', 'index': 0}]]}
    wf['connections'][persist_name] = {'main': [[{'node': downstream, 'type': 'main', 'index': 0}]]}

    # Final asked-field persistence. WU92 may ask a useful discovery question even when
    # WU90 required_missing_fields is empty. Persist only a whitelisted next_field when
    # the final guarded response actually contains a question, immediately before the
    # later WU95 Redis state save. Registration awaiting_field remains authoritative.
    asked_name = 'Persist WU104 Final Asked Field'
    asked_js = r"""const j=$input.first().json||{};
const state=(j.sales_state&&typeof j.sales_state==='object')?JSON.parse(JSON.stringify(j.sales_state)):{};
state.journey=(state.journey&&typeof state.journey==='object')?state.journey:{};
const conv=(state.conversion&&typeof state.conversion==='object')?state.conversion:{};
const registrationAwait=String(conv.awaiting_field||'').trim();
const intake=(j.intake_question_candidate&&typeof j.intake_question_candidate==='object')?j.intake_question_candidate:null;
const rawField=String(intake?.next_field||'').trim().toLowerCase().replace(/[-\s]+/g,'_');
const aliases={
 grade:'grade',grade_level:'grade',student_grade:'grade',
 subject:'subject',student_subject:'subject',subjects:'subject',
 city:'location',location:'location',student_city:'location',parent_city:'location',
 day:'day',date:'day',lesson_day:'day',schedule_day:'day',scheduling_day:'day',scheduling_date:'day',
 time:'time',lesson_time:'time',schedule_time:'time',scheduling_time:'time',time_window:'time',scheduling_time_window:'time'
};
const safe=aliases[rawField]||null;
const out=(j.sales_agent_output&&typeof j.sales_agent_output==='object')?j.sales_agent_output:{};
const purposeful=String(out.purposeful_question||'').trim();
const answer=String(out.answer_text||'');
const questionPresent=Boolean(purposeful)||/[?؟]/u.test(answer);
let status='CLEARED_NO_FINAL_QUESTION';
let persisted=null;
let source='FINAL_RESPONSE_NO_QUESTION';
if(registrationAwait){
 status='REGISTRATION_AWAITING_FIELD_AUTHORITATIVE';
 persisted=registrationAwait;
 source='CONVERSION_AWAITING_FIELD';
 state.journey.awaiting_entity=registrationAwait;
}else if(questionPresent&&safe){
 status='PERSISTED_FROM_FINAL_QUESTION';
 persisted=safe;
 source='WU92_INTAKE_NEXT_FIELD';
 state.journey.awaiting_entity=safe;
}else{
 state.journey.awaiting_entity=null;
 if(questionPresent&&!safe){status='QUESTION_PRESENT_NO_SAFE_FIELD';source='NO_WHITELISTED_NEXT_FIELD';}
}
state.updated_at=new Date().toISOString();
const evidence={
 schema:'SPM_WU104_FINAL_ASKED_FIELD_WRITE_V1',
 status,
 persisted_entity:persisted,
 source,
 question_present:questionPresent,
 intake_next_field_present:Boolean(rawField),
 raw_message_logged:false,
 raw_session_logged:false,
 secret_values_logged:false
};
return [{json:{...j,sales_state:state,wu104_final_asked_field_write:evidence}}];"""
    asked_node = {
        'id': '10400000-0000-4000-8000-000000000104',
        'name': asked_name,
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': [-69456, 6064],
        'parameters': {'jsCode': asked_js},
    }
    wf['nodes'].append(asked_node)

    final_upstream = 'Apply WU97 Fail-Closed Privacy Security Guard'
    final_downstream = 'Serialize WU95 Production Sales State'
    final_existing = wf['connections'].get(final_upstream, {}).get('main', [])
    if final_existing != [[{'node': final_downstream, 'type': 'main', 'index': 0}]]:
        raise RuntimeError(f'unexpected final WU95 serialization connection: {final_existing!r}')
    wf['connections'][final_upstream] = {'main': [[{'node': asked_name, 'type': 'main', 'index': 0}]]}
    wf['connections'][asked_name] = {'main': [[{'node': final_downstream, 'type': 'main', 'index': 0}]]}

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
        'cr': 'CR-104-02',
        'production_modified': False,
    }, indent=2))


if __name__ == '__main__':
    main()
