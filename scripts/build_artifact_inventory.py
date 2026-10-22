#!/usr/bin/env python3
"""Inventory the frozen A01-A06 input universe; never infer current status from names."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SCOPE = 'metadata/repository_audit_scope.json'
OUTPUT = 'metadata/artifact_inventory.csv'
FIELDS = [
    'path', 'file_kind', 'artifact_role', 'role_evidence', 'release_identity',
    'currency_status', 'currency_evidence', 'producer', 'producer_status',
    'producer_evidence', 'source_input_manifest', 'lineage_limit', 'retention_rule',
    'sha256', 'size_bytes', 'tracked_at_scope', 'scope_id',
]


def sha(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def manifest_paths(value):
    """Recognize existing hash manifest forms, without parsing arbitrary JSON as lineage."""
    if isinstance(value, list):
        return [r['path'] for r in value if isinstance(r, dict) and isinstance(r.get('path'), str)
                and re.fullmatch(r'[a-f0-9]{64}', str(r.get('sha256', '')))]
    if isinstance(value, dict):
        candidate = value.get('files', value)
        if isinstance(candidate, dict):
            return [p for p, digest in candidate.items() if isinstance(p, str)
                    and isinstance(digest, str) and re.fullmatch(r'[a-f0-9]{64}', digest)]
    return []


def output_memberships(root, scope):
    memberships = defaultdict(list)
    for item in scope['files']:
        p = item['path']
        if Path(p).name not in {'output_manifest.json', 'release_manifest.json', 'final_output_manifest.json'}:
            continue
        for member in manifest_paths(json.loads((root / p).read_text())):
            memberships[member].append(p)
    return memberships


def kind(path):
    suffix = Path(path).suffix.lower()
    return {'.csv': 'csv_table', '.json': 'json_record_or_collection', '.jsonpatch': 'json_patch',
            '.md': 'markdown_document', '.py': 'python_code', '.r': 'r_code',
            '.yml': 'yaml_workflow', '.pdf': 'pdf_document', '.html': 'html_document',
            '.png': 'raster_image', '.svg': 'vector_image', '.docx': 'word_document',
            '.txt': 'text_file'}.get(suffix, 'configuration_or_other')


def classify(path, memberships, pointer):
    """Separate artifact role, version identity and evidence-backed currency."""
    p = Path(path)
    if path.startswith('.github/workflows/'):
        role, evidence = 'ci_workflow', 'Workflow configuration location and YAML content'
    elif path.startswith('tests/fixtures/'):
        role, evidence = 'test_fixture', 'Test fixture location; inspect fixture label before substantive reuse'
    elif path.startswith('tests/'):
        role, evidence = 'test_code', 'Test code location and executable content'
    elif path.startswith('scripts/') or p.suffix.lower() in {'.py', '.r'}:
        role, evidence = 'production_or_analysis_code', 'Executable code; validation and production responsibilities may overlap'
    elif path.startswith('data/standards/') or path in {'data/current_research_reference.json'}:
        role, evidence = 'control_record', 'Foundation standard or explicit research-reference pointer'
    elif '/templates/' in path:
        role, evidence = 'empty_or_design_template', 'Protocol template location; does not establish completed activity'
    elif '/sources/' in path or '/originals/' in path or '/source_capture/' in path:
        role, evidence = 'retained_source_capture', 'Declared source/original capture location; authenticity is a separate review'
    elif path in memberships:
        role, evidence = 'manifested_release_output', ';'.join(sorted(memberships[path]))
    elif path.startswith('reports/'):
        role, evidence = 'report_component', 'Versioned report tree; can include narrative, analysis, figures and rendered deliverables'
    elif path.startswith('data/'):
        role, evidence = 'analytical_data_unresolved', 'Data table/record; canonicality and derivation require explicit review'
    elif path.startswith('docs/'):
        role, evidence = 'research_or_standard_document', 'Documentation; currency is assessed independently'
    elif path.startswith('assets/'):
        role, evidence = 'presentation_asset', 'Presentation asset location'
    elif path == 'README.md':
        role, evidence = 'navigation_and_status_document', 'Repository entry point; historical and current statements coexist'
    else:
        role, evidence = 'configuration_or_unresolved', 'No stronger role established by this inventory'
    release = re.search(r'(?:^|/)(census_v\d+|white_paper_\d{4}-\d{2}-\d{2})(?:/|$)', path)
    release_id = release.group(1) if release else 'unversioned_or_not_established'
    if path == pointer.get('reference_path'):
        currency, authority = 'designated_current_research_reference', 'data/current_research_reference.json:reference_path; fixed V8/V9 scope only'
    elif path == 'data/current_research_reference.json':
        currency, authority = 'research_reference_pointer', 'Explicit pointer content; not whole-project canonical manifest'
    elif path.startswith('data/standards/') or path in {
        'docs/foundation_standards.md', 'docs/desired_end_state.md', 'docs/decision_taxonomy.md',
        'docs/candidate_advancement.md', 'docs/source_authority_standard.md',
        'docs/cost_accounting_standard.md', 'docs/guardrail_standard.md',
    }:
        currency, authority = 'prospective_foundation_standard', 'F01-F06 task authorization; no operational case promotion'
    else:
        currency, authority = 'not_established_by_inventory', 'Version/path or manifest membership does not establish currency, supersession, adoption or implementation'
    return role, evidence, release_id, currency, authority


def producer_for(root, path, memberships):
    """Use only a release's declared output root and explicit build/check entrypoint."""
    declarations = {
        'data/census_v8/': ('scripts/build_v8_pilot.py', 'data/census_v8/output_manifest.json'),
        'data/census_v9/': ('scripts/v9_cyprus.py', 'data/census_v9/output_manifest.json'),
        'data/census_v10/': ('scripts/build_v10_protocol.py', 'data/census_v10/output_manifest.json'),
        'data/census_v11/': ('scripts/rehearse_v11.py', 'data/census_v11/output_manifest.json'),
        'data/census_v12/': ('scripts/prepare_v12_patch.py', 'data/census_v12/output_manifest.json'),
        'data/census_v13/': ('scripts/adopt_v13_reference.py', 'data/census_v13/output_manifest.json'),
    }
    for prefix, (script, manifest) in declarations.items():
        if path.startswith(prefix) and manifest in memberships.get(path, []):
            body = (root / script).read_text()
            if prefix in body:
                return script, 'release_generator_association', f'{manifest} membership; {script} declares {prefix}'
    return '', 'not_established', 'File-specific writer not established; consult A04 lineage and code before moving files'


