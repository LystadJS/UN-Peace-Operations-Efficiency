"""Resolve frozen audit inputs after explicitly archived controls evolve.

Only declared archives are used. Hashes are verified before returning a path;
the helper never silently falls back to changed live bytes.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path, PurePosixPath

ARCHIVE_MAP = 'metadata/frozen_input_archive.json'


def frozen_source_path(root, path):
    root = Path(root)
    rel = PurePosixPath(path)
    if rel.is_absolute() or '..' in rel.parts:
        raise ValueError(f'unsafe frozen path: {path}')
    mapping = root / ARCHIVE_MAP
    if not mapping.exists():
        return root / path
    rows = json.loads(mapping.read_text())['files']
    matches = [r for r in rows if r['path'] == path]
    if len(matches) > 1:
        raise ValueError(f'duplicate frozen archive entry: {path}')
    if not matches:
        return root / path
    entry = matches[0]
    archive = PurePosixPath(entry['archive_path'])
    if archive.is_absolute() or '..' in archive.parts or not str(archive).startswith('history/pre_controls/'):
        raise ValueError(f'unsafe archive path: {archive}')
    target = root / archive
    if not target.is_file() or target.is_symlink():
        raise ValueError(f'missing/unsafe archived source: {archive}')
    if hashlib.sha256(target.read_bytes()).hexdigest() != entry['sha256']:
        raise ValueError(f'archived source hash mismatch: {archive}')
    return target
