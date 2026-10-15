#!/usr/bin/env python3
"""Bounded public-source recovery for the V6 audit; records access and exact versions.

Follows public PDF links embedded in official document portals. Never bypasses
access controls, invents a document URL, or changes a frozen V1-V5 source table.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen
from urllib.parse import urlsplit, urljoin
from datetime import datetime, timezone
from io import BytesIO
import hashlib,json,re,html
from bs4 import BeautifulSoup
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/census_v6/source_capture'
RAW=ROOT/'v6_raw_sources'
EXTRAS={
 'KOREA_HOST_INDEX':'https://www.police.ac.kr/police/police/master/74/boardList.do?mdex=police125',
 'ITS_CALENDAR':'https://peacekeepingresourcehub.un.org/en/news',
 'UNOWAS_APRIL_BRIEFING':'https://unowas.unmissions.org/en/news/at-the-security-council-special-representative-simao-encourages-continued-regional',
 'UNOWAS_APRIL_COVERAGE':'https://press.un.org/en/2025/sc16036.doc.htm',
 'UNOCA_JUNE_COVERAGE':'https://press.un.org/en/2025/sc16081.doc.htm',
 'UNOCA_REPORT_BRIEFING_ARCHIVE':'https://unoca.unmissions.org/en/unoca-reports-of-the-secretary-general',
 'KOREA_MOBILE_INDEX':'https://m.police.ac.kr/PM/user/main/userMain.do',
}
def official(url):
 h=(urlsplit(url).hostname or '').lower()
 return url.startswith('https://') and any(h==x or h.endswith('.'+x) for x in ('un.org','unmissions.org','police.ac.kr','korea.kr'))
def get(url):
 if not official(url):raise ValueError('off_allowlist')
 with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; public-source-census/6.0)'}),timeout=12) as r:
  data=r.read(15000001);final=r.url
 if len(data)>15000000 or not official(final):raise ValueError('size_or_redirect')
 sha=hashlib.sha256(data).hexdigest();ext='.pdf' if data.startswith(b'%PDF') else '.html'
 (RAW/(sha+ext)).write_bytes(data)
 return data,final,sha

def main():
 RAW.mkdir(exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
 access=json.loads((OUT/'document_access.json').read_text())
 def recover(row):
  initial=[a['url'] for a in row['attempts']]
  if row['status']=='downloaded_symbol_checked':return row
  queue=list(dict.fromkeys(initial));seen=set();trials=[]
  while queue and len(seen)<10:
   url=queue.pop(0)
   if url in seen or not official(url):continue
   seen.add(url)
   try:
    body,final,sha=get(url)
    if body.startswith(b'%PDF'):
     pages=[p.extract_text() or '' for p in PdfReader(BytesIO(body)).pages]
     normalized=re.sub(r'\s+','',pages[0])
     target=re.sub(r'\s+','',row['symbol'])
     if target not in normalized:raise ValueError('requested_symbol_not_on_cover')
     name=row['symbol'].replace('/','_').replace('.','_')+'.pages.json'
     (RAW/name).write_text(json.dumps(pages,ensure_ascii=False))
     row.update(status='downloaded_symbol_checked',url=url,final_url=final,sha256=sha,pages=len(pages),text_file=name,recovery_attempts=trials)
     return row
    soup=BeautifulSoup(body,'html.parser');links=[]
    for el in soup.find_all(['a','iframe','embed','object']):
     candidate=el.get('href') or el.get('src') or el.get('data') or ''
     candidate=urljoin(final,html.unescape(candidate))
     if official(candidate) and ('.pdf' in candidate.lower() or 'symbol/access' in candidate or '/doc/undoc/' in candidate.lower() or '/access.nsf/' in candidate):links.append(candidate)
    for match in re.findall(r'https?[^\s\"\'<>]+',body.decode('utf-8',errors='ignore')):
     candidate=html.unescape(match).replace('\\/','/')
     if official(candidate) and ('.pdf' in candidate.lower() or 'symbol/access' in candidate):links.append(candidate)
    queue.extend(u for u in dict.fromkeys(links) if u not in seen)
    trials.append(dict(url=url,status='html_not_document',sha256=sha,pdf_links=len(links),title=soup.title.get_text(' ',strip=True) if soup.title else ''))
   except Exception as e:trials.append(dict(url=url,status=type(e).__name__+':'+str(e)[:150]))
  row['recovery_attempts']=trials
  return row
 with ThreadPoolExecutor(max_workers=4) as pool:access['records']=list(pool.map(recover,access['records']))
 access['recovery_at']=datetime.now(timezone.utc).isoformat()
 (OUT/'document_access.json').write_text(json.dumps(access,indent=2))
 notices=[]
 for name,url in EXTRAS.items():
  try:
   body,final,sha=get(url);soup=BeautifulSoup(body,'html.parser')
   text=soup.get_text('\n',strip=True);(RAW/(name+'.txt')).write_text(text)
   links=[]
   for a in soup.find_all('a',href=True):
    label=a.get_text(' ',strip=True)
    if any(term in label for term in ['유엔','Briefing','briefing','Statement','statement','DOWNLOAD','English']):
     links.append(dict(title=label,url=urljoin(final,a['href']),onclick=a.get('onclick','')))
   notices.append(dict(source_id=name,url=url,final_url=final,status='downloaded',sha256=sha,text_file=name+'.txt',relevant_links=links))
  except Exception as e:notices.append(dict(source_id=name,url=url,status=type(e).__name__+':'+str(e)[:150]))
 (OUT/'notice_access.json').write_text(json.dumps(notices,indent=2,ensure_ascii=False))
 print(json.dumps({r['symbol']:r['status'] for r in access['records']},indent=2))
 print(json.dumps(notices,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
