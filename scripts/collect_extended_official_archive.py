#!/usr/bin/env python3
"""Bounded source-index discovery for additional official UN mission/training archives.

It inventories URLs only. A listing item is NOT a delivered field or training
event, and a listed course is not proof of enrollment, attendance or completion.
All off-domain links, publication dates after cutoff and incomplete pagination
remain explicitly outside release. No authentication or restricted records.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, re
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit, urlencode
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
ARCHIVES=[
 ("UNISFA_news","https://unisfa.unmissions.org/en/news","/en/news/"),
 ("UNMISS_news","https://unmiss.unmissions.org/en/news","/en/news/"),
 ("MONUSCO_news","https://monusco.unmissions.org/en/news-articles","/en/news/"),
 ("MINUSCA_news","https://minusca.unmissions.org/en/news","/en/news/"),
 ("UNSSC_courses","https://www.unssc.org/courses","/courses/"),
 ("UNSSC_events","https://www.unssc.org/events","/events/"),
 ("UNITAR_stories","https://unitar.org/about/news-stories/stories","/about/news-stories/stories/"),
 ("UNITAR_training_catalogue","https://event.unitar.org/full-catalog","/full-catalog/"),
 ("CSM_news","https://www.un.org/climatesecuritymechanism/en/news","/climatesecuritymechanism/en/news/")]
DATE=re.compile(r"\b(\d{1,2})\s+(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+(20\d{2})\b",re.I)
ASOF="2026-10-13"

def clean(url):
 p=urlsplit(url)
 return urlunsplit((p.scheme.lower(),p.netloc.lower(),p.path.rstrip("/"),"",""))

def scoped(url,base,fragment):
 p=urlsplit(url);b=urlsplit(base)
 if p.scheme!="https" or p.hostname!=b.hostname or fragment not in p.path:return False
 return p.path.rstrip("/")!=b.path.rstrip("/") and len(p.path)>len(b.path)+2

def fetch(url):
 try:
  req=Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; UnitedNations-public-document-census/1.0)","Accept":"text/html"})
  with urlopen(req,timeout=11) as r:
   if r.status!=200:raise ValueError("HTTP_status")
   if "html" not in (r.headers.get("Content-Type") or "").lower():raise ValueError("not_html")
   data=r.read(2_000_001)
   if len(data)>2_000_000 or len(data)<100:raise ValueError("size_or_empty")
   if urlsplit(r.url).hostname!=urlsplit(url).hostname:raise ValueError("redirect_host_mismatch")
  return data,"downloaded",hashlib.sha256(data).hexdigest()
 except Exception as e:return b"",type(e).__name__+":"+str(e)[:90],""

def extract(data,base,frag,source,page,url):
 html=BeautifulSoup(data,"html.parser")
 scope=html.find("main") or html
 found={}
 for a in scope.find_all("a",href=True):
  href=clean(urljoin(url,a["href"]))
  if not scoped(href,base,frag):continue
  title=a.get_text(" ",strip=True)
  if len(title)<12:continue
  # Dates in listing cards are hints; they are NOT validated publication
  # dates and cannot be converted into dates of the underlying activity.
  ancestor=a.parent
  for _ in range(2):
   if ancestor is not None:ancestor=ancestor.parent
  text=ancestor.get_text(" ",strip=True)[:600] if ancestor else ""
  dm=DATE.search(text)
  label=dm.group(0) if dm else "not_verified"
  status="undated_listing"
  if dm:
   try:
    day=datetime.strptime(dm.group(0),"%d %B %Y").date().isoformat()
   except ValueError:
    try:day=datetime.strptime(dm.group(0),"%d %b %Y").date().isoformat()
    except ValueError:day=""
   status=("unverified_listing_date_in_study_window" if day and "2025-01-01"<=day<=ASOF else
           "listing_date_out_of_study_window_or_unparseable")
  found[href]=dict(source_id="ARC"+hashlib.sha256(href.encode()).hexdigest()[:16],
    archive=source,official_notice_url=href,display_title=title[:320],
    listing_date_text_unverified=label,listing_date_status=status,
    first_listing_page=page,first_listing_url=url,
    evidence_level="listing_only_not_approved_delivered_event",
    canonical_event_id="not_assigned",
    duplicate_paid_service="not_estimated",incremental_net_savings="not_estimated")
 return found

def page_url(base,page):
 return base + ("&" if "?" in base else "?") + urlencode({"page":page})

def write(path,records,fields):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(records)

def run(out,maxpages,workers):
 jobs=[(name,base,frag,index,page_url(base,index)) for name,base,frag in ARCHIVES for index in range(maxpages)]
 def work(job):
  site,base,frag,page,url=job
  data,status,sha=fetch(url)
  links=extract(data,base,frag,site,page,url) if data else {}
  return dict(archive=site,archive_page=page,archive_page_url=url,fetch_status=status,
   response_sha256=sha,discovered_links=len(links),
   scope="bounded_public_source_page_not_complete_2025_2026_activity_register",
   asof=ASOF),links
 with ThreadPoolExecutor(max_workers=workers) as pool:done=list(pool.map(work,jobs))
 logs=[x[0] for x in done]
 links={}
 for _,items in done:
  for k,row in items.items():links.setdefault(k,row)
 listings=sorted(links.values(),key=lambda x:(x["archive"],x["official_notice_url"]))
 write(out/"archive_page_access.csv",logs,list(logs[0]))
 link_keys=list(listings[0]) if listings else [
  "source_id","archive","official_notice_url","display_title","listing_date_text_unverified",
  "listing_date_status","first_listing_page","first_listing_url","evidence_level",
  "canonical_event_id","duplicate_paid_service","incremental_net_savings"]
 write(out/"archive_discovered_url_frame.csv",listings,link_keys)
 byarchive={}
 for name,*_ in ARCHIVES:
  site=[x for x in logs if x["archive"]==name]
  a=[x for x in listings if x["archive"]==name]
  byarchive[name]=dict(pages_attempted=len(site),
   downloaded_pages=sum(x["fetch_status"]=="downloaded" for x in site),
   source_index_links=len(a),pagination_complete=False,
   full_2025_2026_event_population_known=False,
   event_count_verified=0)
 summary=dict(asof=ASOF,archives_attempted=len(ARCHIVES),pages_attempted=len(logs),
  downloaded_pages=sum(x["fetch_status"]=="downloaded" for x in logs),
  discovered_distinct_link_ids=len(listings),source_lineage_by_archive=byarchive,
  public_training_catalogue_not_delivered_event=True,
  unique_field_or_training_events_inferred=0,
  actual_event_denominator="unknown",duplicate_paid_services="not_estimated",
  incremental_net_savings="not_estimated",generated_at=datetime.now(timezone.utc).isoformat())
 (out/"archive_collection_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
 print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=="__main__":
 ap=argparse.ArgumentParser()
 ap.add_argument("--out",type=Path,default=ROOT/"data"/"census_v3")
 ap.add_argument("--max-pages",type=int,default=3)
 ap.add_argument("--workers",type=int,default=4)
 args=ap.parse_args()
 if not 1<=args.max_pages<=8 or not 1<=args.workers<=5:raise ValueError("Unsafe crawl bounds")
 run(args.out,args.max_pages,args.workers)
