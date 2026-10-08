#!/usr/bin/env python3
"""Validate Phase 9 public SG Cluster III and A/81/7 framework reconciliation.

No ACABQ Cluster III-specific mission report is asserted. The 2027 envelope
holding unissued recommendations unchanged is an explicitly non-official
sensitivity test, never ACABQ-approved funding or incremental savings.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TABLES = {
    "acabq_2027_clusterIII_sg_baseline": "spm_id",
    "acabq_2027_main_crosscutting_framework": "framework_id",
    "acabq_2027_clusterIII_crosscutting_map": "mapping_id",
    "acabq_2027_conditional_envelope": "scenario_id",
    "acabq_2027_mission_reconciliation": "spm_id",
    "acabq_2027_cluster_reconciliation": "cluster_id",
    "spm_2027_mission_budget": "spm_id",
    "spm_2027_embedded_efficiencies": "efficiency_id",
    "clusterIII_2027_research_priorities": "spm_id",
    "acabq_2027_ranked_consolidation": "candidate_id",
    "ranked_consolidation_validation": "candidate_id",
    "consolidation_comprehensive_2027": "hierarchy_id",
    "acabq_2027_unissued_report_scope": "report_symbol",
}

def load(table, key):
    with (ROOT / "data" / (table + ".csv")).open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames or key not in reader.fieldnames:
            raise AssertionError(f"Invalid CSV schema: {table}")
        rows = list(reader)
    if not rows or len({r[key] for r in rows}) != len(rows):
        raise AssertionError(f"Missing or duplicated key: {table}")
    if any(None in r or any(v is None or not str(v).strip() for v in r.values())
           for r in rows):
        raise AssertionError(f"Blank or malformed row: {table}")
    return rows

def approx(actual, expected, tolerance=0.011):
    assert abs(float(actual) - float(expected)) < tolerance, (actual, expected)

def check():
    tables = {table: load(table, key) for table, key in TABLES.items()}
    nine = tables["acabq_2027_clusterIII_sg_baseline"]
    original = {r["spm_id"]: r for r in tables["spm_2027_mission_budget"]}
    advice = {r["spm_id"]: r for r in tables["acabq_2027_mission_reconciliation"]}
    ef = {r["efficiency_id"]: r for r in tables["spm_2027_embedded_efficiencies"]}
    assert len(nine) == 9 and len(advice) == len(original) == 36
    assert all(x["cluster_id"] == "SPM_CLUSTER_3" for x in nine)
    assert len({x["spm_id"] for x in nine}) == 9
    used_eff = set()
    for row in nine:
        ident = row["spm_id"]
        sg = original[ident]
        recom = advice[ident]
        approx(row["budget_2026_GA_approved_usd_thousands"],
               sg["regular_budget_2026_approved_usd_thousands"])
        approx(row["budget_2027_SG_proposed_usd_thousands"],
               sg["regular_budget_2027_proposed_usd_thousands"])
        approx(row["budget_2027_minus_2026_usd_thousands"],
               float(sg["regular_budget_2027_proposed_usd_thousands"]) -
               float(sg["regular_budget_2026_approved_usd_thousands"]))
        approx(float(recom["sg_2027_proposal_usd_thousands"]),
               row["budget_2027_SG_proposed_usd_thousands"])
        assert recom["acabq_recommended_2027_usd_thousands"] == "not_extracted"
        assert recom["acabq_minus_sg_usd_thousands"] == "not_calculable"
        assert recom["SG_prior_to_proposal_budget_reconciliation"] == "verified_mission_source_table_1"
        assert row["ACABQ_clusterIII_specific_adjustment_usd_thousands"] == "not_determined"
        assert row["incremental_net_savings_usd_thousands"] == "not_estimated"
        assert row["SG_2026_to_2027_budget_status"] == "fully_reconciled_to_primary_SG_document"
        ids = row["prebudgeted_efficiency_ids"].split(";")
        if ids != ["none_separately_identified_in_Add4_Table3"]:
            assert all(i in ef and ef[i]["cluster_id"] == "III" for i in ids)
            assert not (set(ids) & used_eff), "Efficiency double counted across missions"
            used_eff.update(ids)
            approx(sum(float(ef[i]["projected_2027_efficiency_usd_thousands"]) for i in ids),
                   row["identified_prebudgeted_2027_efficiencies_usd_thousands"])
        else:
            approx(row["identified_prebudgeted_2027_efficiencies_usd_thousands"], 0)
            assert row["prebudgeted_status"] == "no_separately_itemized_efficiency_not_proof_of_zero"
    assert len(used_eff) == 19
    def summation(field):
        return sum(float(x[field]) for x in nine)
    approx(summation("budget_2026_GA_approved_usd_thousands"), 324549.9)
    approx(summation("budget_2027_SG_proposed_usd_thousands"), 325353.9)
    approx(summation("budget_2027_minus_2026_usd_thousands"), 804.0)
    approx(summation("identified_prebudgeted_2027_efficiencies_usd_thousands"), 14560.4)
    approx(summation("planned_personnel_2026_table2"), 2457)
    approx(summation("planned_personnel_2027_table2"), 2332)
    approx(summation("proposed_personnel_change"), -125)
    assert all(x["personnel_unit"].startswith("Table_2_all") for x in nine)

    # Never classify closed missions' prior financing as extra incremental savings.
    approx(324549.9 + 121473.1, 446023.0)
    approx(325353.9 - 446023.0, -120669.1)

    framework = tables["acabq_2027_main_crosscutting_framework"]
    mapping = tables["acabq_2027_clusterIII_crosscutting_map"]
    assert len(framework) == 16 and len(mapping) == 51
    fw = {x["framework_id"] for x in framework}
    mids = {x["spm_id"] for x in nine}
    assert all(x["crosscutting_numeric_adjustment"] == "not_determined_by_main_report"
               and x["is_clusterIII_specific_dollar_recommendation"] == "no"
               and x["source_url"].startswith("https://docs.un.org/en/A/81/7")
               for x in framework)
    assert all(x["framework_id"] in fw and x["spm_id"] in mids
               and x["stated_as_direct_clusterIII_ACABQ_mission_recommendation"] == "no"
               and x["recommended_2027_clusterIII_financial_adjustment_usd"] == "not_determined"
               for x in mapping)
    assert {x["spm_id"] for x in mapping} == mids

    outstanding = tables["acabq_2027_unissued_report_scope"]
    assert len(outstanding) == 2
    assert {r["report_symbol"] for r in outstanding} == {"A/81/7/Add.1", "A/81/7/Add.4"}
    assert all(r["report_status"] == "not_yet_issued_per_user_2026_10_08"
               and r["financial_advice"] == "not_determined"
               and r["not_equal_zero"] == "yes" for r in outstanding)

    controls = {x["cluster_id"]: x for x in tables["acabq_2027_cluster_reconciliation"]}
    assert controls["SPM_CLUSTER_3"]["acabq_adjusted_2027_usd_thousands"] == "not_extracted"
    assert controls["ALL_36_PLUS_RSCE"]["acabq_adjusted_2027_usd_thousands"] == "not_calculable"

    scenario = {x["scenario_id"]: x for x in tables["acabq_2027_conditional_envelope"]}
    assert set(scenario) == {"S1_2027_SG_SUBMITTED", "S2_PARTIAL_ADVICE_CARRY_FORWARD"}
    for r in scenario.values():
        approx(sum(float(r[f]) for f in
                   ("cluster_I_usd_thousands", "cluster_II_usd_thousands",
                    "cluster_III_usd_thousands", "RSCE_usd_thousands")),
               r["hypothetical_total_usd_thousands"])
        assert r["is_ACABQ_complete_recommendation"] == "no"
    approx(scenario["S1_2027_SG_SUBMITTED"]["hypothetical_total_usd_thousands"], 422671)
    approx(scenario["S2_PARTIAL_ADVICE_CARRY_FORWARD"]["hypothetical_total_usd_thousands"], 422488.5)
    assert "NOT_official" in scenario["S2_PARTIAL_ADVICE_CARRY_FORWARD"]["source_status"]

    umbrellas = tables["acabq_2027_ranked_consolidation"]
    prior = tables["ranked_consolidation_validation"]
    children = tables["clusterIII_2027_research_priorities"]
    combined = tables["consolidation_comprehensive_2027"]
    assert len(umbrellas) == len(prior) == 14 and len(children) == 9 and len(combined) == 23
    assert sorted(int(x["revised_public_rank"]) for x in umbrellas) == list(range(1, 15))
    assert sorted(int(x["rank"]) for x in prior) == list(range(1, 15))
    assert sorted(int(x["clusterIII_research_rank"]) for x in children) == list(range(1, 10))
    umbids = {x["candidate_id"] for x in umbrellas}
    assert set(x["candidate_id"] for x in prior) == umbids
    assert all(x["parent_candidate_id"] in umbids and x["spm_id"] in mids
               and x["incremental_net_savings"] == "not_estimated"
               and x["ACABQ_clusterIII_specific_adjustment"] == "not_determined"
               and x["not_additive_to_parent_scope"] == "yes"
               for x in children)
    assert set(x["hierarchy_id"] for x in combined) == (
        {"U_" + x for x in umbids} | {"M_" + x for x in mids})
    assert all(x["new_savings_usd"] == "not_estimated"
               and x["do_not_sum_hierarchy"] == "yes" for x in combined)
    assert [x["candidate_id"] for x in
            sorted(umbrellas, key=lambda r: int(r["revised_public_rank"]))[:5]] == (
               ["C16", "C07", "C01", "C04", "C09"])
    assert all(x["new_net_savings_USD"] == "not_estimated" for x in umbrellas)

    for path in ("docs/acabq_2027_clusterIII_review.md",
                 "docs/acabq_2027_ranked_assessment.md",
                 "docs/public_only_executive_brief.md"):
        assert (ROOT / path).exists(),path
    print("PHASE 9 PUBLIC FINANCIAL RECONCILIATION PASSED")
    print("Nine SG mission budgets 324549.9 (2026 approved) -> 325353.9 (2027 proposed); +804.0 USD thousands")
    print("Planned personnel Table 2: 2457 to 2332, NOT observed job abolishments")
    print("19 already embedded Cluster III efficiencies totaling 14560.4 USD thousands")
    print("16 A/81/7 crosscutting principles, 51 mission-applicability links; 0 unsupported ACABQ Cluster III cuts")
    print("14 ranked umbrellas + 9 child work packages; no verified incremental savings")
    print("Partial-advice 422488.5 USD thousands is a labeled hypothetical, not ACABQ recommendation")

if __name__ == "__main__":
    check()
