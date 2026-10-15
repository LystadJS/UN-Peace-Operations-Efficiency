#!/usr/bin/env python3
"""Build/check a guarded AM11 correction preview; never edit or adopt a reference.

--build writes only V12 candidate outputs. --check replays and compares them.
--source-check additionally re-extracts two retained original PDF passages.
The assistant-reviewed repair is not independent human or institutional approval.
"""
from __future__ import annotations
import argparse
import copy
import csv
import hashlib
import io
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = 'data/census_v12/'
BASE = '2e8d5c6303d677f4c7fd797d6cd679309ce69f9d'
CANDIDATE = 'data/census_v11/initial_candidate.json'
REQUESTS = 'data/census_v11/amendment_requests.json'
PINNED = {
    CANDIDATE: 'f111f2f0156a021a947129158f36cf5ef49d135eaf3b63df40a43836068afd51',
    REQUESTS: 'd71fc9e472d3455e3b257d8849ca5b8e7817d1b0989d6e7ff365df0d486a63c5',
    'data/census_v11/output_manifest.json': '701bed3d58183eb8ecd8f5457e2dd18156a94f0c3f6c915980a6bdc6d9f8f4b4',
    'data/census_v11/frozen_input_manifest.json': '3c4dfe30e1c729e96cf6467b9027c8688909173af8a4dcd7388186f412d12203',
    'data/census_v11/validation_receipt.json': 'f56be546836635061c7ae2b75ed65ed8529db8b3ad0a70b4461f630edae05c5a',
    'data/census_v10/activation_status.json': '907521e172a99645ecb535566c59cb1a85be23fd4fcd3202b2007ebc1bdf8d48',
    'data/census_v10/protocol.json': '8b257060a493d867e5a7e28fafbb071b5e41c96d140c63565499515ecd8bb8ec',
    'data/census_v10/product_obligations.csv': 'df511a8ac721738bb3de57d9c0be1d5fe4ce57eed9bcbf8e13533e22e0e1cb70',
    'data/census_v10/fixed_source_scope.csv': 'e6689a562982f46ab616a13dd3a9ec7bb9beb3e8082ec35d8d4667823e59a678',
    'data/census_v9/reviewed_design.json': '4878dbbe77344be458ac948ada7de6124c44c8f575351af2835489ff88262dd7',
}
TARGETS = {'AM11-01': 'V9:CY028', 'AM11-02': 'V9:CY041'}


