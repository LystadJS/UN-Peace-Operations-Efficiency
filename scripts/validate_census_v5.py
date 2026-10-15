#!/usr/bin/env python3
"""Validate and export the October 15 public-source extension; never infer savings.

--collect runs the bounded public collector with news/node link coverage enabled
for V5 only. Default validation is offline and preserves older frozen datasets.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/census_v5'
ASOF = '2026-10-15'

def load_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))

def export_csv(path, rows):
    fields = list(dict.fromkeys(k for row in rows for k in row))
    if not fields:
        raise ValueError('Empty export schema: ' + str(path))
    def encode(value):
        if value is None:
            return ''
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False, sort_keys=True)
        return value
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({k: encode(row.get(k)) for k in fields} for row in rows)

def ensure(condition, message):
    if not condition:
        raise AssertionError(message)

def collect():
    import collect_census_v5 as job
    import collect_extended_official_archive as archive
    # Older collectors only admitted /en/news/ links. Drupal node aliases are
    # also part of V5 discovery. Never change frozen V3/V4 parsing or files.
    def scoped(url, base, fragment):
        target, origin = urlsplit(url), urlsplit(base)
        if target.scheme != 'https' or target.hostname != origin.hostname:
            return False
        path = target.path.rstrip('/')
        is_article = fragment in path or bool(re.fullmatch(r'/en/node/\d+', path))
        return is_article and path != origin.path.rstrip('/')
    archive.scoped = scoped
    saved = sys.argv[:]
    try:
        sys.argv = [saved[0]]
        job.main()
    finally:
        sys.argv = saved

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--collect', action='store_true')
    parser.add_argument('--export', action='store_true')
    args = parser.parse_args()
    if args.collect:
        collect()
    seed_path = DATA / 'reviewed_evidence.json'
    data = json.loads(seed_path.read_text(encoding='utf-8'))
    summary = json.loads((DATA / 'index_refresh_summary.json').read_text())
    ensure(data['asof'] == summary['asof'] == ASOF, 'Cutoff mismatch')
    ensure(data['financial_duplication'] == 'not_established', 'Unsupported duplication')
    ensure(data['incremental_net_savings'] == data['unique_people'] == 'not_estimated', 'Unsupported estimate')
    sources = {s['source_id']: s for s in data['sources']}
    events = {e['event_id']: e for e in data['events']}
    ensure(len(sources) == len(data['sources']), 'Repeated source ID')
    ensure(len(events) == len(data['events']) == 16, 'Repeated or unexpected activity ID')
    ensure(Counter(e['kind'] for e in events.values()) == {'training':11, 'field_activity':2, 'meeting':3}, 'Event-grain change')
    for source in sources.values():
        host = urlsplit(source['url']).hostname or ''
        ensure(host.endswith('.un.org') or host.endswith('.unmissions.org'), 'Non-UN source')
        ensure(source['review_basis'], 'Missing source review level')
        if source.get('publication_date'):
            ensure('2025-01-01' <= source['publication_date'] <= ASOF, 'Source outside window')
    for event in events.values():
        ensure(set(event['source_ids']) <= sources.keys(), 'Dangling event citation')
        ensure(event['delivery_status'] in {'completed_reported','delivered_reported','held_reported'}, 'Schedule promoted to delivery')
        for field in ('event_start', 'event_end', 'completed_by'):
            if event.get(field):
                date.fromisoformat(event[field])
                ensure('2025-01-01' <= event[field] <= ASOF, 'Activity date outside cutoff')
        if event.get('event_start') and event.get('event_end'):
            ensure(event['event_start'] <= event['event_end'], 'Reversed dates')
        if event['date_precision'].startswith('completed_by_publication'):
            ensure(event['event_start'] is None and event['event_end'] is None, 'Publication relabeled as event date')
            ensure(event['completed_by'], 'Missing completion bound')
        if event['attendance_value'] is None:
            ensure(event['attendance_qualifier'] == 'not_reported', 'Missing count treated as zero')
        else:
            ensure(isinstance(event['attendance_value'], int) and event['attendance_value'] > 0, 'Invalid count')
    ensure(events['V5E014']['attendance_unit'] == 'Member States represented', 'States relabeled as people')
    ensure(events['V5E011']['event_start'] is None, 'Announcement promoted to actual date')
    ensure(events['V5E005']['source_ids'] == events['V5E006']['source_ids'], 'Shared source bridge lost')
    ensure('conflict' in events['V5E006']['date_precision'], 'Source duration conflict concealed')
    ensure((date.fromisoformat(events['V5E006']['event_end']) - date.fromisoformat(events['V5E006']['event_start'])).days == 35, 'Duration mismatch')
    ensure(len(data['programme_groups']) == 1, 'Programme group count changed')
    ensure(data['programme_groups'][0]['exact_event_count'] is None, 'Grouped visits converted to events')
    ensure(set(data['programme_groups'][0]['related_event_ids']) <= events.keys(), 'Programme link broken')
    ensure(len(data['scheduled_training']) == 8, 'Calendar control count changed')
    calendar_stages = Counter()
    for listing in data['scheduled_training']:
        ensure(listing['source_id'] in sources, 'Calendar citation missing')
        ensure('attendance_value' not in listing, 'Advertised attendance invented')
        if listing['planned_start']:
            expected = ('past_schedule_delivery_unverified' if listing['planned_end'] < ASOF else
                        'future_schedule' if listing['planned_start'] > ASOF else
                        'scheduled_in_progress_delivery_unverified')
        else:
            ensure(listing['planned_month'] > ASOF[:7], 'Undated planned month misclassified')
            expected = 'future_schedule'
        ensure(listing['stage_at_cutoff'] == expected, 'Calendar chronology changed')
        calendar_stages[expected] += 1
    all_ids = set(events) | {x['group_id'] for x in data['programme_groups']} | {x['mechanism_id'] for x in data['existing_mechanisms']}
    ensure(len(data['opportunities']) == 6, 'Prioritization count changed')
    for item in data['opportunities']:
        ensure(set(item['evidence_ids']) <= all_ids, 'Opportunity evidence not found')
        ensure(item['protect'] and item['baseline'] and item['next_test'], 'Mandate/baseline gate missing')
        ensure(item['financial_status'] == 'not_estimated', 'Unsupported monetization')
    control = data['protected_controls']
    ensure(control['planned_2027_output_categories'] == 32 and control['previously_supported_retrospective_categories'] == 20, 'Frozen output comparison altered')
    ensure(control['parent_consolidation_ranking'] == control['mission_consolidation_ranking'] == control['mandated_deliverables'] == 'unchanged', 'Unapproved mandate/rank change')
    reports = load_csv(DATA / 'index_refresh/council_reports.csv')
    variants = load_csv(DATA / 'index_refresh/council_meeting_variants.csv')
    captures = load_csv(DATA / 'index_refresh/council_fetches.csv')
    ensure(len(captures) == 4 and all(x['status'] == 'fetched_index' for x in captures), 'Fresh Council capture incomplete')
    ensure(len(reports) == len({r['document_symbol'] for r in reports}) == summary['council_reports'], 'Report count mismatch')
    ensure(len(variants) == len({r['record_id'] for r in variants}) == summary['meeting_variants'], 'Variant count mismatch')
    ensure(len({r['meeting_base_id'] for r in variants}) == summary['formal_meeting_ids'], 'Base meeting count mismatch')
    ensure(len({r['meeting_base_id'] for r in variants if r['year'] == '2025'}) == 255, '2025 formal meeting benchmark failed')
    ensure(all(r['indexed_date'] <= ASOF for r in reports) and all(r['date'] <= ASOF for r in variants), 'Post-cutoff Council entry')
    actual_anomalies = sorted(r['document_symbol'] for r in reports if r['date_year_mismatch'] == 'true')
    ensure(actual_anomalies == sorted(summary['report_date_year_mismatches']), 'Index anomalies lost')
    pages = load_csv(DATA / 'source_frame/archive_page_access.csv')
    frame = load_csv(DATA / 'source_frame/archive_discovered_url_frame.csv')
    union = load_csv(DATA / 'source_frame/exact_url_union.csv')
    ensure(len(pages) == summary['new_archive_pages_attempted'] == 48, 'Bounded page frame changed')
    ensure(sum(p['fetch_status'] == 'downloaded' for p in pages) == summary['new_archive_pages_downloaded'], 'Access count mismatch')
    ensure(len(frame) == len({r['official_notice_url'] for r in frame}) == summary['new_frame_exact_source_urls'], 'Discovery frame mismatch')
    ensure(len(union) == len({r['official_notice_url'] for r in union}) == summary['combined_exact_source_urls'], 'Exact URL union mismatch')
    ensure(summary['combined_exact_source_urls'] == summary['prior_exact_source_urls'] + summary['new_exact_urls_beyond_prior'], 'Nonadditive union failed')
    ensure(summary['delivered_events_inferred_from_listings'] == summary['report_to_meeting_links_inferred_from_topic'] == 0, 'Improper automatic promotion')
    collisions = load_csv(DATA / 'prior_source_collisions.csv')
    fetches = load_csv(DATA / 'reviewed_source_fetches.csv')
    ensure({r['source_id'] for r in fetches} == set(sources), 'Reviewed-source retrieval attempt missing')
    for row in captures:
        ensure(bool(re.fullmatch('[0-9a-f]{64}', row['sha256'])), 'Missing Council source hash')
    for row in fetches:
        if row['fetch_status'] == 'downloaded':
            ensure(bool(re.fullmatch('[0-9a-f]{64}', row['raw_sha256'])), 'Missing article hash')
    # Index-first statistics are not an audit of underlying report contents.
    result = dict(asof=ASOF, status='passed_structural_and_provenance_gates',
                  reviewed_evidence_sha256=hashlib.sha256(seed_path.read_bytes()).hexdigest(),
                  adjudicated_event_records=len(events), event_records_by_kind=dict(Counter(e['kind'] for e in events.values())),
                  source_records=len(sources), reviewed_source_bodies_downloaded=sum(r['fetch_status']=='downloaded' for r in fetches),
                  reviewed_source_body_failures=sum(r['fetch_status']!='downloaded' for r in fetches),
                  programme_groups=1, advertised_courses=8, calendar_stages=dict(calendar_stages),
                  identity_tests=len(data['identity_tests']), prioritized_production_tests=6,
                  prior_exact_source_collision_rows=len(collisions), global_new_unique_events='not_certified',
                  explicit_event_date_or_range=sum(not e['date_precision'].startswith('completed_by_publication') for e in events.values()),
                  publication_bounded_event_dates=sum(e['date_precision'].startswith('completed_by_publication') for e in events.values()),
                  unique_people='not_estimated', financial_duplication='not_established', incremental_net_savings='not_estimated')
    if args.export:
        for key, filename in [('sources','reviewed_sources.csv'),('events','adjudicated_activities.csv'),
                              ('scheduled_training','advertised_training_controls.csv'),('identity_tests','event_identity_tests.csv'),
                              ('opportunities','shared_production_recommendations.csv')]:
            export_csv(DATA / filename, data[key])
        (DATA / 'validation_summary.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
        report = ['# UN peace-operations census: 15 October 2026 extension', '',
                  '**Public-source frame and adjudicated evidence; not a complete census of delivered field activities.**', '',
                  '## Decision', '',
                  'Use existing coordination systems and shared source inputs while retaining separate mandated products. No duplicate paid service or incremental net saving is established.', '',
                  '## Refreshed source populations', '',
                  '| Unit | Previous freeze | October 15 refresh |', '|---|---:|---:|',
                  f"| SG Council report symbols | {summary['prior_report_count']} | {summary['council_reports']} |",
                  f"| Formal Council meeting IDs | {summary['prior_meeting_ids']} | {summary['formal_meeting_ids']} |",
                  f"| Council transcript variants | {summary['prior_meeting_variants']} | {summary['meeting_variants']} |",
                  f"| Exact mission/department source URLs | {summary['prior_exact_source_urls']} | {summary['combined_exact_source_urls']} |", '',
                  f"Six additional archives: **{summary['new_archive_pages_downloaded']}/{summary['new_archive_pages_attempted']}** listing pages retrieved; **{summary['new_exact_urls_beyond_prior']}** additional exact URL identities. These are not additional delivered activities. News and Drupal node links are admitted; bounded pagination and incomplete publication remain limitations.", '',
                  'Source data: [Council catalogue](../data/census_v5/index_refresh/council_reports.csv), [meeting variants](../data/census_v5/index_refresh/council_meeting_variants.csv), [changes since October 12](../data/census_v5/index_refresh/changes_from_oct12.csv), [access log](../data/census_v5/source_frame/archive_page_access.csv), [summary](../data/census_v5/index_refresh_summary.json).', '',
                  '## Adjudicated activity extension', '',
                  '**16 activity records: 11 training/seminar cohorts, two field activities and three meetings.** A separate retrospective programme group and eight advertised courses are not added to that event count. Ten records have an explicit date or date range; six are only bounded by publication. V5 IDs are local research identities, not a claim that every record is absent from every earlier archive or represents a globally new event.', '',
                  '| ID | Activity | Occurrence evidence | Attendance unit |', '|---|---|---|---|']
        for e in events.values():
            when = (e.get('event_start') or '') + (' to ' if e.get('event_start') and e.get('event_end') else '') + (e.get('event_end') or '')
            if not when:
                when = 'Completed by ' + e['completed_by'] + '; exact dates unknown'
            count = 'Not reported' if e['attendance_value'] is None else f"{('>' if e['attendance_qualifier']=='more_than' else '')}{e['attendance_value']} {e['attendance_unit']}"
            links = ', '.join(f"[{sid}]({sources[sid]['url']})" for sid in e['source_ids'])
            report.append(f"| {e['event_id']} | {e['title']} ({links}) | {when} | {count} |")
        report += ['', '## Identity and source controls', '',
                   '- One seminar announcement plus one delivery report is one event; two language publications of a joint mission are not two missions.',
                   '- Two Beledweyne firefighting cohorts remain separate despite one article. The source describes four weeks for the January-February course but its dates span 35 elapsed days; this is unresolved.',
                   '- The Entebbe 7-9 April 2025 workshop is dated separately from a broader multi-visit programme. The latter is not an additional individual event.',
                   '- Conference counts, Member States represented, graduates and course participants are different units. No cross-course unique-person total is calculated.',
                   '- Two advertised courses have elapsed scheduled end dates, one spans the cutoff, and five are future listings. None is certified delivered from a calendar entry.',
                   f"- {result['reviewed_source_bodies_downloaded']}/{result['source_records']} curated source bodies were retrieved in the automated pass. Indexed official-source review and raw-response retrieval are recorded separately. A failed fresh download does not establish absence of the activity.",
                   f"- {len(collisions)} exact source-URL collision rows were found against prior CSVs. The [collision ledger](../data/census_v5/prior_source_collisions.csv) is not a complete title/date/entity alias reconciliation; no global new-event total is released.",
                   f"- Preserved Council index year/date anomalies: {', '.join(actual_anomalies) or 'none'}. Index titles and dates alone establish neither report identity nor report-to-meeting production reuse.", '',
                   'Evidence and controls: [activity ledger](../data/census_v5/adjudicated_activities.csv), [sources](../data/census_v5/reviewed_sources.csv), [calendar controls](../data/census_v5/advertised_training_controls.csv), [identity tests](../data/census_v5/event_identity_tests.csv), [source fetches](../data/census_v5/reviewed_source_fetches.csv).', '',
                   '## Additional shared-production priorities', '',
                   '| Priority | Share or reuse | Protected boundary | Next evidence test |', '|---|---|---|---|']
        for item in data['opportunities']:
            report.append(f"| {item['priority']}. {item['title']} | {item['share']} | {item['protect']} | {item['next_test']} |")
        report += ['', 'LCM and the Deployment Review application are existing arrangements, not newly proposed platforms. Joint technical assessment and joint field missions are observed cooperation; potential additional reuse remains a testable inference. UNSOS logistics and supplier-orientation cases do not establish separately funded duplication.', '',
                   '[Source-linked production tests](../data/census_v5/shared_production_recommendations.csv) distinguish observed baselines, proposed reuse, safeguards and required evidence.', '',
                   '## Release and remaining work', '',
                   'Council reports, formal meetings, field visits and courses remain separate strata. S/PV resumptions are transcript variants, not extra base meetings. Informal consultations are outside the formal-record denominator. Publication URLs, course sessions, programme groups and people are not interchangeable.', '',
                   'Earlier freezes and the 20/32 retrospectively supported 2027 output categories remain unchanged. Parent consolidation and mission rankings are not promoted from topical evidence. Existing UNITAR-UNSSC institutional integration remains in the previous authorized-reform baseline; no new saving is rebooked.', '',
                   'Remaining work: recover blocked article bodies; complete cross-version title/date/entity alias checks; reconcile advertised cohorts to completion records; obtain explicit report/briefing source links; test common cost objects only with authorized procurement and service evidence. Full field/training population completeness, unique people and incremental savings remain unverified.', '',
                   'Reproduce: `python3 scripts/validate_census_v5.py --collect --export` for a new retrieval of the frozen-cutoff frame; `python3 scripts/validate_census_v5.py` validates retained outputs offline. Historical files are not rewritten.', '',
                   '**A passing validator confirms the specified structure, chronology and source controls, not independent authentication of every source statement or financial substitutability.**', '']
        # Keep this statement derived rather than hard-coded as the record mix evolves.
        report = [line.replace('Ten records have an explicit date or date range; six are only bounded by publication.',
                              f"{result['explicit_event_date_or_range']} records have an explicit date or date range; {result['publication_bounded_event_dates']} are only bounded by publication.") for line in report]
        (ROOT / 'docs/census_2025_2026_oct15_v5.md').write_text('\n'.join(report), encoding='utf-8')
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
