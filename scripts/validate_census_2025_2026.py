#!/usr/bin/env python3
"""Validate scoped 2025-2026 report-symbol index and partial activity census."""
import csv
from datetime import date
from pathlib import Path
root=Path(__file__).resolve().parents[1]
def read(name,key):
 with (root/"data"/(name+".csv")).open(encoding="utf-8",newline="") as f:
  data=list(csv.DictReader(f))
 assert data and len({r[key] for r in data})==len(data),name
 assert all(None not in r and all(v is not None and str(v).strip() for v in r.values()) for r in data),name
 return data
reports=read("census_2025_2026_security_council_reports","symbol")
events=read("census_2025_2026_public_activities","item_id")
coverage=read("census_2025_2026_coverage_matrix","collection")
pairs=read("census_2025_2026_report_pair_tests","pair_id")
assert len(reports)==79 and len({r["series"] for r in reports})==17
assert sum(r["year"]=="2025" for r in reports)==46
assert sum(r["year"]=="2026" for r in reports)==33
assert len(events)==49 and len(coverage)==5 and len(pairs)==14
ids={r["symbol"] for r in reports}
assert all(p["first_symbol"] in ids and p["second_symbol"] in ids for p in pairs)
assert all(p["duplicate_expenditure_supported"]=="no" and p["financial_savings"]=="not_estimated" for p in pairs)
assert all(r["duplicate_cost"]=="not_verified" and r["incremental_savings"]=="not_estimated" for r in reports)
assert all(r["financial_duplication"]=="not_verified" and r["new_net_savings"]=="not_estimated" for r in events)
assert all(r["full_text_verified"]=="not_in_this_census_expansion" for r in reports)
assert all(r["coverage_claim"] and "not" in r["coverage_claim"].lower() for r in coverage)
for r in events:
 start=date.fromisoformat(r["start"]); end=date.fromisoformat(r["end"])
 assert start<=end<=date(2026,10,8)
 if r["item_id"]=="EV038":
  assert start.year==1984 or start.year==2024
 else:
  assert start.year>=2025
assert {r["item_id"] for r in events if r["item_id"].startswith("NEW")}=={"NEW001","NEW002","NEW003"}
assert {r["series"] for r in reports} >= {"UNOWAS","UNOCA","UNAMA","MONUSCO","MINUSCA","UNMISS","UNISFA","BINUH"}
print("CENSUS RELEASE PASSED: 79 scoped Council reports (46+33), 17 report series, 49 activity/output records and 14 identity-screening pairs.")
print("Activity archive coverage is PARTIAL; full-text duplication and monetary net savings NOT VERIFIED.")
