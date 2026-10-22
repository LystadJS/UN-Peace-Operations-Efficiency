#!/usr/bin/env python3
"""Synthetic bundle and static workflow publication corruption controls."""
import copy
import contextlib
import csv
import hashlib
import io
import json
from pathlib import Path
import stat
import sys
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import publish_release as p

POLICY = p.js((ROOT / 'metadata/publication_policy.json').read_bytes())
SOURCE = 'a' * 40
REPOSITORY = 'SYNTHETIC/REPOSITORY'


def bundle(files=None, mutate=None, extras=None, symlink=None):
    files = files if files is not None else {'docs/current_status.md': b'SYNTHETIC output\n'}
    validation = json.dumps({'status': 'PASS', 'scope': 'SYNTHETIC', 'tested_commit': SOURCE,
        'group': 'baseline', 'group_plan_sha256': 'e' * 64, 'passed_steps': 1,
        'results': [{'id': 'SYNTHETIC', 'exit_code': 0}], 'changed_tracked_files': [],
        'initial_tracked_clean': True}).encode()
    controls = json.dumps(dict(json.loads(validation), group='repository-controls')).encode()
    manifest = {'schema_version': 1, 'source_sha': SOURCE, 'tested_sha': SOURCE,
                'source_workflow': '.github/workflows/publish_release.yml',
                'validation_receipt_sha256': p.digest(validation),
                'controls_receipt_sha256': p.digest(controls),
                'files': [{'path': k, 'sha256': p.digest(v), 'size_bytes': len(v), 'mode': '100644'}
                          for k, v in files.items()]}
    if mutate:
        mutate(manifest)
    payload = {**files, 'release_manifest.json': json.dumps(manifest).encode(),
               '_release/validation.json': validation, '_release/controls.json': controls, **(extras or {})}
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as archive:
        for name, data in payload.items():
            info = zipfile.ZipInfo(name)
            info.external_attr = ((stat.S_IFLNK if name == symlink else stat.S_IFREG) | 0o644) << 16
            archive.writestr(info, data)
    return buffer.getvalue()


def wrapped(raw):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as archive:
        archive.writestr('release-bundle.zip', raw)
    return buffer.getvalue()


class FakeAPI:
    def __init__(self, raw, base=SOURCE, conclusion='success', existing=None):
        self.raw, self.base, self.conclusion = raw, base, conclusion
        self.existing = existing or []
        self.calls = []

    def request(self, route, method='GET', data=None, **kwargs):
        self.calls.append((route, method, data))
        if route == '/actions/runs/123':
            return {'status': 'completed', 'conclusion': self.conclusion, 'event': 'workflow_dispatch',
                    'head_sha': SOURCE, 'head_repository': {'full_name': REPOSITORY},
                    'path': '.github/workflows/publish_release.yml'}
        if route.startswith('/actions/runs/123/artifacts'):
            return {'total_count': 1, 'artifacts': [{'name': 'SYNTHETIC', 'id': 12, 'expired': False}]}
        if route == '/actions/artifacts/12/zip':
            return wrapped(self.raw)
        if route == '/git/ref/heads/main':
            return {'object': {'sha': self.base}}
        if route == '/git/commits/' + SOURCE:
            return {'tree': {'sha': 'b' * 40}}
        if route.startswith('/git/trees/'):
            return {'truncated': False, 'tree': [x if isinstance(x, dict) else {'path': x} for x in self.existing]}
        if route in {'/git/blobs', '/git/trees', '/git/commits'}:
            return {'sha': 'c' * 40}
        if route == '/git/refs':
            return {}
        if route == '/pulls':
            return {'html_url': 'https://github.com/SYNTHETIC/REPOSITORY/pull/1'}
        raise AssertionError(route)


