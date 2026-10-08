#!/usr/bin/env python3
"""Build source-faithful Security Council report and formal meeting index snapshots.

This enumerates official *index entries*, not underlying Council speech content.
No claim of report duplication is made from shared countries, topics or dates.
2026 data end at the earlier of 8 October and the last record in the index.
The 2025 benchmark is 255 DISTINCT formal meeting IDs; resumed transcripts
may create extra index rows. Private consultations are not meeting transcripts.

Dependencies: beautifulsoup4 (HTML). Requires web access when --fetch is used.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import datetime, date, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

REPORT_ENDPOINT = (
    "https://main.un.org/securitycouncil/en/content/"
    "reports-submitted-transmitted-secretary-general-security-council-{}"
)
MEET_ENDPOINT = (
    "https://ydsftksff8.execute-api.us-east-1.amazonaws.com/"
    "dev/render_meeting/scmeetings_{}/EN"
)
AS_OF = date(2026, 10, 8)
MONTHS = (
    "January February March April May June July August September "
    "October November December"
).split()
DOC_RE = re.compile(r"\bS/(2025|2026)/(\d{1,4})\b")
PV_RE = re.compile(r"\bS/PV\.(\d{4,5})\b")
DATE_RE = re.compile(
    r"\b(\d{1,2})\s+("
    + "|".join(MONTHS)
    + r")\s+(2025|2026)\b",
    flags=re.IGNORECASE,
)
DATE_FORMAT = "%d %B %Y"
FAMILY_RULES = [
    ("UNOWAS", r"West Africa and the Sahel|Peace consolidation in West Africa|UNOWAS"),
    ("UNOCA", r"\bCentral Africa\b|Central African region|Regional Office for Central Africa|UNOCA"),
    ("UNAMA", r"Afghanistan"),
    ("UNSCOL_UNIFIL", r"resolution 1701|Lebanon"),
    ("UNIFIL", r"United Nations Interim Force in Lebanon|UNIFIL"),
    ("UNSMIL", r"Libya"),
    ("MONUSCO", r"Democratic Republic of the Congo|MONUSCO"),
    ("MINUSCA", r"Central African Republic|MINUSCA"),
    ("UNMISS", r"South Sudan"),
    ("UNISFA", r"Abyei"),
    ("BINUH", r"United Nations Integrated Office in Haiti|Haiti"),
    ("COLOMBIA", r"Verification Mission in Colombia|Colombia"),
    ("UNFICYP_CYPRUS", r"Cyprus"),
    ("MINURSO_SAHARA", r"Western Sahara|MINURSO"),
    ("UNSOS_SOMALIA", r"Somalia|AUSSOM|Al-Shabaab"),
    ("UNDOF", r"United Nations Disengagement Observer Force|UNDOF"),
    ("UNMIK", r"Kosovo"),
    ("YEMEN", r"Yemen|Hudaydah|Houthi"),
    ("WPS", r"women and peace and security"),
    ("COUNTERTERRORISM", r"ISIL|Da.esh|terrorist acts|Counter.Terrorism"),
    ("CROSS_CUTTING_PEACE_OPERATIONS", r"peacekeeping operations|peace operations"),
]
def family(text: str) -> str:
    for label, pattern in FAMILY_RULES:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return label
    return "OTHER_COUNCIL_AGENDA"

def parse_date(text: str) -> str:
    match = DATE_RE.search(text)
    if not match:
        return ""
    try:
        return datetime.strptime(match.group(0), DATE_FORMAT).date().isoformat()
    except ValueError:
        return ""

def context_for(anchor):
    for tag in ("tr", "li"):
        n = anchor.find_parent(tag)
        if n is not None:
            return n
    n = anchor.find_parent("div", class_=re.compile("views.row|row", re.I))
    if n:
        return n
    return anchor.parent.parent or anchor.parent

def extract_report(html: bytes, year: int) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    results = {}
    for a in soup.find_all("a"):
        title = a.get_text(" ", strip=True)
        m = DOC_RE.search(title)
        if not m or int(m.group(1)) != year:
            continue
        sym = m.group(0)
        ctx = context_for(a)
        cells = ctx.find_all("td", recursive=False)
        if len(cells) >= 3:
            raw_date = cells[1].get_text(" ", strip=True)
            doc_title = cells[2].get_text(" ", strip=True)
        else:
            raw = ctx.get_text(" | ", strip=True)
            md = DATE_RE.search(raw)
            raw_date = md.group(0) if md else "not_found_in_index"
            doc_title = raw.split(raw_date, 1)[-1].strip(" |:") if md else ""
            doc_title = re.sub(r"^S/\d{4}/\d+\s*[|:-]*\s*", "", doc_title)
            doc_title = doc_title[:500]
        date_val = parse_date(raw_date)
        if not doc_title or len(doc_title) > 500:
            doc_title = ctx.get_text(" ", strip=True).split(sym, 1)[-1][:400].strip()
        if not doc_title:
            raise ValueError("Missing report title for " + sym)
        if not date_val:
            raise ValueError("Missing report date for " + sym + ": " + raw_date[:100])
        u = a.get("href") or ("https://docs.un.org/en/" + sym)
        if u.startswith("/"):
            from urllib.parse import urljoin
            u = urljoin(REPORT_ENDPOINT.format(year), u)
        item = dict(
            document_symbol=sym, indexed_date=date_val, title=doc_title,
            index_year=year, family=family(doc_title),
            date_year_mismatch=str(date_val[:4] != str(year)).lower(),
            source_link=u, registry_url=REPORT_ENDPOINT.format(year),
            source_status="official_index_entry_not_full_text_comparison",
            identical_to_another_report="not_tested",
            financial_duplication="not_estimated",
        )
        results[sym] = item
    return sorted(results.values(), key=lambda x: (x["indexed_date"], x["document_symbol"]))

def extract_meeting(html: bytes, year: int) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    results = {}
    for a in soup.find_all("a"):
        title = a.get_text(" ", strip=True)
        m = PV_RE.search(title)
        if not m:
            continue
        base = m.group(0)
        ctx = context_for(a)
        cells = ctx.find_all("td", recursive=False)
        if len(cells) >= 4:
            raw_date = cells[1].get_text(" ", strip=True)
            topic = cells[3].get_text(" ", strip=True)
        else:
            raw = ctx.get_text(" | ", strip=True)
            md = DATE_RE.search(raw)
            raw_date = md.group(0) if md else "date_missing"
            after = raw.split(raw_date, 1)[-1] if md else ""
            fields = [f.strip() for f in after.split("|")]
            topic = fields[2] if len(fields) >= 3 else after[-220:].strip()
        date_value = parse_date(raw_date)
        if not date_value or int(date_value[:4]) != year:
            continue
        variant = "resumption" if re.search("resumption", title, re.I) else (
            "closed" if re.search("closed", title, re.I) else "original")
        suffix = re.search(r"\((Resumption\s+\d+)\)", title, re.I)
        variant_id = suffix.group(1).replace(" ", "_") if suffix else variant
        ident = base + ("/" + variant_id if variant == "resumption" else "")
        url = a.get("href") or ("https://docs.un.org/en/" + base)
        if url.startswith("/"):
            from urllib.parse import urljoin
            url = urljoin(MEET_ENDPOINT.format(year), url)
        item = dict(
            record_id=ident, meeting_base_id=base,
            date=date_value, year=year, topic=topic[:500],
            agenda_family=family(topic),
            variant=variant, source_link=url,
            registry_url=MEET_ENDPOINT.format(year),
            is_resumption=str(variant == "resumption").lower(),
            record_grain="verbatim_document_variant_not_unique_meeting",
            source_status="public_2025_or_2026_meeting_index_entry",
            meeting_to_report_link="not_inferred_from_same_topic_alone",
            financial_duplication="not_estimated",
        )
        results[ident] = item
    return sorted(results.values(), key=lambda x: (x["date"], x["record_id"], x["variant"]))

def fetch(url: str) -> bytes:
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; UN-Peace-Operations-Efficiency-research/1.0)",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urlopen(req, timeout=45) as response:
        payload = response.read(8_000_000)
        if response.status != 200 or len(payload) < 1000:
            raise OSError(f"Bad HTTP response/empty index: {url}")
        return payload

def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise AssertionError(f"Cannot write empty source dataset: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("data"))
    parser.add_argument("--input-fixture-dir", type=Path, default=None,
                        help="Use local frozen HTML instead of live network")
    parser.add_argument("--minimum-2026-meetings", type=int, default=110)
    parser.add_argument("--minimum-2025-meetings", type=int, default=255)
    args = parser.parse_args()
    source = []
    all_reports = []
    all_meetings = []
    for year in (2025, 2026):
        for kind,url in (
            ("secretary_general_reports", REPORT_ENDPOINT.format(year)),
            ("security_council_formal_meetings", MEET_ENDPOINT.format(year)),
        ):
            if args.input_fixture_dir:
                file = args.input_fixture_dir / f"{kind}_{year}.html"
                body = file.read_bytes()
            else:
                body = fetch(url)
            rows = extract_report(body, year) if kind.startswith("secretary") else extract_meeting(body, year)
            if kind.startswith("secretary"):
                all_reports.extend(rows)
            else:
                all_meetings.extend(rows)
            source.append(dict(
                source_id=f"{kind}_{year}",year=year,source_url=url,
                snapshot_as_of=str(AS_OF),
                retrieved_row_count=len(rows),
                source_sha256=hashlib.sha256(body).hexdigest(),
                extraction_status="success_index_entries_only",
                completeness_claim="snapshot_of_published_entries_not_entire_UN_output_universe",
            ))
            print(kind,year,len(rows),file=sys.stderr)
    n_reports=Counter(r["index_year"] for r in all_reports)
    n_meets=Counter(m["year"] for m in all_meetings)
    unique_meets=Counter()
    for year in (2025,2026):
        unique_meets[year]=len({m["meeting_base_id"] for m in all_meetings if m["year"]==year})
    if n_reports[2025] < 80 or n_reports[2026] < 45:
        raise AssertionError("Published SG report source changed unexpectedly or extraction incomplete: "+str(n_reports))
    if unique_meets[2025] < args.minimum_2025_meetings:
        raise AssertionError("2025 formal meetings index incomplete: "+str(unique_meets))
    if unique_meets[2026] < args.minimum_2026_meetings:
        raise AssertionError("2026 meeting index unexpectedly short: "+str(unique_meets))
    if len({r["document_symbol"] for r in all_reports}) != len(all_reports):
        raise AssertionError("Duplicate report document symbols")
    if len({m["record_id"] for m in all_meetings}) != len(all_meetings):
        raise AssertionError("Duplicate meeting record IDs")
    if any(r["indexed_date"]>str(AS_OF) for r in all_reports):
        raise AssertionError("Future-dated report in frozen as-of snapshot")
    if any(m["date"]>str(AS_OF) for m in all_meetings):
        raise AssertionError("Future-dated meeting in frozen as-of snapshot")
    stats = []
    for year in (2025,2026):
        stats.append(dict(source_id=f"SG_{year}",year=year,scope="SG_annual_report_index",index_items=n_reports[year],
              unique_base_meetings="not_applicable",
              annual_official_total="not_asserted_as_all_council_documents",
              census_status="index_extracted_as_of_2026_10_08"))
        stats.append(dict(source_id=f"MEET_{year}",year=year,scope="Council_formal_meeting_records",
              index_items=n_meets[year],
              unique_base_meetings=unique_meets[year],
              annual_official_total="255_formal_2025" if year==2025 else "not_yet_complete_year",
              census_status="formal_index_not_informal_consultation_census"))
    write_csv(args.output_dir / "systematic_sg_reports_2025_2026.csv",all_reports)
    write_csv(args.output_dir / "systematic_sc_meetings_2025_2026.csv",all_meetings)
    write_csv(args.output_dir / "systematic_census_source_snapshots.csv",source)
    write_csv(args.output_dir / "systematic_census_index_totals.csv",stats)
    summary={
        "as_of":str(AS_OF),
        "report_rows":dict(n_reports),
        "meeting_record_rows":dict(n_meets),
        "unique_formal_meeting_base_ids":dict(unique_meets),
        "official_2025_formal_meeting_benchmark":255,
        "official_2025_informal_consultations_not_included":115,
        "limitations":[
            "Index entries are not a census of all UN peace-operations products.",
            "Meeting rows may include resumptions; do not confuse S/PV documents with distinct Council meetings.",
            "2026 index is as published and may omit meetings since last indexed date.",
            "2026 report index includes one observed 2025-year metadata anomaly; preserve raw date.",
            "Meeting attendance, drafting overlap, shared inputs, and duplicate invoices are not asserted from topic matching.",
            "Field travel and training are not comprehensively indexed in these Council registers.",
        ],
    }
    (args.output_dir/"systematic_census_metadata.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True)+"\n",encoding="utf-8")
    print("SUCCESS",json.dumps({k:summary[k] for k in ("report_rows","meeting_record_rows","unique_formal_meeting_base_ids")}),file=sys.stderr)

if __name__ == "__main__":
    main()
