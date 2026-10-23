#!/usr/bin/env python3
"""Validate evidence boundaries, disjoint recognition and class-separated totals."""
import argparse
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
import validate_candidate_advancement as advancement

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'data/portfolio/verified_benefit_ledger.json'
CLASSES = {'CASHABLE_SAVING', 'COST_AVOIDANCE', 'RECOVERY', 'NET_COST_INCREASE',
           'CAPACITY_GAIN', 'CONTROL_IMPROVEMENT', 'NO_FINANCIAL_CLAIM'}
STATES = {'SCREENING_CANDIDATE', 'VALIDATION_READY', 'OPERATIONALLY_VALIDATED',
          'FINANCIALLY_VALIDATED', 'IMPLEMENTATION_READY', 'REALIZATION_IN_PROGRESS',
          'REALIZED', 'RETAIN_CURRENT_PROCESS', 'CLOSED_INSUFFICIENT_EVIDENCE'}
MONETARY = {'CASHABLE_SAVING', 'COST_AVOIDANCE', 'RECOVERY', 'NET_COST_INCREASE'}


def monetary_amount(entry):
    """Positive benefits and adverse cost increases use mutually exclusive signs."""
    raw = entry['net_amount']
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError('finite exact-decimal string required')
    try:
        amount = Decimal(raw)
    except InvalidOperation:
        raise ValueError('finite exact-decimal string required') from None
    if not amount.is_finite():
        raise ValueError('finite exact-decimal string required')
    if entry['benefit_class'] == 'NET_COST_INCREASE':
        if amount >= 0:
            raise ValueError('NET_COST_INCREASE must be strictly negative in baseline-minus-intervention convention')
    elif amount <= 0:
        raise ValueError('saving, avoidance and recovery amounts must be strictly positive; zero is a non-benefit finding')
    return amount


def reconcile(entries):
    """No entries means unknown portfolio benefit, not a measured zero."""
    totals = {k: None for k in sorted(CLASSES)}
    headline = None
    for entry in entries:
        cls = entry['benefit_class']
        if cls in MONETARY:
            amount = monetary_amount(entry)
            totals[cls] = str(Decimal(totals[cls] or '0') + amount)
        if cls == 'CASHABLE_SAVING' and entry['candidate_state'] == 'REALIZED':
            headline = str(Decimal(headline or '0') + amount)
    return {'class_totals_usd': totals, 'headline_realized_savings_usd': headline,
            'cross_class_total': None, 'cross_class_total_status': 'PROHIBITED',
            'recognized_records': len(entries),
            'coverage_status': 'NOT_ESTIMATED' if not entries else 'PARTIAL_VERIFIED_RECORDS_ONLY'}


