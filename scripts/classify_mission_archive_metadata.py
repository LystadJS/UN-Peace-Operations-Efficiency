#!/usr/bin/env python3
"""Classify bounded public mission news notice TITLES into review candidates.

Does not assert that every notice is an event, that every event was reported,
or that a title identifies an actual organizer, field-trip date, or cost.
A notice may match several themes, but a single priority class is output.
No staff or other confidential data is used.
"""
from __future__ import annotations
import csv
import re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RULES=[
 ("possible_field_visit", r"\b(visits?|mission|assessment mission|field trip|fact.finding|working visit|visite|mission conjointe|joint visit|joint mission|field assessment)\b"),
 ("possible_training_or_workshop",r"\b(training|trainings|workshops?|seminars?|academ(y|ie)|masterclass|course|webinar|capacity.building|atelier|formation|training programme|coaching|certificate|apprenticeship)\b"),
 ("possible_report_or_publication",r"\b(report|briefing|press release|publication|strategy|framework|analysis|assessment|étude|rapport|booklet|policy brief|guide|guidelines|declaration)\b")
]
def classify(title):
    for label,pat in RULES:
        if re.search(pat,title,re.I):
            return label
    return "other_notice_not_counted_as_activity"

def csv_load(path):
    with path.open(encoding="utf-8-sig",newline="") as handle:
        reader=csv.DictReader(handle)
        assert reader.fieldnames
        rows=list(reader)
    return rows

def write_csv(path,rows):
    assert rows
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

def main():
    path=ROOT/"data/mission_archive_notice_metadata_2025_2026.csv"
    if not path.exists():
        raise SystemExit("Official archive metadata not published; run bounded archive harvester first.")
    src=csv_load(path)
    seen=set()
    out=[]
    for r in src:
        url=r["notice_url"]
        if url in seen:
            raise AssertionError("Repeated notice URL: "+url)
        seen.add(url)
        title=r["title_from_listing"]
        kind=classify(title)
        out.append({
            "notice_url":url,
            "publisher_site":r["publisher_site"],
            "title_from_listing":title,
            "candidate_theme":kind,
            "listing_card_date_or_unknown":r["date_as_shown_in_listing"],
            "date_is_actual_event_date":"not_verified",
            "index_listed_date_is_publication_date":"not_independently_confirmed",
            "full_article_read":"no",
            "canonical_activity_id":"not_assigned",
            "coorganizer_roles_verified":"no",
            "duplicate_url_suppressed":"yes_each_notice_once",
            "linked_field_or_training_output":"hypothesis_to_adjudicate_from_full_official_article",
            "asof":"2026-10-08",
            "census_status":"bounded_article_title_census_not_actual_event_census",
            "financial_duplicate_service":"not_estimated",
        })
    out.sort(key=lambda r:(r["publisher_site"],r["candidate_theme"],r["notice_url"]))
    write_csv(ROOT/"data/mission_archive_candidate_triage.csv",out)
    sites=sorted({r["publisher_site"] for r in out}|{"UNRCCA"})
    categories=[label for label,_ in RULES]+["other_notice_not_counted_as_activity"]
    total_counts=Counter((r["publisher_site"],r["candidate_theme"]) for r in out)
    summary=[{
        "publisher_site":s,
        "candidate_class":c,
        "notice_title_count":total_counts[(s,c)],
        "total_notices_on_site":sum(r["publisher_site"]==s for r in out),
        "role_and_event_date_status":"not_independently_confirmed_from_archive_title",
        "complete_article_inventory":"no",
        "complete_event_census":"no",
        "no_events_confirmed_is_not_zero":("site_archive_blocked" if s=="UNRCCA" else "event_numbers_not_inferable_from_titles"),
    } for s in sites for c in categories]
    write_csv(ROOT/"data/mission_archive_classification_summary.csv",summary)
    print("ARCHIVE CLASSIFICATION ONLY:",len(out),"notice URL titles,",
          dict(Counter(r["candidate_theme"] for r in out)),
          "strict events confirmed = 0 from titles alone.")
    print("Source date/role must be confirmed from full article. UNRCCA archive blocked.")
if __name__=="__main__":
    main()
