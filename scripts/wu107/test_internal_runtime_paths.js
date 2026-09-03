#!/usr/bin/env node
const fs = require('fs');

const candidatePath = process.argv[2];
if (!candidatePath) throw new Error('candidate path required');
const wf = JSON.parse(fs.readFileSync(candidatePath, 'utf8'));
const nodes = new Map((wf.nodes || []).map(n => [n.name, n]));

const N_BUILD = 'Build WU107 Handoff Execution Request [STAGING]';
const N_DECIDE = 'Build WU107 Queue Decision';
const N_SUCCESS = 'Apply WU107 Verified Queue Result';
const N_EXISTING = 'Apply WU107 Existing Handoff Result';
const N_LOAD_FAIL = 'Build WU107 Handoff Load Failure Context';
const N_SAVE_FAIL = 'Build WU107 Handoff Save Failure Context';

function code(name) {
  const n = nodes.get(name);
  if (!n || n.type !== 'n8n-nodes-base.code') throw new Error(`missing code node: ${name}`);
  return n.parameters.jsCode;
}

function run(name, current, contexts = {}) {
  const fn = new Function('$input', '$', code(name));
  const $input = { first: () => ({ json: current }) };
  const $ = (nodeName) => ({
    first: () => {
      if (!(nodeName in contexts)) throw new Error(`missing mocked context: ${nodeName}`);
      return { json: contexts[nodeName] };
    }
  });
  const out = fn($input, $);
  if (!Array.isArray(out) || !out[0] || typeof out[0].json !== 'object') {
    throw new Error(`${name}: unexpected output`);
  }
  return out[0].json;
}

function check(cond, msg) {
  if (!cond) throw new Error(msg);
}

function containsAny(text, values) {
  return values.some(v => text.includes(v));
}

const sensitive = {
  parent: 'Sensitive Parent Name',
  student: 'Sensitive Student Name',
  phone: '+15551234567',
  email: 'sensitive.person@example.com',
  rawSession: 'RAW-CHAT-SESSION-DO-NOT-PERSIST',
  rawMessage: 'I want a human and this raw message must not persist',
  password: 'PasswordShouldNeverPersist123!',
  apiKey: 'sk-test-should-never-persist'
};

const input = {
  classification: { spm_intent: 'human_handoff', secondary_spm_intent: null, language: 'en' },
  language_hint: 'en',
  channel: 'website_chat',
  correlation_id: 'corr-fixture-only',
  session_id: sensitive.rawSession,
  raw_message: sensitive.rawMessage,
  password: sensitive.password,
  api_key: sensitive.apiKey,
  journey_decision: { stage: 'pricing' },
  sales_state: {
    analytics: { session_key: 'conv-abcdefghijklmnop' },
    entities: {
      global: {
        parent_name: sensitive.parent,
        phone: sensitive.phone,
        email: sensitive.email,
        grade: '8',
        subject: 'Math'
      },
      students: [{ name: sensitive.student, grade: '8', subject: 'Math' }]
    },
    support: { active_override: false, handoff_requested: true },
    journey: { stage: 'pricing' }
  }
};

const built = run(N_BUILD, input);
check(built.wu107_handoff_request?.execution_required === true, 'fixture did not create executable handoff request');

