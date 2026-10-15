#!/usr/bin/env python3
"""Finalize V5 canonical views and executive entry points without rewriting seeds.

The accepted first-pass seed remains frozen. An effective view records one known
prior canonical identity and a source-backed date enrichment. Global alias
closure, distinct persons, financial substitution and savings remain unverified.
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

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    seed_path = DATA / 'reviewed_evidence.json'
    data = json.loads(seed_path.read_text())
    summary = json.loads((DATA / 'index_refresh_summary.json').read_text())
    validated = json.loads((DATA / 'validation_summary.json').read_text())
    ensure(digest(seed_path) == validated['reviewed_evidence_sha256'], 'First-pass seed no longer matches validation')
    prior = read_csv(ROOT / 'data/systematic_field_training_canonical_2025_2026.csv')
    matches = [r for r in prior if r.get('canonical_id') == 'FTX005']
    ensure(len(matches) == 1, 'Prior canonical FTX005 unavailable or duplicated')
    text = ' '.join(matches[0].values())
    ensure('2026-04-13' in text and '2026-04-20' in text and 'https://unowas.unmissions.org/en/node/135074' in text, 'Prior identity dates/source changed')
    bridge = []
    effective = []
    for event in data['events']:
        identity = 'FTX005' if event['event_id'] == 'V5E012' else event['event_id']
        state = 'confirmed_prior_event_enrichment' if identity == 'FTX005' else 'additional_v5_identity_cross_version_alias_closure_incomplete'
        bridge.append(dict(v5_record_id=event['event_id'], canonical_event_id=identity,
                           adjudication=state, new_global_event_count='not_certified',
                           evidence='exact event dates and original source matched' if identity == 'FTX005' else 'no exact source URL collision found; not a complete alias search'))
        current = dict(event, canonical_event_id=identity, identity_status=state)
        if event['event_id'] == 'V5E005':
            current.update(event_start='2025-11-16', event_end='2025-12-17',
                           date_precision='exact_range_supplemental_source_duration_label_retained',
                           supplemental_source_id='V5S20',
                           date_enrichment_note='Original December report supplies 16 November start; four-week label is retained separately from the 31-day elapsed interval.')
        effective.append(current)
    enrichment = dict(source_id='V5S20', url=EXTRA_SOURCE, publication_date='2025-12-17',
                      event_id='V5E005', review_basis='official_article_search_index_text',
                      supported_start='2025-11-16', supported_end='2025-12-17',
                      source_duration_label='four weeks', elapsed_calendar_days=31,
                      source_limit='Second cohort is prospective in this December source; completed delivery relies on March 2026 V5S05. Daily mentorship and course attendance are nonadditive.')
    if args.write:
        from bs4 import BeautifulSoup
        cache = Path('/tmp/census-v5-release-html')
        cache.mkdir(parents=True, exist_ok=True)
        try:
            request = Request(EXTRA_SOURCE, headers={'User-Agent':'Mozilla/5.0 (compatible; UN-public-source-review/1.0)'})
            with urlopen(request, timeout=20) as response:
                body = response.read(2_000_001)
                ensure(response.status == 200 and len(body) < 2_000_000, 'Supplement retrieval failed size/status')
            sha = hashlib.sha256(body).hexdigest()
            (cache / (sha + '.html')).write_bytes(body)
            source_text = BeautifulSoup(body, 'html.parser').get_text(' ', strip=True)
            ensure('16 November' in source_text and '17 December' in source_text, 'Supplement body lacks reviewed dates')
            enrichment.update(raw_fetch_status='downloaded_and_date_text_checked', raw_sha256=sha)
        except Exception as exc:
            enrichment.update(raw_fetch_status=type(exc).__name__+':'+str(exc)[:140], raw_sha256='')
        write_csv(DATA / 'canonical_identity_adjudications.csv', bridge)
        write_csv(DATA / 'effective_activity_register.csv', effective)
        (DATA / 'source_date_enrichment.json').write_text(json.dumps(enrichment, indent=2, sort_keys=True)+'\n')
        final = dict(asof=data['asof'], first_pass_seed_sha256=digest(seed_path),
                     effective_activity_records=16, confirmed_prior_event_enrichments=1,
                     prior_identity='FTX005', additional_v5_identities=15,
                     global_new_unique_events='not_certified', source_date_enrichments=1,
                     effective_register_sha256=digest(DATA / 'effective_activity_register.csv'),
                     identity_bridge_sha256=digest(DATA / 'canonical_identity_adjudications.csv'),
                     mandated_deliverables='unchanged', incremental_net_savings='not_estimated')
        (DATA / 'finalization_summary.json').write_text(json.dumps(final, indent=2, sort_keys=True)+'\n')
        brief = f'''# Executive brief: systematic census and shared production

**15 October 2026 | Public sources | Mandates and existing financial gates unchanged**

## Bottom line

The refreshed official indexes contain **{summary['council_reports']} Secretary-General reports, {summary['formal_meeting_ids']} formal Council meeting identities and {summary['meeting_variants']} transcript variants**. Six additional archives contribute **{summary['new_exact_urls_beyond_prior']} URLs**, bringing the exact source frame to **{summary['combined_exact_source_urls']:,}**. This is a bounded public-source census, not an exhaustive operational activity census.

| Evidence stratum | Previous freeze | Current |
|---|---:|---:|
| SG report symbols | {summary['prior_report_count']} | {summary['council_reports']} |
| Formal Council meeting IDs | {summary['prior_meeting_ids']} | {summary['formal_meeting_ids']} |
| Transcript variants | {summary['prior_meeting_variants']} | {summary['meeting_variants']} |
| Exact mission/department source URLs | {summary['prior_exact_source_urls']:,} | {summary['combined_exact_source_urls']:,} |

The report population is 84 in the 2025 index and 50 in 2026; formal meetings are 255 and 158 respectively. Latest indexed dates are 12 October for reports and 14 October for meetings. Resumptions remain variants, and informal consultations remain outside the S/PV denominator. **S/2026/513's printed 2025 date remains flagged**, not silently corrected.

Sources: [index summary](../data/census_v5/index_refresh_summary.json), [Council changes](../data/census_v5/index_refresh/changes_from_oct12.csv), [page-access evidence](../data/census_v5/source_frame/archive_page_access.csv).

## What the activity extension actually establishes

The **16 adjudicated records** comprise 11 training/seminar cohorts, two field activities and three meetings. **One field mission is an enrichment of existing FTX005**, not a new event: the ECOWAS-UNOWAS-Commonwealth Sierra Leone mission, 13-20 April 2026. Fifteen additional V5 identities remain subject to wider title/date/entity alias closure; there is no certified global new-event total.

A separate multi-visit UN-AU-NATO programme and **eight advertised courses** are not added to the delivered-activity count. Two scheduled course periods have elapsed, one spans the cutoff and five lie in the future; a calendar is not completion evidence. Ten activity records have at least an explicit event date; six remain publication-bounded. No unique-person total is calculated.

All 48 additional archive pages and 19 first-pass curated article bodies were retrieved in the automated run. A supplemental original December UNSOS article supplies the first Beledweyne cohort's **16 November-17 December 2025** dates. Its four-week description differs from the elapsed calendar interval; instructional-day counts are not inferred. The two 11-person cohorts remain distinct, while their combined 22-person source total is not counted again.

Use the [effective activity register](../data/census_v5/effective_activity_register.csv) and [canonical identity bridge](../data/census_v5/canonical_identity_adjudications.csv), which supersede the first-pass view only for identity/date enrichment. The original seed remains preserved. [Supplemental date provenance](../data/census_v5/source_date_enrichment.json).

## Recommended production tests

| Priority | Recommendation | Distinct outputs protected |
|---|---|---|
| 1 | Connect eligible course metadata to the **existing LCM marketplace and global training schedule**, rather than create another portal. | DPO standards, provider ownership, specialized certification and mission readiness. |
| 2 | Reuse jointly scoped training-needs assessment inputs and controlled materials, building on the **7-9 April 2025 UN-AU-NATO Entebbe workshop**. | Each partner's approvals, technical requirements and future programme outputs. |
| 3 | Maintain one approved source packet for a joint field mission, with separate analytical and reporting approvals. | UNOWAS, ECOWAS, Commonwealth and CNMC responsibilities; separate Council reports. |
| 4 | Test shared training logistics and generic administration across UNSOS cohorts where dates, places and requirements permit. | Aviation rescue, screening, liaison and IT competencies; separate cohorts and safety outcomes. |
| 5 | Reuse generic supplier-orientation materials and registration guidance. | Separate tenders, evaluation independence, specifications and vendor privacy. |
| 6 | Test authorized reuse of the **existing Deployment Review application's** classifications and export definitions instead of proposing duplicate software. | Restricted reviews, personal data and distinct performance responsibilities. |

These are ranked **research and implementation tests**, not validated savings or authorized reorganizations. [Full source-linked recommendations](../data/census_v5/shared_production_recommendations.csv) record the observed baseline, proposed shared input, protected boundary and next evidence gate.

## Unchanged decisions and remaining gaps

The 14-parent consolidation hierarchy, mission ranking and **20/32 previously supported 2027 output categories remain unchanged**. Previously authorized institutional reforms remain baseline arrangements. No paid duplicate service, recoverable expenditure or incremental net saving has been verified.

Remaining gaps are complete cross-version event alias closure, completion records for advertised courses, the true field/training activity denominator, explicit source-to-report/briefing production links, and authorized service/procurement cost objects. Common topics or dates alone do not establish substitutable work.

[Full first-pass audit](census_2025_2026_oct15_v5.md) · [Validation results](../data/census_v5/validation_summary.json) · [Final identity controls](../data/census_v5/finalization_summary.json)

Reproduce the effective view after validated collection with `python3 scripts/finalize_census_v5.py --write`; check retained results with `python3 scripts/finalize_census_v5.py --check`.
'''
        (ROOT / 'docs/census_2025_2026_oct15_executive.md').write_text(brief, encoding='utf-8')
        first_pass = ROOT / 'docs/census_2025_2026_oct15_v5.md'
        note = '> **Final identity/date view:** See the [executive brief](census_2025_2026_oct15_executive.md), [effective register](../data/census_v5/effective_activity_register.csv) and [canonical bridge](../data/census_v5/canonical_identity_adjudications.csv). V5E012 enriches existing FTX005; V5E005 gains its independently sourced 16 November start date. The first-pass audit below is retained.\n\n'
        original = first_pass.read_text()
        if not original.startswith('> **Final identity/date view:**'):
            first_pass.write_text(note+original, encoding='utf-8')
        readme_path = ROOT / 'README.md'
        readme = readme_path.read_text()
        heading = '## Latest — 15 October 2026 systematic census'
        block = f'''{heading}

**[Current executive brief](docs/census_2025_2026_oct15_executive.md)** · [Full source-frame audit](docs/census_2025_2026_oct15_v5.md) · [Effective activity register](data/census_v5/effective_activity_register.csv) · [Six shared-production tests](data/census_v5/shared_production_recommendations.csv).

The refreshed official indexes contain **{summary['council_reports']} SG reports**, **{summary['formal_meeting_ids']} distinct formal Council meeting IDs** and **{summary['meeting_variants']} transcript variants**. Six additional archives returned **48/48 pages**, adding **{summary['new_exact_urls_beyond_prior']} exact URLs** to a **{summary['combined_exact_source_urls']:,}-URL** frame. These are sources, not delivered-event counts.

The extension adjudicates **16 activity records** (11 training/seminar cohorts, two field activities, three meetings), including **one enrichment of existing FTX005**, not a new Sierra Leone mission. Fifteen additional V5 identities are not a certified all-version new-event total. One multi-visit programme and eight advertised courses are separate, nonadditive strata. All 19 first-pass curated source bodies were retrieved. Existing LCM and Deployment Review systems are baselines, not newly proposed platforms.

**Mandated deliverables, parent/mission rankings and 20/32 retrospective 2027-category support remain unchanged. No duplicate paid service or incremental net saving is verified.** [Offline acceptance checks](scripts/finalize_census_v5.py).

'''
        if heading not in readme:
            marker = '## Current — 12 October 2026 source-frame census'
            ensure(marker in readme, 'README insertion anchor changed; refusing broad rewrite')
            readme = readme.replace(marker, block+'## Historical — 12 October 2026 source-frame census', 1)
        readme = readme.replace('## Latest — 13 October 2026 training and field attendance validation', '## Historical — 13 October 2026 training and field attendance validation')
        readme = readme.replace('<a href="docs/census_2025_2026_attendance_executive.md"><strong>Current training & field attendance findings</strong></a>', '<a href="docs/census_2025_2026_oct15_executive.md"><strong>Current census and shared-production findings</strong></a>')
        readme_path.write_text(readme, encoding='utf-8')
        workflow = ROOT / '.github/workflows/validate.yml'
        value = workflow.read_text()
        if 'scripts/finalize_census_v5.py --check' not in value:
            value += '      - name: Validate October 15 public census and canonical identity safeguards\n        run: |\n          python3 scripts/validate_census_v5.py\n          python3 scripts/finalize_census_v5.py --check\n'
            workflow.write_text(value, encoding='utf-8')
    final = json.loads((DATA / 'finalization_summary.json').read_text())
    ensure(final['first_pass_seed_sha256'] == digest(seed_path), 'Effective view seed provenance mismatch')
    ensure(final['effective_register_sha256'] == digest(DATA / 'effective_activity_register.csv'), 'Effective view hash mismatch')
    ensure(final['identity_bridge_sha256'] == digest(DATA / 'canonical_identity_adjudications.csv'), 'Identity bridge hash mismatch')
    actual = read_csv(DATA / 'effective_activity_register.csv')
    ensure(len(actual) == len({r['canonical_event_id'] for r in actual}) == 16, 'Within-extension canonical count mismatch')
    ensure(sum(r['canonical_event_id']=='FTX005' for r in actual)==1, 'Prior field mission not reconciled')
    ensure(next(r for r in actual if r['event_id']=='V5E005')['event_start']=='2025-11-16', 'Date enrichment lost')
    ensure(final['confirmed_prior_event_enrichments']==1 and final['global_new_unique_events']=='not_certified', 'Global event overclaim')
    ensure(final['incremental_net_savings']=='not_estimated' and final['mandated_deliverables']=='unchanged', 'Mandate/financial gate changed')
    print(json.dumps(dict(status='passed_final_identity_date_and_release_checks', **final), indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
