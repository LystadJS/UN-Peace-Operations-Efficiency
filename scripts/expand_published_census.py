#!/usr/bin/env python3
"""Census a bounded public notice frame; never promote candidate events to facts.

Refreshes official Council indexes and enumerates six official notice archives,
then reads every discovered article up to the declared safety bound. Publication
metadata, event mentions, record variants and human adjudication remain separate.
Legacy Phase 10/11 snapshots are untouched. Requires beautifulsoup4.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, re, time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SITES = {
 'UNOWAS':'https://unowas.unmissions.org/en/news',
 'UNOCA':'https://unoca.unmissions.org/en/news',
 'UNRCCA':'https://unrcca.unmissions.org/en/news',
 'UNAMA':'https://unama.unmissions.org/en/news',
 'DPPA':'https://dppa.un.org/en/news',
 'DPO':'https://peacekeeping.un.org/en/news'}
MONTHS = 'January February March April May June July August September October November December'.split()
MONTH = '(?:'+'|'.join(MONTHS)+')'
DATERX = re.compile(r'\b(?:\d{1,2}\s*(?:–|-|to|and)\s*)?\d{1,2}\s+'+MONTH+r'\s+20\d{2}\b', re.I)
CATS = {
 'training':re.compile(r'\b(train(?:ing|ed|ers)?|workshops?|courses?|syllabus|academy|seminars?)\b',re.I),
 'field_activity':re.compile(r'\b(visits?|visited|field mission|travelled|traveled|delegation)\b',re.I),
 'meeting':re.compile(r'\b(meeting|met with|consultation|dialogue|forum|conference|briefing|convened)\b',re.I)}
JOINT = re.compile(r'\b(joint(?:ly)?|co-organiz\w*|co-organis\w*|co-host\w*|in cooperation with|in collaboration with)\b', re.I)
ENTITY = re.compile(r'\b(UNOWAS|UNOCA|UNRCCA|UNAMA|DPPA|DPO|UNSSC|UNPOL|UNMISS|UNOCT|UNDP|UNEP|UNODC|UNFICYP|UNSCOL|UNIFIL|BINUH|MONUSCO)\b')


def read_csv(path):
 if not path.exists(): return []
 with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def write_csv(path, rows, fields=None):
 path.parent.mkdir(parents=True,exist_ok=True)
 fields=fields or (list(rows[0]) if rows else ['empty'])
 with path.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def normal_url(url):
 p=urlsplit(url)
 return urlunsplit((p.scheme.lower(),p.netloc.lower(),p.path.rstrip('/'),p.query,''))

def allowed(url):
 p=urlsplit(url)
 return p.scheme=='https' and (p.hostname or '') in {urlsplit(x).hostname for x in SITES.values()}

def fetch(url, cache):
 req=Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; UN-PO-public-research/2.0)', 'Accept':'text/html,application/xhtml+xml'})
 with urlopen(req,timeout=12) as resp:
  body=resp.read(6_000_001)
  if resp.status!=200 or len(body)>6_000_000 or len(body)<200:raise ValueError('HTTP_or_size')
  if 'html' not in (resp.headers.get('Content-Type') or '').lower():raise ValueError('not_HTML')
  final=resp.url
 sha=hashlib.sha256(body).hexdigest()
 cache.mkdir(parents=True,exist_ok=True)
 (cache/(sha+'.html')).write_bytes(body)
 return body,sha,final

def parse_day(raw):
 raw=raw.strip()
 if re.match(r'^\d{4}-\d{2}-\d{2}',raw):
  try:return date.fromisoformat(raw[:10]).isoformat()
  except ValueError:return ''
 for fmt in ('%d %B %Y','%B %d, %Y','%d %b %Y'):
  try:return datetime.strptime(raw,fmt).date().isoformat()
  except ValueError:pass
 return ''

def publication_date(soup):
 """Use explicit publication metadata, never an arbitrary body/event date."""
 candidates=[]
 for key in ('article:published_time','datePublished','date','dcterms.created'):
  for attr in ('property','name','itemprop'):
   for el in soup.find_all('meta',attrs={attr:key}):
    raw=el.get('content','');d=parse_day(raw)
    if d:candidates.append((d,'meta:'+key,raw))
 for el in soup.select('time[datetime]'):
  if 'modif' in str(el.get('property','')).lower():continue
  raw=el.get('datetime','');d=parse_day(raw)
  if d:candidates.append((d,'time_datetime',raw))
 for el in soup.find_all('script',type='application/ld+json'):
  try:data=json.loads(el.string or el.get_text())
  except (ValueError,TypeError):continue
  def walk(obj):
   if isinstance(obj,dict):
    if 'datePublished' in obj:
     raw=str(obj['datePublished']);d=parse_day(raw)
     if d:candidates.append((d,'jsonld_datePublished',raw))
    for v in obj.values():walk(v)
   elif isinstance(obj,list):
    for v in obj:walk(v)
  walk(data)
 if not candidates:
  # UN Peace Operations Drupal article templates place the *publication* date
  # in the first item of the article masthead's horizontal metadata list.
  # This is not a date inferred from the article body or an event mentioned in it.
  article=soup.select_one('article.node--type-uw-article,article.uwl-news__mpw')
  if article is not None and article.find('h1') is not None:
   masthead=article.select_one('#section--masthead .uw-horizontal-list')
   if masthead is None:masthead=article.select_one('.uw-horizontal-list')
   first=masthead.select_one('li.list-item') if masthead else None
   if first is not None:
    raw=first.get_text(' ',strip=True)
    d=parse_day(raw)
    if d:candidates.append((d,'article_masthead_publication_date',raw))
 if not candidates:
  for el in soup.select('.field--name-created,.field--name-field-date,.news-date,.date-display-single,.node__submitted time'):
   raw=el.get_text(' ',strip=True);d=parse_day(raw)
   if d:candidates.append((d,'labelled_publication_date',raw))
 if not candidates:return '','not_verified',''
 dates={x[0] for x in candidates}
 if len(dates)>1:return '','conflicting_publication_metadata','; '.join(x[2] for x in candidates)[:300]
 return candidates[0]

def paragraphs(soup):
 body=soup.select_one('.field--name-body') or soup.select_one('.field--type-text-with-summary') or soup.find('article') or soup.find('main')
 if body is None:return [],'body_not_located'
 for el in body.select('nav,footer,header,aside,script,style,.related-content,.field--name-field-related-content'):el.decompose()
 result=[]
 for el in body.find_all(['p','li']):
  if el.find_parent('li') is not None:continue
  text=' '.join(el.stripped_strings)
  if len(text)>=50 and text not in result:result.append(text)
 return result,'body_paragraphs' if result else 'body_empty'

def extract_article(body,url,site,asof):
 soup=BeautifulSoup(body,'html.parser')
 h=soup.find('h1');title=h.get_text(' ',strip=True) if h else ''
 day,method,raw=publication_date(soup)
 ps,body_status=paragraphs(soup)
 if not title or not ps:status='insufficient_article_content'
 elif not day:status='publication_date_unresolved'
 elif day>asof:status='after_cutoff'
 elif day<'2025-01-01':status='before_window'
 else:status='publication_in_window'
 nid='N'+hashlib.sha256(url.encode()).hexdigest()[:16]
 meta=dict(notice_id=nid,publisher=site,url=url,title=title[:350],publication_date=day,
  publication_date_method=method,publication_date_raw=raw[:300],body_status=body_status,
  paragraph_count=len(ps),chronology_status=status,entity_mentions=';'.join(sorted(set(ENTITY.findall(' '.join(ps))))),
  full_article_sha256=hashlib.sha256(body).hexdigest(),analysis_asof=asof,
  event_census_status='notice_not_adjudicated_event',incremental_savings='not_estimated')
 candidates=[]
 for index,p in enumerate(ps,1):
  categories=[k for k,rx in CATS.items() if rx.search(p)]
  if not categories or status in ('before_window','after_cutoff','insufficient_article_content'):continue
  candidates.append(dict(candidate_id=nid+f'-P{index:04d}',notice_id=nid,publisher=site,
   publication_date=day,chronology_status=status,paragraph_index=index,
   categories=';'.join(categories),joint_language=str(bool(JOINT.search(p))).lower(),
   entity_mentions=';'.join(sorted(set(ENTITY.findall(p)))),
   explicit_event_date_mentions=';'.join(DATERX.findall(p)),
   source_excerpt=p[:900],excerpt_truncated=str(len(p)>900).lower(),url=url,
   evidence_status='machine_located_paragraph_needs_event_identity_and_role_review',
   event_id='not_assigned',duplicate_payment='not_estimated'))
 return meta,candidates

def discover(site,base,args):
 known={};attempts=[];seen=set();stop='page_limit'
 for page in range(args.max_pages):
  url=base+'?page='+str(page)
  try:
   body,sha,final=fetch(url,args.cache)
   soup=BeautifulSoup(body,'html.parser');main=soup.find('main') or soup
   links={}
   for a in main.find_all('a',href=True):
    u=normal_url(urljoin(url,a['href']));p=urlsplit(u)
    if not allowed(u) or not ('/news/' in p.path or '/node/' in p.path):continue
    title=a.get_text(' ',strip=True)
    if len(title)<14:continue
    links[u]=(site,title)
   novelty=set(links)-seen
   attempts.append(dict(site=site,page=page,url=url,status='downloaded',sha256=sha,links=len(links),new_links=len(novelty),stop_reason=''))
   if not links:
    stop='no_article_links_not_proof_all_events';break
   if not novelty:
    stop='repeated_page_frontier_stopped_not_event_complete';break
   known.update(links);seen.update(links)
   # Some UN mission news templates have server-side ?page=N navigation but
   # omit a parseable "next" element. Probe sequential pages until the frontier
   # repeats or becomes empty; neither condition proves a census of events.
   nxt=soup.select_one('a[rel="next"],li.pager__item--next a,li.pager-next a')
   if nxt is None:stop='no_pager_control_page_probing_until_repeat_or_limit'
  except Exception as exc:
   attempts.append(dict(site=site,page=page,url=url,status=type(exc).__name__+':'+str(exc)[:140],sha256='',links=0,new_links=0,stop_reason=''))
   stop='access_failure';break
  time.sleep(.15)
 if attempts:attempts[-1]['stop_reason']=stop
 return known,attempts

def council_snapshot(args):
 import build_systematic_census as old
 captures=[];reports=[];meetings=[]
 for year in (2025,2026):
  for kind,url in [('reports',old.REPORT_ENDPOINT.format(year)),('meetings',old.MEET_ENDPOINT.format(year))]:
   try:
    body=old.fetch(url);sha=hashlib.sha256(body).hexdigest()
    (args.cache/(sha+'.html')).write_bytes(body)
    raw=old.extract_report(body,year) if kind=='reports' else old.extract_meeting(body,year)
    kept=[r for r in raw if r.get('indexed_date',r.get('date',''))<=args.as_of]
    for row in kept:row.update(snapshot_asof=args.as_of,snapshot_sha256=sha)
    (reports if kind=='reports' else meetings).extend(kept)
    captures.append(dict(source=kind,year=year,url=url,asof=args.as_of,status='fetched_index',sha256=sha,parsed_rows=len(raw),retained_rows=len(kept),future_rows_excluded=len(raw)-len(kept)))
   except Exception as exc:captures.append(dict(source=kind,year=year,url=url,asof=args.as_of,status=type(exc).__name__+':'+str(exc)[:100],sha256='',parsed_rows=0,retained_rows=0,future_rows_excluded=0))
 if reports:write_csv(args.out/'council_reports.csv',reports)
 if meetings:write_csv(args.out/'council_meeting_variants.csv',meetings)
 write_csv(args.out/'council_fetches.csv',captures)
 return reports,meetings,captures

def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'data/census_v2')
 p.add_argument('--cache',type=Path,default=Path('/tmp/census-v2-html'))
 p.add_argument('--as-of',default='2026-10-12');p.add_argument('--max-pages',type=int,default=40)
 p.add_argument('--max-articles',type=int,default=2000);p.add_argument('--workers',type=int,default=6)
 args=p.parse_args();date.fromisoformat(args.as_of)
 if args.as_of!='2026-10-12':raise ValueError('Snapshot is explicitly frozen at 12 October 2026')
 if not 1<=args.workers<=8 or not 1<=args.max_pages<=100 or not 1<=args.max_articles<=5000:raise ValueError('Unsafe collection bound')
 args.out.mkdir(parents=True,exist_ok=True);args.cache.mkdir(parents=True,exist_ok=True)
 reports,meetings,index_attempts=council_snapshot(args)
 seeds={}
 for row in read_csv(ROOT/'data/mission_archive_notice_metadata_2025_2026.csv'):
  u=normal_url(row['notice_url'])
  if allowed(u):seeds[u]=(row['publisher_site'],row['title_from_listing'])
 for row in read_csv(ROOT/'data/retrospective_2025_2026_sources.csv'):
  u=normal_url(row['official_url'])
  if allowed(u) and ('/news/' in u or '/node/' in u):
   site=next((k for k,v in SITES.items() if urlsplit(v).hostname==urlsplit(u).hostname),'')
   seeds.setdefault(u,(site,row['title']))
 with ThreadPoolExecutor(max_workers=6) as pool: discoveries=list(pool.map(lambda kv:discover(*kv,args),SITES.items()))
 listing=[]
 for items,trials in discoveries:seeds.update(items);listing.extend(trials)
 write_csv(args.out/'archive_pages.csv',listing)
 urls=sorted(seeds);selected=set(urls[:args.max_articles])
 frame=[dict(notice_url=u,publisher=seeds[u][0],listing_title=seeds[u][1],selected_for_fetch=str(u in selected).lower(),frame_type='union_prior_discovery_current_archives_verified_seeds',asof=args.as_of) for u in urls]
 write_csv(args.out/'notice_frame.csv',frame)
 def work(u):
  try:
   body,sha,final=fetch(u,args.cache)
   if not allowed(final):raise ValueError('redirect_outside_mission_allowlist')
   meta,cs=extract_article(body,u,seeds[u][0],args.as_of)
   return dict(url=u,status='downloaded',final_url=final,sha256=sha),meta,cs
  except Exception as exc:return dict(url=u,status=type(exc).__name__+':'+str(exc)[:140],final_url='',sha256=''),None,[]
 attempts=[];notices=[];candidates=[]
 with ThreadPoolExecutor(max_workers=args.workers) as pool:
  for i,(attempt,meta,cs) in enumerate(pool.map(work,sorted(selected)),1):
   attempts.append(attempt)
   if meta:notices.append(meta);candidates.extend(cs)
   if i%100==0:print('Article fetches',i,'of',len(selected),flush=True)
 write_csv(args.out/'article_fetches.csv',attempts)
 if notices:write_csv(args.out/'notices.csv',notices)
 if candidates:
  candidates.sort(key=lambda r:(r['publisher'],r['publication_date'],r['url'],r['paragraph_index']))
  write_csv(args.out/'event_paragraph_candidates.csv',candidates)
  priority=[r for r in candidates if r['joint_language']=='true' and len(r['entity_mentions'].split(';'))>=2]
  write_csv(args.out/'joint_review_queue.csv',priority)
 stats=[];byurl={x['url']:x for x in attempts}
 for site in SITES:
  fs=[u for u in urls if seeds[u][0]==site];ns=[n for n in notices if n['publisher']==site]
  pages=[a for a in listing if a['site']==site]
  stats.append(dict(publisher=site,frame_notices=len(fs),attempted=sum(u in byurl for u in fs),downloaded=len(ns),
   dated_publication_in_window=sum(n['chronology_status']=='publication_in_window' for n in ns),
   publication_unresolved=sum(n['chronology_status']=='publication_date_unresolved' for n in ns),
   before_window=sum(n['chronology_status']=='before_window' for n in ns),after_cutoff=sum(n['chronology_status']=='after_cutoff' for n in ns),
   article_incomplete=sum(n['chronology_status']=='insufficient_article_content' for n in ns),
   archive_stop=pages[-1]['stop_reason'] if pages else 'not_attempted',
   event_population_denominator='unknown',adjudicated_event_completeness='not_claimed',asof=args.as_of))
 write_csv(args.out/'coverage.csv',stats)
 payload=dict(asof=args.as_of,executed_at=datetime.now(timezone.utc).isoformat(),
  frame_notices=len(frame),article_attempts=len(attempts),downloaded_notices=len(notices),
  candidate_paragraphs=len(candidates),publications_in_window=sum(n['chronology_status']=='publication_in_window' for n in notices),
  council_reports=len(reports),council_meeting_variants=len(meetings),distinct_council_meetings=len({r['meeting_base_id'] for r in meetings}),
  council_index_success=sum(r['status']=='fetched_index' for r in index_attempts),
  release_scope='public-source-frame-census; field/training candidates require adjudication; not all delivered UN activities',
  duplicate_spending='not_estimated',unknown_event_counts_not_zero=True)
 (args.out/'summary.json').write_text(json.dumps(payload,indent=2)+'\n')
 print(json.dumps(payload,indent=2))

if __name__=='__main__':main()
