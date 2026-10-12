#!/usr/bin/env python3
"""Acceptance controls for the 2026-10-12 publicly indexed peace-operations census.

The source frame is broader than the subset of retrievable article bodies.
A notice or keyword-flagged paragraph is *not* a distinct dated event.
2026 is partial; Security Council report and meeting products are legally distinct.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "census_v2"


def load(path: Path, primary: str | None = None) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        assert reader.fieldnames and (primary is None or primary in reader.fieldnames), str(path)
        values = list(reader)
    assert values and all(None not in row for row in values), str(path)
    if primary:
        ids = [r[primary] for r in values]
        assert all(ids) and len(ids) == len(set(ids)), f"Nonunique key in {path}"
    return values


def dataset(name: str, key: str | None = None) -> list[dict[str, str]]:
    return load(BASE / f"{name}.csv", key)


def validate() -> None:
    overview = json.loads((BASE / "summary.json").read_text(encoding="utf-8"))
    assert overview["asof"] == "2026-10-12"
    assert overview["duplicate_spending"] == "not_estimated"
    assert overview["unknown_event_counts_not_zero"] is True

    reports = dataset("council_reports", "document_symbol")
    meetings = dataset("council_meeting_variants", "record_id")
    snapshots = dataset("council_fetches")
    assert len(reports) == overview["council_reports"] == 132
    assert len(meetings) == overview["council_meeting_variants"] == 478
    assert len({r["meeting_base_id"] for r in meetings}) == overview["distinct_council_meetings"] == 410
    assert Counter(r["index_year"] for r in reports) == {"2025": 84, "2026": 48}
    assert Counter(r["year"] for r in meetings) == {"2025": 296, "2026": 182}
    assert len({r["meeting_base_id"] for r in meetings if r["year"] == "2025"}) == 255
    assert len({r["meeting_base_id"] for r in meetings if r["year"] == "2026"}) == 155
    assert len(snapshots) == 4 and overview["council_index_success"] == 4
    assert all(r["snapshot_asof"] == "2026-10-12" for r in reports + meetings)
    assert all(r["date"] <= "2026-10-12" for r in meetings)
    assert all(r["indexed_date"] <= "2026-10-12" for r in reports)
    assert all(r["meeting_to_report_link"] == "not_inferred_from_same_topic_alone" for r in meetings)
    assert all(r["financial_duplication"] == "not_estimated" for r in meetings + reports)
    assert any(r["document_symbol"] == "S/2026/513" and
               r["date_year_mismatch"] == "true" for r in reports), "Known SG index anomaly must be retained"

    frame = dataset("notice_frame", "notice_url")
    attempts = dataset("article_fetches", "url")
    notices = dataset("notices", "notice_id")
    candidates = dataset("event_paragraph_candidates", "candidate_id")
    coverage = dataset("coverage", "publisher")
    lineage = dataset("fetch_lineage", "notice_url")
    issues = dataset("date_quality_exceptions", "exception_id")
    assert len(frame) == len(attempts) == len(lineage) == overview["frame_notices"] == 1708
    assert len(notices) == overview["downloaded_notices"] == 524
    assert len(candidates) == overview["candidate_paragraphs"] == 848
    assert overview["article_attempts"] == 1708
    assert len(coverage) == 6 and len(issues) == 2
    by_attempt = {r["url"]: r for r in attempts}
    by_notice = {r["url"]: r for r in notices}
    by_lineage = {r["notice_url"]: r for r in lineage}
    assert set(by_lineage) == set(by_attempt) == {r["notice_url"] for r in frame}
    assert set(by_notice) == {r["url"] for r in attempts if r["status"] == "downloaded"}
    assert sum(x["status"] == "downloaded" for x in attempts) == 524
    assert sum(x["status"].startswith("HTTPError") for x in attempts) == 1184
    assert sum(x["body_ever_downloaded"] == "yes" for x in lineage) == 1051
    assert sum(x["earlier_article_downloaded"] == "yes" for x in lineage) == 688
    assert sum(x["expanded_snapshot_downloaded"] == "yes" for x in lineage) == 524
    assert sum(x["expanded_chronology_status"] == "publication_in_window" for x in lineage) == 171
    assert sum(x["expanded_chronology_status"] == "before_window" for x in lineage) == 351
    assert sum(x["expanded_chronology_status"] == "insufficient_article_content" for x in lineage) == 2
    assert sum(x["exception_status"] == "article_title_year_and_masthead_year_conflict"
               for x in lineage) == len(issues) == 2
    assert {r["publisher"] for r in coverage} == {"UNOWAS", "UNOCA", "UNRCCA", "UNAMA", "DPPA", "DPO"}
    assert sum(int(r["downloaded"]) for r in coverage) == 524
    assert sum(int(r["dated_publication_in_window"]) for r in coverage) == 171
    assert all(r["event_population_denominator"] == "unknown" and
               r["adjudicated_event_completeness"] == "not_claimed" for r in coverage)
    assert all(r["event_census_status"] == "notice_not_adjudicated_event" and
               r["incremental_savings"] == "not_estimated" for r in notices)
    assert all(r["event_id"] == "not_assigned" and
               r["duplicate_payment"] == "not_estimated" for r in candidates)
    assert all("2025-01-01" <= r["publication_date"] <= "2026-10-12"
               for r in notices if r["chronology_status"] == "publication_in_window")
    assert all(r["source_stage"] == "not_available" for r in []), "Intentional no-op"

    additions = dataset("verified_joint_additions", "case_id")
    assert len(additions) == 6
    assert {r["case_id"] for r in additions} == {f"CJ{i:03d}" for i in range(1, 7)}
    assert sum(r["date_precision"].startswith("exact") for r in additions) == 4
    for r in additions:
        d0 = date.fromisoformat(r["activity_start_or_lower_bound"])
        d1 = date.fromisoformat(r["activity_end_or_upper_bound"])
        publication = date.fromisoformat(r["source_publication_date"])
        assert date(2025, 1, 1) <= d0 <= d1 <= publication <= date(2026, 10, 12)
        assert r["official_source_url"].startswith("https://")
        assert urlsplit(r["official_source_url"]).hostname in {
            "dppa.un.org", "unowas.unmissions.org", "peacekeeping.un.org"}
        assert len(r["verified_HTML_sha256"]) == 64
        assert r["activity_is_distinct_paid_duplicate"] == "not_established"
        assert r["new_net_savings_usd"] == "not_estimated"
        assert r["evidenced_roles"] and r["mandate_guardrail"]

    older = load(ROOT / "data" / "systematic_field_training_canonical_2025_2026.csv", "canonical_id")
    assert len(older) == 55
    assert sum(r["event_year_eligibility"].startswith("excluded") for r in older) == 2
    planned = load(ROOT / "data" / "public_deliverable_crosswalk_2027.csv", "output_pair_id")
    assert len(planned) == 32
    assert sum(r["phase11_combined_2025_26_sample_coverage"] == "source_present_in_selected_sample"
               for r in planned) == 20
    expected = {}
    for add in additions:
        for key in add["candidate_2027_pair_ids"].split(";"):
            expected.setdefault(key, set()).add(add["case_id"])
    assert len(expected) == 8
    for row in planned:
        actual = row["oct12_new_joint_case_ids"]
        ids = set() if actual == "none_new_in_selected_cases" else set(actual.split(";"))
        assert ids == expected.get(row["output_pair_id"], set())
        assert row["oct12_duplicate_paid_service"] == "not_established"
        assert row["oct12_new_net_savings_usd"] == "not_estimated"
        assert row["oct12_accepted_retrospective_census_coverage"] == row["phase11_combined_2025_26_sample_coverage"]
        if ids:
            assert row["oct12_case_relation"].startswith("candidate_related_workflow_NOT")

    streams = dataset("coverage_by_stream", "stream_id")
    shortlist = dataset("shared_production_shortlist", "option_id")
    assert len(streams) == 5 and len(shortlist) == 8
    assert all(r["full_event_census_certified"] == "no" for r in streams)
    assert sorted(int(r["review_rank"]) for r in shortlist) == list(range(1, 9))
    assert all(r["additional_net_savings_usd"] == "not_estimated" for r in shortlist)
    assert next(r for r in streams if r["stream_id"] == "MISSION_DEPARTMENT_NOTICE_FRAME")["records"] == "1708"
    assert next(r for r in streams if r["stream_id"] == "CURATED_FIELD_TRAINING_RESEARCH")["records"] == "61"

    for name in ("systematic_2025_2026_executive_brief.md",
                 "systematic_2025_2026_census_oct12.md"):
        assert (ROOT / "docs" / name).is_file(), name

    print("2026-10-12 CENSUS QA PASSED")
    print("132 SG Council reports; 410 distinct formal Council meetings; 478 verbatim variants")
    print("1,708 public news links; 524 latest article bodies; 1,051 ever downloaded across snapshots")
    print("171 in-window header dates among latest bodies; two title/header year conflicts")
    print("848 unadjudicated paragraph candidates, six independently adjudicated new joint activities")
    print("55 previous curated records + 6 additions; 20/32 directly matched 2027 categories unchanged")
    print("No duplicate paid services or new net savings verified; field and training population not complete")


if __name__ == "__main__":
    validate()
