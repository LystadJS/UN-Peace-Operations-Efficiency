#!/usr/bin/env python3
"""Prepare/verify a bounded release bundle; explicit publication opens a PR only."""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / 'metadata/publication_policy.json'
SHA = re.compile(r'^[0-9a-f]{40}$')
SHA256 = re.compile(r'^[0-9a-f]{64}$')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def js(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=unique)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def validate_receipt(result, source, group='baseline'):
    require(isinstance(result, dict) and result.get('status') == 'PASS', 'validation receipt must report PASS')
    require(result.get('tested_commit') == source and result.get('group') == group,
            'receipt must bind the required suite to the exact source commit')
    require(isinstance(result.get('group_plan_sha256'), str) and
            bool(SHA256.fullmatch(result['group_plan_sha256'])), 'missing validation plan hash')
    outcomes = result.get('results')
    require(isinstance(outcomes, list) and outcomes and
            all(isinstance(r, dict) and type(r.get('exit_code')) is int and r['exit_code'] == 0 for r in outcomes),
            'validation results incomplete or failed')
    require(type(result.get('passed_steps')) is int and result['passed_steps'] == len(outcomes),
            'validation result count mismatch')
    require(result.get('changed_tracked_files') == [], 'validation changed tracked files')
    require(result.get('initial_tracked_clean') is True,
            'validation must start from an explicitly clean tracked source tree')


def safe_path(value):
    require(isinstance(value, str) and value and '\\' not in value, 'invalid bundle path')
    require(bool(re.fullmatch(r'[A-Za-z0-9_./-]+', value)), 'unsupported bundle path characters')
    p = PurePosixPath(value)
    require(not p.is_absolute() and '..' not in p.parts and p.as_posix() == value and ':' not in value,
            'bundle path must be canonical and relative')
    require(all(x not in {'', '.'} for x in p.parts), 'empty/dot bundle path')
    return p


def allowed(path, policy):
    p = safe_path(path)
    if path in policy['allowed_current_paths']:
        return True
    prefix = policy['allowed_additive_release_prefix']
    return path.startswith(prefix) and len(p.parts) >= 4 and p.suffix in policy['additive_release_extensions']


def regular_local(root, relative):
    safe_path(relative)
    path = root / relative
    require(path.is_file(), 'missing bundle file: ' + relative)
    require(not any(x.is_symlink() for x in [path, *path.parents] if x != root.parent), 'symlinked bundle input')
    require(path.resolve().is_relative_to(root.resolve()), 'bundle input escapes root')
    return path


def prepare(root, paths, receipt, controls_receipt, workflow, output, policy):
    require(paths and len(paths) == len(set(paths)), 'select distinct approved output paths')
    require(workflow in policy['historical_candidate_workflows'] or workflow == '.github/workflows/publish_release.yml',
            'unrecognized source workflow')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    require(bool(SHA.fullmatch(source)), 'invalid source commit')
    validation = Path(receipt).read_bytes()
    result = js(validation)
    validate_receipt(result, source)
    controls = Path(controls_receipt).read_bytes()
    validate_receipt(js(controls), source, 'repository-controls')
    files, payloads = [], {}
    for path in sorted(paths):
        require(allowed(path, policy), 'output not approved for publication: ' + path)
        raw = regular_local(root, path).read_bytes()
        require(len(raw) <= policy['maximum_file_bytes'], 'bundle file too large')
        files.append({'path': path, 'sha256': digest(raw), 'size_bytes': len(raw), 'mode': '100644'})
        payloads[path] = raw
    manifest = {'schema_version': 1, 'source_sha': source, 'tested_sha': source,
                'source_workflow': workflow, 'validation_receipt_sha256': digest(validation),
                'controls_receipt_sha256': digest(controls), 'files': files}
    payloads['release_manifest.json'] = (json.dumps(manifest, indent=2, sort_keys=True) + '\n').encode()
    payloads['_release/validation.json'] = validation
    payloads['_release/controls.json'] = controls
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_STORED) as archive:
        for path, raw in sorted(payloads.items()):
            item = zipfile.ZipInfo(path, date_time=(1980, 1, 1, 0, 0, 0))
            item.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(item, raw)
    body = buffer.getvalue()
    verify(body, digest(body), source, policy)
    Path(output).write_bytes(body)
    return {'status': 'PASS_bundle_prepared_not_published', 'source_sha': source,
            'bundle_sha256': digest(body), 'files': len(files)}


