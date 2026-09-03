#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_INPUT_SHA256 = "a258d9c294fe56c43ea120b14739119f294f7254b03cbecd9f21bf7831ac8809"
EXPECTED_NODE_COUNT = 151
TARGET = "Apply WU107 Existing Handoff Result"

EXISTING_CODE_CR10702 = r"""const j=$input.first().json||{};
const d=j.wu107_queue_decision||{};
const r=d.existing_record||{};
const o={...(j.sales_agent_output||{})};
const lang=String(j.wu107_handoff_request?.requested_language||'en');
const persistedState=String(r.handoff_state||'FAILED');
const queueVerified=r.downstream_receipt_present===true;
const acceptanceVerified=Boolean(
 persistedState==='ACCEPTED' &&
 queueVerified &&
 r.downstream_acceptance_present===true
);
let effectiveState='FAILED';
let truthReconciled=false;
if(acceptanceVerified){
 effectiveState='ACCEPTED';
}else if(queueVerified && ['QUEUED','ACCEPTED'].includes(persistedState)){
 effectiveState='QUEUED';
 truthReconciled=persistedState!=='QUEUED';
}else if(persistedState==='REQUESTED'){
 effectiveState='REQUESTED';
}else if(persistedState==='CANCELLED'){
 effectiveState='CANCELLED';
}else if(persistedState==='FAILED'){
 effectiveState='FAILED';
}else{
 effectiveState='FAILED';
 truthReconciled=true;
}
const success=['QUEUED','ACCEPTED'].includes(effectiveState);
const failClosed=!success;
if(effectiveState==='ACCEPTED'){
 if(lang==='ar')o.answer_text='تم تأكيد قبول طلب الدعم من جهة بشرية مخولة.';
 else if(lang==='fr')o.answer_text='L’acceptation de votre demande d’assistance par une personne autorisée a été confirmée.';
 else o.answer_text='An authorized human acceptance of your support request has been verified.';
}else if(effectiveState==='QUEUED'){
 if(lang==='ar')o.answer_text='طلبك موجود بالفعل في قائمة الدعم. لم يتم بعد تأكيد استلامه من موظف محدد.';
 else if(lang==='fr')o.answer_text='Votre demande est déjà dans la file d’assistance. Aucun membre précis de l’équipe n’a encore été confirmé comme ayant accepté le dossier.';
 else o.answer_text='Your request is already in the support queue. A specific team member has not yet been confirmed as having accepted the case.';
}else{
 if(lang==='ar')o.answer_text='تم حفظ طلبك، لكن لا أستطيع تأكيد وضعه في قائمة الدعم الآن.';
 else if(lang==='fr')o.answer_text='Votre demande est préservée, mais je ne peux pas confirmer sa mise en file d’assistance pour le moment.';
 else o.answer_text='Your request is preserved, but I cannot confirm that it is in the support queue right now.';
}
o.purposeful_question=null;
const result={
 schema:'SPM_WU107_HANDOFF_EXECUTION_RESULT_V1',
 handoff_state:effectiveState,
 persisted_handoff_state:persistedState,
 truth_reconciled:truthReconciled,
 tool_executed:false,
 success,
 idempotency_key:r.idempotency_key||null,
 handoff_event_id:r.handoff_event_id||null,
 queue_receipt_verified:Boolean(queueVerified),
 human_acceptance_verified:Boolean(acceptanceVerified),
 provider:r.queue_provider||'STAGING_REDIS',
 reason_code:truthReconciled?'WU107_EXISTING_TRUTH_RECONCILED':`WU107_${d.decision||'EXISTING_STATE'}`
};
const action={
 ...(j.action_result||{}),
 requested_action:'human_handoff_create',
 executed:false,
 status:effectiveState==='ACCEPTED'?'WU107_HANDOFF_ALREADY_ACCEPTED':(effectiveState==='QUEUED'?'WU107_HANDOFF_ALREADY_QUEUED':'WU107_HANDOFF_NOT_CONFIRMED'),
 business_reference:r.handoff_event_id||null,
 reason_code:result.reason_code,
 irreversible_action:true,
 fail_closed:failClosed
};
return [{json:{...j,sales_agent_output:o,action_result:action,wu107_handoff_execution:result}}];"""


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    actual = digest(a.input)
    if actual != EXPECTED_INPUT_SHA256:
        raise SystemExit(f'CR10702_INPUT_SHA_FAIL:{actual}')
    d = json.loads(a.input.read_text(encoding='utf-8'))
    if len(d.get('nodes', [])) != EXPECTED_NODE_COUNT:
        raise SystemExit('CR10702_INPUT_NODE_COUNT_FAIL')
    matches = [n for n in d['nodes'] if n.get('name') == TARGET]
    if len(matches) != 1:
        raise SystemExit('CR10702_TARGET_IDENTITY_FAIL')
    node = matches[0]
    old = node.get('parameters', {}).get('jsCode', '')
    required_old = [
        "const accepted=state==='ACCEPTED'&&r.downstream_acceptance_present===true;",
        "handoff_state:accepted?'ACCEPTED':state",
        "success:['QUEUED','ACCEPTED'].includes(state)",
    ]
    for marker in required_old:
        if marker not in old:
            raise SystemExit('CR10702_UNEXPECTED_INPUT_EXISTING_CODE:' + marker)
    node['parameters']['jsCode'] = EXISTING_CODE_CR10702
    node['notes'] = (
        'CR-107-02: derive existing handoff truth from queue/acceptance evidence. '
        'An ACCEPTED label without authoritative acceptance evidence is downgraded to the strongest verified state; '
        'ACCEPTED requires both durable queue receipt and downstream acceptance evidence.'
    )
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'CR10702_INPUT_SHA256={actual}')
    print(f'CR10702_OUTPUT_SHA256={digest(a.output)}')
    print(f'CR10702_NODE_COUNT={len(d["nodes"])}')
    print('CR10702_CHANGED_WU107_NODES=1')
    print('CR10702_WU106_LOCKED_NODES_MUTATED=false')
    print('CR10702_PRODUCTION_MUTATION=false')


if __name__ == '__main__':
    main()
