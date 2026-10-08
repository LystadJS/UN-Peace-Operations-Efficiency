#!/usr/bin/env python3
"""Synthesize public 2025-2026 Council index census and bounded mission event samples.

Nothing here estimates duplication prevalence or new savings. Index record,
article notice and independently identified event are different units.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import csv

R=Path(__file__).resolve().parents[1]
def read(name):
    with (R/"data"/(name+".csv")).open(encoding="utf-8-sig",newline="") as f:
        rows=list(csv.DictReader(f))
    assert rows,name
    assert all(None not in x for x in rows),name
    return rows
def write(name,rows):
    assert rows
    p=R/"data"/(name+".csv")
    with p.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)

prior=read("retrospective_2025_2026_activities")
prior_sources={x["source_id"]:x for x in read("retrospective_2025_2026_sources")}
new=read("systematic_verified_field_training_additions")
reports=read("systematic_sg_reports_2025_2026")
meetings=read("systematic_sc_meetings_2025_2026")
links=read("systematic_report_meeting_links_2025_2026")
index_totals=read("systematic_census_index_totals")
archive_coverage=read("mission_archive_coverage_2025_2026")
notice=read("mission_archive_notice_metadata_2025_2026")
triage=read("mission_archive_candidate_triage")
proposed=read("public_deliverable_crosswalk_2027")
assert len(prior)==38 and len(new)==17 and len(reports)==132
assert len(meetings)==474 and len(links)==14 and len(proposed)==32
assert len(notice)==len(triage)
canonical=[]
for x in prior:
    past=x["activity_id"]=="EV038"
    evidence=prior_sources[x["primary_source_id"]]
    rough=any(k in x["identity_and_double_count_guardrail"].lower()
              for k in ("month", "not_verified","approx","indicative","first_week"))
    canonical.append(dict(
        canonical_id=x["activity_id"],source_layer="Phase10_adjudicated_public",
        kind=x["activity_type"],activity_or_output=x["verified_activity_or_product"],
        entities_and_roles=x["documented_entity_roles"],
        reported_start=x["actual_start_date_or_month_start"],
        reported_end=x["actual_end_date_or_month_end"],
        date_precision=("out_of_window_2024" if past else
                        "approximate_or_month" if rough else "source_record_dates"),
        publisher_article_date="not_separately_available",
        official_source_url=evidence["official_url"],
        source_id=x["primary_source_id"],
        event_year_eligibility="excluded_2024" if past else "2025_26_evidence_item",
        canonical_event_financial_unit="no",
        actual_paid_duplicate="not_verified",
        new_net_savings_usd="not_estimated",
        caution=x["identity_and_double_count_guardrail"]))
for x in new:
    excluded=x["event_date_precision"]=="date_precision_unverified"
    canonical.append(dict(
        canonical_id=x["event_id"],source_layer="Phase11_curated_public_article",
        kind=x["deliverable_type"],activity_or_output=x["canonical_event_or_publication"],
        entities_and_roles=x["evidenced_roles"],
        reported_start=x["event_start_date"],reported_end=x["event_end_date"],
        date_precision=x["event_date_precision"],
        publisher_article_date=x["publication_date"],
        official_source_url=x["official_url"],
        source_id=x["event_id"],
        event_year_eligibility="excluded_unverified_event_date" if excluded
                               else "2025_26_evidence_item",
        canonical_event_financial_unit="no",
        actual_paid_duplicate="not_verified",
        new_net_savings_usd="not_estimated",
        caution=x["adjudication_caution"]))
assert len(canonical)==55 and len({r["canonical_id"] for r in canonical})==55
write("systematic_field_training_canonical_2025_2026",canonical)

def lookup_kind(kind):
    kind=kind.lower()
    if "field" in kind or "visit" in kind: return "field_activity_or_mission"
    if any(t in kind for t in ("training","workshop","seminar","academy","syllabus",
                               "conference","practice_note")): return "training_and_learning"
    if any(t in kind for t in ("report","briefing","publication","guidance","strategic")): return "reported_product"
    return "other_activity_or_support"

groups=Counter()
for r in canonical:
    groups[(lookup_kind(r["kind"]),r["event_year_eligibility"])]+=1

nReports=Counter(int(x["index_year"]) for x in reports)
variants=Counter(int(x["year"]) for x in meetings)
uniq=Counter()
for year in (2025,2026):
    uniq[year]=len({x["meeting_base_id"] for x in meetings if int(x["year"])==year})
assert (nReports[2025],nReports[2026])==(84,48)
assert (variants[2025],variants[2026])==(296,178)
assert (uniq[2025],uniq[2026])==(255,151)
assert len(set(x["report_symbol"] for x in links))==len(links)
archive_counts={x["site"]:int(x["archive_notice_links"]) for x in archive_coverage}
assert sum(archive_counts.values())==len(notice) and archive_counts["UNRCCA"]==0
candidate_classes=Counter(x["candidate_theme"] for x in triage)

rows=[
 dict(domain="Secretary-General Council reports",grain="unique_indexed_report_symbol",
      official_2025=84,official_2026_through_oct08=48,combined_rows=132,
      census_scope="complete_rows_from_two_retrieved_official_annual_index_pages",
      source_or_method="UN_Security_Council_reports_index_2025_and_2026",
      hidden_or_missing="Non_SG_Council_documents_excluded_full_text_not_all_read",
      actual_duplicate_paid_costs="not_verified",
      conclusion="source_index_snapshot_census_not_identical_output_census"),
 dict(domain="Security Council formal meetings",grain="unique_meeting_base_id_not_resumption",
      official_2025=255,official_2026_through_oct08=151,combined_rows=406,
      census_scope="retrieved_official_formal_meeting_document_index",
      source_or_method="UN_Security_Council_formal_meeting_indexes",
      hidden_or_missing="296_2025_and_178_2026_document_variants_2025_115_informal_consultations_not_included",
      actual_duplicate_paid_costs="not_verified",
      conclusion="2025_255_matches_annual_official_total_2026_partial_year"),
 dict(domain="Formal Council transcript/document variants",grain="S_PV_document_variant",
      official_2025=296,official_2026_through_oct08=178,combined_rows=474,
      census_scope="index_variants_with_resumptions_not_independent_meetings",
      source_or_method="same_formal_meeting_indexes",
      hidden_or_missing="Do_not_count_resumed_segments_as_new_meetings",
      actual_duplicate_paid_costs="not_verified",
      conclusion="same_meeting_id_can_have_multiple_index_variants"),
 dict(domain="Mission news archive notice links",grain="URL_title_not_actual_event",
      official_2025="not_year_partitioned",official_2026_through_oct08="not_year_partitioned",
      combined_rows=len(notice),
      census_scope="bounded_pagination_five_accessible_archives_of_six_attempted",
      source_or_method="UNOWAS_UNOCA_UNAMA_DPPA_DPO_archive_listing_cards",
      hidden_or_missing="UNRCCA_blocked;dates_missing_on_many_cards;multiple_notices_per_event",
      actual_duplicate_paid_costs="not_verified",
      conclusion="source_discovery_queue_not_field_training_census"),
 dict(domain="Individually identified curated activities/publications",
      grain="analyst_canonical_activity_or_output_record",
      official_2025="not_population_estimate",official_2026_through_oct08="not_population_estimate",
      combined_rows=len(canonical),
      census_scope="Phase10_38_plus_new_Phase11_17_curated_records",
      source_or_method="retrospective_activities_plus_17_official_field_training_notices",
      hidden_or_missing="one_2024_excluded_one_2025_event_date_unverified_multiple_event_date_precision_types",
      actual_duplicate_paid_costs="not_verified",
      conclusion="not_exhaustive_population_and_not_all_55_are_event_days"),
 dict(domain="Direct SG report to Council meeting links",
      grain="report_meeting_link_with_evidence_grade",
      official_2025="not_population_estimate",official_2026_through_oct08="not_population_estimate",
      combined_rows=len(links),
      census_scope="source_attested_subset_of_possible_reporting_meeting_pairs",
      source_or_method="specific_Council_agendas_WebTV_official_document_symbols",
      hidden_or_missing="one_topic_date_candidate_not_direct_link_other_attendances_unchecked",
      actual_duplicate_paid_costs="not_verified",
      conclusion="do_not_infer_report_meeting_link_by_keyword_only"),
]
write("systematic_2025_2026_coverage_matrix",rows)

activity_count=[
 dict(kind=k,window_status=window,number_of_catalogued_canonical_records=v,
      unit="curated_source_identified_record_not_comprehensive_event_population",
      actual_duplication_status="not_verified",new_savings_usd="not_estimated")
 for (k,window),v in sorted(groups.items())
]
write("systematic_2025_2026_canonical_type_summary",activity_count)
# Link individually verified notices to the previously frozen 2027 output categories.
# A match is evidence coverage only; it cannot certify the same final deliverable.
valid_ids={r["output_pair_id"] for r in proposed}
new_links=[]
for source in new:
    ids=source["linked_2027_deliverable_ids"].split(";")
    for ident in ids:
        if ident not in valid_ids:
            raise AssertionError("Unrecognized 2027 pair in curated evidence: "+ident)
        new_links.append(dict(
            link_id="NEW"+str(len(new_links)+1).zfill(3),
            official_event_id=source["event_id"],
            planned_2027_pair_id=ident,
            event_or_publication=source["canonical_event_or_publication"],
            official_notice_url=source["official_url"],
            event_date_precision=source["event_date_precision"],
            named_roles_as_reported=source["evidenced_roles"],
            relationship_category=source["documented_reuse_type"],
            case_evidence_level=("date_not_independently_verified" if
                source["event_date_precision"]=="date_precision_unverified"
                else "source_identified_activity_with_explicit_role_caveats"),
            identical_deliverable_already_paid_twice="not_established",
            net_savings_usd="not_estimated"))
write("systematic_field_training_to_2027_links",new_links)
for row in proposed:
    ftx=[x for x in new_links if x["planned_2027_pair_id"]==row["output_pair_id"]]
    dated=[x for x in ftx if x["case_evidence_level"]!="date_not_independently_verified"]
    old_supported=row["retrospective_2025_26_match_ids"]!="none_found_in_selected_sample"
    row["phase11_curated_official_activity_ids"]=(
        ";".join(sorted({x["official_event_id"] for x in ftx})) if ftx else "none_in_new_curated_sample")
    row["phase11_dated_or_partial_activity_ids"]=(
        ";".join(sorted({x["official_event_id"] for x in dated})) if dated else "none")
    row["phase11_combined_2025_26_sample_coverage"]=(
        "source_present_in_selected_sample" if dated or old_supported
        else "unmatched_in_selected_sample_NOT_zero")
    row["phase11_financial_duplicate_service"]="not_verified"
    row["phase11_net_new_savings_usd"]="not_estimated"
write("public_deliverable_crosswalk_2027",proposed)
c=sum(x["phase11_combined_2025_26_sample_coverage"]=="source_present_in_selected_sample" for x in proposed)
if c!=20:
    raise AssertionError(f"Unexpected expanded selected-source category coverage {c}, expected 20")

print("SYSTEMATIC PUBLIC SOURCE VIEWS")
print("Council report symbols",len(reports),"formal meeting IDs",sum(uniq.values()),
      "PV variants",len(meetings),"bounded news notices",len(notice))
print("Curated canonical",len(canonical),"eligible",sum(r["event_year_eligibility"]=="2025_26_evidence_item" for r in canonical))
print("Archive potential tags",dict(candidate_classes))
