#!/usr/bin/env python3
"""V7 cover-layout adapter: tolerate PDF spacing, not wrong source identities.

Original bytes are unchanged. A separate full-file parser is used downstream.
Both raw cover extraction and compact comparison values are retained for review.
"""
from __future__ import annotations
import argparse
import io
import json
import re
from datetime import datetime
from pathlib import Path
from pypdf import PdfReader
import recover_census_v7_transcripts as recovery

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/census_v7'

def inspect(body,row):
    if not body.startswith(b'%PDF'):
        raise ValueError('Response is not an original PDF')
    reader=PdfReader(io.BytesIO(body),strict=True)
    texts=[page.extract_text() or '' for page in reader.pages]
    cover=texts[0]
    compact=re.sub(r'\s+','',cover)
    expected=datetime.strptime(row['meeting_date'],'%Y-%m-%d')
    expected_date=f'{expected.day}{expected.strftime("%B%Y")}'
    checks={
        'exact_cover_symbol':bool(re.search(re.escape(row['meeting_record'])+r'(?!\d)',compact)),
        'english_council_heading':'SecurityCouncil' in compact,
        'english_agenda_heading':'Agenda' in compact,
        'exact_cover_date':expected_date in compact,
        'at_least_two_pages':len(texts)>=2,
        'all_pages_extractable':all(len(t.strip())>=120 for t in texts),
    }
    diag=OUT/'cover_layout_checks';diag.mkdir(parents=True,exist_ok=True)
    name=row['meeting_record'].replace('/','_')
    (diag/(name+'.json')).write_text(json.dumps(dict(symbol=row['meeting_record'],
        pdf_sha256=recovery.sha(body),cover_extraction=cover,compact_cover=compact,
        expected_date=expected_date,checks=checks),ensure_ascii=False,indent=2)+'\n')
    if not all(checks.values()):
        (diag/(name+'.UNACCEPTED.pdf')).write_bytes(body)
        raise ValueError('Cover or content gates failed: '+str(checks))
    return texts

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--collect',action='store_true')
    args=parser.parse_args()
    recovery.inspect=inspect
    if args.collect:recovery.capture()
    recovery.check()

if __name__=='__main__':main()
