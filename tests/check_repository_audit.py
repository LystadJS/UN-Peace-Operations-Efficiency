#!/usr/bin/env python3
"""Synthetic preservation and coverage corruption tests."""
import csv
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import validate_repository_audit as audit


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'metadata').mkdir()
        (self.root / 'source.txt').write_text('SYNTHETIC source\n')
        raw = (self.root / 'source.txt').read_bytes()
        self.scope = {'files': [{'path': 'source.txt', 'sha256': hashlib.sha256(raw).hexdigest(),
                                 'size_bytes': len(raw), 'tracked': True}]}
        self.save()

    def save(self):
        (self.root / 'metadata/repository_audit_scope.json').write_text(json.dumps(self.scope))

    def test_original_input_passes(self):
        self.assertEqual(audit.validate_scope(self.root)[1], {'source.txt'})

    def test_changed_bytes_fail_even_same_size(self):
        (self.root / 'source.txt').write_text('SYNTHETIC Source\n')
        with self.assertRaises(ValueError):
            audit.validate_scope(self.root)

    def test_missing_input_fails(self):
        (self.root / 'source.txt').unlink()
        with self.assertRaises(ValueError):
            audit.validate_scope(self.root)

    def test_unsafe_path_fails(self):
        for name in ('../source.txt', '/source.txt'):
            self.scope['files'][0]['path'] = name
            self.save()
            with self.assertRaises(ValueError):
                audit.validate_scope(self.root)

    def test_duplicate_scope_fails(self):
        self.scope['files'] *= 2
        self.save()
        with self.assertRaises(ValueError):
            audit.validate_scope(self.root)

    def test_duplicate_registry_coverage_fails(self):
        with (self.root / 'metadata/table.csv').open('w', newline='') as handle:
            writer = csv.writer(handle)
            writer.writerows([['path'], ['source.txt'], ['source.txt']])
        with self.assertRaises(ValueError):
            audit.table_paths(self.root, 'metadata/table.csv')


if __name__ == '__main__':
    unittest.main()
