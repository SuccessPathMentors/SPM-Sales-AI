#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_BASE_SHA = "2e219adbdd612106b782993cbcb2f94da6c0737b250264060b473f12f0fcc81f"
EXPECTED_BASE_NODES = 141
EXPECTED_CANDIDATE_NODES = 151
GATEWAY = "Deterministic Action Gateway [RC3 SCOPE LOCK]"
TELEMETRY = "Build Telemetry Envelope"
BUILD = "Build WU107 Handoff Execution Request [STAGING]"
IF_EXEC = "Is WU107 Handoff Execution Required?"
LOAD = "Load WU107 Handoff Record [STAGING]"
DECIDE = "Build WU107 Queue Decision"
IF_WRITE = "Is WU107 Queue Write Required?"
SAVE = "Save WU107 Handoff Record [STAGING]"
SUCCESS = "Apply WU107 Verified Queue Result"
EXISTING = "Apply WU107 Existing Handoff Result"
LOAD_FAIL = "Build WU107 Handoff Load Failure Context"
SAVE_FAIL = "Build WU107 Handoff Save Failure Context"
NEW = {BUILD,IF_EXEC,LOAD,DECIDE,IF_WRITE,SAVE,SUCCESS,EXISTING,LOAD_FAIL,SAVE_FAIL}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def target_names(conns, name, output=0):
    main=conns.get(name,{}).get('main',[])
    if output>=len(main): return []
    return [x.get('node') for x in main[output]]


