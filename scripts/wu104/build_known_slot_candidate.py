#!/usr/bin/env python3
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_WRAPPER = ROOT / 'scripts' / 'wu104' / 'build_context_await_candidate.py'


def load_base_wrapper():
    spec = importlib.util.spec_from_file_location('wu104_context_wrapper_for_known_slot_fix', BASE_WRAPPER)
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

    node = node_by_name(wf, 'Persist WU104 Awaited Context Hint')
    js = node['parameters']['jsCode']

    marker = "state.journey=(state.journey&&typeof state.journey==='object')?state.journey:{};\nconst conv=(state.conversion&&typeof state.conversion==='object')?state.conversion:{};"
    replacement = r"""state.journey=(state.journey&&typeof state.journey==='object')?state.journey:{};
state.entities=(state.entities&&typeof state.entities==='object')?state.entities:{global:{},students:[]};
state.entities.students=Array.isArray(state.entities.students)?state.entities.students:[];
const ex=(j.entity_extraction&&typeof j.entity_extraction==='object')?j.entity_extraction:{};
const records=Array.isArray(ex.records)?ex.records:[];
const academicReconcile={
 schema:'SPM_WU104_KNOWN_SLOT_RECONCILE_V1',
 eligible_single_student:state.entities.students.length===1,
 subject_reconciled:false,
 grade_reconciled:false,
 skipped_multi_student:state.entities.students.length>1,
 source:'VALIDATED_CURRENT_TURN_ENTITY_RECORDS',
 raw_message_logged:false,
 raw_session_logged:false,
 secret_values_logged:false
};
function latestValid(names){
 const allowed=new Set(names);
 for(let i=records.length-1;i>=0;i--){
  const r=records[i]||{};
  if(!allowed.has(String(r.entity||'')))continue;
  if(String(r.status||'').toLowerCase()!=='valid')continue;
  if(r.canonical===undefined||r.canonical===null||r.canonical==='')continue;
  return r;
 }
 return null;
}
if(state.entities.students.length===1){
 const student=(state.entities.students[0]&&typeof state.entities.students[0]==='object')?{...state.entities.students[0]}:{};
 const subjectRec=latestValid(['subject','subjects']);
 if(subjectRec){
  const vals=(Array.isArray(subjectRec.canonical)?subjectRec.canonical:[subjectRec.canonical])
   .map(v=>String(v||'').trim()).filter(Boolean);
  if(vals.length){student.subjects=[...new Set(vals)];academicReconcile.subject_reconciled=true;}
 }
 const gradeRec=latestValid(['grade','grades']);
 if(gradeRec){
  const vals=Array.isArray(gradeRec.canonical)?gradeRec.canonical:[gradeRec.canonical];
  const grade=String(vals[0]||'').trim();
  if(grade){student.grade=grade;academicReconcile.grade_reconciled=true;}
 }
 state.entities.students[0]=student;
}
const conv=(state.conversion&&typeof state.conversion==='object')?state.conversion:{};"""
    if marker not in js:
        raise RuntimeError('CR-104-04 insertion marker not found')
    js = js.replace(marker, replacement, 1)

    old_return = "return [{json:{...j,sales_state:state,wu104_await_context_write:evidence}}];"
    new_return = "return [{json:{...j,sales_state:state,wu104_await_context_write:evidence,wu104_known_slot_reconcile:academicReconcile}}];"
    if old_return not in js:
        raise RuntimeError('CR-104-04 return marker not found')
    js = js.replace(old_return, new_return, 1)
    node['parameters']['jsCode'] = js

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
        'cr': 'CR-104-04',
        'known_slot_reconciliation': 'SINGLE_STUDENT_VALIDATED_GRADE_SUBJECT_ONLY',
        'production_modified': False,
    }, indent=2))


if __name__ == '__main__':
    main()
