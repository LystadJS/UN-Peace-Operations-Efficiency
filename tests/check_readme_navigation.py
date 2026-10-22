#!/usr/bin/env python3
"""Synthetic and retained-input checks for generated current navigation."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import build_readme_navigation as nav


class NavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads((nav.ROOT/nav.NAVIGATION).read_text())
        cls.pointer = json.loads((nav.ROOT/'data/current_research_reference.json').read_text())

    def test_required_current_roles(self):
        nav.validate(self.config)
        rendered = nav.render(self.config, self.pointer)['README.md']
        self.assertIn('docs/current_status.md', rendered)
        self.assertNotIn('## Latest: V11', rendered)
        self.assertNotIn('watch** is active', rendered)

    def test_duplicate_role_fails(self):
        c = copy.deepcopy(self.config)
        c['current_roles'].append(c['current_roles'][0])
        with self.assertRaises(ValueError): nav.validate(c)

    def test_traversal_fails(self):
        c = copy.deepcopy(self.config)
        c['current_roles'][0]['path'] = '../outside.md'
        with self.assertRaises(ValueError): nav.validate(c)

    def test_history_complete(self):
        c = copy.deepcopy(self.config)
        c['history'] = [r for r in c['history'] if r['id'] != 'V13']
        with self.assertRaises(ValueError): nav.validate(c)

    def test_state_changes_force_review(self):
        for field,value in [('reference_version','14.0'),('course_watch_policy','Active'),('live_use_gates',{})]:
            p = copy.deepcopy(self.pointer)
            p[field] = value
            with self.assertRaises(ValueError): nav.render(self.config,p)

    def test_financial_and_historical_qualifiers(self):
        output = nav.render(self.config,self.pointer)
        self.assertIn('FINANCIALLY_VALIDATED',output['README.md'])
        self.assertIn('two affected rechecks are separate',output['README.md'])
        self.assertIn('not a fresh legal-status review',output['docs/release_history.md'])
        self.assertIn(nav.BASELINE,output['docs/release_history.md'])

    def test_missing_archive_blocks_replacement(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError): nav.verify_archive(Path(td))

    def test_archive_tampering_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            archive=root/nav.ARCHIVE
            archive.parent.mkdir(parents=True)
            archive.write_text('SYNTHETIC modified historical README')
            (root/'metadata').mkdir()
            scope={'files':[{'path':'README.md','sha256':hashlib.sha256(b'SYNTHETIC original').hexdigest()}]}
            (root/'metadata/repository_audit_scope.json').write_text(json.dumps(scope))
            with self.assertRaises(ValueError): nav.verify_archive(root)

    def test_boolean_schema_rejected(self):
        c = copy.deepcopy(self.config)
        c['schema_version'] = True
        with self.assertRaises(ValueError): nav.validate(c)

    def test_malformed_collection_rows_rejected(self):
        for field in ('current_roles','history','priority_cases'):
            c = copy.deepcopy(self.config)
            c[field][0] = None
            with self.assertRaises(ValueError): nav.validate(c)


if __name__ == '__main__':
    unittest.main()
