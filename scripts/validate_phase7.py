#!/usr/bin/env python3
import csv
from pathlib import Path
root=Path(__file__).resolve().parents[1]
def load(name,key):
 with (root/"data"/(name+".csv")).open(newline="",encoding="utf-8") as f:
  r=list(csv.DictReader(f))
 assert r and len({x[key] for x in r})==len(r),name
 assert all(None not in x and all(v not in ("",None) for v in x.values()) for x in r),name
 return r
request=load("restricted_transaction_request_spec","request_id")
base=load("transaction_evidence_requests","request_id")
assert len(request)==len(base)==18
assert {x["request_id"] for x in request}=={x["request_id"] for x in base}
cross=load("public_deliverable_crosswalk_2027","output_pair_id")
assert len(cross)==32
for name,prefix in [("deliverable_unowas_unoca","UO"),("deliverable_unama_unrcca","UA"),("deliverable_dppa_dpo_regional","DD"),("deliverable_training_comparison","TR")]:
 x=load(name,"id")
 assert len(x)==8 and {r["id"] for r in x}=={r["output_pair_id"] for r in cross if r["output_pair_id"].startswith(prefix)}
assert all(r["financial_cost_verified"]=="not_estimated" and r["same_final_output_documented"]=="no" for r in cross)
assert all(r["source_a_url"].startswith("https://") and r["source_b_url"].startswith("https://") for r in cross)
rep=load("acabq_2027_report_status","symbol")
assert len(rep)==5 and all(x["reviewed_recommendation_usd_thousands"]=="not_extracted" for x in rep)
pending=load("acabq_2027_mission_reconciliation","spm_id")
sg={x["spm_id"]:x for x in load("spm_2027_mission_budget","spm_id")}
assert len(pending)==36
for r in pending:
 assert r["sg_2027_proposal_usd_thousands"]==sg[r["spm_id"]]["regular_budget_2027_proposed_usd_thousands"]
 assert r["acabq_recommended_2027_usd_thousands"]=="not_extracted"
assert abs(sum(float(r["sg_2027_proposal_usd_thousands"]) for r in pending)-419411.9)<0.1
print("PHASE7 PASS: 18 requested extract packages, 32 documented paired deliverables, 36 SG SPM amounts and no invented ACABQ numeric recommendations.")
