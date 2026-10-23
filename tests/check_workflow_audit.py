#!/usr/bin/env python3
"""Clearly synthetic regression fixtures; no workflow is executed."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import audit_workflows as a


SYNTHETIC = '''name: Synthetic fixture
on:
  pull_request:
  workflow_dispatch:
permissions:
  contents: write
jobs:
  check:
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
      - run: python scripts/example.py --check
'''


class WorkflowAuditTests(unittest.TestCase):
    def test_on_is_not_boolean(self):
        parsed = a.parse(SYNTHETIC)
        self.assertIn('on', parsed)
        self.assertNotIn(True, parsed)

    def test_job_override_does_not_inherit_workflow_write(self):
        row = a.inspect('SYNTHETIC.yml', SYNTHETIC)
        perms = a.json.loads(row['permissions_json'])['check']
        self.assertEqual(perms['explicit_scopes'], {'contents':'read'})
        self.assertEqual(perms['other_scopes'], 'none')

    def test_no_permissions_is_unknown_not_read(self):
        parsed = a.parse(SYNTHETIC)
        self.assertEqual(a.permissions({}, {})['level'], 'repository_default_unknown')

    def test_duplicate_yaml_keys_rejected(self):
        with self.assertRaises(ValueError):
            a.parse(SYNTHETIC + '\npermissions: read-all\n')

    def test_explicit_main_publication_detected(self):
        row = a.inspect('SYNTHETIC.yml', SYNTHETIC.replace('python scripts/example.py --check', 'git push origin HEAD:main'))
        self.assertEqual(row['direct_main_push'], 'true')

    def test_comment_does_not_publish(self):
        row = a.inspect('SYNTHETIC.yml', SYNTHETIC.replace('python scripts/example.py --check', 'echo "git push origin HEAD:main"'))
        self.assertEqual(row['direct_main_push'], 'false')

    def test_direct_script_target_and_tag_recorded(self):
        row = a.inspect('SYNTHETIC.yml', SYNTHETIC)
        self.assertEqual(a.json.loads(row['direct_invoked_scripts_json']), ['scripts/example.py'])
        self.assertEqual(a.json.loads(row['actions_json'])[0]['pin'], 'tag_or_branch')

    def test_full_sha_classified(self):
        row = a.inspect('SYNTHETIC.yml', SYNTHETIC.replace('@v4', '@'+'a'*40))
        self.assertEqual(a.json.loads(row['actions_json'])[0]['pin'], 'commit_sha')

    def test_historical_name_not_verified_obsolete(self):
        row = a.inspect('.github/workflows/v8_release.yml', SYNTHETIC)
        self.assertNotIn('verified_obsolete', row['obsolescence_status'])

    def test_mixed_dependency_pins_not_fully_pinned(self):
        self.assertTrue(a.pip_exact_pins('python -m pip install --quiet pypdf==5.9.0 PyYAML==6.0.3'))
        self.assertFalse(a.pip_exact_pins('python -m pip install pypdf==5.9.0 PyYAML'))
        self.assertFalse(a.pip_exact_pins('python -m pip install -r requirements.txt'))
        self.assertFalse(a.pip_exact_pins('python -m pip install example==1.*'))

    def test_scope_coverage_and_reproduction(self):
        out = a.outputs()
        rows = list(a.csv.DictReader(a.io.StringIO(out[a.OUT])))
        scope = a.json.loads((a.ROOT/a.SCOPE).read_text())
        expected = {r['path'] for r in scope['files'] if r['path'].startswith('.github/workflows/')}
        self.assertEqual({r['workflow_path'] for r in rows}, expected)
        self.assertEqual(len(rows), len(expected))
        for path, content in out.items():
            self.assertEqual((a.ROOT/path).read_text(), content)


if __name__ == '__main__':
    unittest.main()
