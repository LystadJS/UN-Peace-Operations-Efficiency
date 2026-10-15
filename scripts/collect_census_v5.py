#!/usr/bin/env python3
"""Frozen 2026-10-15 source-frame refresh. Index entries are never actual events.

Uses the accepted Council parsers and bounded archive collector, without changing
historical freezes. Raw public HTML is an Actions artifact, not private data.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlsplit
import collect_extended_official_archive as archives
import expand_published_census as council

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/census_v5'
ASOF = '2026-10-15'
NEW_ARCHIVES = [
    ('UNSOS_news', 'https://unsos.unmissions.org/en/news', '/en/news/'),
    ('UNFICYP_news', 'https://unficyp.unmissions.org/en/news', '/en/news/'),
    ('UNMIK_news', 'https://unmik.unmissions.org/en/news', '/en/news/'),
    ('UNDOF_news', 'https://undof.unmissions.org/en/news', '/en/news/'),
    ('OICT_news', 'https://unite.un.org/en/news', '/en/news/'),
    ('UNPOL_news', 'https://police.un.org/en/news', '/en/news/'),
]

def read(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))

def write(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, default=Path('/tmp/census-v5-html'))
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    idx = OUT / 'index_refresh'
    idx.mkdir(exist_ok=True)
    reports, meetings, captures = council.council_snapshot(
        SimpleNamespace(out=idx, cache=args.cache, as_of=ASOF))
    # Fail closed on missing Council indexes; never overwrite earlier snapshots.
    if len(captures) != 4 or any(x['status'] != 'fetched_index' for x in captures):
        raise RuntimeError('Incomplete fresh Council indexes: inspect council_fetches.csv')
    if any(not r['indexed_date'] for r in reports) or any(not r['date'] for r in meetings):
        raise RuntimeError('Missing Council date')
    if len({r['document_symbol'] for r in reports}) != len(reports):
        raise RuntimeError('Repeated report identity')
    if len({r['record_id'] for r in meetings}) != len(meetings):
        raise RuntimeError('Repeated meeting variant')
    if sum(r['index_year'] == 2025 for r in reports) < 80:
        raise RuntimeError('Unexpected 2025 report coverage loss')
    if len({r['meeting_base_id'] for r in meetings if r['year'] == 2025}) != 255:
        raise RuntimeError('2025 formal meeting control differs from 255; review before release')
    old_reports = read(ROOT / 'data/census_v2/council_reports.csv')
    old_meetings = read(ROOT / 'data/census_v2/council_meeting_variants.csv')
    changes = []
    for kind, old, new, key in [('report', old_reports, reports, 'document_symbol'),
                              ('meeting_variant', old_meetings, meetings, 'record_id')]:
        old_map = {r[key]: r for r in old}
        new_map = {r[key]: r for r in new}
        for identity in sorted(set(old_map) | set(new_map)):
            status = ('added' if identity not in old_map else
                      'absent_from_current_index' if identity not in new_map else 'retained')
            if status == 'retained':
                date_key = 'indexed_date' if kind == 'report' else 'date'
                if old_map[identity][date_key] != new_map[identity][date_key]:
                    status = 'index_date_changed_requires_review'
            if status != 'retained':
                row = new_map.get(identity, old_map.get(identity))
                changes.append(dict(kind=kind, identity=identity, change=status,
                                    indexed_date=row.get('indexed_date', row.get('date', '')),
                                    official_url=row['source_link']))
    write(idx / 'changes_from_oct12.csv', changes,
          ['kind', 'identity', 'change', 'indexed_date', 'official_url'])
    original_fetch = archives.fetch
    def cached_fetch(url):
        data, status, sha = original_fetch(url)
        if data:
            (args.cache / (sha + '.html')).write_bytes(data)
        return data, status, sha
    archives.fetch = cached_fetch
    archives.ASOF = ASOF
    archives.ARCHIVES = NEW_ARCHIVES
    archives.run(OUT / 'source_frame', 8, 4)
    prior = set()
    prior_files = []
    for version in ('census_v2', 'census_v3', 'census_v4'):
        base = ROOT / 'data' / version
        for pattern in ('notice_frame.csv', 'archive_discovered_url_frame.csv'):
            for path in sorted(base.rglob(pattern)):
                prior_files.append(str(path.relative_to(ROOT)))
                for row in read(path):
                    value = row.get('notice_url') or row.get('official_notice_url')
                    if value:
                        prior.add(value)
    discovered = read(OUT / 'source_frame/archive_discovered_url_frame.csv')
    current = {r['official_notice_url'] for r in discovered}
    union = sorted(prior | current)
    write(OUT / 'source_frame/exact_url_union.csv', [
        dict(official_notice_url=url, in_previous_frames=str(url in prior).lower(),
             in_oct15_frame=str(url in current).lower(),
             unit='source_URL_not_event', asof=ASOF) for url in union],
        ['official_notice_url', 'in_previous_frames', 'in_oct15_frame', 'unit', 'asof'])
    raw_summary = json.loads((OUT / 'source_frame/archive_collection_summary.json').read_text())
    summary = dict(
        asof=ASOF, generated_at=datetime.now(timezone.utc).isoformat(),
        council_reports=len(reports), reports_by_index_year=dict(Counter(str(r['index_year']) for r in reports)),
        formal_meeting_ids=len({r['meeting_base_id'] for r in meetings}),
        meeting_ids_by_year={str(y):len({r['meeting_base_id'] for r in meetings if r['year']==y}) for y in (2025,2026)},
        meeting_variants=len(meetings), variant_counts=dict(Counter(r['variant'] for r in meetings)),
        report_date_year_mismatches=[r['document_symbol'] for r in reports if r['date_year_mismatch']=='true'],
        latest_report_index_date=max(r['indexed_date'] for r in reports),
        latest_meeting_index_date=max(r['date'] for r in meetings),
        prior_report_count=len(old_reports), prior_meeting_ids=len({r['meeting_base_id'] for r in old_meetings}),
        prior_meeting_variants=len(old_meetings), council_change_count=len(changes),
        prior_exact_source_urls=len(prior), prior_frame_files=prior_files,
        new_archive_pages_attempted=raw_summary['pages_attempted'],
        new_archive_pages_downloaded=raw_summary['downloaded_pages'],
        new_frame_exact_source_urls=len(current), new_exact_urls_beyond_prior=len(current-prior),
        combined_exact_source_urls=len(union),
        archive_event_completeness='not_certified', delivered_events_inferred_from_listings=0,
        report_to_meeting_links_inferred_from_topic=0, unique_people='not_estimated',
        duplicate_paid_service='not_established', incremental_net_savings='not_estimated')
    (OUT / 'index_refresh_summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True)+'\n')
    # Curated evidence can be added independently; audit exact source collisions
    # against all previous CSV rows, but never auto-merge events from a shared URL.
    seed = OUT / 'reviewed_evidence.json'
    if seed.exists():
        reviewed = json.loads(seed.read_text())
        urls = {s['url'] for s in reviewed['sources']}
        source_audit = []
        for source in reviewed['sources']:
            data, status, sha = cached_fetch(source['url'])
            source_audit.append(dict(source_id=source['source_id'], url=source['url'],
                                     fetch_status=status, raw_sha256=sha,
                                     prior_review_basis=source['review_basis']))
        write(OUT / 'reviewed_source_fetches.csv', source_audit,
              ['source_id','url','fetch_status','raw_sha256','prior_review_basis'])
        collisions = []
        for path in sorted((ROOT / 'data').rglob('*.csv')):
            if OUT in path.parents:
                continue
            for number, row in enumerate(read(path), 2):
                text = ' '.join(str(v) for v in row.values() if v)
                matches = [u for u in urls if u in text]
                if matches:
                    id_values = ';'.join(f'{k}={v}' for k,v in row.items()
                                         if v and ('event_id' in k or 'canonical_id' in k or 'activity_id' in k))
                    collisions.append(dict(prior_file=str(path.relative_to(ROOT)), prior_line=number,
                                           source_urls=';'.join(matches), prior_identity_fields=id_values,
                                           adjudication='same_source_is_not_automatically_same_event'))
        write(OUT / 'prior_source_collisions.csv', collisions,
              ['prior_file','prior_line','source_urls','prior_identity_fields','adjudication'])
    print(json.dumps(summary, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
