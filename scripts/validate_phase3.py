#!/usr/bin/env python3
"""Validate 2026/27 GA appropriation evidence, cost inclusions, staffing and remaining SPM gaps."""
from pathlib import Path
import argparse
import csv
import hashlib
import re

ROOT=Path(__file__).resolve().parents[1]
DATA={
    "mission_budget_register":"mission_id",
    "ga_mission_reconciliation":"mission_id",
    "ga_approved_resource_components":"component_id",
    "ga_approved_all_missions":"mission_id",
    "ga_adopted_directives":"directive_id",
    "ga_apportionment_schedule":"segment_id",
    "ga_unmiss_abolishments":"abolition_record",
    "approved_document_manifest":"source_id",
    "candidate_validation":"candidate_id",
    "ranked_consolidation_validation":"candidate_id",
    "quality_issues":"issue_id",
    "spm_2027_addenda":"addendum_id",
    "spm_fiscal_boundary":"boundary_id"
}
def load(name,key):
    with (ROOT/"data"/(name+".csv")).open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        assert reader.fieldnames and key in reader.fieldnames,name
        rows=list(reader)
    assert rows and len(rows)==len({r[key] for r in rows}),"Bad primary keys: "+name
    assert all(None not in r and all(v is not None and str(v).strip() for v in r.values()) for r in rows),"Missing field: "+name
    return rows
def eq(a,b,tol=.12):
    return abs(float(a)-float(b))<=tol