def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',required=True);p.add_argument('--candidate',required=True);a=p.parse_args()
    if sha(a.baseline)!=EXPECTED_BASE_SHA: raise SystemExit('WU107_TEST_BASE_SHA_FAIL')
    base=json.loads(Path(a.baseline).read_text()); cand=json.loads(Path(a.candidate).read_text())
    if len(base.get('nodes',[]))!=EXPECTED_BASE_NODES: raise SystemExit('WU107_BASE_NODE_COUNT_FAIL')
    if len(cand.get('nodes',[]))!=EXPECTED_CANDIDATE_NODES: raise SystemExit('WU107_CANDIDATE_NODE_COUNT_FAIL')
    if cand.get('active') is not False: raise SystemExit('WU107_CANDIDATE_MUST_BE_INACTIVE')
    if cand.get('name')!='[STAGING] SPM_WU107_HUMAN_HANDOFF_EXECUTION_V1': raise SystemExit('WU107_NAME_FAIL')

    bmap={n['name']:n for n in base['nodes']}; cmap={n['name']:n for n in cand['nodes']}
    missing=set(bmap)-set(cmap)
    if missing: raise SystemExit('WU107_REMOVED_LOCKED_NODES:'+','.join(sorted(missing)))
    for name,node in bmap.items():
        if cmap[name]!=node: raise SystemExit('WU107_MUTATED_LOCKED_NODE:'+name)
    if set(cmap)-set(bmap)!=NEW: raise SystemExit('WU107_NEW_NODE_SET_FAIL')

    # Locked gateway remains unchanged and still records upstream exclusion.
    gateway_code=cmap[GATEWAY]['parameters']['jsCode']
    for marker in ["human_handoff_execution:'EXCLUDED'","RC3_HUMAN_HANDOFF_EXECUTION_EXCLUDED","human_handoff_enabled:false"]:
        if marker not in gateway_code: raise SystemExit('WU107_LOCKED_GATEWAY_MARKER_MISSING:'+marker)

    conns=cand['connections']
    if target_names(conns,GATEWAY)!=[BUILD]: raise SystemExit('WU107_GATEWAY_INSERTION_FAIL')
    if target_names(conns,BUILD)!=[IF_EXEC]: raise SystemExit('WU107_BUILD_ROUTE_FAIL')
    if target_names(conns,IF_EXEC,0)!=[LOAD] or target_names(conns,IF_EXEC,1)!=[TELEMETRY]: raise SystemExit('WU107_EXEC_BYPASS_FAIL')
    if target_names(conns,LOAD,0)!=[DECIDE] or target_names(conns,LOAD,1)!=[LOAD_FAIL]: raise SystemExit('WU107_LOAD_PATH_FAIL')
    if target_names(conns,DECIDE)!=[IF_WRITE]: raise SystemExit('WU107_DECISION_PATH_FAIL')
    if target_names(conns,IF_WRITE,0)!=[SAVE] or target_names(conns,IF_WRITE,1)!=[EXISTING]: raise SystemExit('WU107_WRITE_BRANCH_FAIL')
    if target_names(conns,SAVE,0)!=[SUCCESS] or target_names(conns,SAVE,1)!=[SAVE_FAIL]: raise SystemExit('WU107_SAVE_BRANCH_FAIL')
    for name in [SUCCESS,EXISTING,LOAD_FAIL,SAVE_FAIL]:
        if target_names(conns,name)!=[TELEMETRY]: raise SystemExit('WU107_TELEMETRY_REJOIN_FAIL:'+name)

    # Redis isolation and credential inheritance.
    redis_ref=bmap['Load Sales State [STAGING NAMESPACE]']['credentials']['redis']
    for name in [LOAD,SAVE]:
        node=cmap[name]
        if node.get('type')!='n8n-nodes-base.redis': raise SystemExit('WU107_NON_REDIS_ADAPTER:'+name)
        if node.get('credentials',{}).get('redis')!=redis_ref: raise SystemExit('WU107_REDIS_CREDENTIAL_DRIFT:'+name)
        if node.get('retryOnFail') is not True or int(node.get('maxTries',0))!=3: raise SystemExit('WU107_RETRY_POLICY_FAIL:'+name)
        if node.get('onError')!='continueErrorOutput': raise SystemExit('WU107_ERROR_PATH_FAIL:'+name)
    if 'spm:staging:handoff:' not in cmap[BUILD]['parameters']['jsCode']: raise SystemExit('WU107_NAMESPACE_FAIL')

    # PII/minimum-context hard stops.
    build_code=cmap[BUILD]['parameters']['jsCode']
    for forbidden in ['j.session_id','raw_conversation','card_number','bank_account','password','api_key']:
        if forbidden in build_code: raise SystemExit('WU107_PII_OR_SECRET_CONTRACT_FAIL:'+forbidden)
    decide_code=cmap[DECIDE]['parameters']['jsCode']
    for forbidden in ['parent_name','student_name','phone:', 'email:', 'raw_message:','raw_session_id']:
        if forbidden in decide_code: raise SystemExit('WU107_QUEUE_RECORD_PII_FAIL:'+forbidden)

    # Queue write truth cannot become human acceptance.
    success=cmap[SUCCESS]['parameters']['jsCode']
    if "handoff_state:'QUEUED'" not in success: raise SystemExit('WU107_SUCCESS_NOT_QUEUED')
    if 'human_acceptance_verified:false' not in success: raise SystemExit('WU107_FALSE_ACCEPTANCE_RISK')
    if 'WU107_VERIFIED_QUEUE_WRITE' not in success: raise SystemExit('WU107_TOOL_EVIDENCE_MARKER_MISSING')
    if 'A specific team member has not yet been confirmed' not in success: raise SystemExit('WU107_CUSTOMER_TRUTH_TEXT_MISSING')

    existing=cmap[EXISTING]['parameters']['jsCode']
    if "state==='ACCEPTED'&&r.downstream_acceptance_present===true" not in existing: raise SystemExit('WU107_ACCEPTANCE_EVIDENCE_GATE_FAIL')

    # No WU-108/WhatsApp/HTTP/Sheets adapter added in WU-107.
    new_nodes=[cmap[x] for x in NEW]
    forbidden_types={'n8n-nodes-base.googleSheets','n8n-nodes-base.httpRequest','n8n-nodes-base.whatsApp'}
    if any(n.get('type') in forbidden_types for n in new_nodes): raise SystemExit('WU107_OUT_OF_SCOPE_ADAPTER_ADDED')
    text=json.dumps(new_nodes,ensure_ascii=False)
    if 'CMBMpxX5AqqK2UTn' in text or 'spm:production:' in text: raise SystemExit('WU107_PRODUCTION_REFERENCE_FAIL')

    print('WU107_CANDIDATE_STATIC_PASS')
    print('locked_nodes_unchanged=141 new_nodes=10 candidate_nodes=151 redis_isolated=PASS acceptance_truth=PASS')

if __name__=='__main__': main()
