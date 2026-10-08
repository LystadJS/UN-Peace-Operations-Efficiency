#!/usr/bin/env python3
"""Bounded official mission news ARCHIVE metadata collection, not an event census.

Mission sites' archive pages may block bots or paginate irregularly.
Every source attempt is recorded, and articles are labeled as notices:
several notices can refer to one event and some events are never publicized.
No claim of complete field/training event coverage may be made from this file.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import re
import time
from datetime import datetime, date
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

AS_OF=date(2026,10,8)
TARGETS = {
    "UNOWAS": "https://unowas.unmissions.org/en/news",
    "UNOCA": "https://unoca.unmissions.org/en/news",
    "UNRCCA": "https://unrcca.unmissions.org/en/news",
    "UNAMA": "https://unama.unmissions.org/en/news",
    "DPPA": "https://dppa.un.org/en/news",
    "DPO": "https://peacekeeping.un.org/en/news",
}
MONTHS=("January February March April May June July August September October November December").split()
DATE_RE = re.compile(r"\b(\d{1,2})\s+("+"|".join(MONTHS)+r")\s+(2024|2025|2026)\b",re.I)
ISO_RE = re.compile(r"\b(202[4-6])-(\d{2})-(\d{2})\b")
def article_date(txt):
    m=DATE_RE.search(txt)
    if m:
        try:return datetime.strptime(m.group(0),"%d %B %Y").date().isoformat()
        except ValueError:pass
    m=ISO_RE.search(txt)
    if m:
        try:return date.fromisoformat(m.group(0)).isoformat()
        except ValueError:pass
    return "not_verified_in_archive_card"
def fetch(url):
    req=Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; UN-PO-Efficiency-public-index/1.0)",
                            "Accept":"text/html,application/xhtml+xml"})
    with urlopen(req,timeout=22) as response:
        data=response.read(5_000_000)
        if response.status!=200 or len(data)<300:
            raise OSError("status_or_length_invalid")
        return data
def cards(body,site,listing_url):
    soup=BeautifulSoup(body,"html.parser")
    results={}
    for a in soup.find_all("a",href=True):
        h=a["href"]
        if "/en/news/" not in h and "/en/node/" not in h:
            continue
        url=urljoin(listing_url,h)
        if url.rstrip("/")==TARGETS.get(site):
            continue
        title=a.get_text(" ",strip=True)
        if not title or len(title)<14 or len(title)>260:
            continue
        parent=a.find_parent(class_=re.compile("views.row|card|search.result|node|list.item",re.I))
        if parent is None:
            parent=a.find_parent("article")
        if parent is None:
            parent=a.parent.parent
        snippet=(parent.get_text(" ",strip=True) if parent else a.get_text(" ",strip=True))[:800]
        published=article_date(snippet)
        if published!="not_verified_in_archive_card":
            if not (date(2025,1,1)<=date.fromisoformat(published)<=AS_OF):
                continue
        results[url]=dict(
            notice_url=url,publisher_site=site,title_from_listing=title,
            date_as_shown_in_listing=published,listing_page_url=listing_url,
            selected_for_2025_26="date_verified" if published!="not_verified_in_archive_card" else "date_not_verified_requires_review",
            content_adjudication="not_read_full_article",
            event_id="not_assigned",
            entity_role="not_inferred_from_organizer_keyword",
            financial_duplication="not_estimated",
            completeness_claim="partial_archive_metadata_not_all_field_visits_or_training"
        )
    return results
def write(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,default=Path("data"))
    p.add_argument("--max-pages",type=int,default=12)
    args=p.parse_args()
    records={}
    attempts=[]
    for site,base in TARGETS.items():
        first=None;empty=0
        for page in range(args.max_pages):
            url=base+("?page="+str(page))
            try:
                body=fetch(url)
                parsed=cards(body,site,url)
                added=0
                for u,r in parsed.items():
                    if u not in records:
                        records[u]=r;added+=1
                status="downloaded"
                sha=hashlib.sha256(body).hexdigest()
            except Exception as exc:
                status="fetch_blocked_or_failed:"+exc.__class__.__name__
                sha="not_available"
                parsed={};added=0
            attempts.append(dict(
                publisher_site=site,page_index=page,listing_url=url,
                attempted_status=status,raw_page_sha256=sha,
                parsed_candidate_links=len(parsed),new_unique_notice_urls=added,
                as_of=str(AS_OF),completeness_status="not_a_full_event_census"))
            if status!="downloaded":
                break
            if added==0:
                empty+=1
            else:
                empty=0
            if empty>=2:
                break
            time.sleep(.14)
    attempts.sort(key=lambda r:(r["publisher_site"],r["page_index"]))
    write(args.output_dir/"mission_archive_attempts_2025_2026.csv",attempts)
    if records:
        write(args.output_dir/"mission_archive_notice_metadata_2025_2026.csv",
              sorted(records.values(),key=lambda r:(r["publisher_site"],r["date_as_shown_in_listing"],r["notice_url"])))
    stats=[]
    for site in TARGETS:
        a=[r for r in attempts if r["publisher_site"]==site]
        subset=[r for r in records.values() if r["publisher_site"]==site]
        failures=sum(not r["attempted_status"]=="downloaded" for r in a)
        stats.append(dict(site=site,attempted_pages=len(a),successful_pages=len(a)-failures,
                          archive_notice_links=len(subset),
                          published_dates_confirmed=sum(r["selected_for_2025_26"]=="date_verified" for r in subset),
                          first_page_fetch_status=a[0]["attempted_status"],
                          coverage_status=("access_blocked" if failures and len(a)==1 else
                             "bounded_pagination_partial_not_complete"),
                          as_of=str(AS_OF),
                          true_field_or_training_event_total="unknown_not_observable_from_news"))
    write(args.output_dir/"mission_archive_coverage_2025_2026.csv",stats)
    print("ARCHIVE METADATA HARVEST",[(x["site"],x["successful_pages"],x["archive_notice_links"],x["coverage_status"]) for x in stats])
    print("No claim of complete activities from news listings; no unverified cross-mission coorganization.")
if __name__=="__main__":
    main()
