#!/usr/bin/env python3
"""Validate mission-budget supplements without requiring external packages."""
from __future__ import annotations
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {
    "mission_source_extension": "source_id",
    "mission_budget_register": "mission_id",
    "support_account_units": "allocation_id",
    "mission_function_crosswalk": "mission_crosswalk_id",
    "un80_implementation_audit": "reform_id",
    "cost_allocation_bridge": "bridge_id",
    "implementation_cases": "case_id",
}
def load(name, key):
    p = ROOT / "data" / (name + ".csv")
    with p.open(encoding="utf-8", newline="") as f:
        read = csv.DictReader(f)
        assert read.fieldnames and key in read.fieldnames, name
        rows = list(read)
    assert rows, name
    assert len(rows) == len({r[key] for r in rows}), "Duplicate keys: " + name
    assert all(None not in r and all(str(v).strip() for v in r.values()) for r in rows), "Blank field: " + name
    return rows
def close(a,b,epsilon=0.12):
    return abs(a-b) <= epsilon
def main():
    ds = {name: load(name, key) for name,key in SCHEMAS.items()}
    sources = {r["source_id"] for r in ds["mission_source_extension"]}
    budgets = ds["mission_budget_register"]
    missions = {r["mission_id"] for r in budgets}
    crosswalk_file = ROOT / "data" / "crosswalk.csv"
    with crosswalk_file.open(encoding="utf-8",newline="") as f:
        cross = {r["crosswalk_id"] for r in csv.DictReader(f)}
    with (ROOT / "data" / "un80_register.csv").open(encoding="utf-8",newline="") as f:
        reforms = {r["reform_id"] for r in csv.DictReader(f)}
    assert len(budgets) == 6 and len(sources) == 7, "Six missions + support account expected"
    for r in budgets:
        assert r["source_id"] in sources and r["budget_status"] == "SG_proposal_not_appropriation"
        assert r["assessed_appropriation_status"].startswith("GA_80_")
        for prefix, target in [("apportioned_2025_26", "apportioned_2025_26_gross"),
                               ("proposed_2026_27", "proposed_2026_27_gross")]:
            amount = sum(float(r[prefix+"_"+x]) for x in ("military_police", "civilian", "operational"))
            assert close(amount,float(r[target])), "Gross category mismatch: " + r["mission_id"]
        diff = float(r["proposed_2026_27_gross"]) - float(r["apportioned_2025_26_gross"])
        assert close(diff,float(r["proposal_minus_prior_apportionment"])), "Variance mismatch"
        assert r["net_incremental_savings"] == "not_estimated"
    assert sum(float(r["proposed_2026_27_usd_thousands"]) for r in ds["support_account_units"]) - 95464.1 < 0.1
    assert close(sum(float(r["proposed_2026_27_usd_thousands"]) for r in ds["support_account_units"]),95464.1)
    for r in ds["mission_function_crosswalk"]:
        assert r["mission_id"] in missions
        assert all(x in cross for x in r["baseline_crosswalk_ids"].split(";"))
        assert r["net_incremental_savings"] == "not_estimated"
        assert r["implementation_evidence"] == "not_independently_verified"
    assert {r["reform_id"] for r in ds["un80_implementation_audit"]} == reforms
    for r in ds["un80_implementation_audit"]:
        assert r["net_incremental_savings"] == "not_estimated"
    for r in ds["mission_source_extension"]:
        assert r["evidence_url"].startswith("https://")
    print("MISSION AUDIT VALIDATION PASSED")
    print("Mission budgets:",len(budgets),"Mission crosswalks:",len(ds["mission_function_crosswalk"]),
          "UN80 audit records:",len(ds["un80_implementation_audit"]),
          "Allocation bridge:",len(ds["cost_allocation_bridge"]),
          "Support account units:",len(ds["support_account_units"]))
    print("Checks: schema, IDs, reference integrity, arithmetic, non-additivity and non-estimated savings.")
if __name__ == "__main__":
    main()
