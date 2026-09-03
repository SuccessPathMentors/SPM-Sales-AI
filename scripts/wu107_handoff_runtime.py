#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import Dict, Optional

TERMINAL = {'ACCEPTED', 'FAILED', 'CANCELLED'}
RETRYABLE = {'TIMEOUT', 'RATE_LIMIT', 'TRANSIENT_5XX'}
NON_RETRYABLE = {'AUTHORIZATION', 'VALIDATION', 'POLICY_REJECTED'}

@dataclass
class ProviderResult:
    result: str  # accepted_for_queue | failed
    receipt_id: Optional[str] = None
    human_acceptance_id: Optional[str] = None
    failure_class: Optional[str] = None

@dataclass
class HandoffRecord:
    idempotency_key: str
    state: str = 'REQUESTED'
    attempt_count: int = 0
    receipt_id: Optional[str] = None
    human_acceptance_id: Optional[str] = None
    failure_class: Optional[str] = None
    events: list = field(default_factory=list)

    @property
    def may_claim_human_received(self) -> bool:
        return self.state == 'ACCEPTED' and bool(self.human_acceptance_id)

class HandoffStore:
    def __init__(self):
        self.records: Dict[str, HandoffRecord] = {}
        self.created_count = 0

    def get_or_create(self, key: str) -> HandoffRecord:
        if key in self.records:
            return self.records[key]
        rec = HandoffRecord(idempotency_key=key)
        rec.events.append('REQUESTED')
        self.records[key] = rec
        self.created_count += 1
        return rec

class HandoffExecutor:
    MAX_ATTEMPTS = 3

    def __init__(self, store: HandoffStore):
        self.store = store

    def execute(self, key: str, provider_result: ProviderResult) -> HandoffRecord:
        rec = self.store.get_or_create(key)
        if rec.state in TERMINAL:
            return rec

        rec.attempt_count += 1

        if provider_result.result == 'accepted_for_queue':
            if not provider_result.receipt_id:
                rec.state = 'FAILED'
                rec.failure_class = 'VALIDATION'
                rec.events.append('FAILED:missing_receipt')
                return rec

            rec.receipt_id = provider_result.receipt_id
            rec.state = 'QUEUED'
            rec.events.append('QUEUED')

            # Queue receipt is explicitly NOT human acceptance.
            if provider_result.human_acceptance_id:
                rec.human_acceptance_id = provider_result.human_acceptance_id
                rec.state = 'ACCEPTED'
                rec.events.append('ACCEPTED')
            return rec

        if provider_result.result != 'failed':
            rec.state = 'FAILED'
            rec.failure_class = 'VALIDATION'
            rec.events.append('FAILED:unknown_provider_result')
            return rec

        failure_class = provider_result.failure_class or 'VALIDATION'
        rec.failure_class = failure_class

        if failure_class in RETRYABLE and rec.attempt_count < self.MAX_ATTEMPTS:
            rec.state = 'REQUESTED'
            rec.events.append(f'RETRYABLE:{failure_class}')
            return rec

        rec.state = 'FAILED'
        rec.events.append(f'FAILED:{failure_class}')
        return rec

    def accept_human(self, key: str, acceptance_id: str) -> HandoffRecord:
        rec = self.store.records[key]
        if rec.state != 'QUEUED' or not rec.receipt_id:
            raise ValueError('Human acceptance requires verified QUEUED state and receipt')
        if not acceptance_id:
            raise ValueError('Acceptance evidence required')
        rec.human_acceptance_id = acceptance_id
        rec.state = 'ACCEPTED'
        rec.events.append('ACCEPTED')
        return rec

    def cancel(self, key: str) -> HandoffRecord:
        rec = self.store.records[key]
        if rec.state not in {'REQUESTED', 'QUEUED'}:
            return rec
        rec.state = 'CANCELLED'
        rec.events.append('CANCELLED')
        return rec
