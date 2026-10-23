#!/usr/bin/env python3
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate_benefit_ledger import TARGET, validate, reconcile
import validate_candidate_advancement as advancement


def synthetic_entry():
    dictionary = advancement.read(advancement.DICTIONARY)
    states = ['SCREENING_CANDIDATE', 'VALIDATION_READY', 'OPERATIONALLY_VALIDATED',
              'FINANCIALLY_VALIDATED', 'IMPLEMENTATION_READY', 'REALIZATION_IN_PROGRESS', 'REALIZED']
    history = []
    for index, state in enumerate(states):
        checks = dictionary['states'][state]['requires']
        history.append({'state': state, 'recorded_at': f'2026-10-23T00:{index:02}:00Z',
                        'evidence_cutoff': '2026-10-22', 'actor': 'SYNTHETIC',
                        'rationale': 'Synthetic structural test only; no institutional finding',
                        'validator_version': '1.0', 'checks': dict.fromkeys(checks, True),
                        'evidence_receipts': {c: ['SYNTHETIC'] for c in checks}})
    return {'entry_id': 'SYNTHETIC', 'case_id': 'SYNTHETIC', 'benefit_class': 'CASHABLE_SAVING',
            'candidate_state': 'REALIZED', 'state_history': states,
            'candidate_version': '1',
            'candidate_record': {'candidate_id': 'SYNTHETIC', 'version': '1', 'current_state': 'REALIZED',
                                 'claim_class': 'REALIZED_SAVING', 'savings_amount': 1.25,
                                 'currency': 'USD', 'period': 'SYNTHETIC-PERIOD', 'history': history},
            'candidate_history_receipt': {'controlled_locator': 'SYNTHETIC', 'sha256': '0' * 64,
                                          'reviewer': 'SYNTHETIC', 'reviewed_at': '2026-10-23T00:08:00Z',
                                          'scope': 'Synthetic declaration only'},
            'cost_objects': ['SYNTHETIC-OBJECT'], 'period': 'SYNTHETIC-PERIOD', 'currency': 'USD', 'unit': 'USD',
            'scenario_id': 'SYNTHETIC', 'baseline_id': 'SYNTHETIC', 'counterfactual_receipt': 'SYNTHETIC',
            'financial_validation_receipt': 'SYNTHETIC', 'operational_guardrail_receipt': 'SYNTHETIC',
            'reviewer_receipt': 'SYNTHETIC', 'net_amount': '1.25', 'internal_transfers_eliminated': True,
            'full_system_cost_receipt': 'SYNTHETIC', 'incrementality': 'NEW_PROJECT_EFFECT_VERIFIED',
            'realization_receipt': 'SYNTHETIC'}


class LedgerChecks(unittest.TestCase):
    def base(self, entries=None):
        data = json.loads(TARGET.read_text())
        if entries is not None:
            data['entries'] = entries
            try:
                data['reconciliation'] = reconcile(entries)
            except ValueError:
                pass  # Deliberately invalid amount must be reported by validate.
        return data

    def test_actual_empty_unknown(self):
        data = self.base()
        self.assertEqual(validate(data), [])
        self.assertIsNone(data['reconciliation']['headline_realized_savings_usd'])

    def test_empty_zero_rejected(self):
        data = self.base(); data['reconciliation']['headline_realized_savings_usd'] = '0'
        self.assertTrue(validate(data))

    def test_early_savings_rejected(self):
        row = synthetic_entry(); row['state_history'] = []; row['candidate_state'] = 'SCREENING_CANDIDATE'
        self.assertTrue(validate(self.base([row])))

    def test_duplicate_object_across_classes_rejected(self):
        one = synthetic_entry(); two = copy.deepcopy(one)
        two.update(entry_id='SECOND', benefit_class='RECOVERY')
        self.assertTrue(validate(self.base([one, two])))

    def test_internal_charge_rejected(self):
        row = synthetic_entry(); row['internal_transfers_eliminated'] = False
        self.assertTrue(validate(self.base([row])))

    def test_embedded_reform_rejected(self):
        row = synthetic_entry(); row['incrementality'] = 'ALREADY_EMBEDDED'
        self.assertTrue(validate(self.base([row])))

    def test_realization_receipt_required(self):
        row = synthetic_entry(); row['realization_receipt'] = None
        self.assertTrue(validate(self.base([row])))

    def test_avoidance_cannot_bypass_financial_validation(self):
        row = synthetic_entry(); row.update(benefit_class='COST_AVOIDANCE', state_history=[], financial_validation_receipt=None)
        self.assertTrue(validate(self.base([row])))

    def test_capacity_not_monetized(self):
        row = synthetic_entry(); row.update(benefit_class='CAPACITY_GAIN', state_history=['OPERATIONALLY_VALIDATED'])
        self.assertTrue(validate(self.base([row])))

    def test_exact_decimal_reconciliation(self):
        one = synthetic_entry(); two = copy.deepcopy(one)
        two.update(entry_id='SECOND', cost_objects=['OTHER'], net_amount='0.10')
        two['candidate_record']['savings_amount'] = 0.10
        data = self.base([one, two])
        self.assertEqual(validate(data), [])
        self.assertEqual(data['reconciliation']['headline_realized_savings_usd'], '1.35')

    def test_positive_classes_reject_zero_negative_and_nonfinite(self):
        for cls in ['CASHABLE_SAVING', 'RECOVERY', 'COST_AVOIDANCE']:
            for amount in ['-10', '0', '-0', 'NaN', 'Infinity', '-Infinity', '', 1.25]:
                with self.subTest(cls=cls, amount=amount):
                    row = synthetic_entry(); row.update(benefit_class=cls, net_amount=amount)
                    errors = validate(self.base([row]))
                    self.assertTrue(any('strictly positive' in e or 'finite exact-decimal' in e for e in errors))
                    with self.assertRaises(ValueError):
                        reconcile([row])

    def test_adverse_class_sign_and_no_headline(self):
        row = synthetic_entry(); row.update(benefit_class='NET_COST_INCREASE', net_amount='-10')
        row['candidate_record'].update(claim_class='NET_COST_INCREASE', savings_amount=None, currency=None, period=None)
        data = self.base([row])
        self.assertEqual(validate(data), [])
        self.assertEqual(data['reconciliation']['class_totals_usd']['NET_COST_INCREASE'], '-10')
        self.assertIsNone(data['reconciliation']['headline_realized_savings_usd'])
        for amount in ['0', '10']:
            row['net_amount'] = amount
            self.assertTrue(any('strictly negative' in e for e in validate(self.base([row]))))

    def test_state_strings_without_f03_record_rejected(self):
        row = synthetic_entry(); row['candidate_record'] = None
        self.assertTrue(any('invalid F03' in e for e in validate(self.base([row]))))

    def test_skipped_or_unreceipted_f03_gate_rejected(self):
        for mutation in ['skip', 'receipt', 'review']:
            row = synthetic_entry()
            if mutation == 'skip':
                del row['candidate_record']['history'][2]
            elif mutation == 'receipt':
                row['candidate_record']['history'][3]['evidence_receipts']['financial_review_receipt'] = ['OTHER']
            else:
                row['candidate_history_receipt'] = 'A_STATE_NAME_IS_NOT_A_REVIEW_RECEIPT'
            self.assertTrue(validate(self.base([row])))


if __name__ == '__main__':
    unittest.main()
