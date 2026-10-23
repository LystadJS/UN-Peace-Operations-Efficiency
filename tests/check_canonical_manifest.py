#!/usr/bin/env python3
"""Synthetic negative controls for the scoped artifact manifest and archive."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_canonical_manifest as m
from frozen_audit_inputs import frozen_source_path


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'a.txt').write_text('SYNTHETIC original\n')
        (self.root / 'b.txt').write_text('SYNTHETIC replacement\n')
        self.rows = [{'artifact_id': p, 'path': p, 'role': 'synthetic', 'currency': 'CURRENT' if p == 'b.txt' else 'HISTORICAL',
                      'scope': 'synthetic scope', 'designation_basis': 'synthetic reviewed receipt',
                      'hash_mode': 'immutable_sha256', 'sha256': m.sha(self.root / p), 'frozen_baseline': None}
                     for p in ('a.txt', 'b.txt')]
        self.manifest = {'schema_version': 1, 'artifacts': self.rows,
                         'current_roles': {'test': {'path': 'b.txt', 'scope': 'test', 'designation_basis': 'synthetic receipt'}},
                         'generated_artifacts': [], 'supersession_relationships': []}

    def test_valid_scoped_sources(self):
        self.assertEqual(m.validate_manifest(self.manifest, self.root), 2)

    def test_changed_source_fails(self):
        (self.root / 'a.txt').write_text('changed')
        with self.assertRaises(ValueError): m.validate_manifest(self.manifest, self.root)

    def test_missing_historical_source_fails(self):
        (self.root / 'a.txt').unlink()
        with self.assertRaises(OSError): m.validate_manifest(self.manifest, self.root)

    def test_broken_current_link_fails(self):
        self.manifest['current_roles']['test']['path'] = 'missing.txt'
        with self.assertRaises(ValueError): m.validate_manifest(self.manifest, self.root)

    def test_unscoped_role_fails(self):
        self.manifest['current_roles']['test']['scope'] = ''
        with self.assertRaises(ValueError): m.validate_manifest(self.manifest, self.root)

    def test_unscoped_supersession_fails(self):
        self.manifest['supersession_relationships'] = [{'predecessor': 'a.txt', 'successor': 'b.txt', 'scope': '', 'evidence_refs': ['synthetic']}]
        with self.assertRaises(ValueError): m.validate_manifest(self.manifest, self.root)

    def test_supersession_cycle_fails(self):
        self.manifest['supersession_relationships'] = [{'predecessor': a, 'successor': b, 'scope': 'synthetic', 'evidence_refs': ['synthetic']} for a,b in [('a.txt','b.txt'),('b.txt','a.txt')]]
        with self.assertRaises(ValueError): m.validate_manifest(self.manifest, self.root)

    def test_self_hash_contract_fails(self):
        self.manifest['generated_artifacts'] = [{'path': m.MANIFEST}]
        with self.assertRaises(ValueError): m.validate_manifest(self.manifest, self.root)

    def test_archive_survives_authorized_live_change(self):
        archived = self.root / 'history/pre_controls/a.txt'; archived.parent.mkdir(parents=True)
        archived.write_bytes((self.root / 'a.txt').read_bytes())
        (self.root / 'metadata').mkdir()
        entry = {'path': 'a.txt', 'archive_path': 'history/pre_controls/a.txt', 'sha256': m.sha(archived)}
        (self.root / 'metadata/frozen_input_archive.json').write_text(json.dumps({'files': [entry]}))
        (self.root / 'a.txt').write_text('new authorized live control')
        self.assertEqual(frozen_source_path(self.root, 'a.txt'), archived)
        archived.write_text('tampered')
        with self.assertRaises(ValueError): frozen_source_path(self.root, 'a.txt')

    def test_missing_archive_never_falls_back(self):
        (self.root / 'metadata').mkdir()
        (self.root / 'metadata/frozen_input_archive.json').write_text(json.dumps({'files': [{'path': 'a.txt', 'archive_path': 'history/pre_controls/a.txt', 'sha256': '0'*64}]}))
        with self.assertRaises(ValueError): frozen_source_path(self.root, 'a.txt')

    def test_real_outputs_reproduce(self):
        for path, body in m.build().items():
            self.assertEqual((m.ROOT / path).read_text(), body)


if __name__ == '__main__': unittest.main()
