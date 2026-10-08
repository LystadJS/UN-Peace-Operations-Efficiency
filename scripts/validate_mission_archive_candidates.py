#!/usr/bin/env python3
"""Validate bounded archive notice triage without treating notices as actual events."""
import csv
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def read(filename):
    with (R/"data"/filename).open(newline="",encoding="utf-8") as fh:
        return list(csv.DictReader(fh))
source=read("mission_archive_notice_metadata_2025_2026.csv")
triage=read("mission_archive_candidate_triage.csv")
summary=read("mission_archive_classification_summary.csv")
coverage=read("mission_archive_coverage_2025_2026.csv")
assert len(source)==len(triage)>100 and len(summary)==24 and len(coverage)==6
assert len({r["notice_url"] for r in triage})==len(triage)
assert {r["notice_url"] for r in triage}=={r["notice_url"] for r in source}
assert {r["publisher_site"] for r in triage}<={"UNOWAS","UNOCA","UNRCCA","UNAMA","DPPA","DPO"}
assert all(r["date_is_actual_event_date"]=="not_verified" and
           r["coorganizer_roles_verified"]=="no" and
           r["full_article_read"]=="no" and
           r["canonical_activity_id"]=="not_assigned" and
           r["financial_duplicate_service"]=="not_estimated" for r in triage)
assert all(r["complete_event_census"]=="no" and
           r["complete_article_inventory"]=="no" for r in summary)
sites=Counter(r["publisher_site"] for r in triage)
assert sum(sites.values())==len(triage)
for cov in coverage:
    assert sites[cov["site"]]==int(cov["archive_notice_links"])
    assert cov["true_field_or_training_event_total"]=="unknown_not_observable_from_news"
assert sites.get("UNRCCA",0)==0
print("BOUNDED PUBLIC NOTICE CLASSIFICATION VALIDATION PASSED")
print("Notice titles:",len(triage),"confirmed individual event identities from notices:",0,
      "verified event costs:",0)