def build(root: Path):
    scope = json.loads((root / SCOPE).read_text())
    require(isinstance(scope.get('files'), list) and scope['files'], 'Missing frozen file universe')
    paths = [r['path'] for r in scope['files']]
    require(len(paths) == len(set(paths)), 'Duplicate path in frozen scope')
    pointer = json.loads((root / 'data/current_research_reference.json').read_text())
    memberships = output_memberships(root, scope)
    rows = []
    for item in sorted(scope['files'], key=lambda x: x['path']):
        path = item['path']
        require(not Path(path).is_absolute() and '..' not in Path(path).parts, f'Unsafe scope path: {path}')
        body = (root / path).read_bytes()
        require(sha(body) == item['sha256'] and len(body) == item['size_bytes'], f'Scope content changed: {path}')
        role, evidence, release, currency, currency_evidence = classify(path, memberships, pointer)
        producer, producer_status, producer_evidence = producer_for(root, path, memberships)
        parent = Path(path).parent
        manifests = [str(parent / n) for n in ('input_manifest.json', 'frozen_input_manifest.json', 'frozen_input_manifest.csv')
                     if str(parent / n) in paths]
        rows.append(dict(zip(FIELDS, [path, kind(path), role, evidence, release, currency,
            currency_evidence, producer, producer_status, producer_evidence, ';'.join(manifests),
            'Release input manifest is contextual, not proof every listed input produces this individual file',
            'preserve_byte_identical_source_or_release' if role in {'retained_source_capture', 'manifested_release_output'} else 'retain_until_explicit_reviewed_migration',
            item['sha256'], str(item['size_bytes']), str(item['tracked']).lower(), scope['scope_id']])))
    return rows


def encode(rows):
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=FIELDS, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--write', action='store_true', help='Generate the inventory; otherwise check exact output')
    mode.add_argument('--check', action='store_true', help='Check exact output (the default)')
    args = parser.parse_args()
    rows = build(ROOT)
    expected = encode(rows)
    target = ROOT / OUTPUT
    if args.write:
        target.write_text(expected, encoding='utf-8')
    else:
        require(target.read_text() == expected, 'Inventory differs; review frozen scope, then regenerate')
    print(f'PASS: {len(rows)} frozen input files; roles={dict(sorted(Counter(r["artifact_role"] for r in rows).items()))}')
    print('Current authority and file-specific lineage remain explicit where not established; no files moved.')


if __name__ == '__main__':
    main()