class BundleTests(unittest.TestCase):
    def reject(self, raw, policy=POLICY):
        with self.assertRaises((ValueError, zipfile.BadZipFile)):
            p.verify(raw, p.digest(raw), SOURCE, policy)

    def test_valid_bundle(self):
        raw = bundle()
        manifest, files = p.verify(raw, p.digest(raw), SOURCE, POLICY)
        self.assertEqual(manifest['tested_sha'], SOURCE)
        self.assertEqual(set(files), {'docs/current_status.md'})

    def test_outer_artifact_is_unwrapped_without_extraction(self):
        raw = bundle()
        self.assertEqual(p.artifact_bundle(wrapped(raw), POLICY), raw)

    def test_manifest_hash_mismatch(self):
        self.reject(bundle(mutate=lambda m: m['files'][0].update(sha256='0' * 64)))

    def test_wrong_bundle_hash(self):
        with self.assertRaises(ValueError):
            p.verify(bundle(), '0' * 64, SOURCE, POLICY)

    def test_wrong_source_or_tested_commit(self):
        self.reject(bundle(mutate=lambda m: m.update(tested_sha='b' * 40)))

    def test_unbound_or_incomplete_validation_receipt_rejected(self):
        valid = {'status': 'PASS', 'tested_commit': SOURCE, 'group': 'baseline',
                 'group_plan_sha256': 'e' * 64, 'passed_steps': 1,
                 'results': [{'exit_code': 0}], 'changed_tracked_files': [], 'initial_tracked_clean': True}
        for field, value in [('tested_commit', 'b' * 40), ('group', 'unknown'),
                             ('results', []), ('passed_steps', 0), ('changed_tracked_files', ['README.md']),
                             ('initial_tracked_clean', False), ('initial_tracked_clean', 'true')]:
            with self.assertRaises(ValueError):
                p.validate_receipt(dict(valid, **{field: value}), SOURCE)

    def test_protected_and_unsafe_paths(self):
        for name in ('../README.md', '/README.md', '.github/workflows/evil.yml',
                     'data/census_v13/research_reference.json', 'reports/releases/x/../evil.md',
                     'reports/releases/x/bad\nname.md'):
            self.reject(bundle(files={name: b'SYNTHETIC'}))

    def test_unmanifested_file(self):
        self.reject(bundle(extras={'reports/releases/x/extra.md': b'SYNTHETIC'}))

    def test_symlink_rejected(self):
        self.reject(bundle(symlink='docs/current_status.md'))

    def test_size_ceiling(self):
        policy = dict(POLICY, maximum_uncompressed_bytes=5)
        self.reject(bundle(), policy)

    def test_duplicate_rows_rejected(self):
        self.reject(bundle(mutate=lambda m: m['files'].append(copy.deepcopy(m['files'][0]))))

    def test_invalid_run_and_artifact_names_rejected_before_network(self):
        api = FakeAPI(bundle())
        for rid, name in (('$(bad)', 'SYNTHETIC'), ('123', '../bad')):
            with self.assertRaises(ValueError):
                p.publish(api, REPOSITORY, rid, name, '0' * 64, SOURCE, POLICY)
        self.assertFalse(api.calls)

    def test_controller_source_mismatch_stops_before_api_construction(self):
        argv = ['publish_release.py', 'publish', '--repository', REPOSITORY,
                '--run-id', '123', '--artifact-name', 'SYNTHETIC',
                '--sha256', 'e' * 64, '--source-sha', SOURCE]
        with patch.object(sys, 'argv', argv), \
                patch.object(p.subprocess, 'check_output', return_value='b' * 40 + '\n'), \
                patch.object(p, 'GitHub') as api, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(p.main(), 1)
            api.assert_not_called()

    def test_failed_run_cannot_publish(self):
        raw = bundle()
        api = FakeAPI(raw, conclusion='failure')
        with self.assertRaises(ValueError):
            p.publish(api, REPOSITORY, '123', 'SYNTHETIC', p.digest(raw), SOURCE, POLICY)
        self.assertTrue(all(method == 'GET' for _, method, _ in api.calls))

    def test_base_movement_cannot_publish(self):
        raw = bundle()
        api = FakeAPI(raw, base='d' * 40)
        with self.assertRaises(ValueError):
            p.publish(api, REPOSITORY, '123', 'SYNTHETIC', p.digest(raw), SOURCE, POLICY)
        self.assertTrue(all(method == 'GET' for _, method, _ in api.calls))

    def test_append_only_release_cannot_replace_existing(self):
        raw = bundle(files={'reports/releases/example/result.md': b'SYNTHETIC'})
        api = FakeAPI(raw, existing=['reports/releases/example/result.md'])
        with self.assertRaises(ValueError):
            p.publish(api, REPOSITORY, '123', 'SYNTHETIC', p.digest(raw), SOURCE, POLICY)

    def test_success_only_creates_branch_and_draft_pr(self):
        raw = bundle()
        api = FakeAPI(raw)
        result = p.publish(api, REPOSITORY, '123', 'SYNTHETIC', p.digest(raw), SOURCE, POLICY)
        self.assertEqual(result['status'], 'CANDIDATE_PR_CREATED_NOT_MERGED')
        writes = [(r, m, d) for r, m, d in api.calls if m != 'GET']
        self.assertFalse(any('heads/main' in r for r, _, _ in writes))
        self.assertTrue(next(d for r, _, d in writes if r == '/git/refs')['ref'].startswith('refs/heads/release-candidates/'))
        self.assertTrue(next(d for r, _, d in writes if r == '/pulls')['draft'])

    def test_unchanged_payload_creates_no_branch_or_pr(self):
        raw = bundle()
        content = b'SYNTHETIC output\n'
        sha = hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()
        api = FakeAPI(raw, existing=[{'path': 'docs/current_status.md', 'sha': sha}])
        result = p.publish(api, REPOSITORY, '123', 'SYNTHETIC', p.digest(raw), SOURCE, POLICY)
        self.assertEqual(result['status'], 'NO_CHANGES')
        self.assertTrue(all(method == 'GET' for _, method, _ in api.calls))