def validate(data):
    errors, identities, ids = [], set(), set()
    entries = data.get('entries', [])
    for index, entry in enumerate(entries):
        prefix = f'entry[{index}] '
        required = ['entry_id', 'case_id', 'benefit_class', 'candidate_state', 'state_history',
                    'cost_objects', 'period', 'currency', 'unit', 'scenario_id', 'baseline_id',
                    'counterfactual_receipt', 'financial_validation_receipt', 'operational_guardrail_receipt',
                    'reviewer_receipt', 'net_amount', 'internal_transfers_eliminated',
                    'full_system_cost_receipt', 'incrementality', 'realization_receipt',
                    'candidate_record', 'candidate_version', 'candidate_history_receipt']
        missing = [key for key in required if key not in entry]
        if missing:
            errors.append(prefix + 'missing: ' + ', '.join(missing)); continue
        if entry['entry_id'] in ids:
            errors.append(prefix + 'duplicate entry ID')
        ids.add(entry['entry_id'])
        cls, state = entry['benefit_class'], entry['candidate_state']
        if cls not in CLASSES or state not in STATES:
            errors.append(prefix + 'unknown class or candidate state'); continue
        # A list of state-name strings is not F03 gate evidence. Require the full
        # declared event/check/receipt history and validate it with F03 itself.
        record = entry['candidate_record']
        try:
            dictionary = advancement.read(advancement.DICTIONARY)
            advancement.validate_records({'schema_version': 1, 'candidates': [record]}, dictionary)
            expected_class = 'REALIZED_SAVING' if cls == 'CASHABLE_SAVING' and state == 'REALIZED' else cls
            if (record['candidate_id'] != entry['case_id'] or record['version'] != entry['candidate_version']
                    or record['current_state'] != state or record['claim_class'] != expected_class
                    or [e['state'] for e in record['history']] != entry['state_history']):
                errors.append(prefix + 'F03 candidate identity, version, claim or history disagrees with ledger')
            if cls == 'CASHABLE_SAVING' and (
                    Decimal(str(record['savings_amount'])) != monetary_amount(entry)
                    or record['currency'] != entry['currency'] or record['period'] != entry['period']):
                errors.append(prefix + 'F03 savings amount or perimeter disagrees with ledger')
            if cls in MONETARY:
                financial_events = [e for e in record['history'] if e['state'] == 'FINANCIALLY_VALIDATED']
                if not financial_events or entry['financial_validation_receipt'] not in financial_events[0]['evidence_receipts']['financial_review_receipt']:
                    errors.append(prefix + 'financial review receipt is not linked to the F03 event')
        except (ValueError, TypeError, KeyError, InvalidOperation) as exc:
            errors.append(prefix + 'invalid F03 candidate declaration: ' + str(exc))
        history_receipt = entry['candidate_history_receipt']
        if (not isinstance(history_receipt, dict)
                or any(not isinstance(history_receipt.get(key), str) or not history_receipt[key].strip()
                       for key in ['controlled_locator', 'sha256', 'reviewer', 'reviewed_at', 'scope'])
                or len(history_receipt.get('sha256', '')) != 64
                or any(c not in '0123456789abcdef' for c in history_receipt.get('sha256', ''))):
            errors.append(prefix + 'reviewed candidate-history receipt with controlled locator and SHA256 required')
        if not entry['cost_objects'] or not isinstance(entry['cost_objects'], list):
            errors.append(prefix + 'nonempty cost-object list required'); continue
        for obj in entry['cost_objects']:
            # Exclude class/scenario from identity: changing labels cannot count the same effect again.
            identity = (obj, entry['period'])
            if identity in identities:
                errors.append(prefix + 'overlapping cost object and period across class or scenario')
            identities.add(identity)
        if entry['currency'] != 'USD' or entry['unit'] != 'USD':
            errors.append(prefix + 'monetary recognition requires USD; nonmonetary units stay in separate capacity evidence')
        if cls not in MONETARY:
            if entry['net_amount'] is not None:
                errors.append(prefix + 'capacity/control/no-claim must not be monetized')
            if cls in {'CAPACITY_GAIN', 'CONTROL_IMPROVEMENT'} and (
                    'OPERATIONALLY_VALIDATED' not in entry['state_history']
                    or not entry['operational_guardrail_receipt'] or not entry['reviewer_receipt']):
                errors.append(prefix + 'verified capacity/control effect requires operational validation and review')
            continue
        try:
            monetary_amount(entry)
        except ValueError as exc:
            errors.append(prefix + str(exc))
        for field in ['baseline_id', 'scenario_id', 'counterfactual_receipt', 'operational_guardrail_receipt',
                      'reviewer_receipt', 'full_system_cost_receipt']:
            if not entry[field]:
                errors.append(prefix + field + ' missing')
        if entry['internal_transfers_eliminated'] is not True:
            errors.append(prefix + 'internal charges must be eliminated once')
        if entry['incrementality'] != 'NEW_PROJECT_EFFECT_VERIFIED':
            errors.append(prefix + 'embedded/baseline reforms excluded from new project ledger')
        if not entry['financial_validation_receipt'] or 'FINANCIALLY_VALIDATED' not in entry['state_history']:
            errors.append(prefix + 'verified monetary ledger requires substantive financial validation')
        if state not in {'FINANCIALLY_VALIDATED', 'IMPLEMENTATION_READY', 'REALIZATION_IN_PROGRESS', 'REALIZED'}:
            errors.append(prefix + 'monetary effect is not mature enough for verified recognition')
        if cls == 'CASHABLE_SAVING':
            if 'FINANCIALLY_VALIDATED' not in entry['state_history'] or not entry['financial_validation_receipt']:
                errors.append(prefix + 'savings requires actual financial-validation history and receipt')
            if state not in {'FINANCIALLY_VALIDATED', 'IMPLEMENTATION_READY', 'REALIZATION_IN_PROGRESS', 'REALIZED'}:
                errors.append(prefix + 'savings cannot be recognized at this state')
        if state == 'REALIZED' and not entry['realization_receipt']:
            errors.append(prefix + 'realized finding requires observed realization receipt')
        if cls == 'RECOVERY' and not entry['realization_receipt']:
            errors.append(prefix + 'verified recovery requires receipt/applied credit, not receivable alone')
    if not errors:
        if data.get('reconciliation') != reconcile(entries):
            errors.append('Declared totals do not reconcile to eligible class-separated entries')
    if not entries and (data.get('status') != 'EMPTY_NO_VERIFIED_BENEFITS' or data.get('portfolio_completion') != 'NOT_OPERATIONALLY_ADJUDICATED'):
        errors.append('Empty ledger cannot certify complete adjudication or measured zero')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--records', type=Path, default=TARGET)
    args = parser.parse_args()
    errors = validate(json.loads(args.records.read_text()))
    if errors:
        raise SystemExit('\n'.join(errors))
    print('Benefit ledger and class-separated reconciliation valid; empty ledger is not measured zero')


if __name__ == '__main__':
    main()