def validate(source_dir=None):
    d={n:load(n,k) for n,k in DATA.items()}
    expected={"MINUSCA":"276","MONUSCO":"278","UNIFIL":"282","UNISFA":"275","UNMISS":"283","UNSOS":"285"}
    ga={r["mission_id"]:r for r in d["ga_mission_reconciliation"]}
    sg={r["mission_id"]:r for r in d["mission_budget_register"]}
    assert set(expected)==set(ga)==set(sg)
    for mid,symbol in expected.items():
        x=ga[mid]
        assert x["ga_resolution"]=="A/RES/80/"+symbol
        assert x["ga_adoption_status"]=="verified_in_uploaded_operative_resolution"
        assert x["reconciliation_status"]=="approved_maintenance_and_appropriation_components_verified"
        assert eq(x["sg_proposal_usd_thousands"],sg[mid]["proposed_2026_27_gross"])
        assert sg[mid]["budget_status"]=="SG_proposal_not_appropriation"
        assert sg[mid]["net_incremental_savings"]=="not_estimated"
        maintain=sum(float(x[k]) for k in ("ga_approved_military_police_usd_thousands","ga_approved_civilian_usd_thousands","ga_approved_operational_usd_thousands"))
        share=sum(float(x[k]) for k in ("ga_support_account_share_usd_thousands","ga_logistics_base_share_usd_thousands","ga_regional_service_centre_share_usd_thousands"))
        assert eq(maintain,x["ga_approved_maintenance_usd_thousands"])
        assert eq(maintain+share,x["ga_appropriation_usd_thousands"])
        assert eq(maintain-float(x["sg_proposal_usd_thousands"]),x["adopted_minus_proposed_usd_thousands"])
    assert eq(sum(float(x["sg_proposal_usd_thousands"]) for x in ga.values()),4120950.7)
    assert eq(sum(float(x["ga_approved_maintenance_usd_thousands"]) for x in ga.values()),4028188.0)
    assert eq(sum(float(x["ga_appropriation_usd_thousands"]) for x in ga.values()),4442119.4)
    assert eq(sum(float(x["adopted_minus_proposed_usd_thousands"]) for x in ga.values()),-92762.7)
    allmission=d["ga_approved_all_missions"]
    assert len(allmission)==11 and eq(sum(float(x["approved_maintenance_usd_thousands"]) for x in allmission),4625940.1)
    for x in allmission:
        if x["mission_id"] in ga:
            assert eq(x["approved_maintenance_usd_thousands"],ga[x["mission_id"]]["ga_approved_maintenance_usd_thousands"])
    for mid in ga:
        components=[x for x in d["ga_approved_resource_components"] if x["mission_id"]==mid]
        assert len(components)==17
        groups={k:[float(x["approved_usd_thousands"]) for x in components if x["hierarchy"]==k]
                for k in ("maintenance_top_level","operational_subcomponent","corporate_share_in_GA_appropriation","GA_total_top_level")}
        assert [len(groups[k]) for k in groups]==[3,10,3,1]
        assert eq(sum(groups["maintenance_top_level"]),ga[mid]["ga_approved_maintenance_usd_thousands"])
        assert eq(sum(groups["operational_subcomponent"]),ga[mid]["ga_approved_operational_usd_thousands"])
        assert eq(sum(groups["corporate_share_in_GA_appropriation"]),float(ga[mid]["ga_appropriation_usd_thousands"])-float(ga[mid]["ga_approved_maintenance_usd_thousands"]))
        assert eq(groups["GA_total_top_level"][0],ga[mid]["ga_appropriation_usd_thousands"])
    segments=d["ga_apportionment_schedule"]
    assert len(segments)==11
    for mid in ga:
        assert eq(sum(float(x["apportioned_usd_thousands"]) for x in segments if x["mission_id"]==mid),ga[mid]["ga_appropriation_usd_thousands"])
    assert len(d["ga_unmiss_abolishments"])==11
    assert sum(int(x["GA_abolished_posts_or_positions"]) for x in d["ga_unmiss_abolishments"])==91
    assert sum(int(x["GA_abolished_posts_or_positions"]) for x in d["ga_unmiss_abolishments"] if x["section_in_annex"]=="Electoral Affairs Division")==53
    candidate={x["candidate_id"] for x in d["candidate_validation"]}
    assert len(d["ga_adopted_directives"])==15 and "C19" in candidate
    assert all(x["linked_candidate_id"]=="-" or x["linked_candidate_id"] in candidate for x in d["ga_adopted_directives"])
    ranked=d["ranked_consolidation_validation"]
    assert len(ranked)==14 and sorted(int(x["rank"]) for x in ranked)==list(range(1,15))
    assert all(x["candidate_id"] in candidate and x["net_savings_status"]=="not_estimated" for x in ranked)
    rank={x["candidate_id"]:x for x in ranked}
    for cid,mid in [("C12","UNIFIL"),("C15","UNMISS"),("C19","UNISFA"),("C08","UNSOS")]:
        assert eq(rank[cid]["scope_amount_usd_thousands"],ga[mid]["ga_approved_maintenance_usd_thousands"])
    assert eq(rank["C13"]["scope_amount_usd_thousands"],4000)
    docs=d["approved_document_manifest"]
    assert len(docs)==7 and {x["source_id"] for x in docs}=={"GA_ANNEX"}|{"GA_"+x for x in expected}
    for x in docs:
        assert re.fullmatch(r"[0-9a-f]{64}",x["sha256"])
        if source_dir:
            file=source_dir/x["filename"]
            assert file.is_file(),"Missing source file: "+str(file)
            assert hashlib.sha256(file.read_bytes()).hexdigest()==x["sha256"],"SHA mismatch: "+str(file)
    assert all(ga[x["scope"]]["uploaded_resolution_sha256"]==x["sha256"] for x in docs if x["scope"] in ga)
    assert len(d["spm_2027_addenda"])==4
    assert [float(x["proposed_cost_usd_thousands"]) for x in d["spm_2027_addenda"]]==[422671,56331.2,37726.8,325353.9]
    spm={x["boundary_id"]:x for x in d["spm_fiscal_boundary"]}
    assert eq(float(spm["SB02"]["amount_usd_thousands"])-float(spm["SB03"]["amount_usd_thousands"]),4959.6)
    issue={x["issue_id"]:x for x in d["quality_issues"]}
    assert issue["Q08"]["status"]=="resolved" and issue["Q09"]["status"]=="resolved"
    print("PHASE 3 VALIDATION PASSED")
    print("Six GA appropriations reconciled; 102 components and 11 all-mission totals verified")
    print("SG maintenance=4,120,950.7 GA maintenance=4,028,188.0 GA inclusive=4,442,119.4 thousand USD")
    print("Approved minus requested maintenance=-92,762.7 thousand USD; not a savings estimate")
    print("UNMISS abolished positions=91, electoral positions=53; 14 research rankings")
    print("SPM detailed addenda still pending; no verified duplicate spending or incremental net savings")
    print("Upload hashes confirmed" if source_dir else "Hash format checked; --source-dir verifies bytes")
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-dir",type=Path,default=None)
    args=parser.parse_args()
    validate(args.source_dir)