// RT-107-10: PII-minimized queue record using the exact decision-node JS.
const decided = run(N_DECIDE, { wu107_handoff_raw: '' }, { [N_BUILD]: built });
const record = decided.wu107_queue_decision?.record_candidate;
check(record && record.handoff_schema === 'SPM_WU107_HANDOFF_RECORD_V1', 'RT10 queue record missing');
check(record.handoff_session_key === 'conv-abcdefghijklmnop', 'RT10 pseudonymous session key mismatch');
check(record.raw_message_logged === false, 'RT10 raw_message_logged must be false');
check(record.raw_session_logged === false, 'RT10 raw_session_logged must be false');
check(record.raw_contact_logged === false, 'RT10 raw_contact_logged must be false');
check(record.secret_values_logged === false, 'RT10 secret_values_logged must be false');
check(record.customer_context_summary?.known_contact?.phone_present === true, 'RT10 phone presence boolean missing');
check(record.customer_context_summary?.known_contact?.email_present === true, 'RT10 email presence boolean missing');
const recordText = JSON.stringify(record);
check(!containsAny(recordText, Object.values(sensitive)), 'RT10 sensitive literal leaked into queue record');
for (const forbiddenKey of ['parent_name','student_name','phone','email','raw_message','raw_session_id','raw_conversation','password','api_key','token','secret','card_number','bank_account']) {
  check(!(forbiddenKey in record), `RT10 forbidden top-level field present: ${forbiddenKey}`);
}
console.log('WU107_RT10_PII_MINIMIZATION_EXECUTABLE_PASS');

// RT-107-11: a verified queue write yields QUEUED only, never human acceptance.
const queuedOut = run(N_SUCCESS, {}, { [N_DECIDE]: decided });
const queuedResult = queuedOut.wu107_handoff_execution;
check(queuedResult?.handoff_state === 'QUEUED', 'RT11 verified queue write must yield QUEUED');
check(queuedResult.queue_receipt_verified === true, 'RT11 queue receipt must be verified');
check(queuedResult.human_acceptance_verified === false, 'RT11 queue receipt must not imply human acceptance');
check(queuedOut.action_result?.status === 'WU107_HANDOFF_QUEUED', 'RT11 action status mismatch');
check(/not yet been confirmed/i.test(queuedOut.sales_agent_output?.answer_text || ''), 'RT11 customer truth wording missing');
console.log('WU107_RT11_QUEUE_RECEIPT_NOT_ACCEPTANCE_EXECUTABLE_PASS');

// Internal idempotency semantics: existing QUEUED record is reused and no new write is requested.
const existingQueuedDecision = run(
  N_DECIDE,
  { wu107_handoff_raw: JSON.stringify(record) },
  { [N_BUILD]: built }
);
check(existingQueuedDecision.wu107_queue_decision?.decision === 'EXISTING_QUEUED', 'RT02 existing queue decision mismatch');
check(existingQueuedDecision.wu107_queue_decision?.write_required === false, 'RT02 duplicate logical handoff must not request another write');
const existingQueuedOut = run(N_EXISTING, existingQueuedDecision);
check(existingQueuedOut.wu107_handoff_execution?.handoff_state === 'QUEUED', 'RT02 reused record must remain QUEUED');
check(existingQueuedOut.wu107_handoff_execution?.tool_executed === false, 'RT02 existing queue must not execute a duplicate tool write');
check(existingQueuedOut.wu107_handoff_execution?.idempotency_key === record.idempotency_key, 'RT02 idempotency key changed');
console.log('WU107_RT02_IDEMPOTENCY_EXECUTABLE_PASS');

// RT-107-12: controlled authoritative acceptance fixture.
const acceptedRecord = {
  ...record,
  handoff_state: 'ACCEPTED',
  downstream_receipt_present: true,
  downstream_acceptance_present: true,
  accepted_at: '2026-09-03T00:00:00.000Z'
};
const acceptedInput = {
  ...decided,
  wu107_queue_decision: {
    decision: 'EXISTING_ACCEPTED',
    write_required: false,
    existing_state: 'ACCEPTED',
    existing_record: acceptedRecord,
    record_candidate: record
  }
};
const acceptedOut = run(N_EXISTING, acceptedInput);
check(acceptedOut.wu107_handoff_execution?.handoff_state === 'ACCEPTED', 'RT12 verified acceptance must yield ACCEPTED');
check(acceptedOut.wu107_handoff_execution?.human_acceptance_verified === true, 'RT12 verified acceptance flag missing');
check(acceptedOut.wu107_handoff_execution?.queue_receipt_verified === true, 'RT12 accepted record must retain receipt evidence');
check(acceptedOut.wu107_handoff_execution?.success === true, 'RT12 verified acceptance must succeed');

