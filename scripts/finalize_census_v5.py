#!/usr/bin/env python3
"""Publish effective V5 identities, source-backed corrections and current overview.

The first-pass seed is retained. Corrections bind to public original source
bodies, not to a new inferred cohort. No global event or person total is released.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/census_v5'
EXTRA_SOURCE = 'https://unsos.unmissions.org/en/node/133222'
NETWORKING_BODY_SHA = 'badfd8c59b9ff811b5f50d05a29f351a09de735c258eeaea9638dde6b5e61660'

def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))

def write_csv(path, rows):
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(value, ensure_ascii=False) if isinstance(value, (list,dict)) else value for key,value in row.items()})

def ensure(condition, message):
    if not condition:
        raise AssertionError(message)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n', encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    seed_path = DATA / 'reviewed_evidence.json'
    data = json.loads(seed_path.read_text())
    summary = json.loads((DATA / 'index_refresh_summary.json').read_text())
    validated = json.loads((DATA / 'validation_summary.json').read_text())
    ensure(digest(seed_path) == validated['reviewed_evidence_sha256'], 'First-pass seed provenance mismatch')
    prior = read_csv(ROOT / 'data/systematic_field_training_canonical_2025_2026.csv')
    matches = [r for r in prior if r.get('canonical_id') == 'FTX005']
    ensure(len(matches) == 1, 'Prior canonical FTX005 unavailable or duplicated')
    text = ' '.join(matches[0].values())
    ensure(all(value in text for value in ('2026-04-13','2026-04-20','https://unowas.unmissions.org/en/node/135074')), 'Prior identity dates/source changed')
    network_source = next(r for r in read_csv(DATA / 'reviewed_source_fetches.csv') if r['source_id']=='V5S07')
    ensure(network_source['raw_sha256'] == NETWORKING_BODY_SHA, 'Networking source changed; re-review attendance before release')
    bridge, effective = [], []
    for event in data['events']:
        identity = 'FTX005' if event['event_id'] == 'V5E012' else event['event_id']
        state = 'confirmed_prior_event_enrichment' if identity == 'FTX005' else 'additional_v5_identity_cross_version_alias_closure_incomplete'
        bridge.append(dict(v5_record_id=event['event_id'], canonical_event_id=identity, adjudication=state,
                           new_global_event_count='not_certified',
                           evidence='exact event dates and original source matched' if identity=='FTX005' else 'no exact source URL collision found; not a complete alias search'))
        current = dict(event, canonical_event_id=identity, identity_status=state)
        if event['event_id']=='V5E005':
            current.update(event_start='2025-11-16', event_end='2025-12-17',
                           date_precision='exact_range_supplemental_source_duration_label_retained',
                           supplemental_source_id='V5S20',
                           date_enrichment_note='December report supplies 16 November start. Four-week label and 31 elapsed calendar days retained separately.')
        if event['event_id']=='V5E008':
            current.update(attendance_value=8, attendance_qualifier='sum_of_reported_subgroups',
                           subgroup='6 Somali National Army personnel and 2 Somali Police Force personnel',
                           attendance_enrichment_note='Full archived V5S07 body reports six plus two. Distinct from V5E003; cross-course participant identities remain unknown.')
        effective.append(current)
    if args.write:
        from bs4 import BeautifulSoup
        cache = Path('/tmp/census-v5-release-html')
        cache.mkdir(parents=True, exist_ok=True)
        enrichment = dict(source_id='V5S20', url=EXTRA_SOURCE, publication_date='2025-12-17', event_id='V5E005',
                          review_basis='official_article_search_index_text', supported_start='2025-11-16', supported_end='2025-12-17',
                          source_duration_label='four weeks', elapsed_calendar_days=31,
                          source_limit='Second cohort is prospective here; completed delivery relies on March 2026 V5S05. Mentorship and course counts are nonadditive.')
        try:
            request = Request(EXTRA_SOURCE, headers={'User-Agent':'Mozilla/5.0 (compatible; UN-public-source-review/1.0)'})
            with urlopen(request, timeout=20) as response:
                body = response.read(2_000_001)
                ensure(response.status==200 and len(body)<2_000_000, 'Supplement response size/status')
            sha = hashlib.sha256(body).hexdigest()
            (cache / (sha+'.html')).write_bytes(body)
            body_text = BeautifulSoup(body, 'html.parser').get_text(' ', strip=True)
            ensure('16 November' in body_text and '17 December' in body_text, 'Reviewed dates absent from supplement')
            enrichment.update(raw_fetch_status='downloaded_and_date_text_checked', raw_sha256=sha)
        except Exception as exc:
            enrichment.update(raw_fetch_status=type(exc).__name__+':'+str(exc)[:140], raw_sha256='')
        write_csv(DATA / 'canonical_identity_adjudications.csv', bridge)
        write_csv(DATA / 'effective_activity_register.csv', effective)
        save_json(DATA / 'source_date_enrichment.json', enrichment)
        attendance = dict(event_id='V5E008', source_id='V5S07', url=network_source['url'], raw_sha256=NETWORKING_BODY_SHA,
                          review_basis='original archived article body; bytes independently SHA-256 checked after Actions artifact download',
                          source_excerpt='This training benefited six personnel from the SNA and two from the Somali Police Force (SPF)',
                          reported_subgroups=[6,2], derived_cohort_count=8,
                          unique_people_across_courses='not_estimated', correction='First-pass missing count superseded in effective view; no new event added')
        save_json(DATA / 'attendance_enrichment.json', attendance)
        final = dict(asof=data['asof'], first_pass_seed_sha256=digest(seed_path), effective_activity_records=16,
                     confirmed_prior_event_enrichments=1, prior_identity='FTX005', additional_v5_identities=15,
                     global_new_unique_events='not_certified', source_date_enrichments=1, source_attendance_enrichments=1,
                     effective_register_sha256=digest(DATA / 'effective_activity_register.csv'),
                     identity_bridge_sha256=digest(DATA / 'canonical_identity_adjudications.csv'),
                     mandated_deliverables='unchanged', incremental_net_savings='not_estimated')
        save_json(DATA / 'finalization_summary.json', final)
        brief = f'''# Executive brief: systematic census and shared production

**15 October 2026 | Public sources | Mandates and existing financial gates unchanged**

## Bottom line

The official indexes now contain **{summary['council_reports']} Secretary-General reports, {summary['formal_meeting_ids']} formal Council meeting identities and {summary['meeting_variants']} transcript variants**. Six additional archives contribute **{summary['new_exact_urls_beyond_prior']} URLs**, expanding the exact source frame to **{summary['combined_exact_source_urls']:,}**. This is a bounded public-source census, not an exhaustive operational activity census.

| Evidence stratum | Previous freeze | Current |
|---|---:|---:|
| SG report symbols | {summary['prior_report_count']} | {summary['council_reports']} |
| Formal Council meeting IDs | {summary['prior_meeting_ids']} | {summary['formal_meeting_ids']} |
| Transcript variants | {summary['prior_meeting_variants']} | {summary['meeting_variants']} |
| Exact mission/department source URLs | {summary['prior_exact_source_urls']:,} | {summary['combined_exact_source_urls']:,} |

Reports comprise 84 in the 2025 index and 50 in 2026; formal meetings comprise 255 and 158 respectively. Latest indexed dates are 12 October for reports and 14 October for meetings. Resumptions remain variants; informal consultations remain outside the formal-record denominator. **S/2026/513's printed 2025 date remains flagged**, not silently corrected.

Sources: [index summary](../data/census_v5/index_refresh_summary.json), [Council changes](../data/census_v5/index_refresh/changes_from_oct12.csv), [page-access evidence](../data/census_v5/source_frame/archive_page_access.csv).

## What the activity extension establishes

**16 reviewed records** comprise 11 training/seminar cohorts, two field activities and three meetings. One field mission enriches **existing FTX005**, not a new event: the ECOWAS-UNOWAS-Commonwealth Sierra Leone mission, 13-20 April 2026. Fifteen additional V5 identities remain subject to wider title/date/entity alias closure; no global new-event total is certified.

A separate multi-visit UN-AU-NATO programme and **eight advertised courses** are not added to that count. Two scheduled periods have elapsed, one spans the cutoff and five are future; a calendar does not certify delivery. Ten activity records have at least an explicit event date; six remain publication-bounded. No unique-person total is calculated.

All 48 additional archive pages and 19 first-pass curated bodies were retrieved. All 19 body hashes were independently checked against the downloaded Actions artifact. A supplemental December UNSOS article supplies the first Beledweyne cohort's **16 November-17 December 2025** dates. Its four-week description differs from the elapsed calendar interval; instructional-day counts are not inferred. The two 11-person cohorts remain separate; the combined 22-person source total is not added again.

Full-body review also recovers **eight participants** in the advanced networking course: six army and two police personnel. This is an attendance enrichment, not a new cohort, and does not establish whether individuals also attended the earlier eight-person IT course.

Use the [effective activity register](../data/census_v5/effective_activity_register.csv) and [canonical bridge](../data/census_v5/canonical_identity_adjudications.csv). These supersede the first-pass view only for documented identity, date and attendance enrichments; the original seed remains preserved. [Date source](../data/census_v5/source_date_enrichment.json) · [Attendance source](../data/census_v5/attendance_enrichment.json).

## Recommended production tests

| Priority | Recommendation | Protected boundary |
|---|---|---|
| 1 | Connect eligible course metadata to the **existing LCM marketplace and global training schedule**, rather than create another portal. | DPO standards, provider ownership, specialized certification and mission readiness. |
| 2 | Reuse jointly scoped training-needs assessment inputs and controlled materials, building on the **7-9 April 2025 UN-AU-NATO Entebbe workshop**. | Each partner's approvals, technical requirements and future programme outputs. |
| 3 | Maintain one approved source packet for a joint field mission, with separate analytical and reporting approvals. | UNOWAS, ECOWAS, Commonwealth and CNMC responsibilities; separate Council reports. |
| 4 | Test shared UNSOS training logistics and generic administration where dates, places and requirements permit. | Distinct aviation rescue, screening, liaison and IT competencies, cohorts and safety outcomes. |
| 5 | Reuse generic supplier-orientation materials and registration guidance. | Separate tenders, evaluation independence, specifications and vendor privacy. |
| 6 | Test authorized reuse of the **existing Deployment Review application's** classifications and export definitions. | Restricted reviews, personal data and distinct performance responsibilities. |

These are ranked research and implementation tests, **not validated savings or authorized reorganizations**. [Source-linked recommendations](../data/census_v5/shared_production_recommendations.csv) retain the observed baseline, proposed shared input, protected output and next evidence gate.

## Unchanged decisions and remaining gaps

The 14-parent consolidation hierarchy, mission ranking and **20/32 previously supported 2027 output categories remain unchanged**. Previously authorized institutional reforms remain baseline arrangements. No paid duplicate service, recoverable expenditure or incremental net saving is verified.

Remaining gaps: complete cross-version event alias closure; completion records for advertised courses; the actual field/training activity denominator; explicit source-to-report/briefing production links; and authorized service/procurement cost objects. Common topics or dates alone do not establish substitutable work.

[First-pass audit](census_2025_2026_oct15_v5.md) · [Validation](../data/census_v5/validation_summary.json) · [Final identity controls](../data/census_v5/finalization_summary.json)

Rebuild effective views with `python3 scripts/finalize_census_v5.py --write`; validate retained results with `python3 scripts/finalize_census_v5.py --check`.
'''
        (ROOT / 'docs/census_2025_2026_oct15_executive.md').write_text(brief, encoding='utf-8')
        first_pass = ROOT / 'docs/census_2025_2026_oct15_v5.md'
        original = first_pass.read_text()
        if original.startswith('> **Final identity/date view:**'):
            original = original.split('\n\n',1)[1]
        note = '> **Final identity/date view:** See the [executive brief](census_2025_2026_oct15_executive.md), [effective register](../data/census_v5/effective_activity_register.csv) and [canonical bridge](../data/census_v5/canonical_identity_adjudications.csv). V5E012 enriches FTX005; V5E005 gains its 16 November start; V5E008 gains its eight-person attendance count. The first-pass audit below is retained.\n\n'
        first_pass.write_text(note+original, encoding='utf-8')
        readme_path = ROOT / 'README.md'
        readme = readme_path.read_text()
        heading = '## Latest — 15 October 2026 systematic census'
        if heading not in readme:
            marker = '## Current — 12 October 2026 source-frame census'
            ensure(marker in readme, 'README insertion anchor changed')
            block = f'''{heading}

**[Current executive brief](docs/census_2025_2026_oct15_executive.md)** · [Source-frame audit](docs/census_2025_2026_oct15_v5.md) · [Effective activities](data/census_v5/effective_activity_register.csv) · [Six shared-production tests](data/census_v5/shared_production_recommendations.csv).

The refreshed indexes contain **{summary['council_reports']} SG reports**, **{summary['formal_meeting_ids']} formal Council meeting IDs** and **{summary['meeting_variants']} transcript variants**. Six additional archives returned **48/48 pages**, adding **{summary['new_exact_urls_beyond_prior']} exact URLs** to a **{summary['combined_exact_source_urls']:,}-URL** frame. Sources are not delivered-event counts.

The extension adjudicates **16 activity records** (11 training/seminar cohorts, two field activities, three meetings), including **one enrichment of existing FTX005**, not a new Sierra Leone mission. Fifteen additional V5 identities are not a certified all-version new-event total. A multi-visit programme and eight advertised courses remain nonadditive. All 19 first-pass curated bodies were retrieved. Existing LCM and Deployment Review systems are baselines, not new platforms.

**Mandates, parent/mission rankings and 20/32 retrospective 2027-category support remain unchanged. No duplicate paid service or incremental net saving is verified.** [Offline acceptance](scripts/finalize_census_v5.py).

'''
            readme = readme.replace(marker, block+'## Historical — 12 October 2026 source-frame census',1)
        readme = readme.replace('## Latest — 13 October 2026 training and field attendance validation','## Historical — 13 October 2026 training and field attendance validation')
        readme = readme.replace('<a href="docs/census_2025_2026_attendance_executive.md"><strong>Current training & field attendance findings</strong></a>','<a href="docs/census_2025_2026_oct15_executive.md"><strong>Current census and shared-production findings</strong></a>')
        readme_path.write_text(readme, encoding='utf-8')
        workflow = ROOT / '.github/workflows/validate.yml'
        value = workflow.read_text()
        if 'scripts/finalize_census_v5.py --check' not in value:
            value += '      - name: Validate October 15 public census and canonical identity safeguards\n        run: |\n          python3 scripts/validate_census_v5.py\n          python3 scripts/finalize_census_v5.py --check\n'
            workflow.write_text(value, encoding='utf-8')
    final = json.loads((DATA / 'finalization_summary.json').read_text())
    ensure(final['first_pass_seed_sha256']==digest(seed_path), 'Effective view seed mismatch')
    ensure(final['effective_register_sha256']==digest(DATA/'effective_activity_register.csv'), 'Effective view hash mismatch')
    ensure(final['identity_bridge_sha256']==digest(DATA/'canonical_identity_adjudications.csv'), 'Identity bridge hash mismatch')
    actual = read_csv(DATA/'effective_activity_register.csv')
    ensure(len(actual)==len({r['canonical_event_id'] for r in actual})==16, 'Within-extension canonical count mismatch')
    ensure(sum(r['canonical_event_id']=='FTX005' for r in actual)==1, 'Prior field mission not reconciled')
    ensure(next(r for r in actual if r['event_id']=='V5E005')['event_start']=='2025-11-16', 'Date enrichment lost')
    ensure(next(r for r in actual if r['event_id']=='V5E008')['attendance_value']=='8', 'Attendance enrichment lost')
    ensure(final['confirmed_prior_event_enrichments']==1 and final['global_new_unique_events']=='not_certified', 'Global count overclaim')
    ensure(final['incremental_net_savings']=='not_estimated' and final['mandated_deliverables']=='unchanged', 'Financial/mandate gate changed')
    print(json.dumps(dict(status='passed_final_identity_date_attendance_and_release_checks', **final), indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
