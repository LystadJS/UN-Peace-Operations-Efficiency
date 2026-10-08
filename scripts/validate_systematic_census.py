#!/usr/bin/env python3
"""Validate official 2025-2026 Council index snapshots, not fiscal savings.

The published index itself may lag actual 2026 activity. This gate checks
completeness relative to retrieved source tables and the known official
2025 meeting total (255), and rejects treating resumptions as new meetings.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AS_OF=date(2026,10,8)
def read(name,key):
    path=ROOT/"data"/name
    with path.open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        assert reader.fieldnames and key in reader.fieldnames,name
        rows=list(reader)
    assert rows and len(rows)==len({x[key] for x in rows}),name
    assert all(None not in x and all(v is not None and str(v).strip() for v in x.values())
               for x in rows),name
    return rows
def validate():
    report=read("systematic_sg_reports_2025_2026.csv","document_symbol")
    meets=read("systematic_sc_meetings_2025_2026.csv","record_id")
    snapshots=read("systematic_census_source_snapshots.csv","source_id")
    totals=read("systematic_census_index_totals.csv","source_id")
    assert len(snapshots)==4 and len(totals)==4
    p=Counter(int(x["index_year"]) for x in report)
    meeting=Counter(int(x["year"]) for x in meets)
    assert p[2025]>=80 and p[2026]>=45 and len(report)>=125,(p,len(report))
    assert all(x["source_status"]=="official_index_entry_not_full_text_comparison" for x in report)
    assert all(x["identical_to_another_report"]=="not_tested" for x in report)
    assert all(x["financial_duplication"]=="not_estimated" for x in report)
    assert all(x["financial_duplication"]=="not_estimated" for x in meets)
    for row in report:
        assert date.fromisoformat(row["indexed_date"])<=AS_OF
        assert int(row["index_year"]) in (2025,2026)
        assert row["document_symbol"].startswith("S/"+row["index_year"]+"/")
        assert row["source_link"].startswith("https://")
        assert row["registry_url"].startswith("https://main.un.org/securitycouncil")
        assert row["date_year_mismatch"]==str(row["indexed_date"][:4]!=row["index_year"]).lower()
    for row in meets:
        eventdate=date.fromisoformat(row["date"])
        assert eventdate<=AS_OF and int(row["year"])==eventdate.year
        assert row["record_id"].startswith("S/PV.")
        assert row["meeting_base_id"].startswith("S/PV.")
        assert row["registry_url"].startswith("https://ydsftksff8.")
        assert row["meeting_to_report_link"]=="not_inferred_from_same_topic_alone"
        assert row["is_resumption"]==str(row["variant"]=="resumption").lower()
    base_2025={x["meeting_base_id"] for x in meets if x["year"]=="2025"}
    base_2026={x["meeting_base_id"] for x in meets if x["year"]=="2026"}
    assert len(base_2025)==255,len(base_2025)
    assert len(base_2026)>=110,len(base_2026)
    assert len(base_2025)<=meeting[2025] and len(base_2026)<=meeting[2026]
    # Confirm canonical records from previous quality-controlled evidence.
    reportids={x["document_symbol"] for x in report}
    for sym in ("S/2025/187","S/2025/342","S/2025/771","S/2025/772",
                "S/2026/445","S/2026/537","S/2026/99"):
        assert sym in reportids,sym
    mids={x["meeting_base_id"] for x in meets}
    for sym in ("S/PV.10060","S/PV.10073","S/PV.10058","S/PV.10146"):
        assert sym in mids,sym
    known_issue=[x for x in report if x["document_symbol"]=="S/2026/513"]
    if known_issue:
        assert known_issue[0]["date_year_mismatch"]=="true"
        assert known_issue[0]["indexed_date"]=="2025-06-23"
    for r in snapshots:
        assert len(r["source_sha256"])==64
        assert r["source_url"].startswith("https://")
        assert r["extraction_status"]=="success_index_entries_only"
    m=json.loads((ROOT/"data"/"systematic_census_metadata.json").read_text(encoding="utf-8"))
    assert m["as_of"]=="2026-10-08"
    assert m["official_2025_formal_meeting_benchmark"]==255
    assert m["official_2025_informal_consultations_not_included"]==115
    assert sum(p.values())==len(report) and sum(meeting.values())==len(meets)
    print("OFFICIAL COUNCIL INDEX CENSUS VALIDATION PASSED")
    print("SG reports listed 2025",p[2025],"2026",p[2026],
          "total",len(report))
    print("Council meeting record variants 2025",meeting[2025],
          "2026",meeting[2026])
    print("Distinct formal meeting IDs 2025",len(base_2025),"2026",len(base_2026))
    print("Note: 2025 consultations 115 excluded; 2026 index may lag the as-of date.")
    print("No inferred duplicate mandated report, joint attendance, or cost saving.")
if __name__=="__main__":
    validate()
