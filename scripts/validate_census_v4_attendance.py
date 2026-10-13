#!/usr/bin/env python3
"""Source-identity and no-savings gates for October 2026 training/field census."""
from pathlib import Path
from datetime import date
import csv,json
ROOT=Path(__file__).resolve().parents[1]
V=ROOT/"data"/"census_v4"
def read(path,key):
 with path.open(encoding="utf-8-sig",newline="") as f:
  r=list(csv.DictReader(f))
 assert r and all(None not in x and x[key] for x in r),path
 assert len({x[key] for x in r})==len(r),path
 return r
def sub(p,k):return read(V/(p+".csv"),k)
a=sub("attendance_evidence","evidence_id")
n=sub("attendance_normalized_controls","evidence_id")
i=sub("reconciled_event_identity","evidence_id")
e=sub("attendance_exclusions_and_aggregates","control_id")
o=sub("shared_administration_procurement_reassessment","review_id")
c=sub("source_coverage_and_nonadditivity","stream")
assert len(a)==len(n)==len(i)==30
assert {x["evidence_id"] for x in a}=={x["evidence_id"] for x in n}=={x["evidence_id"] for x in i}
assert len(e)==15 and len(o)==12 and len(c)==8
assert {x["canonical_event_id"] for x in a if x["canonical_event_id"].startswith("NEV")}=={f"NEV{j:03}" for j in range(1,23)}
assert sum(x["canonical_identity_status"].startswith("prior_") for x in i)==8
assert sum(x["observation_grain"]=="multi_course_or_multimonth_programme_group" for x in i)==3
assert sum(x["precision"]=="source_reported_count" for x in n)==22
assert sum(x["precision"]=="approximate_reported_count" for x in n)==4
assert sum(x["precision"]=="not_exactly_recoverable_or_shared" for x in n)==4
assert all(x["new_net_savings_usd"]=="not_estimated" for x in n+i)
assert all(x["verified_duplicate_expense"]=="not_established" and x["sum_unique_people_across_rows"]=="no" for x in n)
by={x["evidence_id"]:x for x in a}
assert by["AT001"]["event_date_or_start"]=="2025-02-12"
assert by["AT001"]["event_end_or_bound"]=="2025-03-21"
assert by["AT005"]["reported_attendance"]=="10"
assert by["AT003"]["reported_attendance"]==by["AT004"]["reported_attendance"]
assert by["AT017"]["reported_attendance"]=="not_independently_confirmed_total"
assert by["AT022"]["reported_attendance"]=="30"
assert e[0]["original_period"]=="2022-08-22_to_2022-08-26"
assert e[1]["original_period"]=="2025-02-12_to_2025-03-21"
assert all(x["is_additional_saving"]=="no" for x in e)
for x in a:
 for key in ("event_date_or_start","event_end_or_bound","published_on"):
  d=x[key]
  if len(d)==10 and d[4:5]=="-" and d[7:8]=="-":
   assert date(2025,1,1)<=date.fromisoformat(d)<=date(2026,10,13)
 assert x["official_source_url"].startswith("https://")
f=sub("deeper_official_archives/archive_discovered_url_frame","source_id")
p=sub("deeper_official_archives/archive_page_access","archive_page_url")
summary=json.loads((V/"deeper_official_archives"/"archive_collection_summary.json").read_text())
assert len(f)==767 and len(p)==88 and summary["downloaded_pages"]==79
assert summary["archives_attempted"]==11 and summary["pages_attempted"]==88
assert summary["actual_event_denominator"]=="unknown"
assert sum(x["fetch_status"]=="downloaded" for x in p)==79
assert all(x["canonical_event_id"]=="not_assigned" and x["incremental_net_savings"]=="not_estimated" for x in f)
p2=read(ROOT/"data/census_v2/union_dated_notice_coverage.csv","notice_url")
p3=read(ROOT/"data/census_v3/archive_discovered_url_frame.csv","source_id")
A={x["notice_url"] for x in p2}|{x["official_notice_url"] for x in p3}
B={x["official_notice_url"] for x in f}
assert len(A)==1957 and len(B)==767 and len(A|B)==2487
assert all(x["incremental_net_savings_usd"]=="not_estimated" for x in o)
assert [int(x["research_rank"]) for x in o]==list(range(1,13))
assert all(x["full_delivered_activity_denominator"]=="unknown" for x in c)
for name in ("census_2025_2026_attendance_v4.md","census_2025_2026_attendance_executive.md"):
 assert (ROOT/"docs"/name).is_file()
print("V4 PUBLIC CENSUS GATES PASS: 88 archive pages, 767 links, 2487 union URLs")
print("30 attendance records: 22 new linked IDs, 8 existing, 3 programme groups")
print("2022 exclusion, 2025 DPO bootcamp correction, 12 savings-free reviews accepted")
