#!/usr/bin/env python3
"""Deeper bounded October 13 public archive INDEX pass; no inferred events."""
from pathlib import Path
import argparse
import collect_extended_official_archive as src

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--pages",type=int,default=8)
    args=ap.parse_args()
    if not 3<args.pages<=8:
        raise ValueError("Deeper index bounded to pages 0..7; never mark coverage exhaustive")
    src.ARCHIVES=[
        (name,url,fragment) for name,url,fragment in src.ARCHIVES
        if name!="MONUSCO_news"
    ]+[
        ("MONUSCO_actualites","https://monusco.unmissions.org/en/actualites","/en/news/"),
        ("UNSMIL_news","https://unsmil.unmissions.org/en/news","/en/news/"),
        ("UNIFIL_news","https://unifil.unmissions.org/en/news","/en/news/"),
    ]
    assert len(src.ARCHIVES)==11
    dest=Path(__file__).resolve().parents[1]/"data"/"census_v4"/"deeper_official_archives"
    src.run(dest,args.pages,4)
    import json
    summ=json.loads((dest/"archive_collection_summary.json").read_text())
    assert summ["pages_attempted"]==11*args.pages
    assert summ["unique_field_or_training_events_inferred"]==0
    assert summ["incremental_net_savings"]=="not_estimated"
    assert all(not v["full_2025_2026_event_population_known"]
                for v in summ["source_lineage_by_archive"].values())

if __name__=="__main__":
    main()
