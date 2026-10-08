#!/usr/bin/env python3
"""Check that bounded official news archives do NOT claim an exhaustive event census."""
import csv
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def read(filename):
    with (ROOT/"data"/filename).open(newline="",encoding="utf-8") as f:
        rdr=csv.DictReader(f)
        assert rdr.fieldnames
        data=list(rdr)
    return data
def main():
    a=read("mission_archive_attempts_2025_2026.csv")
    s=read("mission_archive_coverage_2025_2026.csv")
    sites={"UNOWAS","UNOCA","UNRCCA","UNAMA","DPPA","DPO"}
    assert len(s)==6 and {r["site"] for r in s}==sites
    assert len(a)>=6 and all(r["publisher_site"] in sites for r in a)
    assert all(r["completeness_status"]=="not_a_full_event_census" for r in a)
    assert all(r["true_field_or_training_event_total"]=="unknown_not_observable_from_news" for r in s)
    notice=ROOT/"data"/"mission_archive_notice_metadata_2025_2026.csv"
    if notice.exists():
        b=read(notice.name)
        assert len({r["notice_url"] for r in b})==len(b)
        assert all(r["publisher_site"] in sites and r["notice_url"].startswith("https://") for r in b)
        for r in b:
            if r["date_as_shown_in_listing"]!="not_verified_in_archive_card":
                assert date(2025,1,1)<=date.fromisoformat(r["date_as_shown_in_listing"])<=date(2026,10,8)
            assert r["content_adjudication"]=="not_read_full_article"
            assert r["financial_duplication"]=="not_estimated"
            assert r["event_id"]=="not_assigned"
    else:
        assert all(int(row["archive_notice_links"])==0 for row in s)
    print("MISSION ARCHIVE BOUNDED HARVEST CHECK PASSED")
    print("Archives:",[(x["site"],x["coverage_status"],x["archive_notice_links"]) for x in s])
    print("No complete field-visit/training census or duplicate-cost assertion inferred from notices.")
if __name__=="__main__":
    main()