def ensure(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def sha(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def encode(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode()


def row_hash(value: object) -> str:
    return sha(encode(value))


def read_json(root: Path, name: str):
    return json.loads((root / name).read_text(encoding='utf-8'))


def read_csv(root: Path, name: str) -> list[dict]:
    with (root / name).open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def csv_bytes(rows: list[dict]) -> bytes:
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    for row in rows:
        writer.writerow({k: json.dumps(v, ensure_ascii=False, sort_keys=True)
                         if isinstance(v, (dict, list)) else v for k, v in row.items()})
    return buffer.getvalue().encode()


def closed_gates(root: Path) -> dict:
    protocol = read_json(root, 'data/census_v10/protocol.json')
    ensure(protocol['authorization_status'] == 'not_authorized_for_live_use', 'Live authority changed')
    ensure(protocol['safeguards']['automatic_start'] is False, 'Automatic start enabled')
    ensure(all(v is None for a in protocol['case_activation'].values() for v in a.values()),
           'An activation field has been populated')
    gates = read_json(root, 'data/census_v10/activation_status.json')
    ensure(set(gates) == {'SP08P1', 'SP09P1'}, 'Case scope changed')
    for case in gates.values():
        ensure(case['status'] == 'BLOCKED_FOR_LIVE_USE' and
               case['live_execution_authorized'] is False and
               case['institutional_authority_verified'] is False, 'A live gate is open')
    templates = sorted((root / 'data/census_v10/templates').glob('*.csv'))
    ensure(len(templates) == 9, 'Expected nine empty instruments')
    ensure(all(not read_csv(root, str(p.relative_to(root))) for p in templates), 'Instrument populated')
    return gates


def verify_inputs(root: Path) -> dict:
    pins = dict(PINNED)
    # Hash-pinned manifests transitively protect historical data and summaries.
    for name in ('data/census_v11/output_manifest.json', 'data/census_v11/frozen_input_manifest.json'):
        ensure(sha((root / name).read_bytes()) == PINNED[name], 'Manifest changed: ' + name)
        for path, digest in read_json(root, name).items():
            ensure(path.split('/')[0] in {'data', 'docs', 'scripts', 'tests'}, 'Unsafe source path')
            ensure((root / path).resolve().is_relative_to(root.resolve()), 'Source escapes repository')
            ensure(path not in pins or pins[path] == digest, 'Conflicting source hashes')
            pins[path] = digest
    for name, digest in pins.items():
        ensure(sha((root / name).read_bytes()) == digest, 'Frozen input changed: ' + name)
    closed_gates(root)
    return pins


def operations(before: list[dict], amendments: list[dict]) -> list[dict]:
    ensure(len(before) == 61 and len({r['observation_id'] for r in before}) == 61, 'Wrong obligation population')
    ensure(len(amendments) == 2 and {a['amendment_id']: a['observation_id'] for a in amendments} == TARGETS,
           'Amendment scope changed')
    result = []
    for a in amendments:
        ensure(a['status'] == 'proposed_source_checked_not_applied_to_frozen_reference' and
               a['owner_approval'] == 'not_obtained', 'Amendment adoption state changed')
        index = next(i for i, r in enumerate(before) if r['observation_id'] == a['observation_id'])
        row = before[index]
        for field in ('observation_id', 'source_sha256', 'source_assertion', 'qualified_values'):
            result.append({'op': 'test', 'path': f'/{index}/{field}', 'value': row[field]})
        values = json.loads(row['qualified_values'])
        ensure(not (set(values) & set(a['value_updates'])), 'An additive value update overwrites a field')
        values.update(a['value_updates'])
        result.extend([
            {'op': 'replace', 'path': f'/{index}/source_assertion', 'value': a['proposed_assertion']},
            {'op': 'replace', 'path': f'/{index}/qualified_values',
             'value': json.dumps(values, ensure_ascii=False, sort_keys=True, separators=(',', ':'))},
        ])
    return result


def replay(before: list[dict], ops: list[dict]) -> list[dict]:
    """Small fail-closed RFC6902 test/replace subset; returns an in-memory copy."""
    rows = copy.deepcopy(before)
    for op in ops:
        ensure(set(op) == {'op', 'path', 'value'}, 'Unsupported operation fields')
        match = re.fullmatch(r'/(\d+)/(observation_id|source_sha256|source_assertion|qualified_values)', op['path'])
        ensure(match is not None, 'Unsupported JSON Pointer')
        index, field = int(match[1]), match[2]
        ensure(index < len(rows) and field in rows[index], 'Invalid target')
        if op['op'] == 'test':
            ensure(rows[index][field] == op['value'], 'Patch precondition failed: ' + op['path'])
        elif op['op'] == 'replace':
            ensure(field in {'source_assertion', 'qualified_values'}, 'Identity or provenance edit forbidden')
            rows[index][field] = op['value']
        else:
            raise ValueError('Only test/replace operations are supported')
    return rows


def validate_preview(before: list[dict], after: list[dict], ops: list[dict], amendments: list[dict]) -> None:
    ensure(ops == operations(before, amendments), 'Patch differs from the bounded approved-for-preparation proposal')
    ensure(after == replay(before, ops), 'Preview does not match patch')
    changed = [a['observation_id'] for a, b in zip(before, after) if a != b]
    ensure(len(after) == len(before) and set(changed) == set(TARGETS.values()), 'Collateral reference change')
    for old, new in zip(before, after):
        ensure(set(old) == set(new), 'Row schema changed')
        ensure(all(old[k] == new[k] for k in old if k not in {'source_assertion', 'qualified_values'}),
               'Identity, attribution or source locator changed')
        a, b = json.loads(old['qualified_values']), json.loads(new['qualified_values'])
        ensure(all(k in b and b[k] == v for k, v in a.items()), 'An inherited qualified value was lost')
    keyed = {r['observation_id']: r for r in after}
    custody = json.loads(keyed['V9:CY028']['qualified_values'])
    ensure(custody['information_exchange_instances'] == custody['count'] == 202 and
           custody['custody_exchange_count'] == 3 and
           custody['custody_action'] == 'exchange_of_individuals_in_custody', 'Custody action/count lost')
    money = json.loads(keyed['V9:CY041']['qualified_values'])
    ensure(money['lifetime_utilized_eur_comparator'] == '>' and money['lifetime_period_start_year'] == 2019,
           'Strict lower bound or inception period lost')
    ensure(money['allocation_eur'] == 1500000 and money['allocation_period'] == '2023-2026' and
           money['percent'] == 67 and money['comparator'] == 'approximately' and money['savings'] is None,
           'Allocation perimeter/qualification or financial boundary changed')


def verify_source_text(root: Path) -> None:
    import fitz
    from pypdf import PdfReader
    # Some PDF extractors insert spaces within words; ignore whitespace for locator checks only.
    norm = lambda t: re.sub(r'\s+', '', unicodedata.normalize('NFKC', t)).casefold()
    design = read_json(root, 'data/census_v9/reviewed_design.json')
    for symbol, page, phrases in (
        ('S/2026/9', 3, ['exchanged information on 202 instances and exchanged three individuals in custody']),
        ('S/2026/551', 5, ['approximately 67 per cent', '1.5 million euros', '2023–2026',
                           'Over 1.7 million euros have been utilized', 'since its inception in 2019']),
    ):
        s = next(s for s in design['sources'] if s['actual_symbol'] == symbol)
        path = root / s['file']
        ensure(sha(path.read_bytes()) == s['sha256'], 'Original PDF changed')
        with fitz.open(path) as doc:
            reader = PdfReader(path)
            ensure(len(doc) == len(reader.pages) == s['pages'], 'PDF page-count mismatch')
            ensure(symbol in doc[0].get_text(), 'Wrong source cover')
            for text in (doc[page - 1].get_text(), reader.pages[page - 1].extract_text() or ''):
                ensure(all(norm(p) in norm(text) for p in phrases), 'Source clause not recovered: ' + symbol)


def outputs(root: Path) -> dict[str, bytes]:
    pins = verify_inputs(root)
    before, amendments = read_json(root, CANDIDATE), read_json(root, REQUESTS)
    ops = operations(before, amendments)
    after = replay(before, ops)
    validate_preview(before, after, ops, amendments)
    reviews = read_csv(root, 'data/census_v11/obligation_reviews.csv')
    ensure(Counter(r['first_pass_disposition'] for r in reviews) ==
           {'supported': 59, 'amendment_requested_scoring_withheld': 2}, 'First-pass counts changed')
    ensure(len(read_csv(root, 'data/census_v10/fixed_source_scope.csv')) == 64, 'Source scope changed')
    review_map = {r['observation_id']: r for r in reviews}
    inverse, diffs, lineage = [], [], []
    for index, (old, new) in enumerate(zip(before, after)):
        amendment = next((a for a in amendments if a['observation_id'] == old['observation_id']), None)
        lineage.append(dict(obligation_id=old['obligation_id'], observation_id=old['observation_id'],
                            product_id=old['product_id'],
                            first_pass_disposition=review_map[old['observation_id']]['first_pass_disposition'],
                            amendment_id=amendment['amendment_id'] if amendment else '',
                            candidate_status='corrected_preview_not_adopted' if amendment else 'unchanged',
                            scoring_status='withheld_pending_reference_adoption' if amendment else 'prior_disposition_retained',
                            owner_review='not_performed'))
        if amendment:
            for field in ('observation_id', 'source_sha256', 'source_assertion', 'qualified_values'):
                inverse.append({'op': 'test', 'path': f'/{index}/{field}', 'value': new[field]})
            for field in ('source_assertion', 'qualified_values'):
                inverse.append({'op': 'replace', 'path': f'/{index}/{field}', 'value': old[field]})
            diffs.append(dict(amendment_id=amendment['amendment_id'], observation_id=old['observation_id'],
                              obligation_id=old['obligation_id'], product_id=old['product_id'],
                              source=amendment['source_symbol'], page=amendment['page'], paragraph=amendment['paragraph'],
                              before_row_sha256=row_hash(old), after_row_sha256=row_hash(new),
                              before_assertion=old['source_assertion'], after_assertion=new['source_assertion'],
                              additive_value_fields=amendment['value_updates'],
                              first_pass_disposition=review_map[old['observation_id']]['first_pass_disposition'],
                              disposition='prepared_not_adopted'))
    ensure(replay(after, inverse) == before, 'Round-trip restore failed')
    evidence = []
    for amendment in amendments:
        s = next(s for s in read_json(root, 'data/census_v9/reviewed_design.json')['sources']
                 if s['actual_symbol'] == amendment['source_symbol'])
        evidence.append(dict(amendment_id=amendment['amendment_id'], source_symbol=s['actual_symbol'],
                             source_path=s['file'], source_sha256=s['sha256'], original_url=s['url'],
                             page=amendment['page'], paragraph=amendment['paragraph'],
                             source_excerpt=amendment['source_excerpt'], review_scope='two retained original passages',
                             semantic_review='assistant_with_prior_exposure_not_independent_human_or_owner'))
    summary = dict(version='12.0-candidate', baseline_commit=BASE, status='prepared_not_adopted',
                   source_observations=64, fixed_obligations=61, product_views=12, candidate_changed_rows=2,
                   candidate_unchanged_rows=59, inherited_fields_deleted=0,
                   first_pass_supported_unchanged=59, first_pass_amendment_holds=2,
                   source_semantics_supported_in_V11=60, scoring_withheld=2, scoring_resumed=False,
                   reference_amendments_adopted=0, owner_approvals=0, live_trials=0,
                   live_gate_status='BLOCKED_FOR_LIVE_USE', live_staff_time_records=0,
                   course_checks_run=0, course_watch='paused_no_reactivation',
                   staff_time_saved='not_estimated', cash_savings='not_estimated',
                   mandates_and_rankings='unchanged', guard_checks='replay_locality_round_trip_first_pass_closed_gates',
                   pinned_input_files=len(pins), evaluation='candidate_repair_not_new_first_pass_or_live_result')
    contract = dict(version='12.0-candidate', baseline_commit=BASE, patch_status='prepared_not_adopted',
                    input_file=CANDIDATE, input_sha256=PINNED[CANDIDATE],
                    request_file=REQUESTS, request_sha256=PINNED[REQUESTS],
                    patch_format='RFC6902 test/replace subset; array positions guarded by identity and old values',
                    candidate_reference_file=OUT+'reference_preview.json',
                    candidate_reference_sha256=sha(encode(after)),
                    forward_patch_sha256=sha(encode(ops)), inverse_patch_sha256=sha(encode(inverse)),
                    permitted_observations=list(TARGETS.values()),
                    permitted_fields=['source_assertion', 'qualified_values'],
                    promotion='requires_explicit_research_reference_adoption; does_not_grant_live_authority',
                    rollback='discard preview layer; frozen files never modified; inverse patch restores input rows')
    files = {
        OUT+'patch_contract.json': encode(contract), OUT+'input_manifest.json': encode(pins),
        OUT+'reference_delta.jsonpatch': encode(ops), OUT+'reference_inverse.jsonpatch': encode(inverse),
        OUT+'reference_preview.json': encode(after), OUT+'correction_diff.csv': csv_bytes(diffs),
        OUT+'first_pass_lineage.csv': csv_bytes(lineage), OUT+'source_evidence.json': encode(evidence),
        OUT+'closed_gate_receipt.json': encode(dict(live_gates=closed_gates(root), reference_adopted=False,
                                                   scoring_resumed=False, owner_approval=False)),
        OUT+'patch_summary.json': encode(summary),
    }
    text = ['# V12 affected support-sheet preview', '',
            '**Prepared candidate only. Not adopted; first-pass holds remain and live-use gates are closed.**', '',
            'Only two selected assertions are previewed. The other 59 obligation rows remain exactly unchanged.', '']
    for d in diffs:
        text += [f"## {d['amendment_id']} | {d['observation_id']} | {d['product_id']}", '',
                 f"Source: **{d['source']}**, page {d['page']}, paragraph {d['paragraph']}.", '',
                 '**Frozen formulation:** '+d['before_assertion'], '',
                 '**Candidate formulation:** '+d['after_assertion'], '',
                 '**Additive structured fields:** `'+json.dumps(d['additive_value_fields'], sort_keys=True)+'`.', '',
                 '**First-pass disposition remains:** `'+d['first_pass_disposition']+'`.', '']
    text += ['The candidate preserves all inherited amounts, units, periods, source hashes, attribution and IDs.',
             'No 205-item total, exact lifetime expenditure, utilization-trend comparison or savings is calculated.',
             'Source checks establish support for these narrow repairs, not independent review or institutional approval.', '']
    files['docs/v12_affected_support_preview.md'] = '\n'.join(text).encode()
    files[OUT+'output_manifest.json'] = encode({name: sha(body) for name, body in files.items()})
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--build', action='store_true')
    mode.add_argument('--check', action='store_true')
    parser.add_argument('--source-check', action='store_true')
    args = parser.parse_args()
    files = outputs(ROOT)  # Validate everything before any write.
    if args.source_check:
        verify_source_text(ROOT)
    if args.build:
        for name, body in files.items():
            path = ROOT / name
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_suffix(path.suffix + '.tmp')
            temporary.write_bytes(body)
            temporary.replace(path)
    for name, body in files.items():
        ensure((ROOT / name).read_bytes() == body, 'Generated output drift: ' + name)
    verify_inputs(ROOT)
    print(json.dumps({'status': 'PASS_candidate_patch_integrity_not_adoption_or_live_authorization',
                      'checked_outputs': len(files), 'source_reextraction': args.source_check,
                      'changed_rows': 2, 'unchanged_rows': 59, 'first_pass_holds_retained': 2,
                      'live_gate': 'BLOCKED_FOR_LIVE_USE'}, indent=2))


if __name__ == '__main__':
    main()
