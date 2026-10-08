#!/usr/bin/env python3
"""Revalidate selected 2025-2026 actual UN peace-operations records.

This is a purposive official-public-source sample. Counts describe record
coverage, NOT prevalence of duplication or any monetary savings.
No external packages, network requests or confidential data are required.
"""
from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEYS = {
    "retrospective_2025_2026_sources": "source_id",
    "retrospective_2025_2026_activities": "activity_id",
    "retrospective_2025_2026_matches": "match_id",
    "retrospective_2025_2026_summary": "pairing",
    "retrospective_2025_2026_reuse_decisions": "case_id",
    "public_deliverable_crosswalk_2027": "output_pair_id",
}

def load(name: str, key: str) -> list[dict[str, str]]:
    path = ROOT / "data" / f"{name}.csv"
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or key not in reader.fieldnames:
            raise AssertionError(f"Invalid schema: {name}")
        rows = list(reader)
    if not rows or len(rows) != len({r[key] for r in rows}):
        raise AssertionError(f"Empty or duplicate keys: {name}")
    if any(None in row or any(v is None or not v.strip() for v in row.values())
           for row in rows):
        raise AssertionError(f"Blank or malformed CSV: {name}")
    return rows

def split_refs(value: str) -> list[str]:
    return [] if value in ("none", "none_found_in_selected_sample") else value.split(";")

