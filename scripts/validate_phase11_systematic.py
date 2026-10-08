#!/usr/bin/env python3
"""Phase 11 source-index census and bounded mission field/training audit gates.

A published notice is not automatically a field mission/training event.
A Council record variant is not an independent formal Council meeting.
A recurring joint workshop does not prove avoidable duplicate expense.
"""
import csv
from collections import Counter
from pathlib import Path

R=Path(__file__).resolve().parents[1]

def get(name,key=None):
    path=R/"data"/(name+".csv")
    with path.open(encoding="utf-8-sig",newline="") as f:
        v=list(csv.DictReader(f))
    assert v,name
    assert all(None not in x for x in v),name
    if key:
        assert len({x[key] for x in v})==len(v),f"{name}: duplicate {key}"
    return v

r=get("systematic_sg_reports_2025_2026","document_symbol")
m=get("systematic_sc_meetings_2025_2026","record_id")
bridges=get("systematic_report_meeting_links_2025_2026","record_id")
coverage=get("systematic_2025_2026_coverage_matrix","domain")
canonical=get("systematic_field_training_canonical_2025_2026","canonical_id")
summary=get("systematic_2025_2026_canonical_type_summary")
archive=get("mission_archive_notice_metadata_2025_2026","notice_url")
archive_cat=get("mission_archive_candidate_triage","notice_url")
archive_sites=get("mission_archive_coverage_2025_2026","site")
archive_classes=get("mission_archive_classification_summary")
added=get("systematic_verified_field_training_additions","event_id")
links=get("systematic_field_training_to_2027_links","link_id")
planned=get("public_deliverable_crosswalk_2027","output_pair_id")
opportunities=get("systematic_2025_2026_shared_production_opportunities","reuse_id")
assert len(r)==132 and len(m)==474 and len(bridges)==14
assert len({x["meeting_base_id"] for x in m if x["year"]=="2025"})==255
assert len({x["meeting_base_id"] for x in m if x["year"]=="2026"})==151
assert len(coverage)==6 and len(canonical)==55
assert len(added)==17 and len(links)>=20
assert len(archive)==len(archive_cat)>=600
assert len(archive_sites)==6 and len(archive_classes)==24
assert len(planned)==32 and len(opportunities)==16
assert len({x["notice_url"] for x in archive})==len(archive)
assert {x["notice_url"] for x in archive}=={x["notice_url"] for x in archive_cat}
assert {x["event_id"] for x in added}=={f"FTX{i:03d}" for i in range(1,18)}
for x in archive_cat:
    assert x["date_is_actual_event_date"]=="not_verified"
    assert x["full_article_read"]=="no"
    assert x["coorganizer_roles_verified"]=="no"
    assert x["financial_duplicate_service"]=="not_estimated"
assert all(x["complete_event_census"]=="no" for x in archive_classes)
assert sum(int(x["archive_notice_links"]) for x in archive_sites)==len(archive)
assert next(x for x in archive_sites if x["site"]=="UNRCCA")["coverage_status"]=="access_blocked"
assert sum(x["event_year_eligibility"]=="2025_26_evidence_item" for x in canonical)==53
assert sum(x["event_year_eligibility"].startswith("excluded") for x in canonical)==2
assert next(x for x in canonical if x["canonical_id"]=="EV038")["event_year_eligibility"]=="excluded_2024"
assert next(x for x in canonical if x["canonical_id"]=="FTX017")["event_year_eligibility"]=="excluded_unverified_event_date"
assert all(x["actual_paid_duplicate"]=="not_verified" and x["new_net_savings_usd"]=="not_estimated" for x in canonical)
byftx={x["event_id"]:x for x in added}
byoutput={x["output_pair_id"]:x for x in planned}
for x in links:
    assert x["official_event_id"] in byftx
    assert x["planned_2027_pair_id"] in byoutput
    assert x["identical_deliverable_already_paid_twice"]=="not_established"
    assert x["net_savings_usd"]=="not_estimated"
new_link=Counter(x["planned_2027_pair_id"] for x in links if x["case_evidence_level"]!="date_not_independently_verified")
for x in planned:
    old=x["retrospective_2025_26_match_ids"]!="none_found_in_selected_sample"
    evid=old or new_link[x["output_pair_id"]]>0
    assert x["phase11_combined_2025_26_sample_coverage"]==("source_present_in_selected_sample" if evid else "unmatched_in_selected_sample_NOT_zero")
    assert x["phase11_financial_duplicate_service"]=="not_verified"
    assert x["phase11_net_new_savings_usd"]=="not_estimated"
assert sum(x["phase11_combined_2025_26_sample_coverage"]=="source_present_in_selected_sample" for x in planned)==20
assert new_link["DD06"]>0
assert not any(x["official_event_id"]=="FTX001" and x["planned_2027_pair_id"]=="TR08" for x in links)
assert all(x["official_url"].startswith("https://") for x in added)
assert all(x["additional_net_savings_usd"]=="not_estimated" and
           x["release_gate"]=="proposal_only_without_transaction_id_and_mandate_clearance"
           for x in opportunities)
assert opportunities[0]["reuse_id"]=="SOP01"
assert opportunities[-1]["reuse_id"]=="SOP16"
assert all(x["actual_duplicate_paid_costs"]=="not_verified" for x in coverage)
def val(domain,key):
    return next(x for x in coverage if x["domain"]==domain)[key]
assert val("Secretary-General Council reports","combined_rows")=="132"
assert val("Security Council formal meetings","combined_rows")=="406"
assert val("Formal Council transcript/document variants","combined_rows")=="474"
assert int(val("Mission news archive notice links","combined_rows"))==len(archive)
assert val("Individually identified curated activities/publications","combined_rows")=="55"
assert val("Direct SG report to Council meeting links","combined_rows")=="14"
assert sum(int(x["number_of_catalogued_canonical_records"]) for x in summary)==55
print("SYSTEMATIC 2025-26 PUBLIC EVIDENCE CENSUS VALIDATION PASSED")
print("132 indexed SG reports; 406 indexed unique formal meetings; 474 PV variants")
print(f"{len(archive)} notice titles from bounded accessible archives (UNRCCA archive blocked)")
print("55 curated activities/outputs, 53 in 2025-26 window, 2 excluded/unverified")
print(f"{len(links)} curated event-to-2027 category links; 20/32 proposed categories supported by selected 2025-26 evidence")
print("16 reusable-work options; 0 verified duplicate charges; new net savings not estimated")
