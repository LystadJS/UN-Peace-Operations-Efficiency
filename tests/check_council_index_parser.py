#!/usr/bin/env python3
"""Offline synthetic HTML test: no live Council data modified."""
from datetime import date
from pathlib import Path
import importlib.util
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("council_index",(root/"scripts/collect_council_index.py"))
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
html=(root/"tests/fixtures/council_index_SYNTHETIC.html").read_text(encoding="utf-8")
rows,issues,count=module.parse_table(html,2026,date(2026,10,8),"SYNTHETIC_OFFLINE_FIXTURE")
assert count==5,(count,rows)
assert {r["symbol"] for r in rows}=={"S/2026/445","S/2026/537"}
assert {x[0] for x in issues}=={"S/2026/513","S/2026/900"}
assert all(r["stage"]=="official_index_table_pending_human_QA" for r in rows)
assert all(r["duplicate_cost"]=="not_estimated" for r in rows)
print("OFFLINE SYNTHETIC COUNCIL INDEX PARSER PASSED: 2 valid 2026 records, 2 date exceptions.")
