#!/usr/bin/env python3
"""Audit 2027 ACABQ budget recommendations against SG proposals.

Sources: uploaded A/81/7 (section 3 and section 5), A/81/7/Add.2 and
A/81/7/Add.3. Cluster III and Add.1 advisory opinions remain unverified.
All budget figures below are USD thousands. Advice is NOT GA appropriation.
"""
import argparse
import csv
import hashlib
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA={
    "acabq_2027_mission_reconciliation":"spm_id",
    "acabq_2027_cluster_reconciliation":"cluster_id",
    "acabq_2027_financial_actions":"action_id",
    "acabq_2027_non_spm_reconciliation":"perimeter_id",
    "acabq_2027_qualitative_directives":"directive_id",
    "acabq_2027_ranked_consolidation":"candidate_id",
    "acabq_2027_source_manifest":"symbol",
    "acabq_2027_report_status":"symbol",
    "spm_2027_mission_budget":"spm_id",
    "ranked_consolidation_validation":"candidate_id",
}
def read(name,key):
    with (ROOT/"data"/(name+".csv")).open(encoding="utf-8-sig",newline="") as f:
        parser=csv.DictReader(f)
        assert parser.fieldnames and key in parser.fieldnames, name
        values=list(parser)
    assert values and len(values)==len({x[key] for x in values}),"Bad primary key "+name
    assert all(None not in x and all(v is not None and str(v).strip() for v in x.values())
               for x in values),"Blank/null "+name
    return values
def close(x,y,t=.011):
    return abs(float(x)-float(y))<=t
