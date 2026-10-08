#!/usr/bin/env python3
"""Validate GA decision links, SPM discrepancies and research-ranking source constraints."""
from pathlib import Path
import csv

root = Path(__file__).resolve().parents[1]

def load(name, primary_key):
    with (root / "data" / (name + ".csv")).open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames and primary_key in reader.fieldnames, name
        rows = list(reader)
    assert rows and len({r[primary_key] for r in rows}) == len(rows), name
    assert all(None not in r and all(v is not None and v.strip() for v in r.values()) for r in rows), name
    return rows

old = {x["mission_id"]:x for x in load("mission_budget_register","mission_id")}
decisions = load("ga_mission_reconciliation","mission_id")
expected = {"UNISFA":"275","MINUSCA":"276","MONUSCO":"278",
            "UNIFIL":"282","UNMISS":"283","UNSOS":"285"}
assert len(decisions) == 6 and {r["mission_id"] for r in decisions} == set(old)
for r in decisions:
    assert r["ga_resolution"] == "A/RES/80/" + expected[r["mission_id"]]
    assert r["ga_adoption_date"] == "2026-06-30"
    assert r["ga_adoption_status"] == "verified_on_official_index"
    assert abs(float(r["sg_proposal_usd_thousands"]) - float(old[r["mission_id"]]["proposed_2026_27_gross"])) < 0.01
    assert r["ga_appropriation_usd_thousands"] == "not_verified_from_full_resolution"
    assert r["adopted_minus_proposed_usd_thousands"] == "not_calculable"
assert abs(sum(float(r["sg_proposal_usd_thousands"]) for r in decisions)-4120950.7) < 0.2

spm = load("spm_2027_addenda","addendum_id")
assert len(spm) == 4 and {r["addendum_id"] for r in spm} == {"SPM01","SPM02","SPM03","SPM04"}
assert all(r["proposed_cost_usd_thousands"] == "not_extracted" for r in spm)
boundary = {r["boundary_id"]:r for r in load("spm_fiscal_boundary","boundary_id")}
assert abs(float(boundary["SB01"]["amount_usd_thousands"]) - 423544.5) < 0.01
assert abs(float(boundary["SB02"]["amount_usd_thousands"])-float(boundary["SB03"]["amount_usd_thousands"])-4959.6) < 0.01

base_ids = {r["candidate_id"] for r in load("candidate_validation","candidate_id")}
ranked = load("ranked_consolidation_validation","candidate_id")
assert len(ranked) == 12
assert sorted(int(r["rank"]) for r in ranked) == list(range(1,13))
assert all(r["candidate_id"] in base_ids and r["net_savings_status"] == "not_estimated" for r in ranked)
rank = {r["candidate_id"]:r for r in ranked}
assert float(rank["C12"]["scope_amount_usd_thousands"]) == float(old["UNIFIL"]["proposed_2026_27_gross"])
assert float(rank["C08"]["scope_amount_usd_thousands"]) == float(old["UNSOS"]["proposed_2026_27_gross"])
assert float(rank["C13"]["scope_amount_usd_thousands"]) == float(old["MINUSCA"]["proposed_2026_27_gross"])
assert float(rank["C01"]["scope_amount_usd_thousands"]) == 10196.1
assert float(rank["C03"]["scope_amount_usd_thousands"]) == 27942.6
assert float(rank["C04"]["scope_amount_usd_thousands"]) == 14142.8

cases = load("historical_transition_audit_cases","historical_case_id")
assert len(cases) == 2 and sorted(float(r["value_usd_thousands"]) for r in cases) == [8500,11800]
for r in cases:
    assert r["historical_case_id"].startswith("H")
print("PHASE 3 VALIDATION PASSED")
print("Legal authorizations 6; full resolution financial amounts unresolved 6")
print("SPM addenda tracked 4; source amount gap USD 4.9596m; rankings 12")
print("No new savings numbers asserted; prior phase finance scope preserved.")
