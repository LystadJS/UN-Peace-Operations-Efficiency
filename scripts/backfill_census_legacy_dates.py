#!/usr/bin/env python3
"""Recover dated publication metadata from the *preserved* original HTML archive.

No new HTTP requests or event inference. Source artifact run: 38314738551
(public pages only). The original collector retrieved 688 pages but failed to
recognize article masthead dates. This reprocesses those exact original bytes,
validates original SHA-256 fingerprints, and reconciles their publication dates
with the later bounded, partly 403-blocked 1708-URL source frame.

A dated notice is NEVER classified as a delivered field trip or training event.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup
from expand_published_census import publication_date

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "census_v2"
ASOF = "2026-10-12"
RUN = "38314738551"
WEEK = re.compile(r"^This Week in DPPA:.*\b(20(?:24|25|26))\b", re.I)


def read(name, primary):
    with (BASE / name).open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames and primary in reader.fieldnames
        arr = list(reader)
    assert arr and len({r[primary] for r in arr}) == len(arr)
    return arr


def write(name, records):
    (BASE / name).parent.mkdir(parents=True, exist_ok=True)
    with (BASE / name).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def main(html_dir):
    lineage = read("fetch_lineage.csv", "notice_url")
    current = {r["url"]: r for r in read("notices.csv", "url")}
    prior = [r for r in lineage if r["earlier_article_downloaded"] == "yes"]
    assert len(prior) == 688, "Earlier published source-frame control differs."
    recovered = []
    by_url = {}
    for r in prior:
        sha = r["earlier_body_sha256"]
        file = html_dir / (sha + ".html")
        if not file.is_file():
            raise FileNotFoundError(f"Cannot authenticate original downloaded HTML {sha}")
        body = file.read_bytes()
        if hashlib.sha256(body).hexdigest() != sha:
            raise AssertionError("Original HTML SHA changed: " + sha)
        soup = BeautifulSoup(body, "html.parser")
        title_tag = soup.select_one("article h1") or soup.find("h1")
        title = title_tag.get_text(" ", strip=True) if title_tag else ""
        day, method, raw = publication_date(soup)
        status = "date_not_verified"
        if day:
            status = ("publication_in_window" if "2025-01-01" <= day <= ASOF else
                      "before_window" if day < "2025-01-01" else "after_cutoff")
        headline = WEEK.search(title)
        title_conflict = bool(headline and day and headline.group(1) != day[:4])
        if title_conflict:
            status = "publication_title_year_conflict_review"
        row = dict(
            notice_url=r["notice_url"], publisher=r["publisher"],
            source_sha256=sha, original_artifact_run=RUN, original_snapshot_asof=ASOF,
            original_article_title=title[:350], publication_date=day or "not_verified",
            publication_date_method=method, publication_date_raw=raw[:160],
            date_classification=status, title_year_conflict=str(title_conflict).lower(),
            article_to_event_identity="not_inferred", is_delivered_activity="not_assessed",
            paid_duplicate_cost="not_estimated", incremental_net_savings="not_estimated")
        recovered.append(row)
        by_url[row["notice_url"]] = row

    merged = []
    for r in lineage:
        earlier = by_url.get(r["notice_url"])
        latest = current.get(r["notice_url"])
        current_day = latest["publication_date"] if latest and latest["publication_date"] else ""
        older_day = earlier["publication_date"] if earlier and earlier["publication_date"] != "not_verified" else ""
        discrepant = bool(current_day and older_day and current_day != older_day)
        conflict = discrepant or bool(earlier and earlier["title_year_conflict"] == "true") or (
            r["exception_status"] != "none_noted")
        valid = [d for d in (current_day, older_day) if d]
        # Preserve raw source values even when conflicted; do not choose a winner.
        best = ("conflict_do_not_infer" if conflict else
                valid[0] if valid else "not_verified")
        in_window = bool(best not in ("conflict_do_not_infer", "not_verified") and
                         "2025-01-01" <= best <= ASOF)
        merged.append(dict(
            notice_url=r["notice_url"], publisher=r["publisher"], asof=ASOF,
            source_ever_downloaded=r["body_ever_downloaded"],
            previous_sha256=r["earlier_body_sha256"], current_sha256=r["expanded_body_sha256"],
            previous_publication_date=older_day or "not_verified",
            current_publication_date=current_day or "not_verified",
            chronology_conflict=str(conflict).lower(),
            best_verified_publication_date=best,
            confirmed_publication_in_study_window=str(in_window).lower(),
            source_date_grain="publication_not_unique_field_or_training_event",
            financial_duplicate="not_estimated"))

    assert len(recovered) == 688 and len(merged) == len(lineage) == 1708
    assert sum(x["source_ever_downloaded"] == "yes" for x in merged) == 1051
    if sum(x["date_classification"] == "publication_in_window" for x in recovered) < 100:
        raise AssertionError("Recovered original archive dates insufficient; avoid false zero.")
    write("legacy_date_recovery.csv", recovered)
    write("union_dated_notice_coverage.csv", merged)

    totals = Counter(x["date_classification"] for x in recovered)
    union_dated = sum(x["confirmed_publication_in_study_window"] == "true" for x in merged)
    issues = sum(x["chronology_conflict"] == "true" for x in merged)
    summary = {
        "asof": ASOF,
        "original_html_artifact_run": RUN,
        "original_notices_authenticated": len(recovered),
        "original_status_counts": dict(sorted(totals.items())),
        "combined_discovered_url_frame": len(merged),
        "ever_downloaded_article_bodies": 1051,
        "combined_distinct_in_window_publications_with_nonconflicting_header_dates": union_dated,
        "date_conflict_notice_count": issues,
        "activity_event_denominator": "unknown",
        "published_notice_is_unique_event": False,
        "duplicate_paid_service": "not_estimated",
        "incremental_net_savings": "not_estimated"}
    (BASE / "legacy_date_recovery_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--html-dir", required=True, type=Path)
    main(parser.parse_args().html_dir)