def verify(source_dir=None):
    d={n:read(n,k) for n,k in DATA.items()}
    m={x["spm_id"]:x for x in d["acabq_2027_mission_reconciliation"]}
    sg={x["spm_id"]:x for x in d["spm_2027_mission_budget"]}
    assert len(m)==len(sg)==36 and set(m)==set(sg)
    bycluster={}
    for ident,x in m.items():
        original=sg[ident]
        assert x["cluster_id"]==original["cluster_id"]
        assert close(x["sg_2027_proposal_usd_thousands"],
                     original["regular_budget_2027_proposed_usd_thousands"])
        bycluster.setdefault(x["cluster_id"],[]).append(x)
        if x["cluster_id"]=="SPM_CLUSTER_3":
            assert x["acabq_recommended_2027_usd_thousands"]=="not_extracted"
            assert x["acabq_minus_sg_usd_thousands"]=="not_calculable"
            assert x["status"]=="requires_full_ACABQ_cluster_III_report"
        else:
            assert x["status"]=="ACABQ_2027_advisory_financial_reconciliation_complete"
            assert close(float(x["acabq_recommended_2027_usd_thousands"])-
                         float(x["sg_2027_proposal_usd_thousands"]),
                         x["acabq_minus_sg_usd_thousands"])
        assert x["savings_classification"]=="ACABQ_advisory_resource_adjustment_not_new_duplication_saving"
        assert x["approved_by_ga_2027"]=="not_approved_in_source_corpus"
    assert [len(bycluster["SPM_CLUSTER_"+str(c)]) for c in (1,2,3)]==[12,15,9]
    assert close(sum(float(x["acabq_recommended_2027_usd_thousands"])
                     for x in bycluster["SPM_CLUSTER_1"]),56148.7)
    assert close(sum(float(x["acabq_recommended_2027_usd_thousands"])
                     for x in bycluster["SPM_CLUSTER_2"]),37726.8)
    assert close(sum(float(x["acabq_recommended_2027_usd_thousands"])
                     for x in m.values() if x["cluster_id"]!="SPM_CLUSTER_3"),93875.5)
    for ident,delta in {"SPM005":-4.8,"SPM006":-87.6,"SPM009":-90.1}.items():
        assert close(m[ident]["acabq_minus_sg_usd_thousands"],delta)
    assert sum(float(x["acabq_minus_sg_usd_thousands"])!=0
               for x in m.values() if x["cluster_id"]!="SPM_CLUSTER_3")==3
    cl={x["cluster_id"]:x for x in d["acabq_2027_cluster_reconciliation"]}
    assert len(cl)==6
    for ident,p,adjusted,diff in [
        ("SPM_CLUSTER_1",56331.2,56148.7,-182.5),
        ("SPM_CLUSTER_2",37726.8,37726.8,0),
        ("REVIEWED_I_II",94058,93875.5,-182.5),
    ]:
        x=cl[ident]
        assert close(x["sg_2027_proposal_usd_thousands"],p)
        assert close(x["acabq_adjusted_2027_usd_thousands"],adjusted)
        assert close(x["acabq_minus_sg_usd_thousands"],diff)
    assert cl["SPM_CLUSTER_3"]["acabq_adjusted_2027_usd_thousands"]=="not_extracted"
    assert cl["ALL_36_PLUS_RSCE"]["acabq_adjusted_2027_usd_thousands"]=="not_calculable"
    actions=d["acabq_2027_financial_actions"]
    assert len(actions)==12
    def total(bucket):
        return sum(float(x["acabq_minus_sg_usd_thousands"]) for x in actions
                   if x["financial_perimeter"]==bucket)
    for bucket,expected in [
        ("SPM_CLUSTER_1",-182.5),
        ("SECTION_3_NON_SPM",-189.3),
        ("SECTION_5_REGULAR",-26.7),
    ]:
        assert close(total(bucket),expected),bucket
    assert sum(x["financial_perimeter"]=="SPM_CLUSTER_1" for x in actions)==4
    nonspm={x["perimeter_id"]:x for x in d["acabq_2027_non_spm_reconciliation"]}
    assert len(nonspm)==2
    for ident,p,delta,target in [
        ("SECTION_3_NON_SPM",132611.2,-189.3,132421.9),
        ("SECTION_5_REGULAR",56931.8,-26.7,56905.1)
    ]:
        x=nonspm[ident]
        assert close(x["sg_2027_proposal_usd_thousands"],p)
        assert close(x["acabq_net_adjustment_usd_thousands"],delta)
        assert close(x["acabq_adjusted_proposal_usd_thousands"],target)
    assert len(d["acabq_2027_qualitative_directives"])==20
    ranks=d["ranked_consolidation_validation"]
    assert len(ranks)==14 and sorted(int(x["rank"]) for x in ranks)==list(range(1,15))
    assert sorted(int(x["old_phase3_rank"]) for x in ranks)==list(range(1,15))
    assert all(x["net_savings_status"]=="not_estimated" for x in ranks)
    q=d["acabq_2027_ranked_consolidation"]
    assert len(q)==14 and sorted(int(x["revised_public_rank"]) for x in q)==list(range(1,15))
    assert sorted(int(x["prior_phase3_rank"]) for x in q)==list(range(1,15))
    assert all(x["verified_incremental_net_savings_usd"]=="not_estimated"
               and x["recommend_cut_now"]=="no" for x in q)
    assert {x["candidate_id"] for x in q}=={x["candidate_id"] for x in ranks}
    assert [next(x["candidate_id"] for x in q if x["revised_public_rank"]==str(i))
            for i in (1,2,3,4)]==["C16","C07","C01","C04"]
    docs=d["acabq_2027_source_manifest"]
    assert len(docs)==3
    for x in docs:
        assert re.fullmatch(r"[0-9a-f]{64}",x["sha256"])
        if source_dir:
            p=source_dir/x["uploaded_filename"]
            assert p.is_file(),str(p)
            assert hashlib.sha256(p.read_bytes()).hexdigest()==x["sha256"],str(p)
    reports={x["symbol"]:x for x in d["acabq_2027_report_status"]}
    assert reports["A/81/7/Add.2"]["reviewed_recommendation_usd_thousands"]=="56148.7"
    assert reports["A/81/7/Add.3"]["reviewed_recommendation_usd_thousands"]=="37726.8"
    assert reports["A/81/7/Add.4"]["reviewed_recommendation_usd_thousands"]=="not_extracted"
    assert all(x["availability"]=="uploaded_full_text_recommendations_extracted"
               for k,x in reports.items() if k in ("A/81/7","A/81/7/Add.2","A/81/7/Add.3"))
    print("ACABQ RECONCILIATION PASSED: 27/36 SPM missions numerically reconciled.")
    print("Cluster I 56331.2 to 56148.7 (-182.5 USD thousands); Cluster II unchanged 37726.8.")
    print("Cluster III (9 missions) and SPM crosscutting Add.1 remain unresolved.")
    print("Non-SPM Section 3 132611.2 to 132421.9; Section 5 56931.8 to 56905.1.")
    print("12 financial actions, 20 qualitative directives, 14 research ranks, 0 incremental savings certified.")
    print("Original source PDFs checksum-verified" if source_dir else "Manifest SHA-256 structures validated; optional --source-dir checks original bytes")
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",type=Path)
    args=p.parse_args()
    verify(args.source_dir)