// P0 negative fixture: an ACCEPTED label without human-acceptance evidence must be reconciled to QUEUED when queue receipt is still verified.
const fakeAcceptedRecord = {
  ...record,
  handoff_state: 'ACCEPTED',
  downstream_receipt_present: true,
  downstream_acceptance_present: false,
  accepted_at: null
};
const fakeAcceptedInput = {
  ...decided,
  wu107_queue_decision: {
    decision: 'EXISTING_ACCEPTED',
    write_required: false,
    existing_state: 'ACCEPTED',
    existing_record: fakeAcceptedRecord,
    record_candidate: record
  }
};
const fakeAcceptedOut = run(N_EXISTING, fakeAcceptedInput);
check(fakeAcceptedOut.wu107_handoff_execution?.handoff_state === 'QUEUED', 'RT12 P0: unverified ACCEPTED label must downgrade to QUEUED when receipt is verified');
check(fakeAcceptedOut.wu107_handoff_execution?.persisted_handoff_state === 'ACCEPTED', 'RT12 P0: original persisted state should remain observable');
check(fakeAcceptedOut.wu107_handoff_execution?.truth_reconciled === true, 'RT12 P0: truth reconciliation marker missing');
check(fakeAcceptedOut.wu107_handoff_execution?.queue_receipt_verified === true, 'RT12 P0: verified queue receipt lost during reconciliation');
check(fakeAcceptedOut.wu107_handoff_execution?.human_acceptance_verified === false, 'RT12 P0: false acceptance evidence');
check(fakeAcceptedOut.wu107_handoff_execution?.success === true, 'RT12 P0: verified queue state should remain successful');
check(fakeAcceptedOut.action_result?.status === 'WU107_HANDOFF_ALREADY_QUEUED', 'RT12 P0: reconciled action status must be queued');
check(fakeAcceptedOut.action_result?.fail_closed === false, 'RT12 P0: verified queue state should not be marked failed');
check(/not yet been confirmed/i.test(fakeAcceptedOut.sales_agent_output?.answer_text || ''), 'RT12 P0: reconciled customer wording must deny human acceptance');
console.log('WU107_RT12_AUTHORITATIVE_ACCEPTANCE_EXECUTABLE_PASS');

// Additional P0 fixture: ACCEPTED label with neither queue receipt nor human acceptance must fail closed.
const unsupportedAcceptedRecord = {
  ...record,
  handoff_state: 'ACCEPTED',
  downstream_receipt_present: false,
  downstream_acceptance_present: false,
  accepted_at: null
};
const unsupportedAcceptedInput = {
  ...decided,
  wu107_queue_decision: {
    decision: 'EXISTING_ACCEPTED',
    write_required: false,
    existing_state: 'ACCEPTED',
    existing_record: unsupportedAcceptedRecord,
    record_candidate: record
  }
};
const unsupportedAcceptedOut = run(N_EXISTING, unsupportedAcceptedInput);
check(unsupportedAcceptedOut.wu107_handoff_execution?.handoff_state === 'FAILED', 'RT12 P0: unsupported ACCEPTED label must fail closed');
check(unsupportedAcceptedOut.wu107_handoff_execution?.success === false, 'RT12 P0: unsupported ACCEPTED label cannot succeed');
check(unsupportedAcceptedOut.wu107_handoff_execution?.human_acceptance_verified === false, 'RT12 P0: unsupported ACCEPTED false acceptance');
check(unsupportedAcceptedOut.action_result?.fail_closed === true, 'RT12 P0: unsupported ACCEPTED must fail closed');

