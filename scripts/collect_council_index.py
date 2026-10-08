#!/usr/bin/env python3
"""Parse official Security Council SG annual-report index tables (offline or HTTPS).

Outputs staging suggestions, not automatically approved census records.
Uses only standard library. No full-document or duplicate-spending inference.
"""
import argparse
import csv
import re
import sys
import urllib.request
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path

MONTH = {m.lower():i for i,m in enumerate(("January","February","March","April","May",
    "June","July","August","September","October","November","December"),1)}
PATTERN = re.compile(r"\bS/(20\d{2})/(\d{1,4})\b")
DATE_RE = re.compile(r"(\d{1,2})\s+([A-Za-z]+)\s+(20\d{2})")

class IndexTable(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows=[]
        self.current=None
        self.cell=None
        self.in_cell=False
    def handle_starttag(self,tag,attrs):
        tag=tag.lower()
        if tag=="tr":
            self.current=[]
        elif tag in ("td","th") and self.current is not None:
            self.cell=[]
            self.in_cell=True
    def handle_data(self,data):
        if self.in_cell and self.cell is not None:self.cell.append(data)
    def handle_endtag(self,tag):
        tag=tag.lower()
        if tag in ("td","th") and self.in_cell and self.current is not None:
            self.current.append(" ".join("".join(self.cell).split()))
            self.in_cell=False
            self.cell=None
        elif tag=="tr" and self.current is not None:
            if self.current:self.rows.append(self.current)
            self.current=None
            self.in_cell=False

def date_from_cells(cells):
    for cell in cells:
        m=DATE_RE.search(cell)
        if m and m.group(2).lower() in MONTH:
            return date(int(m.group(3)),MONTH[m.group(2).lower()],int(m.group(1)))
    return None

def parse_table(html,year,asof,source_url):
    parser=IndexTable()
    parser.feed(html)
    found={}
    failures=[]
    for n,cells in enumerate(parser.rows,1):
        symbols=PATTERN.findall(" ".join(cells))
        if not symbols:continue
        found_ids=sorted({"S/"+y+"/"+str(int(no)) for y,no in symbols})
        d=date_from_cells(cells)
        for symbol in found_ids:
            symbol_year=int(symbol.split("/")[1])
            if symbol_year!=year:continue
            if d is None or d>asof or d.year!=year:
                failures.append((symbol,n,"missing_future_or_mismatched_date",str(d)))
                continue
            title=" ".join(c for c in cells if not PATTERN.search(c) and not DATE_RE.search(c))
            record=dict(year=str(year),symbol=symbol,catalogue_date=d.isoformat(),
                        title=title.strip(),source_url=source_url,
                        stage="official_index_table_pending_human_QA",
                        full_text_read="no",meeting_verified="no",
                        duplicate_cost="not_estimated")
            if symbol in found and found[symbol]["catalogue_date"]!=record["catalogue_date"]:
                failures.append((symbol,n,"conflicting_dates",str(d)))
            else:
                found[symbol]=record
    return list(found.values()),failures,len(parser.rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--year",type=int,choices=(2025,2026),required=True)
    p.add_argument("--html",type=Path,help="Saved official index HTML; no network needed")
    p.add_argument("--url",help="Optional official HTTPS URL, used only when --html absent")
    p.add_argument("--asof",default="2026-10-08")
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    if bool(args.html)==bool(args.url):p.error("Supply exactly one of --html and --url")
    if args.html:
        html=args.html.read_text(encoding="utf-8")
        source=str(args.html)
    else:
        if not args.url.startswith("https://main.un.org/securitycouncil/"):
            p.error("Only the official main.un.org Security Council index endpoint is supported")
        req=urllib.request.Request(args.url,headers={"User-Agent":"UNPeaceOperationsEvidence/1.0"})
        with urllib.request.urlopen(req,timeout=25) as response:
            html=response.read().decode("utf-8",errors="replace")
        source=args.url
    rows,failures,tr_count=parse_table(html,args.year,date.fromisoformat(args.asof),source)
    if not rows:
        print("No qualifying index rows parsed; do not equate with no reports.",file=sys.stderr)
        raise SystemExit(2)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(sorted(rows,key=lambda r:(r["catalogue_date"],r["symbol"])))
    if failures:
        with args.output.with_suffix(".exceptions.csv").open("w",encoding="utf-8",newline="") as f:
            w=csv.writer(f)
            w.writerow(["symbol","table_row","exception","published_date"])
            w.writerows(failures)
    print(f"INDEX STAGING: year={args.year} parsed_table_rows={tr_count} accepted_symbols={len(rows)} exceptions={len(failures)}")
    print("Staged index rows are not yet reconciled against uploaded project census or full report texts.")
if __name__=="__main__":
    main()
