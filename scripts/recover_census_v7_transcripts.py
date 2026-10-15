#!/usr/bin/env python3
"""Recover exactly the seven frozen V6 gaps, never unrelated page/sidebar PDFs.

Capture authentic English S/PV records, cover symbols, meeting dates, page counts,
full-file hashes and reference locations. Document-body retrieval is not a finding
of financial duplication or a complete substantive comparison.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, quote, urljoin, urlsplit
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/census_v7'
TARGETS = {'S/PV.9931','S/PV.9942','S/PV.9998','S/PV.10060','S/PV.10165','S/PV.10195','S/PV.10223'}
HOSTS = {'docs.un.org','documents.un.org','digitallibrary.un.org'}

def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)

def sha(body):
    return hashlib.sha256(body).hexdigest()

def scoped_pdf_link(url, symbol):
    parts = urlsplit(url)
    return (parts.scheme == 'https' and parts.hostname == 'documents.un.org'
            and parts.path == '/api/symbol/access'
            and parse_qs(parts.query).get('s') == [symbol]
            and parse_qs(parts.query).get('l', ['en']) == ['en'])

def fetch(url):
    if urlsplit(url).hostname not in HOSTS:
        raise ValueError('Unapproved source host')
    req = Request(url, headers={'User-Agent':'Mozilla/5.0 (compatible; UN-public-census/7.0)',
                               'Accept':'application/pdf,text/html;q=0.9'})
    with urlopen(req, timeout=25) as response:
        if urlsplit(response.url).hostname not in HOSTS:
            raise ValueError('Redirect outside official document hosts')
        body = response.read(15_000_001)
        if response.status != 200 or not 100 < len(body) < 15_000_000:
            raise ValueError('Invalid HTTP response or size')
        return body, response.url

def inspect(body, row):
    if not body.startswith(b'%PDF'):
        raise ValueError('Response is not original PDF')
    reader = PdfReader(io.BytesIO(body), strict=True)
    texts = [page.extract_text() or '' for page in reader.pages]
    cover = re.sub(r'\s+', ' ', texts[0])
    if row['meeting_record'] not in cover or 'Security Council' not in cover or 'Agenda' not in cover:
        raise ValueError('English cover identity mismatch')
    expected = datetime.strptime(row['meeting_date'], '%Y-%m-%d')
    human = f'{expected.day} {expected.strftime("%B %Y")}'
    if human not in cover:
        raise ValueError('Cover meeting date differs from frozen link')
    if len(texts) < 2 or any(len(text.strip()) < 120 for text in texts):
        raise ValueError('Empty or low-text transcript page requires review')
    return texts

def capture():
    OUT.mkdir(parents=True, exist_ok=True)
    original = OUT / 'originals'; original.mkdir(exist_ok=True)
    pages_dir = OUT / 'pages'; pages_dir.mkdir(exist_ok=True)
    prior = read_csv(ROOT / 'data/census_v6/report_briefing_reuse_tests.csv')
    targets = [r for r in prior if r['current_classification'].startswith('transcript_not_retrieved')]
    if {r['meeting_record'] for r in targets} != TARGETS:
        raise AssertionError('V6 gap population changed; do not silently expand recovery')
    receipts, attempts, refs = [], [], []
    for row in targets:
        sym = row['meeting_record']; viewer = 'https://docs.un.org/en/' + sym
        candidates = []
        try:
            body, final_url = fetch(viewer)
            if body.startswith(b'%PDF'):
                candidates.append(viewer)
            else:
                soup = BeautifulSoup(body, 'html.parser')
                for node in soup.find_all(['iframe','embed','object','a']):
                    value = node.get('src') or node.get('data') or node.get('href')
                    if value:
                        url = urljoin(viewer, value)
                        if scoped_pdf_link(url, sym): candidates.append(url)
            attempts.append(dict(symbol=sym, url=viewer, stage='viewer', status='retrieved',
                                 response_sha256=sha(body), detail=f'{len(candidates)} symbol-scoped links'))
        except Exception as exc:
            attempts.append(dict(symbol=sym, url=viewer, stage='viewer', status='failed',
                                 response_sha256='', detail=type(exc).__name__+':'+str(exc)[:180]))
        candidates += ['https://documents.un.org/api/symbol/access?s='+quote(sym,safe='')+'&l=en&t=pdf',
                       'https://documents.un.org/api/symbol/access?s='+quote(sym,safe='')]
        success = None
        for url in dict.fromkeys(candidates):
            try:
                body, final_url = fetch(url)
                texts = inspect(body, row)
                digest = sha(body); name = sym.replace('/','_')
                pdf = original / (name+'.pdf'); pdf.write_bytes(body)
                page_file = pages_dir / (name+'.json')
                page_file.write_text(json.dumps(texts, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
                ref_pages = []
                for index,text in enumerate(texts,1):
                    normalized = re.sub(r'\s+',' ',text)
                    for match in re.finditer(re.escape(row['report_symbol'])+r'(?!\d)', normalized):
                        ref_pages.append(index)
                        refs.append(dict(record_id=row['record_id'], meeting_record=sym,
                                         report_symbol=row['report_symbol'], printed_page=index,
                                         context=normalized[max(0,match.start()-170):match.end()+210]))
                success = dict(record_id=row['record_id'],meeting_record=sym,report_symbol=row['report_symbol'],
                               meeting_date=row['meeting_date'],status='original_English_PDF_recovered',
                               source_url=url,final_url=final_url,pages=len(texts),bytes=len(body),sha256=digest,
                               pdf_path=str(pdf.relative_to(ROOT)),pages_path=str(page_file.relative_to(ROOT)),
                               pages_sha256=sha(page_file.read_bytes()),
                               report_reference_pages=json.dumps(sorted(set(ref_pages))),
                               cover_symbol_verified='true',cover_date_verified='true',
                               every_page_has_extractable_text='true',
                               financial_duplication='not_established',substantive_review='separate_adjudication_required')
                attempts.append(dict(symbol=sym,url=url,stage='PDF',status='accepted',response_sha256=digest,detail=f'{len(texts)} pages'))
                break
            except Exception as exc:
                attempts.append(dict(symbol=sym,url=url,stage='PDF',status='failed',response_sha256='',detail=type(exc).__name__+':'+str(exc)[:180]))
        if success: receipts.append(success)
    write_csv(OUT/'recovery_attempts.csv',attempts,['symbol','url','stage','status','response_sha256','detail'])
    fields = ['record_id','meeting_record','report_symbol','meeting_date','status','source_url','final_url','pages','bytes','sha256','pdf_path','pages_path','pages_sha256','report_reference_pages','cover_symbol_verified','cover_date_verified','every_page_has_extractable_text','financial_duplication','substantive_review']
    write_csv(OUT/'transcript_recovery.csv',receipts,fields)
    write_csv(OUT/'recovered_reference_locations.csv',refs,['record_id','meeting_record','report_symbol','printed_page','context'])
    summary = dict(cutoff='2026-10-15',retrieved_at=datetime.now(timezone.utc).isoformat(),
                   baseline_commit='c0529f9959ab2e12e36481754b2883a526bec6df',
                   requested_transcripts=7,recovered_transcripts=len(receipts),
                   unresolved=sorted(TARGETS-{r['meeting_record'] for r in receipts}),
                   recovered_pages=sum(r['pages'] for r in receipts),
                   root_cause='V6 global candidate limit consumed by unrelated index/sidebar PDF links before symbol-specific document-viewer links',
                   recovery_method='Symbol-scoped official viewer API; no ASR substitution',
                   financial_duplication='not_established',incremental_net_savings='not_estimated')
    (OUT/'recovery_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps(summary,indent=2))
    if len(receipts)!=7: raise AssertionError('Incomplete recovery; preserve attempts and inspect remaining targets')

def check():
    rows=read_csv(OUT/'transcript_recovery.csv')
    if len(rows)!=7 or {r['meeting_record'] for r in rows}!=TARGETS:
        raise AssertionError('Recovery identity population mismatch')
    for r in rows:
        body=(ROOT/r['pdf_path']).read_bytes()
        if sha(body)!=r['sha256'] or len(body)!=int(r['bytes']): raise AssertionError('Original byte mismatch')
        texts=inspect(body,r)
        if len(texts)!=int(r['pages']):raise AssertionError('Page count mismatch')
        p=ROOT/r['pages_path']
        if sha(p.read_bytes())!=r['pages_sha256'] or json.loads(p.read_text())!=texts:
            raise AssertionError('Text derivation differs from source bytes')
    # Negative controls for the previous unrelated-link bug.
    if scoped_pdf_link('https://main.un.org/securitycouncil/sites/default/files/monthly.pdf','S/PV.9931'):
        raise AssertionError('Unrelated link accepted')
    if scoped_pdf_link('https://documents.un.org/api/symbol/access?s=S/PV.9942&l=en&t=pdf','S/PV.9931'):
        raise AssertionError('Different symbol accepted')
    print('V7 PASS: seven exact symbols, dates, English covers, original hashes, all pages and text derivations; unrelated-link negative controls')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--collect',action='store_true')
    args=parser.parse_args()
    if args.collect:capture()
    check()