// RT-107-13: corrupt persisted queue record must fail closed.
const corruptDecision = run(N_DECIDE, { wu107_handoff_raw: '{not-json' }, { [N_BUILD]: built });
check(corruptDecision.wu107_queue_decision?.decision === 'CORRUPT_EXISTING_FAIL_CLOSED', 'RT13 corrupt decision mismatch');
check(corruptDecision.wu107_queue_decision?.write_required === false, 'RT13 corrupt record must not trigger blind overwrite');
const corruptOut = run(N_EXISTING, corruptDecision);
check(corruptOut.wu107_handoff_execution?.handoff_state === 'FAILED', 'RT13 corrupt record must surface FAILED');
check(corruptOut.wu107_handoff_execution?.success === false, 'RT13 corrupt record must not succeed');
check(corruptOut.wu107_handoff_execution?.human_acceptance_verified === false, 'RT13 corrupt record false acceptance');
check(corruptOut.action_result?.fail_closed === true, 'RT13 corrupt record must fail closed');
console.log('WU107_RT13_CORRUPT_RECORD_FAIL_CLOSED_EXECUTABLE_PASS');

// RT-107-14: exact Redis-load failure code path with mocked node error.
const loadFailOut = run(N_LOAD_FAIL, { error: 'SIMULATED_REDIS_LOAD_FAILURE' }, { [N_BUILD]: built });
check(loadFailOut.wu107_handoff_execution?.handoff_state === 'REQUESTED', 'RT14 load failure must preserve REQUESTED state');
check(loadFailOut.wu107_handoff_execution?.success === false, 'RT14 load failure must not succeed');
check(loadFailOut.wu107_handoff_execution?.queue_receipt_verified === false, 'RT14 load failure cannot verify queue receipt');
check(loadFailOut.wu107_handoff_execution?.human_acceptance_verified === false, 'RT14 load failure false acceptance');
check(loadFailOut.action_result?.fail_closed === true, 'RT14 load failure must fail closed');
check(/could not verify the support queue/i.test(loadFailOut.sales_agent_output?.answer_text || ''), 'RT14 truthful failure wording missing');
console.log('WU107_RT14_REDIS_LOAD_FAILURE_EXECUTABLE_PASS');

// RT-107-15: exact Redis-save failure code path with mocked node error.
const saveFailOut = run(N_SAVE_FAIL, { error: 'SIMULATED_REDIS_SAVE_FAILURE' }, { [N_DECIDE]: decided });
check(saveFailOut.wu107_handoff_execution?.handoff_state === 'REQUESTED', 'RT15 save failure must preserve REQUESTED state');
check(saveFailOut.wu107_handoff_execution?.success === false, 'RT15 save failure must not succeed');
check(saveFailOut.wu107_handoff_execution?.queue_receipt_verified === false, 'RT15 save failure cannot verify queue receipt');
check(saveFailOut.wu107_handoff_execution?.human_acceptance_verified === false, 'RT15 save failure false acceptance');
check(saveFailOut.action_result?.fail_closed === true, 'RT15 save failure must fail closed');
check(/could not place it in the support queue/i.test(saveFailOut.sales_agent_output?.answer_text || ''), 'RT15 truthful failure wording missing');
console.log('WU107_RT15_REDIS_SAVE_FAILURE_EXECUTABLE_PASS');

const report = {
  schema: 'SPM_WU107_INTERNAL_RUNTIME_PATH_CERT_V1',
  candidate_node_count: (wf.nodes || []).length,
  rt10702_idempotency: 'PASS',
  rt10710_pii_minimization: 'PASS',
  rt10711_queue_receipt_not_acceptance: 'PASS',
  rt10712_authoritative_acceptance: 'PASS',
  rt10713_corrupt_record_fail_closed: 'PASS',
  rt10714_redis_load_failure_path: 'PASS',
  rt10715_redis_save_failure_path: 'PASS',
  n8n_write_performed: false,
  raw_customer_data_emitted: false
};
fs.writeFileSync('wu107-internal-runtime-path-cert.json', JSON.stringify(report, null, 2) + '\n');
console.log('WU107_INTERNAL_RUNTIME_PATH_CERT_PASS');