class WorkflowTests(unittest.TestCase):
    def test_twenty_legacy_publishers_are_manual_and_read_only(self):
        import yaml
        self.assertEqual(len(POLICY['historical_candidate_workflows']), 20)
        for name in POLICY['historical_candidate_workflows']:
            data = yaml.safe_load((ROOT / name).read_text())
            triggers = data.get('on', data.get(True))
            self.assertEqual(set(triggers), {'workflow_dispatch'}, name)
            self.assertEqual(data['permissions'], {'contents': 'read'}, name)
            for job in data['jobs'].values():
                self.assertEqual(job['permissions'], {'contents': 'read', 'actions': 'read'}, name)
                for step in job.get('steps', []):
                    if str(step.get('uses', '')).startswith('actions/checkout@'):
                        self.assertIs(step['with']['persist-credentials'], False)
                    run = step.get('run', '')
                    for command in ('git push', 'git commit', 'git add', 'git rebase', 'git pull', 'git config', 'yaml.safe_load'):
                        self.assertNotIn(command, run, (name, command))
                    self.assertNotIn("Path('README.md')", run, name)

    def test_dedicated_workflow_is_explicit_and_write_scope_is_isolated(self):
        import yaml
        data = yaml.safe_load((ROOT / '.github/workflows/publish_release.yml').read_text())
        self.assertEqual(set(data.get('on', data.get(True))), {'workflow_dispatch'})
        self.assertEqual(data['permissions'], {'contents': 'read'})
        self.assertEqual(data['jobs']['prepare']['permissions'], {'contents': 'read'})
        self.assertEqual(data['jobs']['publish-candidate']['permissions']['contents'], 'write')
        self.assertIn("inputs.operation == 'publish'", data['jobs']['publish-candidate']['if'])


if __name__ == '__main__':
    unittest.main()
