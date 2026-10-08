#!/usr/bin/env python3
"""Phase 6 public-only decision layer: source, cost boundary and no-fabrication gates."""
from __future__ import annotations
import csv
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCES={
 "public_opportunity_register":"opportunity_id",
 "public_release_gates":"opportunity_id",
 "public_finance_nodes":"finance_id",
 "public_finance_edges":"edge_id",
 "public_source_watchlist":"watch_id",
 "candidate_validation":"candidate_id",
 "spm_2027_embedded_efficiencies":"efficiency_id",
 "spm_2027_cross_pillar_links":"link_id",
 "ga_adopted_directives":"directive_id",
 "ga_mission_reconciliation":"mission_id",
 "transaction_validation_cases":"case_id"
}
def read(name,key):
    with (ROOT/"data"/(name+".csv")).open(encoding="utf-8",newline="") as f:
        reader=csv.DictReader(f)
        assert reader.fieldnames and key in reader.fieldnames,name
        rows=list(reader)
    assert rows and len(rows)==len({r[key] for r in rows}),"Duplicate/empty key "+name
    assert all(None not in r and all(v is not None and v.strip() for v in r.values())
               for r in rows),"Null/blank field "+name
    return rows
d={name:read(name,key) for name,key in SOURCES.items()}
r=d["public_opportunity_register"]
g=d["public_release_gates"]
by={x["opportunity_id"]:x for x in r}
assert len(r)==len(g)==18 and {x["opportunity_id"] for x in g}==set(by)
assert sum(x["public_track"]=="now" for x in r)==14
assert sum(x["public_track"]=="watch" for x in r)==3
assert sum(x["public_track"]=="negative" for x in r)==1
assert {k:sum(x["readiness_tier"]==k for x in r) for k in ("T1","T2","T3","T4","T0")}=={
    "T1":6,"T2":4,"T3":4,"T4":3,"T0":1}
cand={x["candidate_id"] for x in d["candidate_validation"]}
eff={x["efficiency_id"]:float(x["projected_2027_efficiency_usd_thousands"])*1000
     for x in d["spm_2027_embedded_efficiencies"]}
links={x["link_id"] for x in d["spm_2027_cross_pillar_links"]}
dirs={x["directive_id"] for x in d["ga_adopted_directives"]}
for x in r:
    assert x["parent_candidate_id"] in cand
    assert x["incremental_net_savings_usd"]=="not_estimated"
    assert x["does_this_support_a_cut"]=="no_requires_decision_gates"
    assert x["public_source_url"].startswith("https://")
    assert x["qualitative_feasibility"] in ("high","moderate","low","not_applicable")
    assert x["mandate_risk"] in ("critical","high","moderate","low")
    for tok in x["related_evidence_ids"].split(";"):
        assert tok in links or tok in dirs or tok in eff or tok.startswith("CW") or tok.startswith("WF"),tok
assert {x["opportunity_id"] for x in r if x["readiness_tier"]=="T1"}=={
    "P001","P002","P003","P004","P005","P006"}
assert float(by["P001"]["published_narrow_amount_usd"])==438100
assert float(by["P002"]["published_narrow_amount_usd"])==eff["EFF022"]==1400000
assert float(by["P003"]["published_narrow_amount_usd"])==3259100
assert float(by["P015"]["published_narrow_amount_usd"])==eff["EFF003"]==15000
assert float(by["P016"]["published_narrow_amount_usd"])==eff["EFF018"]==2630000
assert float(by["P017"]["published_narrow_amount_usd"])==eff["EFF020"]==1605700
assert float(by["P001"]["published_narrow_amount_usd"])==(
    eff["EFF019"]+eff["EFF026"]+eff["EFF029"])
for x in g:
    assert x["public_source_mapped"]=="yes"
    assert x["legally_executable_cut"]=="no"
    assert x["full_transaction_match"]=="not_available"
    assert x["additional_net_savings_usd"]=="not_estimated"
    assert x["opportunity_id"] in by
nodes={x["finance_id"]:x for x in d["public_finance_nodes"]}
edges=d["public_finance_edges"]
assert len(nodes)==24 and len(edges)==21
assert all(x["parent_id"] in nodes and x["related_id"] in nodes for x in edges)
for x in edges:
    assert x["relationship"] in {
       "part_of_control","part_of_memo","subset_not_complete","memo_nonadditive",
       "different_period_or_population","different_service_scope","different_period_or_fund"}
    assert x["can_sum_child_into_parent"]==(
        "yes_within_parent_only" if x["relationship"].startswith("part_of") else "no")
def val(k):return float(nodes[k]["amount_usd_thousands"])
for p,child in {
    "SPM27_TOTAL":["SPM27_C1","SPM27_C2","SPM27_C3","SPM27_RSCE"],
    "SPM26_TOTAL":["SPM26_CONT","SPM26_CLOSURES","SPM26_RSCE"],
    "SPM27_EFF":["SPM27_EFF_UF","SPM27_EFF_BINUH","SPM27_EFF_UNSMIL","SPM27_EFF_OTHER"],
    "SPM27_EFF_UF":["SPM27_EFF_UF_V","SPM27_EFF_UF_IT","SPM27_EFF_UF_R"],
    "GA6_FY_INCLUSIVE":["GA6_FY_MAINT","GA6_FY_CORP"]
}.items():
    assert abs(val(p)-sum(val(k) for k in child))<0.001,p
assert val("SPM27_TOTAL")==422671
assert val("SPM27_EFF")==14692.5
assert val("SPM27_EFF_UF")==438.1
assert val("SPM27_EFF_BINUH")==1400
assert val("SPM27_RSCE")==3259.1
assert val("RSCE_FY_TOTAL")==45911.6
assert val("GA6_FY_MAINT")==4028188
watch={x["watch_id"]:x for x in d["public_source_watchlist"]}
assert len(watch)==9
assert watch["W001"]["document_date"]=="2026-10-06"
assert watch["W002"]["document_date"]==watch["W003"]["document_date"]=="2026-08-25"
assert watch["W004"]["verified_status_on_2026_10_08"]=="not_verified_in_current_index_result"
assert all(x["locator"].startswith("https://") for x in watch.values())
assert len(d["ga_mission_reconciliation"])==6
assert len(d["transaction_validation_cases"])==3
assert all(x["additional_addressable_usd"]=="not_estimated" for x in d["transaction_validation_cases"])
print("PHASE 6 PUBLIC-ONLY VALIDATION PASSED")
print("18 public opportunity records: 14 now, 3 monitor, 1 negative control")
print("24 finance nodes, 21 scope edges, 18 legal/transaction gates, 9 source watches")
print("SPM $422.671m proposal, $14.6925m embedded efficiencies; exact finance hierarchies reconcile")
print("No verified new financial savings, redundant posts, or executable mandate cuts asserted")
