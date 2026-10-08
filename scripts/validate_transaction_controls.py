#!/usr/bin/env python3
"""Gate the public transaction-control study; never treat budget lines as actual ledger entries."""
from __future__ import annotations
import csv
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def load(name, key):
    path=ROOT/"data"/(name+".csv")
    with path.open(encoding="utf-8",newline="") as f:
        rdr=csv.DictReader(f)
        assert rdr.fieldnames and key in rdr.fieldnames,name
        rows=list(rdr)
    assert rows and len(rows)==len({r[key] for r in rows}),name
    assert all(None not in r and all(v is not None and v.strip() for v in r.values()) for r in rows),name
    return rows

controls=load("transaction_control_baseline","control_id")
cases=load("transaction_validation_cases","case_id")
requests=load("transaction_evidence_requests","request_id")
sources=load("transaction_sources","source_id")
offsets=load("transaction_offset_reconciliation","check_id")
assert len(controls)==12 and len(cases)==3 and len(requests)==17 and len(sources)==11
assert {r["case_id"] for r in cases}=={"UNIFIL_UNSCOL","BINUH_UNSOH","RSCE"}
valid_ids={r["control_id"] for r in controls}
assert all(r["case_id"] in {c["case_id"] for c in cases} for r in controls)
assert all(r["transaction_verified"]=="no" and r["additional_net_savings_usd"]=="not_estimated"
           and r["transaction_document_id"]=="not_available" for r in controls)
assert sum(int(r["published_amount_usd"]) for r in controls
           if r["amount_category"]=="embedded_2027_efficiency")==1838100
def amount(cid):
    return int(next(x["published_amount_usd"] for x in controls if x["control_id"]==cid))
assert amount("UF01")+amount("UF02")+amount("UF03")==438100
assert amount("BH03")-amount("BH04")==1400000==amount("BH01")
assert amount("BH02")==4000000
assert amount("RS01")-amount("RS02")==936100
assert amount("RS03")==45911600 and amount("RS04")==3443200
assert len(offsets)==5
assert all(r["case_id"] in {c["case_id"] for c in cases} for r in offsets)
for c in cases:
    assert int(c["verified_invoice_asset_or_charge_pairs"])==0
    assert c["additional_addressable_usd"]=="not_estimated" and c["net_realized_savings_usd"]=="not_estimated"
for x in requests:
    assert x["case_id"] in {c["case_id"] for c in cases}
    assert x["received_status"]=="not_provided"
    assert x["internal_only"].startswith("yes_")
    assert all(i in valid_ids for i in x["linked_controls"].split(";"))
for x in sources:
    assert x["source_url"].startswith("https://")
    assert x["evidence_type"] and x["limitations"]
assert not any(x["amount_category"]=="realized_net_savings" for x in controls)
print("PHASE 5 TRANSACTION-BOUNDARY GATES PASSED")
print("3 cases, 12 budget controls, 17 targeted ledger packages, 11 sources, 5 reconciliations")
print("Booked 2027 efficiencies 1,838,100 USD; transaction-verified pairs 0")
print("No additional addressable or realized net savings asserted without internal transaction evidence")
