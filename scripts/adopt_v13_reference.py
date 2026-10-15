#!/usr/bin/env python3
"""Adopt the user-authorized V12 payload into a new, additive research reference.

No network, source re-extraction, full-corpus rescoring, owner approval or live use.
--build creates only new V13 outputs; existing output drift is rejected.
--check replays adoption and the two affected-view checks without writing files.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path
import prepare_v12_patch as patch

ROOT = Path(__file__).resolve().parents[1]
OUT = 'data/census_v13/'
BASE = 'cdb5a3e1b6690e2c5b7a9dfaebfd639fb307f9f3'
REF = '13.0'
TARGETS = {'V9:CY028': 'AM11-01', 'V9:CY041': 'AM11-02'}
PRODUCTS = {'V9:G2': ('S/2026/9', 6), 'V9:G3': ('S/2026/551', 8)}
AUTHORITY = {
    'authority_type': 'explicit_user_instruction_research_reference_only',
    'request_timestamp_utc': '2026-10-15T20:58:38Z',
    'authorized_amendments': ['AM11-01', 'AM11-02'],
    'authorized_action': 'adopt_new_research_reference_and_recheck_only_affected_views',
    'institutional_approval': False,
    'live_use_authorized': False,
}
PINS = {
    'data/census_v12/patch_contract.json': 'd2686fc5e176aebafd34a57a87d35b551fb6eafc0a01337627b78ee0ac9194be',
    'data/census_v12/reference_preview.json': '4059dfffbb370c131a27db760487eb425ae302d530c3509eaf3814e70bce2b65',
    'data/census_v12/reference_delta.jsonpatch': 'f7b44849eeac33ce50af4c0b50a7b17a9ed12d51da0c8eedc4d070b9d899559e',
    'data/census_v12/reference_inverse.jsonpatch': '5baac0033397f3f23d4b56db9977b070468b638709e272cec7df263dd34f2e94',
    'data/census_v12/source_evidence.json': 'be4c8656ea60ff55e786204129ffb54d937ed7ddbf4dfdd2f4b25f0694754afa',
    'data/census_v11/obligation_reviews.csv': 'de6af1d3e47f3bb54a636bf9a07b9d388ed9921e9b3aff59b226afa9d64497d2',
    'scripts/prepare_v12_patch.py': 'f0ae7a87b2dfc0f04c6c38f9532fc6a6c6778130738b961c23ec8770e071b1b4',
}
EXPECTED = {
    'V9:CY028': 'Through the Joint Contact Rooms, the Technical Committee on Crime and Criminal Matters exchanged information in 202 instances and separately exchanged three individuals in custody. These are different actions and units.',
    'V9:CY041': 'Phase two was extended through 2026. By June 2026 approximately 67% of EUR1.5 million allocated for 2023-2026 had been utilized; more than EUR1.7 million had been utilized since inception in 2019. The two amounts have different perimeters and are not savings.',
}
ensure = patch.ensure
encode = patch.encode
sha = patch.sha


def pinned_inputs(root: Path) -> dict:
    for name, value in PINS.items():
        ensure(sha((root / name).read_bytes()) == value, 'Adoption input changed: ' + name)
    pins = patch.verify_inputs(root)  # Integrity only; no substantive source review.
    pins.update(PINS)
    return pins


def render_view(product: str, rows: list[dict], evidence: dict) -> str:
    ensure(product in PRODUCTS, 'Unrequested product view')
    selected = [r for r in rows if r['product_id'] == product]
    ensure(len(selected) == PRODUCTS[product][1], 'Affected view membership changed')
    lines = [f'# Research reference {REF}: {product} support view', '',
             f'**{PRODUCTS[product][0]} | Research-only adoption | Live use blocked**', '',
             'Only the amended assertion is rechecked. Other selected assertions below are carried forward unchanged, not newly rescored. This is a support sheet, not a replacement UN report or an approved operational output.', '']
    for row in selected:
        oid = row['observation_id']
        lines += [f'## {oid}', '',
                  f"Source: {PRODUCTS[product][0]}, {row['locator']}, PDF pages {row['pages']}.",
                  f"Attribution: `{row['attribution_class']}`. Required action: `{row['required_action']}`.",
                  f"Original-file SHA-256: `{row['source_sha256']}`.", '', row['source_assertion'], '',
                  'Qualified values (null remains unknown):', '```json',
                  json.dumps(json.loads(row['qualified_values']), ensure_ascii=False, indent=2, sort_keys=True), '```', '']
        if oid in TARGETS:
            source = evidence[TARGETS[oid]]
            lines += [f"Provenance: [original source]({source['original_url']}), paragraph {source['paragraph']}, page {source['page']}.",
                      f"Research amendment `{TARGETS[oid]}` adopted. Historical first pass: `amendment_requested_scoring_withheld`. Current disposition: `post_amendment_affected_recheck_passed`.", '']
        else:
            lines += ['Current treatment: `carried_forward_unchanged_not_reassessed`.', '']
    lines += ['Separate owner approval is still absent. No staffing, operational or financial effect is inferred.', '']
    return '\n'.join(lines)


def check_affected(rows: list[dict], views: dict[str, str]) -> list[dict]:
    ensure(set(views) == set(PRODUCTS), 'Recheck must contain exactly two affected views')
    by_id = {r['observation_id']: r for r in rows}
    checks = []
    for oid, amendment in TARGETS.items():
        row = by_id[oid]
        ensure(row['source_assertion'] == EXPECTED[oid], 'Adopted assertion changed: ' + oid)
        ensure(row['product_id'] in PRODUCTS, 'Amended assertion moved to wrong view')
        text = views[row['product_id']]
        ensure(text.count('## ' + oid + '\n') == 1 and text.count(EXPECTED[oid]) == 1,
               'Amended rendering missing, repeated or altered')
        values = json.loads(row['qualified_values'])
        ensure(json.dumps(values, ensure_ascii=False, indent=2, sort_keys=True) in text,
               'Rendered qualified values differ from adopted row')
        ensure(row['source_sha256'] in text and row['locator'] in text and
               row['attribution_class'] in text, 'Rendered provenance missing')
        ensure('Historical first pass: `amendment_requested_scoring_withheld`' in text,
               'First-pass hold hidden')
        if oid == 'V9:CY028':
            ensure(row['product_id'] == 'V9:G2', 'Custody view changed')
            ensure(values['count'] == values['information_exchange_instances'] == 202 and
                   values['custody_exchange_count'] == 3 and values['custody_unit'] == 'individuals' and
                   values['custody_action'] == 'exchange_of_individuals_in_custody' and
                   values['period'] == '2025-06-12/2025-12-15', 'Action/unit/period fidelity failed')
            detail = 'Two actions and units preserved; 202 alias is nonadditive; no combined 205 count.'
        else:
            ensure(row['product_id'] == 'V9:G3', 'Lifetime view changed')
            ensure(values['lifetime_utilized_eur_comparator'] == '>' and
                   values['lifetime_utilized_eur_lower_bound'] == 1700000 and
                   values['lifetime_period_start_year'] == 2019 and
                   values['allocation_eur'] == 1500000 and values['allocation_period'] == '2023-2026' and
                   values['asof'] == '2026-06' and values['percent'] == 67 and
                   values['comparator'] == 'approximately' and values['savings'] is None,
                   'Strict bound/period/financial fidelity failed')
            detail = 'Strict lifetime bound and inception retained; approximate allocation measure remains separate.'
        checks.append(dict(amendment_id=amendment, observation_id=oid, product_id=row['product_id'],
                           obligation_id=row['obligation_id'], reference_version=REF,
                           historical_first_pass='amendment_requested_scoring_withheld',
                           current_result='post_amendment_affected_recheck_passed',
                           checks=detail, source_review_basis='retained_V11_V12_source_review_not_reperformed',
                           reviewer='assistant_with_prior_exposure_not_independent_human_or_owner',
                           live_gate='BLOCKED_FOR_LIVE_USE'))
    return checks


def outputs(root: Path) -> dict[str, bytes]:
    pins = pinned_inputs(root)
    old = patch.read_json(root, patch.CANDIDATE)
    changes = patch.read_json(root, patch.REQUESTS)
    forward = patch.read_json(root, 'data/census_v12/reference_delta.jsonpatch')
    new = patch.replay(old, forward)
    patch.validate_preview(old, new, forward, changes)
    payload = (root / 'data/census_v12/reference_preview.json').read_bytes()
    ensure(json.loads(payload) == new, 'Prepared payload does not match replay')
    ensure(patch.replay(new, patch.read_json(root, 'data/census_v12/reference_inverse.jsonpatch')) == old,
           'Inverse lineage failed')
    reviews = patch.read_csv(root, 'data/census_v11/obligation_reviews.csv')
    ensure(Counter(r['first_pass_disposition'] for r in reviews) ==
           {'supported': 59, 'amendment_requested_scoring_withheld': 2}, 'First-pass history changed')
    reviewed = {r['observation_id']: r for r in reviews}
    evidence = {r['amendment_id']: r for r in patch.read_json(root, 'data/census_v12/source_evidence.json')}
    gates = patch.closed_gates(root)
    views = {pid: render_view(pid, new, evidence) for pid in PRODUCTS}
    rechecks = check_affected(new, views)
    history, amendments = [], []
    for a, b in zip(old, new):
        oid = a['observation_id']
        changed = oid in TARGETS
        ensure((a != b) == changed, 'Unintended row difference')
        history.append(dict(obligation_id=a['obligation_id'], observation_id=oid, product_id=a['product_id'],
                            first_pass_disposition=reviewed[oid]['first_pass_disposition'],
                            amendment_id=TARGETS.get(oid, ''),
                            current_reference=REF,
                            current_disposition='post_amendment_affected_recheck_passed' if changed else
                                                'carried_forward_unchanged_not_reassessed',
                            historical_row_sha256=patch.row_hash(a), adopted_row_sha256=patch.row_hash(b),
                            owner_review='not_performed'))
        if changed:
            source = evidence[TARGETS[oid]]
            amendments.append(dict(amendment_id=TARGETS[oid], observation_id=oid, product_id=a['product_id'],
                                   disposition='adopted_in_research_reference_13.0',
                                   before_row_sha256=patch.row_hash(a), after_row_sha256=patch.row_hash(b),
                                   before_assertion=a['source_assertion'], adopted_assertion=b['source_assertion'],
                                   source_symbol=source['source_symbol'], source_page=source['page'],
                                   source_paragraph=source['paragraph'], source_sha256=source['source_sha256']))
    summary = dict(version=REF, status='adopted_research_reference_affected_recheck_complete', baseline_commit=BASE,
                   reference_sha256=sha(payload), adopted_amendments=2, fixed_obligations=61,
                   source_observations=64, total_product_views=12, reference_rows_changed=2,
                   reference_rows_unchanged=59, affected_product_views_rechecked=2,
                   amended_assertions_rechecked=2, post_amendment_assertions_passed=2,
                   unchanged_assertions_carried_in_affected_views=12, unaffected_views_regenerated=0,
                   historical_first_pass_supported=59, historical_first_pass_amendment_holds=2,
                   current_amendment_holds_for_these_two=0, fresh_full_corpus_score='not_run',
                   first_pass_results_rewritten=False, owner_reviews=0, owner_approvals=0, live_trials=0,
                   live_staff_measurements=0, live_gate_status='BLOCKED_FOR_LIVE_USE',
                   course_watch='paused_no_reactivation_no_checks_run', staff_time_saved='not_estimated',
                   cash_savings='not_estimated', mandates_approvals_rankings='unchanged',
                   retrospective_2027_support='20/32 unchanged',
                   review_basis='affected_renderings_against_adopted_source_checked_patch; no new source adjudication')
    adoption = dict(reference_id='UNPO-REF-13.0', version=REF, baseline_commit=BASE,
                    authority=AUTHORITY, status='adopted_for_research_only',
                    adopted_reference_path=OUT+'research_reference.json', adopted_reference_sha256=sha(payload),
                    payload_identical_to='data/census_v12/reference_preview.json',
                    historical_first_pass_path='data/census_v11/obligation_reviews.csv',
                    current_dispositions_path=OUT+'reference_lineage.csv',
                    amendment_dispositions=amendments,
                    scoring_scope='two post-amendment affected assertions only; not a new 61-obligation first pass',
                    rollback='Retain V13 history and explicitly select the preceding reference; do not edit historical versions.',
                    institutional_clearance='not_obtained', live_use='BLOCKED_FOR_LIVE_USE')
    files = {OUT+'research_reference.json': payload, OUT+'adoption_record.json': encode(adoption),
             OUT+'reference_lineage.csv': patch.csv_bytes(history),
             OUT+'affected_recheck.csv': patch.csv_bytes(rechecks),
             OUT+'closed_gate_receipt.json': encode(dict(research_reference_adopted=True, live_gates=gates,
                                                        owner_approval=False, live_execution=False)),
             OUT+'summary.json': encode(summary), OUT+'input_manifest.json': encode(pins)}
    for pid, text in views.items():
        files[OUT+'views/'+pid.replace(':','_')+'.md'] = text.encode()
    report = '''# V13: Research-reference adoption and affected-view recheck

**15 October 2026 | Research reference 13.0 adopted | Live use blocked**

## Decision

AM11-01 and AM11-02 are adopted under the user's explicit 15 October 2026, 20:58:38 UTC instruction. The new research reference contains the exact byte-identical V12 candidate payload; no additional substantive edits are made. The [adoption record](../data/census_v13/adoption_record.json) is the new version's authority and lineage record. This is project research authorization, not UN owner approval.

## Changes and affected views

| Amendment | Corrected reference | Affected view | Result |
|---|---|---|---|
| AM11-01 / V9:CY028 | Keep 202 information-exchange instances distinct from the exchange of three individuals in custody. The added 202 field aliases, rather than adds to, the inherited count. | [V9:G2 / S/2026/9](../data/census_v13/views/V9_G2.md) | Post-amendment rendering check passed. |
| AM11-02 / V9:CY041 | Explicitly retain more than EUR1.7 million since 2019, separately from approximately 67% of EUR1.5 million allocated for 2023-2026 as of June 2026. | [V9:G3 / S/2026/551](../data/census_v13/views/V9_G3.md) | Post-amendment rendering check passed. |

Source support remains the narrow V11/V12 review of S/2026/9 paragraph 18, page 3, and S/2026/551 paragraph 29, page 5. See the [retained source record](../data/census_v12/source_evidence.json) and [prepared patch](v12_reference_correction_patch.md). This adoption checks rendering, inherited qualifications and provenance against that already reviewed patch. It does not claim another source extraction, independent semantic review or whole-document audit.

## First pass versus amended recheck

The historical first pass remains **59 supported unchanged and two amendment holds** out of the fixed 61 obligations. Those historical outcomes are not rewritten. In reference 13.0, both amendments are adopted and their two affected assertions pass the separate post-amendment check. Their current amendment holds are therefore resolved for research use only. There is **no new 61/61 first-pass score**.

All 59 untargeted reference row objects remain identical. Only two affected product-specific sheets are generated: six selected obligations in G2 and eight in G3. Twelve of those assertions are carried forward unchanged, not substantively reassessed. The other ten views are not regenerated. The fixed inventory remains 64 source observations, 61 obligations and 12 product identities.

The [61-row lineage register](../data/census_v13/reference_lineage.csv) separates immutable first-pass dispositions from current research status. The [two-row recheck register](../data/census_v13/affected_recheck.csv) records exactly what was checked. Historical V8-V12 files, candidate-status records and original sources remain unchanged; their earlier statuses describe those historical versions, not the new adopted version.

## Controls and limits

Both SP08P1 and SP09P1 remain **BLOCKED_FOR_LIVE_USE**. Local activation fields remain unset and the nine V10 instruments remain empty. No owner clearance, live trial, staff measurement, course check, task scheduling, operational change or financial estimate is introduced. Mandates, approvals, parent and mission rankings, and the earlier 20/32 support count remain unchanged.

Checks cover exact V12 payload identity, guarded forward/inverse replay, two-row locality, first-pass lineage, action/unit and strict-lower-bound fidelity, rendered provenance and closed activation gates. Input hash checks are preservation controls, not fresh substantive review of unaffected claims. Rechecks are assistant-conducted with prior exposure, not independent human or institutional review.

## Reproduction and handoff

Run `python scripts/adopt_v13_reference.py --check` and `python tests/check_v13_reference.py` from the repository. The build option creates only missing V13 outputs and refuses drift in an existing release. It neither edits nor adopts older reference files. The [summary](../data/census_v13/summary.json) and [output hashes](../data/census_v13/output_manifest.json) describe this bounded release.

This completes the two-amendment research correction. The next substantive boundary is review by the existing workflow owners under the V10 protocol, not another automatic rehearsal or a live start. Neither successful checks nor research-reference adoption supply that authorization.
'''
    files['docs/v13_reference_adoption.md'] = report.encode()
    files[OUT+'output_manifest.json'] = encode({name: sha(body) for name, body in files.items()})
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--build', action='store_true')
    group.add_argument('--check', action='store_true')
    args = parser.parse_args()
    files = outputs(ROOT)
    # Inspect all existing outputs before writing any missing output.
    for name, body in files.items():
        path = ROOT / name
        ensure(not path.exists() or path.read_bytes() == body, 'Existing release drift: ' + name)
        if args.check:
            ensure(path.is_file(), 'Missing adoption output: ' + name)
    if args.build:
        for name, body in files.items():
            path = ROOT / name
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(body)
    for name, body in files.items():
        ensure((ROOT/name).read_bytes() == body, 'Output mismatch: ' + name)
    patch.closed_gates(ROOT)
    print(json.dumps(dict(status='PASS_research_adoption_and_affected_views_only',
                          output_files=len(files), adopted_amendments=2, affected_views=2,
                          first_pass='59 supported; 2 historical holds retained',
                          post_amendment='2 affected assertion checks passed',
                          live_use='BLOCKED_FOR_LIVE_USE'), indent=2))

if __name__ == '__main__':
    main()