def validate() -> None:
    datasets = {name: load(name, key) for name, key in KEYS.items()}
    sources = {r["source_id"]: r for r in datasets["retrospective_2025_2026_sources"]}
    activity = {r["activity_id"]: r for r in datasets["retrospective_2025_2026_activities"]}
    matches = {r["match_id"]: r for r in datasets["retrospective_2025_2026_matches"]}
    planned = {r["output_pair_id"]: r for r in datasets["public_deliverable_crosswalk_2027"]}
    summary = datasets["retrospective_2025_2026_summary"]
    reuse = datasets["retrospective_2025_2026_reuse_decisions"]

    assert len(sources) == 42
    assert len(activity) == 38
    assert len(matches) == 36
    assert len(planned) == 32
    assert len(summary) == 4 and len(reuse) == 11
    assert set(activity) == {f"EV{i:03d}" for i in range(1,39)}
    assert set(matches) == {f"MX{i:03d}" for i in range(1,37)}
    assert set(sources) == {f"SRC{i:03d}" for i in range(1,43)}

    for src in sources.values():
        assert src["official_url"].startswith("https://"), src["source_id"]
        assert src["retrieval_stage"].startswith("official_web_search_result_text_or_index")
        assert src["interpretive_limit"]

    historical = 0
    for row in activity.values():
        assert row["primary_source_id"] in sources
        assert all(sid in sources for sid in split_refs(row["corroborating_source_ids"]))
        start = date.fromisoformat(row["actual_start_date_or_month_start"])
        end = date.fromisoformat(row["actual_end_date_or_month_end"])
        assert start <= end and row["canonical_identity"] == "analyst_assigned_" + row["activity_id"]
        if row["activity_id"] == "EV038":
            historical += 1
            assert row["analysis_period_status"] == "2024_excluded"
            assert start.year == end.year == 2024
        else:
            assert row["analysis_period_status"] == "2025"
            if start.year == 2026:
                assert row["analysis_period_status"] == "2026"
            assert start.year in (2025, 2026)
            assert end <= date(2026, 10, 8)
        assert row["verified_unique_paid_cost"] == "not_available"
        assert row["incremental_net_savings"] == "not_estimated"
    assert historical == 1

    groups = {
        "UNOWAS_UNOCA": ("UNOWAS/UNOCA", "UO", 14, 6),
        "UNAMA_UNRCCA": ("UNAMA/UNRCCA", "UA", 8, 6),
        "DPPA_DPO_REGIONAL": ("DPPA/DPO regional desks", "DD", 7, 3),
        "TRAINING_COMPARISON": ("DPPA/DPO training", "TR", 7, 4)
    }
    for row in matches.values():
        assert row["comparison_family"] in groups
        assert split_refs(row["canonical_activity_ids"])
        assert all(id in activity for id in split_refs(row["canonical_activity_ids"]))
        assert all(id in sources for id in split_refs(row["supporting_source_ids"]))
        assert all(id in planned for id in split_refs(row["original_2027_crosswalk_ids"]))
        assert row["separately_paid_duplicate_work_found"] == "no"
        assert row["duplicate_cost_usd"] == "not_estimated"
        assert row["incremental_net_savings_usd"] == "not_estimated"
        assert row["retrospective_sampling_status"] == (
            "excluded_2024_event" if row["match_id"] == "MX034"
            else "selected_purposive_2025_2026_examples_not_complete_population"
        )
        if row["match_id"] != "MX034":
            assert all(activity[id]["activity_id"] != "EV038"
                       for id in split_refs(row["canonical_activity_ids"]))
    assert matches["MX001"]["observed_relationship"] == "joint_delivery_confirmed"
    assert matches["MX003"]["observed_relationship"] == "joint_delivery_confirmed"
    assert matches["MX015"]["observed_relationship"] == "joint_delivery_confirmed"
    assert matches["MX024"]["observed_relationship"] == "joint_product_confirmed"
    assert matches["MX020"]["joint_activity_or_reuse_documented"] == "no"
    assert matches["MX034"]["observed_relationship"] == "temporal_exclusion"
    assert activity["EV016"]["official_document_or_meeting_symbol"] == "S/PV.10060"
    assert activity["EV017"]["official_document_or_meeting_symbol"] == "S/PV.10073"
    assert activity["EV028"]["official_document_or_meeting_symbol"] == "A/80/798-S/2026/600"

    covered = 0
    for pairid, row in planned.items():
        linked = [m for m in matches.values()
                  if pairid in split_refs(m["original_2027_crosswalk_ids"])]
        from_register = split_refs(row["retrospective_2025_26_match_ids"])
        assert set(from_register) == {m["match_id"] for m in linked}
        assert int(row["retrospective_2025_26_sources_referenced"]) == len({
            s for m in linked for s in split_refs(m["supporting_source_ids"])
        })
        assert row["retrospective_verified_duplicate_cost"] == "no"
        assert row["retrospective_incremental_net_savings_usd"] == "not_estimated"
        assert row["same_final_output_documented"] == "no"
        assert row["financial_cost_verified"] == "not_estimated"
        if linked:
            covered += 1
            assert row["retrospective_sample_coverage"] == "matched_in_purposive_sample"
        else:
            assert row["retrospective_sample_coverage"].startswith("not_found_in_purposive_sample")
    assert covered == 19

    for family, (shown, prefix, case_count, category_count) in groups.items():
        r = next(x for x in summary if x["pairing"] == shown)
        assert int(r["planned_2027_output_categories"]) == 8
        assert int(r["retrospective_adjudication_records"]) == case_count
        assert int(r["categories_with_retrospective_support"]) == category_count
        assert int(r["costed_duplicate_work_confirmed"]) == 0
        assert r["net_new_savings_usd"] == "not_estimated"
        assert sum(m["comparison_family"] == family for m in matches.values()) == case_count
        assert sum(p["output_pair_id"].startswith(prefix) for p in planned.values()) == 8

    for item in reuse:
        assert all(s in matches for s in split_refs(item["source_match_ids"]))
        assert all(a in activity for a in split_refs(item["canonical_activities"]))
        assert all(s in sources for s in split_refs(item["source_ids"]))
        assert all(p in planned for p in split_refs(item["mapped_2027_deliverable_ids"]))
        assert item["duplicate_cost_verified"] == "no"
        assert item["incremental_cost_avoided_usd"] == "not_estimated"
        assert item["ranking_scope"] == "reuse_workflow_research_priority_not_recommended_cut"
    assert sorted(int(r["research_rank"]) for r in reuse) == list(range(1, 12))

    for p in ("docs/retrospective_2025_2026_overlap_audit.md",
              "docs/retrospective_2025_2026_executive_brief.md"):
        assert (ROOT / p).exists()
    print("RETROSPECTIVE 2025–2026 SOURCE/MATCH AUDIT PASSED")
    print("42 sources, 38 canonical activities (37 in window, 1 2024 excluded)")
    print("36 adjudications, 32 planned 2027 output categories, 19 with selected retrospective matches")
    print("4 families and 11 decision cases; no separately priced duplicate costs or incremental net savings")

if __name__ == "__main__":
    validate()