def verify(body, expected, source, policy):
    require(bool(SHA.fullmatch(source)), 'source SHA must be a full commit hash')
    require(bool(SHA256.fullmatch(expected)) and digest(body) == expected, 'bundle SHA-256 mismatch')
    require(len(body) <= policy['maximum_zip_bytes'], 'compressed bundle too large')
    payload = {}
    with zipfile.ZipFile(io.BytesIO(body)) as archive:
        total = 0
        for info in archive.infolist():
            path = info.filename
            safe_path(path)
            require(not info.is_dir() and path not in payload, 'duplicate or directory ZIP member')
            mode = info.external_attr >> 16
            require(not stat.S_ISLNK(mode), 'symlink ZIP member')
            require(not info.flag_bits & 1, 'encrypted ZIP member')
            require(info.file_size <= policy['maximum_file_bytes'], 'member too large')
            total += info.file_size
            require(total <= policy['maximum_uncompressed_bytes'], 'uncompressed bundle too large')
            payload[path] = archive.read(info)
    require({'release_manifest.json', '_release/validation.json', '_release/controls.json'} <= set(payload),
            'missing release manifest/receipts')
    manifest = js(payload.pop('release_manifest.json'))
    validation = payload.pop('_release/validation.json')
    controls = payload.pop('_release/controls.json')
    require(isinstance(manifest, dict), 'manifest must be an object')
    require(manifest.get('schema_version') == 1 and type(manifest.get('schema_version')) is int, 'invalid manifest version')
    require(manifest.get('source_sha') == source and manifest.get('tested_sha') == source, 'source/tested commit mismatch')
    require(manifest.get('source_workflow') in policy['historical_candidate_workflows'] or
            manifest.get('source_workflow') == '.github/workflows/publish_release.yml', 'unapproved source workflow')
    require(digest(validation) == manifest.get('validation_receipt_sha256'), 'validation receipt hash mismatch')
    validate_receipt(js(validation), source)
    require(digest(controls) == manifest.get('controls_receipt_sha256'), 'controls receipt hash mismatch')
    validate_receipt(js(controls), source, 'repository-controls')
    rows = manifest.get('files')
    require(isinstance(rows, list) and rows, 'empty release')
    seen = set()
    for row in rows:
        require(isinstance(row, dict), 'manifest file row must be an object')
        path = row.get('path')
        require(path not in seen and allowed(path, policy), 'duplicate or disallowed manifest path')
        seen.add(path)
        require(path in payload and row.get('mode') == '100644', 'missing file or invalid mode')
        require(type(row.get('size_bytes')) is int and row['size_bytes'] == len(payload[path]), 'member size mismatch')
        require(row.get('sha256') == digest(payload[path]), 'member hash mismatch')
    require(seen == set(payload), 'unmanifested ZIP members')
    return manifest, payload


def artifact_bundle(body, policy):
    """GitHub artifact downloads wrap the uploaded deterministic bundle ZIP."""
    require(len(body) <= policy['maximum_zip_bytes'], 'artifact download too large')
    with zipfile.ZipFile(io.BytesIO(body)) as archive:
        members = archive.infolist()
        require(len(members) == 1 and members[0].filename == 'release-bundle.zip',
                'artifact must contain exactly release-bundle.zip')
        info = members[0]
        require(not stat.S_ISLNK(info.external_attr >> 16) and not info.flag_bits & 1,
                'invalid artifact bundle member')
        require(info.file_size <= policy['maximum_zip_bytes'], 'nested bundle too large')
        return archive.read(info)


class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, newurl):
        redirected = super().redirect_request(request, fp, code, message, headers, newurl)
        if redirected is not None and urllib.parse.urlsplit(newurl).hostname != 'api.github.com':
            redirected.remove_header('Authorization')
        return redirected


