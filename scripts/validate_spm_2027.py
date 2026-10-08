#!/usr/bin/env python3
"""Validate 2027 SPM mission and thematic reconciliation (Python standard library)."""
import argparse
import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = {
 "spm_2027_mission_budget":"spm_id",
 "spm_2027_cluster_bridge":"component_id",
 "spm_2027_closure_bridge":"closure_id",
 "spm_2027_financing_controls":"bridge_id",
 "spm_2027_embedded_efficiencies":"efficiency_id",
 "spm_2027_source_manifest":"source_id",
 "spm_2027_source_discrepancies":"issue_id",
 "spm_2027_extrabudgetary_items":"xb_id",
 "spm_2027_extrabudgetary_coverage":"spm_id",
 "spm_2027_extrabudgetary_reconciliation":"reconciliation_key",
 "spm_2027_cross_pillar_links":"link_id",
 "spm_2027_validation_sequence":"investigation_id",
 "spm_2027_addenda":"addendum_id",
 "ga_approved_all_missions":"mission_id",
 "candidate_validation":"candidate_id"
}
def load(name,key):
    with (ROOT/"data"/(name+".csv")).open(encoding="utf-8",newline="") as file:
        reader=csv.DictReader(file)
        assert reader.fieldnames and key in reader.fieldnames,name
        rows=list(reader)
    assert rows and len(rows)==len({r[key] for r in rows}),"Nonunique or empty "+name
    assert all(None not in r and all(v is not None and str(v).strip() for v in r.values()) for r in rows),name
    return rows
def close(a,b,t=.21):
    return abs(float(a)-float(b))<=t
def verify(source_dir=None):
    d={n:load(n,k) for n,k in FILES.items()}
    missions=d["spm_2027_mission_budget"]
    ids={r["spm_id"] for r in missions}
    assert len(missions)==36
    expected={"SPM_CLUSTER_1":(12,51367.6,56331.2,253,253),
              "SPM_CLUSTER_2":(15,36431.4,37726.8,99,99),
              "SPM_CLUSTER_3":(9,324549.9,325353.9,2457,2332)}
    for cluster,(count,prior,new,people_prior,people_new) in expected.items():
        x=[r for r in missions if r["cluster_id"]==cluster]
        assert len(x)==count
        for col,val in [("regular_budget_2026_approved_usd_thousands",prior),
                        ("regular_budget_2027_proposed_usd_thousands",new),
                        ("personnel_2026_approved_table2",people_prior),
                        ("personnel_2027_proposed_table2",people_new)]:
            assert close(sum(float(r[col]) for r in x),val),f"{cluster}: {col}"
        for r in x:
            assert close(float(r["regular_budget_2027_proposed_usd_thousands"])-
                float(r["regular_budget_2026_approved_usd_thousands"]),
                r["proposal_2027_minus_2026_approved_usd_thousands"])
            assert r["incremental_savings_usd_thousands"]=="not_estimated"
            assert r["budget_status"]=="2027_SG_proposal_not_GA_appropriation"
    controls={r["component_id"]:r for r in d["spm_2027_cluster_bridge"]}
    assert set(controls)=={"CLUSTER_1","CLUSTER_2","CLUSTER_3","DISCONTINUED","RSCE_SPM_SHARE"}
    assert close(sum(float(x["proposed_2027_usd_thousands"]) for x in controls.values()),422671.0)
    assert close(sum(float(x["appropriated_2026_usd_thousands"]) for x in controls.values()),536145.0)
    assert close(sum(float(x["change_usd_thousands"]) for x in controls.values()),-113474.0)
    assert close(sum(float(x["approved_2026_usd_thousands"]) for x in d["spm_2027_closure_bridge"]),121473.1)
    efficiency=d["spm_2027_embedded_efficiencies"]
    assert len(efficiency)==31
    for cluster,target in [("I",68.6),("II",63.5),("III",14560.4)]:
        assert close(sum(float(x["projected_2027_efficiency_usd_thousands"]) for x in efficiency if x["cluster_id"]==cluster),target)
    assert close(sum(float(x["projected_2027_efficiency_usd_thousands"]) for x in efficiency),14692.5)
    assert all(x["incremental_2027_savings_available"]=="not_estimated" for x in efficiency)
    xb=d["spm_2027_extrabudgetary_items"]
    assert len(xb)==17 and all(x["spm_id"] in ids for x in xb)
    assert close(sum(float(x["projected_2027_usd_thousands"]) for x in xb),32976.673,.001)
    cover=d["spm_2027_extrabudgetary_coverage"]
    assert len(cover)==36 and {x["spm_id"] for x in cover}==ids
    assert sum(x["report_status"]=="2027_amounts_explicitly_reported" for x in cover)==14
    assert sum(x["report_status"]=="explicit_no_2027_XB" for x in cover)==1
    assert sum(x["report_status"]=="not_separately_reported" for x in cover)==21
    for x in cover:
        if x["report_status"]=="not_separately_reported":
            assert x["itemized_amount_usd_thousands"]=="not_reported"
    man=d["spm_2027_source_manifest"]
    assert len(man)==4
    for m in man:
        assert len(m["sha256"])==64
        if source_dir:
            p=source_dir/m["original_filename"]
            assert p.is_file(),str(p)
            assert hashlib.sha256(p.read_bytes()).hexdigest()==m["sha256"],str(p)
    peers={x["mission_id"] for x in d["ga_approved_all_missions"]}
    candidate={x["candidate_id"] for x in d["candidate_validation"]}
    links=d["spm_2027_cross_pillar_links"]
    assert len(links)==16
    for link in links:
        assert link["spm_id"] in ids or link["spm_id"]=="RSCE_SPM_SHARE"
        assert link["peer_GA_entity"]=="-" or link["peer_GA_entity"]=="RSCE" or link["peer_GA_entity"] in peers
        assert link["peer_spm_id"]=="-" or link["peer_spm_id"] in ids
        assert link["baseline_candidate_id"] in candidate
        assert link["incremental_net_savings_usd_thousands"]=="not_estimated"
    queue=d["spm_2027_validation_sequence"]
    assert len(queue)==12 and sorted(int(r["research_priority"]) for r in queue)==list(range(1,13))
    assert all(x["link_id"] in {y["link_id"] for y in links} for x in queue)
    assert all(x["existing_candidate_id"] in candidate and x["net_incremental_savings"]=="not_estimated" for x in queue)
    a=d["spm_2027_addenda"]
    assert [float(x["proposed_cost_usd_thousands"]) for x in a]==[422671,56331.2,37726.8,325353.9]
    assert all(x["approved_cost_usd_thousands"]=="2027_not_yet_adopted" for x in a)
    assert len(d["spm_2027_source_discrepancies"])>=7
    print("PHASE 4 SPM VALIDATION PASSED")
    print("36 mission rows, 3 clusters, RSCE 3259.1, chapeau 422671.0 thousand USD")
    print("2026-2027 change -113474.0; closures -121473.1; continuing missions +7063.0")
    print("2027 efficiencies already embedded: 14692.5 thousand USD (31 items)")
    print("2027 XB reported: 32976.673 thousand USD (17 entries); 16 links; 12 research priorities")
    print("SPM proposals NOT approved appropriations; new net savings NOT estimated")
    print("PDF hashes byte verified" if source_dir else "PDF hash manifests validated structurally")
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-dir",type=Path,default=None)
    args=parser.parse_args()
    verify(args.source_dir)
