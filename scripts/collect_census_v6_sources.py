#!/usr/bin/env python3
"""Capture official source bytes for V6; no evidence classifications are inferred."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen
from urllib.parse import urlsplit
from datetime import datetime, timezone
import csv, hashlib, json, re
from io import BytesIO
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/census_v6/source_capture'
RAW=ROOT/'v6_raw_sources'
def read(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def main():
    OUT.mkdir(parents=True,exist_ok=True);RAW.mkdir(exist_ok=True)
    sources={}
    idx={r['document_symbol']:r['source_link'] for r in read(ROOT/'data/census_v5/index_refresh/council_reports.csv')}
    for r in read(ROOT/'data/systematic_report_meeting_links_2025_2026.csv'):
        sources.setdefault(r['report_symbol'],[]).extend([r['original_SG_link']])
        sources.setdefault(r['meeting_record'],[]).extend([r['evidence_url'],r['meeting_official_transcript_url']])
    for r in read(ROOT/'data/census_2025_2026_report_pair_tests.csv'):
        for k in ['first_symbol','second_symbol']:sources.setdefault(r[k],[])
    for sym,urls in sources.items():
        if sym in idx:urls.append(idx[sym])
        urls.extend(['https://docs.un.org/en/'+sym,'https://docs.un.org/'+sym])
    def work(job):
        sym,urls=job;attempts=[]
        for url in dict.fromkeys(urls):
            if not ((urlsplit(url).hostname or '').endswith('.un.org')):continue
            try:
                with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; public-source-census/6.0)'}),timeout=15) as resp:
                    body=resp.read(15000001); final=resp.url
                if not body.startswith(b'%PDF') or len(body)>15000000:raise ValueError('not_PDF_or_oversize')
                reader=PdfReader(BytesIO(body));pages=[p.extract_text() or '' for p in reader.pages]
                joined='\n'.join(pages)
                if sym.replace(' ','') not in joined.replace(' ',''):raise ValueError('symbol_not_in_pdf_text')
                sha=hashlib.sha256(body).hexdigest();(RAW/(sha+'.pdf')).write_bytes(body)
                name=sym.replace('/','_').replace('.','_')
                (RAW/(name+'.pages.json')).write_text(json.dumps(pages,ensure_ascii=False))
                return dict(symbol=sym,status='downloaded_symbol_checked',url=url,final_url=final,sha256=sha,pages=len(pages),text_file=name+'.pages.json',attempts=attempts)
            except Exception as e:attempts.append({'url':url,'error':type(e).__name__+':'+str(e)[:120]})
        return dict(symbol=sym,status='unavailable',url='',final_url='',sha256='',pages=0,text_file='',attempts=attempts)
    with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(work,sorted(sources.items())))
    (OUT/'document_access.json').write_text(json.dumps({'retrieved_at':datetime.now(timezone.utc).isoformat(),'records':rows},indent=2))
    print(json.dumps({r['symbol']:r['status'] for r in rows},indent=2))
if __name__=='__main__':main()