class GitHub:
    def __init__(self, repository, token):
        require(bool(re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository)), 'invalid repository')
        require(bool(token), 'GH_TOKEN required')
        self.base = 'https://api.github.com/repos/' + repository
        self.token = token
        self.opener = urllib.request.build_opener(SafeRedirect())

    def request(self, route, method='GET', data=None, raw=False, limit=33554432):
        require(route.startswith('/') and not route.startswith('//'), 'invalid API route')
        body = json.dumps(data).encode() if data is not None else None
        request = urllib.request.Request(self.base + route, data=body, method=method,
            headers={'Authorization': 'Bearer ' + self.token, 'Accept': 'application/vnd.github+json',
                     'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'UN-Peace-Operations-release'})
        try:
            with self.opener.open(request, timeout=60) as response:
                result = response.read(limit + 1)
                require(len(result) <= limit, 'API response exceeds limit')
        except urllib.error.HTTPError as error:
            raise ValueError(f'GitHub request failed with HTTP {error.code}') from None
        return result if raw else js(result)


def publish(api, repository, run_id, artifact_name, expected, source, policy):
    require(bool(re.fullmatch(r'[0-9]+', run_id)), 'run ID must be numeric')
    require(bool(re.fullmatch(r'[A-Za-z0-9_.-]{1,100}', artifact_name)), 'invalid artifact name')
    require(bool(SHA.fullmatch(source)) and bool(SHA256.fullmatch(expected)), 'full source and bundle hashes required')
    run = api.request('/actions/runs/' + run_id)
    require(run.get('status') == 'completed' and run.get('conclusion') == 'success', 'source run did not succeed')
    require(run.get('event') == 'workflow_dispatch' and run.get('head_sha') == source, 'run event/source mismatch')
    require(run.get('head_repository', {}).get('full_name') == repository, 'source run belongs to another repository')
    artifacts = api.request('/actions/runs/' + run_id + '/artifacts?per_page=100')
    require(artifacts.get('total_count', 0) <= 100, 'too many artifacts; cannot select unambiguously')
    selected = [a for a in artifacts['artifacts'] if a['name'] == artifact_name and not a.get('expired')]
    require(len(selected) == 1, 'artifact missing, expired or ambiguous')
    body = api.request('/actions/artifacts/' + str(selected[0]['id']) + '/zip', raw=True,
                       limit=policy['maximum_zip_bytes'])
    manifest, payload = verify(artifact_bundle(body, policy), expected, source, policy)
    require(run.get('path', '').split('@')[0] == manifest['source_workflow'], 'workflow provenance mismatch')
    base = api.request('/git/ref/heads/' + policy['base_branch'])['object']['sha']
    require(base == source, 'base branch moved or source was not the tested main head; rebuild and revalidate')
    commit = api.request('/git/commits/' + source)
    tree = api.request('/git/trees/' + commit['tree']['sha'] + '?recursive=1')
    require(not tree.get('truncated'), 'base tree truncated')
    existing = {x['path']: x for x in tree['tree']}
    for path in payload:
        if path.startswith(policy['allowed_additive_release_prefix']):
            require(path not in existing, 'versioned release artifacts are append-only')
    changed = {path: content for path, content in payload.items()
               if existing.get(path, {}).get('sha') != hashlib.sha1(
                   b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()}
    if not changed:
        return {'status': 'NO_CHANGES', 'source_sha': source, 'tested_sha': manifest['tested_sha'],
                'run_id': run_id, 'artifact_id': selected[0]['id'], 'bundle_sha256': expected,
                'files_matched': len(payload), 'publication_writes': 0}
    entries = []
    for path, content in sorted(changed.items()):
        blob = api.request('/git/blobs', 'POST', {'content': base64.b64encode(content).decode(), 'encoding': 'base64'})
        entries.append({'path': path, 'mode': '100644', 'type': 'blob', 'sha': blob['sha']})
    built = api.request('/git/trees', 'POST', {'base_tree': commit['tree']['sha'], 'tree': entries})
    require(api.request('/git/ref/heads/' + policy['base_branch'])['object']['sha'] == source,
            'base branch moved during verification; publication stopped')
    created = api.request('/git/commits', 'POST', {'message': 'Prepare reviewed release candidate ' + run_id,
        'tree': built['sha'], 'parents': [source]})
    branch = policy['branch_prefix'] + run_id + '-' + expected[:12]
    api.request('/git/refs', 'POST', {'ref': 'refs/heads/' + branch, 'sha': created['sha']})
    receipt = {'source_sha': source, 'tested_sha': manifest['tested_sha'], 'run_id': run_id,
               'artifact_id': selected[0]['id'], 'bundle_sha256': expected, 'candidate_commit': created['sha']}
    pr = api.request('/pulls', 'POST', {'title': 'Release candidate ' + run_id,
        'head': branch, 'base': policy['base_branch'], 'draft': True,
        'body': 'Explicitly requested candidate publication. No operational or financial authority is implied.\n\n'
                + '```json\n' + json.dumps(receipt, indent=2) + '\n```'})
    return {'status': 'CANDIDATE_PR_CREATED_NOT_MERGED', 'branch': branch, 'pull_request': pr['html_url'], **receipt}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('prepare')
    p.add_argument('--paths', nargs='+', required=True)
    p.add_argument('--validation-receipt', required=True)
    p.add_argument('--controls-receipt', required=True)
    p.add_argument('--source-workflow', required=True)
    p.add_argument('--output', required=True)
    p = sub.add_parser('verify')
    p.add_argument('--bundle', required=True)
    p.add_argument('--sha256', required=True)
    p.add_argument('--source-sha', required=True)
    p = sub.add_parser('publish')
    p.add_argument('--repository', required=True)
    p.add_argument('--run-id', required=True)
    p.add_argument('--artifact-name', required=True)
    p.add_argument('--sha256', required=True)
    p.add_argument('--source-sha', required=True)
    args = parser.parse_args()
    try:
        policy = js(POLICY.read_bytes())
        if args.command == 'prepare':
            result = prepare(ROOT, args.paths, args.validation_receipt, args.controls_receipt,
                             args.source_workflow, args.output, policy)
        elif args.command == 'verify':
            manifest, files = verify(Path(args.bundle).read_bytes(), args.sha256, args.source_sha, policy)
            result = {'status': 'PASS_bundle_only_not_authority', 'files': len(files), 'source_sha': manifest['source_sha']}
        else:
            controller = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
            require(controller == args.source_sha,
                    'publication controller code/policy must match the exact tested source commit')
            api = GitHub(args.repository, os.environ.get('GH_TOKEN', ''))
            result = publish(api, args.repository, args.run_id, args.artifact_name, args.sha256, args.source_sha, policy)
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, KeyError, TypeError, OSError, zipfile.BadZipFile, subprocess.CalledProcessError) as error:
        print('FAIL: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
