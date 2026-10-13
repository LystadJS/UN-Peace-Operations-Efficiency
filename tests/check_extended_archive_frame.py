#!/usr/bin/env python3
"""Offline accession and event-non-inference checks for mission archive discovery."""
import importlib.util
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"scripts"/"collect_extended_official_archive.py"
spec=importlib.util.spec_from_file_location("official_frame",p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
html=(b'<main><div><a href="/en/news/mission-joint-training-news">Joint mission training news</a>'
      b'<span>24 September 2025</span></div><a href="https://example.org/en/news/bad">'
      b'Offsite article should be ignored</a></main>')
out=m.extract(html,"https://unisfa.unmissions.org/en/news","/en/news/",
              "UNISFA_news",0,"https://unisfa.unmissions.org/en/news?page=0")
assert len(out)==1
r=list(out.values())[0]
assert r["canonical_event_id"]=="not_assigned"
assert r["duplicate_paid_service"]=="not_estimated"
assert r["evidence_level"]=="listing_only_not_approved_delivered_event"
assert m.scoped(r["official_notice_url"],"https://unisfa.unmissions.org/en/news","/en/news/")
assert not m.scoped("https://example.org/en/news/bad","https://unisfa.unmissions.org/en/news","/en/news/")
assert len(m.ARCHIVES)==9 and m.ASOF=="2026-10-13"
print("ARCHIVE DISCOVERY OFFLINE TEST PASSED: official host, listing-only, no invented event.")
