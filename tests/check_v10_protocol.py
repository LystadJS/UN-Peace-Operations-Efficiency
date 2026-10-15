#!/usr/bin/env python3
"""V10 source-scope and corruption controls. All mutations are temporary fixtures."""
from pathlib import Path
import copy
import importlib.util
import json
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('v10',ROOT/'scripts/build_v10_protocol.py')
v10=importlib.util.module_from_spec(spec);spec.loader.exec_module(v10)

class ProtocolChecks(unittest.TestCase):
    def test_01_retained_package(self):
        self.assertEqual(v10.validate()['status'],'PASS_protocol_integrity_and_closed_live_gates')
    def test_02_exact_obligations_not_source_inflation(self):
        rows=v10.read_csv(v10.OUT/'product_obligations.csv')
        self.assertEqual(len(rows),61)
        self.assertFalse(any(r['observation_id'] in ['V8:O01','V8:O02','V8:O03'] for r in rows))
    def test_03_complete_component_namespaces(self):
        rows=v10.read_csv(v10.OUT/'component_scope.csv')
        self.assertEqual({r['component_id'] for r in rows},
            {f'V8:P{i:02}' for i in range(1,11)}|{f'V9:K{i:02}' for i in range(1,16)})
    def test_04_source_conflicts_inequality_attribution(self):
        rows={r['observation_id']:r for r in v10.read_csv(v10.OUT/'fixed_source_scope.csv')}
        value=lambda x:json.loads(rows[x]['qualified_values'])
        self.assertEqual(value('V8:O04')['event_start'],'2025-01-28')
        self.assertEqual(value('V8:O15')['event_start'],'2025-01-27')
        self.assertEqual(value('V8:O03')['attendance_comparator'],'>')
        self.assertEqual(value('V9:CY009')['exports_eur_billion'],4.12)
        self.assertEqual(value('V9:CY010')['exports_eur_billion'],2.14)
        self.assertFalse(value('V9:CY018')['secretariat_endorsement'])
        self.assertIsNone(value('V9:CY036')['actual_completion_date'])
    def test_05_empty_instruments(self):
        for name in v10.TEMPLATES:self.assertEqual(v10.read_csv(v10.OUT/'templates'/name),[])
    def test_06_case_local_gates_closed(self):
        for case,cfg in v10.protocol()['case_activation'].items():
            self.assertEqual(v10.activation_status(cfg)['status'],'BLOCKED_FOR_LIVE_USE')
    def test_07_machine_completeness_is_not_authority(self):
        cfg={k:'SYNTHETIC_RECEIPT' for k in v10.REQUIRED_ACTIVATION}
        cfg.update(additional_person_minute_ceiling=60,deadline_safety_buffer_minutes=30)
        ans=v10.activation_status(cfg)
        self.assertFalse(ans['live_execution_authorized'])
        self.assertFalse(ans['institutional_authority_verified'])
    def test_08_invalid_ceiling_is_not_zero_allowance(self):
        for bad in [0,-1,'0',True]:
            cfg={k:'SYNTHETIC' for k in v10.REQUIRED_ACTIVATION}
            cfg.update(additional_person_minute_ceiling=bad,deadline_safety_buffer_minutes=30)
            self.assertEqual(v10.activation_status(cfg)['status'],'BLOCKED_FOR_LIVE_USE')
    def test_09_mutation_regression(self):
        mutations=[
          ('protocol.json',lambda b:b.replace(b'paused_no_checks_run',b'active')),
          ('protocol.json',lambda b:b.replace(b'not_estimated',b'1000_saved')),
          ('product_obligations.csv',lambda b:b.replace(b'OB:V8:O04',b'OB:V8:O01')),
          ('fixed_source_scope.csv',lambda b:b.replace(b'2025-01-28',b'2025-01-27')),
          ('fixed_source_scope.csv',lambda b:b.replace(b'4.12',b'2.14')),
          ('component_scope.csv',lambda b:b.replace(b'V9:K12',b'V9:K99')),
          ('templates/workload.csv',lambda b:b+b'SYNTHETIC_FORBIDDEN_ROW\n'),
        ]
        import shutil
        original=v10.OUT
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/'data';shutil.copytree(original,dest)
            for file,mutation in mutations:
                target=dest/file;baseline=target.read_bytes();target.write_bytes(mutation(baseline));v10.OUT=dest
                try:
                    with self.subTest(file=file):
                        with self.assertRaises((AssertionError,KeyError,ValueError)):v10.validate()
                finally:target.write_bytes(baseline);v10.OUT=original
    def test_10_scenarios_reference_only_registered_observations(self):
        ids={r['observation_id'] for r in v10.read_csv(v10.OUT/'fixed_source_scope.csv')}
        for r in v10.scenario_cards():
            self.assertTrue(set(filter(None,r['reference_observations'].split(';'))) <= ids)
    def test_11_deterministic_scope(self):
        d=v10.load_designs();self.assertEqual(v10.derive_registers(d),v10.derive_registers(copy.deepcopy(d)))
    def test_12_reference_counts_are_not_trial_results(self):
        p=v10.protocol();self.assertEqual(p['safeguards']['live_measurements'],'none')
        self.assertFalse(p['safeguards']['automatic_start'])
        self.assertFalse(p['safeguards']['protected_data_in_public_repo'])
        self.assertEqual(p['comparison']['randomization'],'not_implemented')

if __name__=='__main__':unittest.main(verbosity=2)
