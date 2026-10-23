#!/usr/bin/env python3
"""R02: reproducible lexical discovery, never automatic authority adjudication."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess

BASELINE = '4914e7e41793cbb900bf6d49cd3c6105dd0a6cc9'
PATTERNS = {
    'UN80': r'\bUN[ -]?80\b',
    'UNGA_SESSION': r'\bUNGA[ -]?(?:80|81)\b',
    'ACABQ': r'\bACABQ\b',
    'REFORM': r'\breforms?\b',
    'SESSION_SYMBOL': r'\bA/(?:RES/)?(?:80|81)/[^\s,;"<>\]\|]+',
}
COMPILED = {k: re.compile(v, re.I) for k, v in PATTERNS.items()}
SYMBOL = re.compile(r'\b(?:A|S)/(?:RES/)?\d+/[^\s,;"<>\]\|]+')
CAVEAT = ('SCREENING_LEAD_ONLY: repository wording is not verified primary evidence; '
          'document symbols, UN80 labels, advice and proposals do not establish adoption, '
          'implementation, noncompliance or savings. Verify exact governing text and paragraph.')


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])


def classify(path, manifest):
    row = next((a for a in manifest['artifacts'] if a['path'] == path), None)
    roles = [name for name, value in manifest['current_roles'].items() if value['path'] == path]
    if path.startswith('history/'):
        return 'HISTORICAL', 'archived_control', roles
    if path.startswith(('scripts/', 'tests/', '.github/', 'metadata/')):
        return (row or {}).get('currency', 'UNRESOLVED'), 'control_or_metadata_reference', roles
    if roles:
        return 'CURRENT_IN_DESIGNATED_SCOPE', 'designated_source_assertion', roles
    return (row or {}).get('currency', 'UNRESOLVED'), 'unadjudicated_repository_assertion', roles


def build(root):
    paths = git(root, 'ls-tree', '-r', '--name-only', BASELINE).decode().splitlines()
    manifest = json.loads(git(root, 'show', BASELINE + ':metadata/canonical_manifest.json'))
    records, coverage = [], []
    for path in paths:
        raw = git(root, 'show', BASELINE + ':' + path)
        sha = hashlib.sha256(raw).hexdigest()
        try:
            text = raw.decode('utf-8')
            if '\x00' in text:
                raise UnicodeError('binary NUL')
        except UnicodeError:
            coverage.append({'path': path, 'sha256': sha, 'scan_status': 'BINARY_NOT_TEXT_EXTRACTED', 'matched_lines': 0})
            continue
        hits = 0
        currency, role, current_roles = classify(path, manifest)
        for number, line in enumerate(text.splitlines(), 1):
            matched = [name for name, pattern in COMPILED.items() if pattern.search(line)]
            if not matched:
                continue
            hits += 1
            locator = path + ':L' + str(number)
            records.append({
                'claim_id': 'RC-' + hashlib.sha256(locator.encode()).hexdigest()[:16],
                'path': path, 'locator': locator, 'line': number, 'claim_text': line,
                'matched_categories': matched,
                'source_symbols_mentioned': sorted(set(s.rstrip('.):') for s in SYMBOL.findall(line))),
                'artifact_currency': currency, 'assertion_role': role,
                'designated_current_roles': current_roles,
                'authority_status': 'AUTHORITY_UNRESOLVED', 'authority_caveat': CAVEAT,
                'verification_status': 'NOT_SEMANTICALLY_ADJUDICATED',
                'source_sha256': sha,
            })
        coverage.append({'path': path, 'sha256': sha, 'scan_status': 'UTF8_TEXT_SCANNED', 'matched_lines': hits})
    return {
        'schema_version': 1, 'task_id': 'R02', 'baseline_commit': BASELINE,
        'population_rule': 'Every tracked artifact at A14 commit; subsequent concurrent reform outputs excluded intentionally.',
        'method': 'One discovery record per matching UTF-8 line, including repeated claims and metadata mirrors; no deduplication or legal interpretation.',
        'patterns': PATTERNS, 'authority_caveat': CAVEAT,
        'limitations': [
            'Exhaustive for declared lexical patterns and UTF-8 tracked population only; not a semantic census of all reform obligations.',
            'Binary files, including PDFs, require separate text extraction and operative-text review; exclusions are individually listed.',
            'A source symbol is merely a mention; punctuation and table context require human review.',
            'Current designations are scoped to the manifest; historical versions and metadata copies are not independent corroboration.',
            'No legal interpretation, adopted-action status, implementation verification or financial finding is established.',
        ],
        'coverage': {'tracked_artifacts': len(paths), 'scan_status_counts': dict(sorted(Counter(x['scan_status'] for x in coverage).items())),
                     'matched_artifacts': sum(x['matched_lines'] > 0 for x in coverage), 'discovery_records': len(records),
                     'assertion_role_counts': dict(sorted(Counter(x['assertion_role'] for x in records).items()))},
        'artifacts': coverage, 'claims': records,
    }


def outputs(root):
    result = build(root)
    counts = result['coverage']
    document = f'''# Reform claim discovery inventory — R02

The [machine-readable inventory](../metadata/reform_claim_inventory.json) scans all {counts['tracked_artifacts']} tracked artifacts at A14 commit `{BASELINE}`. It records {counts['discovery_records']} matching lines across {counts['matched_artifacts']} artifacts. Repeated historical wording and metadata mirrors remain traceable; these counts are discovery records, not unique obligations or verified findings.

The declared patterns cover UN80, UNGA80/81, ACABQ, reform wording, and A/80 or A/81 session symbols. Each record retains exact line text, path, 1-based line, mentioned source symbols, source checksum, manifest currency and any scoped current designation. Every tracked artifact has a scan disposition. Binary files are explicitly listed as not text-extracted. The inventory does not claim exhaustive semantic coverage: wording outside these patterns and scanned PDF contents need separate review.

All records begin `AUTHORITY_UNRESOLVED` and `NOT_SEMANTICALLY_ADJUDICATED`. Under the [authority standard](source_authority_standard.md), a document symbol establishes neither adoption nor implementation. A designated current research source can still contain a proposal or an unverified interpretation. R03–R18 must inspect primary texts and adjudicate these leads independently.

Regenerate with `python scripts/build_reform_claim_inventory.py --write`; verify with `--check`. The frozen commit keeps the denominator stable during concurrent development. A later baseline requires an explicitly reviewed change to `BASELINE`, followed by regeneration. No network retrieval occurs here, and no new source-review date is implied.
'''
    return {'metadata/reform_claim_inventory.json': json.dumps(result, indent=2, ensure_ascii=False) + '\n', 'docs/reform_claim_inventory.md': document}


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write', action='store_true')
    mode.add_argument('--check', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    for path, content in outputs(root).items():
        destination = root / path
        if args.write:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding='utf-8')
        elif not destination.exists() or destination.read_text(encoding='utf-8') != content:
            raise SystemExit('stale reform claim inventory: ' + path)
    print('PASS reform claim inventory')


if __name__ == '__main__':
    main()
