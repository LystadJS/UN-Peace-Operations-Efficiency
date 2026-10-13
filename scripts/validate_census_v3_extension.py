#!/usr/bin/env python3
"""Acceptance gates: 13 October 2026 public UN mission/training source extension.

Official index links != dated delivered events; published course offerings !=
completed courses; shared financing != separately paid duplicated expense.
"""
import csv, json
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"data"/"census_v3"
CUTOFF=date(2026,10,13)

def read(path,key):
    with path.open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        assert reader.fieldnames and key in reader.fieldnames,str(path)
        rows=list(reader)
    assert rows and all(None not in x for x in rows),str(path)
    assert len({x[key] for x in rows})==len(rows),str(path)
    return rows

def v3(name,key):
    return read(BASE/(name+".csv"),key)

def validate():
    events=v3("extended_canonical_activities","canonical_id")
    calendars=v3("official_training_calendar_listings","calendar_id")
    matches=v3("reconciled_event_and_course_identities","reconciliation_id")
    options=v3("shared_production_recommendations","option_id")
    products=v3("verified_shared_knowledge_products","product_id")
    aggregates=v3("source_population_aggregate_controls","control_id")
    reform=v3("ga_authorized_training_reform","decision_id")
    pages=v3("archive_page_access","archive_page_url")
    frame=v3("archive_discovered_url_frame","source_id")
    summary=json.loads((BASE/"archive_collection_summary.json").read_text())
    old=read(ROOT/"data"/"systematic_field_training_canonical_2025_2026.csv","canonical_id")
    cj=read(ROOT/"data"/"census_v2"/"verified_joint_additions.csv","case_id")
    old_frame=read(ROOT/"data"/"census_v2"/"union_dated_notice_coverage.csv","notice_url")
    crosswalk=read(ROOT/"data"/"public_deliverable_crosswalk_2027.csv","output_pair_id")
    ranked=read(ROOT/"data"/"acabq_2027_ranked_consolidation.csv","candidate_id")

    assert len(old)==55 and len(cj)==6 and len(old_frame)==1708
    assert len(events)==18 and len(calendars)==9 and len(matches)==16
    assert len(options)==12 and len(products)==2 and len(aggregates)==4 and len(reform)==1
    assert len(pages)==27 and len(frame)==249
    assert summary["asof"]=="2026-10-13" and summary["archives_attempted"]==9
    assert summary["pages_attempted"]==27 and summary["downloaded_pages"]==24
    assert summary["discovered_distinct_link_ids"]==249
    assert summary["actual_event_denominator"]=="unknown"
    assert summary["unique_field_or_training_events_inferred"]==0
    assert summary["incremental_net_savings"]=="not_estimated"
    assert sum(r["fetch_status"]=="downloaded" for r in pages)==24
    assert sum(r["fetch_status"].startswith("HTTPError") for r in pages)==3
    assert all(r["archive"]=="MONUSCO_news" for r in pages if r["fetch_status"].startswith("HTTPError"))
    assert len({r["archive"] for r in pages})==9
    assert all(r["canonical_event_id"]=="not_assigned"
               and r["evidence_level"]=="listing_only_not_approved_delivered_event"
               and r["duplicate_paid_service"]=="not_estimated" for r in frame)
    assert not ({r["official_notice_url"] for r in frame} &
                {r["notice_url"] for r in old_frame})
    assert len(frame)+len(old_frame)==1957
    assert all(urlsplit(r["official_notice_url"]).scheme=="https" for r in frame)

    eventids={r["canonical_id"] for r in events}
    assert eventids=={f"XEV{i:03d}" for i in range(1,19)}
    assert not(eventids & {r["canonical_id"] for r in old})
    grades=Counter(r["study_window_temporal_grade"][0] for r in events)
    assert grades=={"A":7,"B":5,"C":6},grades
    for r in events:
        dates=r["source_event_date_or_range"].split("/")
        assert 1<=len(dates)<=2
        ds=[date.fromisoformat(x) for x in dates]
        assert min(ds)>=date(2025,1,1) and max(ds)<=CUTOFF
        assert r["incremental_net_savings_usd"]=="not_estimated"
        assert r["official_source_url"].startswith("https://")
        assert r["source_publication_date_distinct_from_event_date"]
        assert r["formal_report_identity"]=="distinct_from_Security_Council_or_GA_mandated_final_products"
    e={r["canonical_id"]:r for r in events}
    assert e["XEV009"]["source_event_date_or_range"]==e["XEV010"]["source_event_date_or_range"]=="2025-11-26"
    assert e["XEV009"]["title"]!=e["XEV010"]["title"]
    assert e["XEV015"]["source_event_date_or_range"]=="2026-04-27"
    assert e["XEV016"]["source_event_date_or_range"]=="2026-04-29"
    assert e["XEV015"]["official_source_url"]==e["XEV016"]["official_source_url"]
    assert e["XEV002"]["delivery_status"]=="underway_not_confirmed_completed"

    cat={r["calendar_id"] for r in calendars}
    assert cat=={f"CAT{i:03d}" for i in range(1,10)}
    assert all("verified_delivered" not in r["delivery_status"] or
               r["delivery_status"]=="not_verified_delivered" for r in calendars)
    assert next(r for r in calendars if r["calendar_id"]=="CAT003")["source_class"]=="conflicting_date_fields"
    assert next(r for r in calendars if r["calendar_id"]=="CAT007")["delivery_status"]=="not_event_delivery"
    assert all(r["net_additional_savings"]=="no_savings_claim" for r in calendars)
    known=eventids|cat|{r["canonical_id"] for r in old}|{r["case_id"] for r in cj}
    for m in matches:
        assert all(i in known for i in m["canonical_or_calendar_ids"].split(";"))
        assert m["mandate_and_accounting_guardrail"]
    assert {r["product_id"] for r in products}=={"XOUT001","XOUT002"}
    assert all(r["new_savings_usd"]=="not_estimated" for r in products)
    assert all(r["additivity_or_release_guardrail"] for r in aggregates)
    g=reform[0]
    assert g["official_symbol"]=="A/RES/80/306"
    assert g["adopted_on"]=="2026-09-03"
    assert g["target_operational_date"]=="2027-01-01"
    assert g["incremental_savings_usd"]=="not_estimated"
    assert "already_authorized" in g["status_asof_2026_10_13"]

    assert len(crosswalk)==32 and len(ranked)==14
    assert sum(r["phase11_combined_2025_26_sample_coverage"]==
               "source_present_in_selected_sample" for r in crosswalk)==20
    assert all(r["october13_verified_duplicate_cost"]=="not_established"
               and r["october13_incremental_net_savings"]=="not_estimated"
               and r["october13_acceptance_of_prior_compared_outputs"]==
                   r["phase11_combined_2025_26_sample_coverage"] for r in crosswalk)
    for r in crosswalk:
        value=r["october13_event_identity_evidence_ids"]
        if value!="none_in_new_official_sources":
            assert all(i in eventids for i in value.split(";"))
    assert sorted(int(r["revised_public_rank"]) for r in ranked)==list(range(1,15))
    assert all(r["october13_research_rank_action"]==
               "retain_prior_ranking_due_nonrepresentative_source_frame" for r in ranked)
    assert len({r["rank"] for r in options})==12
    assert all(r["verified_separately_paid_duplicate_cost"]=="not_established"
               and r["additional_net_savings_usd"]=="not_estimated"
               and r["formal_mandates_preserved"]=="yes" for r in options)
    assert options[0]["option_id"]=="SPV301"
    assert options[0]["release_type"]=="already_authorized_UN80_organizational_reform_implementation_watch"

    for name in ("docs/census_2025_2026_extended_oct13.md",
                 "docs/census_2025_2026_extended_executive.md"):
        assert (ROOT/name).exists(),name

    print("2026-10-13 UN MISSION / TRAINING CENSUS EXTENSION PASSED")
    print("Nine official archives sampled: 24/27 pages accessible, 249 new listing links")
    print("Previous distinct URL frame 1708; combined distinct URL frame 1957; not unique events")
    print("18 adjudicated additional event/cohort IDs: 7 exact, 5 Q1-bounded, 6 publication-bounded")
    print("Nine published training offerings/resources, 16 canonical reconciliation decisions")
    print("12 evidence-ranked worksharing reviews; A/RES/80/306 recognized as already authorized")
    print("20/32 prior retrospectively supported categories unchanged, no incremental net savings")

if __name__=="__main__":
    validate()
