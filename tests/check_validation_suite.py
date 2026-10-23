#!/usr/bin/env python3
"""Synthetic runner tests plus archived-command parity; no network or R execution."""
import copy
import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import run_validation_suite as v


class SuiteTests(unittest.TestCase):
    def test_plan_structure(self):
        self.assertEqual(v.check_plan(v.read_plan(), require_paths=False)['groups'], 8)

    def test_archived_command_population_is_exhaustive(self):
        with v.PARITY.open(newline='') as f:
            rows = list(csv.DictReader(f))
        indexed = {(r['old_workflow'], r['old_job'], int(r['old_step'])): r['old_run'] for r in rows}
        expected = {}
        for name in ('validate.yml','v8_validate.yml','v9_checks.yml','v10_protocol_ci.yml',
                     'v11_validate.yml','foundation_standards.yml','census_v6.yml','v8_source_capture.yml'):
            path = '.github/workflows/' + name
            data = yaml.load((ROOT / 'history/pre_controls' / path).read_text(), Loader=yaml.BaseLoader)
            for job, body in data['jobs'].items():
                for ix, step in enumerate(body['steps'], 1):
                    if 'run' in step:
                        expected[(path,job,ix)] = step['run']
        self.assertEqual(indexed, expected)

    def test_missing_legacy_step_is_rejected(self):
        p = v.read_plan()
        p['groups']['baseline']['steps'].pop()
        with self.assertRaises(ValueError):
            v.check_plan(p, require_paths=False)

    def test_changed_flags_are_rejected(self):
        p = v.read_plan()
        p['groups']['v8']['steps'][1]['run'] = 'python tests/check_v8_pilot.py'
        with self.assertRaises(ValueError):
            v.check_plan(p, require_paths=False)

    def test_dynamic_yaml_replay_is_rejected(self):
        p = v.read_plan()
        p['groups']['baseline']['steps'][0]['run'] = 'python -c "yaml.safe_load(text)"'
        with self.assertRaises(ValueError):
            v.check_plan(p, require_paths=False)

    def test_publication_and_dependency_install_are_rejected(self):
        for cmd in ('git push origin main', 'python -m pip install x==1'):
            p = v.read_plan()
            p['groups']['baseline']['steps'][0]['run'] = cmd
            with self.assertRaises(ValueError):
                v.check_plan(p, require_paths=False)

    def test_unpinned_package_is_rejected(self):
        p = v.read_plan()
        p['groups']['baseline']['python_packages'] = ['PyMuPDF']
        with self.assertRaises(ValueError):
            v.check_plan(p, require_paths=False)

    def test_manual_capture_commands_retained_and_never_in_runner(self):
        p = v.read_plan()
        all_runs = '\n'.join(s['run'] for g in p['groups'].values() for s in g['steps'])
        self.assertNotIn('collect_census_v6_sources.py', all_runs)
        self.assertNotIn('urlopen(', all_runs)
        for name in ('census_v6.yml', 'v8_source_capture.yml'):
            old = yaml.load((ROOT/'history/pre_controls/.github/workflows'/name).read_text(), Loader=yaml.BaseLoader)
            new = yaml.load((ROOT/'.github/workflows'/name).read_text(), Loader=yaml.BaseLoader)
            self.assertEqual(set(new['on']), {'workflow_dispatch'})
            old_runs=[s['run'] for j in old['jobs'].values() for s in j['steps'] if 'run' in s]
            new_runs=[s['run'] for j in new['jobs'].values() for s in j['steps'] if 'run' in s]
            self.assertEqual(new_runs, old_runs)

    def test_six_adapters_are_read_only_with_same_job_ids(self):
        names={'validate.yml':'baseline','v8_validate.yml':'v8','v9_checks.yml':'v9',
               'v10_protocol_ci.yml':'v10','v11_validate.yml':'v11','foundation_standards.yml':'foundation'}
        for name, group in names.items():
            old=yaml.load((ROOT/'history/pre_controls/.github/workflows'/name).read_text(), Loader=yaml.BaseLoader)
            new=yaml.load((ROOT/'.github/workflows'/name).read_text(), Loader=yaml.BaseLoader)
            self.assertEqual(new['name'],old['name'])
            self.assertEqual(new['permissions'],{'contents':'read'})
            for job in old['jobs']:
                self.assertEqual(new['jobs'][job]['with']['group'],group)
                self.assertEqual(new['jobs'][job]['uses'],'./.github/workflows/reusable_validation.yml')

    def test_reusable_checkout_does_not_persist_credentials(self):
        data=yaml.load((ROOT/'.github/workflows/reusable_validation.yml').read_text(),Loader=yaml.BaseLoader)
        checkout=data['jobs']['validate']['steps'][0]
        self.assertEqual(checkout['with']['persist-credentials'],'false')
        self.assertEqual(data['permissions'],{'contents':'read'})

    def test_retained_whitepaper_runs_original_guard_in_isolated_baseline(self):
        group=v.read_plan()['groups']['retained-whitepaper']
        self.assertIn('python-docx==1.2.0',group['python_packages'])
        body=group['steps'][0]['run']
        self.assertIn("baseline='32f02e5e689ad9f43e762d5985330df20dda1719'",body)
        self.assertIn("['git','archive',baseline]",body)
        self.assertIn("filter='data'",body)
        self.assertIn("reports/white_paper_2026-10-15/validate.py",body)
        self.assertIn('TemporaryDirectory',body)
        self.assertIn('GIT_ALTERNATE_OBJECT_DIRECTORIES',body)
        self.assertIn("GIT_INDEX_FILE=str(Path(directory)/'.git/index')",body)

    def test_dependency_failure_blocks_execution(self):
        with mock.patch.object(v.shutil,'which',return_value=None):
            with self.assertRaises(ValueError):
                v.preflight({'requires_r':True,'python_packages':[]})

    def test_dirty_checkout_cannot_issue_commit_bound_pass(self):
        with mock.patch.object(v.subprocess,'check_output',return_value=b' M README.md\n'):
            with self.assertRaises(ValueError):
                v.require_clean_checkout(ROOT)

    def test_untracked_validation_controls_cannot_issue_commit_bound_pass(self):
        with mock.patch.object(v.subprocess,'check_output',return_value=b''), \
             mock.patch.object(v.subprocess,'run',return_value=subprocess.CompletedProcess([],1)):
            with self.assertRaises(ValueError):
                v.require_clean_checkout(ROOT)

    def test_untracked_helper_cannot_shadow_committed_inputs(self):
        with mock.patch.object(v.subprocess,'check_output',return_value=b'?? scripts/untracked_helper.py\n') as command:
            with self.assertRaises(ValueError):
                v.require_clean_checkout(ROOT)
        self.assertNotIn('--untracked-files=no',command.call_args.args[0])

    def test_fail_fast_receipt_does_not_mark_unrun_steps_passed(self):
        definition={'steps':[{'id':'one','name':'one','run':'SYNTHETIC one'},
                             {'id':'two','name':'two','run':'SYNTHETIC two'}]}
        fake=mock.Mock(return_value=subprocess.CompletedProcess([],1))
        with mock.patch.object(v,'require_clean_checkout'), mock.patch.object(v,'preflight'), mock.patch.object(v,'tracked_hashes',return_value={}):
            result=v.execute_group('synthetic',definition,run=fake)
        self.assertEqual(result['status'],'FAIL')
        self.assertEqual(result['passed_steps'],0)
        self.assertEqual(fake.call_count,1)

    def test_successful_commands_cannot_hide_tracked_mutation(self):
        definition={'steps':[{'id':'one','name':'one','run':'SYNTHETIC'}]}
        fake=mock.Mock(return_value=subprocess.CompletedProcess([],0))
        with mock.patch.object(v,'require_clean_checkout'), mock.patch.object(v,'preflight'), mock.patch.object(v,'tracked_hashes',side_effect=[{'a':'old'},{'a':'new'}]):
            result=v.execute_group('synthetic',definition,run=fake)
        self.assertEqual(result['status'],'FAIL_TRACKED_MUTATION')
        self.assertEqual(result['changed_tracked_files'],['a'])


if __name__=='__main__':
    unittest.main()
