#!/usr/bin/env python3
"""Build additive V7 reference and watch views; preserve every earlier snapshot.

The recovery entrypoint separately authenticates pypdf text derivations. This
finalizer independently checks original files with PyMuPDF, verifies retained
text hashes and tests only the explicitly selected source-reference passages.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
import fitz

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/census_v7'
OUTPUTS=['report_briefing_links_effective.csv','recovery_content_checks.csv','independent_pdf_checks.csv']
PRESENTATIONS={'S/PV.9931','S/PV.10060','S/PV.10195'}
TARGETS={'S/PV.9931','S/PV.9942','S/PV.9998','S/PV.10060','S/PV.10165','S/PV.10195','S/PV.10223'}

def ensure(value,message):
    if not value:raise AssertionError(message)

def read(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def write(path,rows):
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def normalized(text):return re.sub(r'\s+',' ',text).strip()

def symbol_present(text,symbol):
    return bool(re.search(re.escape(symbol)+r'(?!\d)',re.sub(r'\s+','',text)))

def derive():
    before=read(ROOT/'data/census_v6/report_briefing_reuse_tests.csv')
    receipt=read(DATA/'transcript_recovery.csv')
    ensure(len(receipt)==7 and {r['meeting_record'] for r in receipt}==TARGETS,'Recovery population differs')
    lookup={r['meeting_record']:r for r in receipt}
    texts={};independent=[]
    for r in receipt:
        p=ROOT/r['pdf_path'];doc=fitz.open(p)
        pages=[page.get_text() for page in doc]
        cover=re.sub(r'\s+','',pages[0])
        day=datetime.strptime(r['meeting_date'],'%Y-%m-%d')
        ensure(digest(p)==r['sha256'],'Original hash changed')
        ensure(digest(ROOT/r['pages_path'])==r['pages_sha256'],'Archived page-text hash changed')
        ensure(len(json.loads((ROOT/r['pages_path']).read_text()))==int(r['pages']),'Archived page-text count differs')
        ensure(len(pages)==int(r['pages']),'Independent page count differs')
        ensure(symbol_present(pages[0],r['meeting_record']),'Independent cover symbol differs')
        ensure(f'{day.day}{day.strftime("%B%Y")}' in cover,'Independent cover date differs')
        ensure('SecurityCouncil' in cover and 'Agenda' in cover,'Not an English Council record')
        ensure(all(len(t.strip())>=120 for t in pages),'Empty or low-text page')
        texts[r['meeting_record']]=pages
        independent.append(dict(meeting_record=r['meeting_record'],sha256=r['sha256'],
            pages=len(pages),independent_parser='PyMuPDF '+fitz.VersionBind,
            cover_symbol='pass',cover_date='pass',English_cover='pass',
            all_pages_extractable='pass',raw_bytes_unchanged='pass',
            visual_review_scope='covers and selected reference pages; not every page'))
    current=[];checks=[]
    for old in before:
        row=dict(old);sym=old['meeting_record']
        if sym in lookup:
            r=lookup[sym];pages=texts[sym]
            ensure(symbol_present(pages[1],old['report_symbol']),'Report absent from printed page 2')
            refpages=[n for n,t in enumerate(pages,1) if symbol_present(t,old['report_symbol'])]
            presentation=sym in PRESENTATIONS
            if presentation:ensure('present' in pages[1].lower(),'Presentation verb missing')
            row.update(current_classification='explicit_agenda_or_presentation_report_reference',
                report_reference_pages=json.dumps(refpages),full_transcript_checked='True',
                briefer_to_report_dependency='explicit_presentation_or_formal_agenda_association; not a funded-production finding',
                evidence_version='V7 recovery',source_sha256=r['sha256'],
                original_pdf_path=r['pdf_path'],reference_verified_page=2,
                opening_reference_role=('briefer_explicit_presentation' if presentation else 'formal_agenda_and_president_reference'),
                review_scope='complete file authenticated; specified reference passages reviewed; exhaustive substantive comparison not performed')
            checks.append(dict(check_id='V7-'+old['record_id'],source_symbol=sym,printed_page=2,
                referenced_symbol=old['report_symbol'],relation=row['opening_reference_role'],
                observation='Paired report explicitly identified in the recovered original, not inferred from topic or date.',
                limitation='An explicit reference does not establish duplicate drafting, staff effort or expenditure.',
                source_sha256=r['sha256'],result='pass'))
        else:
            row.update(evidence_version='V6 retained',source_sha256='',original_pdf_path='',
                reference_verified_page='',opening_reference_role='previous_adjudication_retained',
                review_scope='unchanged prior V6 adjudication; not freshly re-reviewed in V7')
        current.append(row)
    extra=[
      ('V7-X01','S/PV.9931',3,'S/PV.9890',['Niger','withdrawal','Multinational Joint Task Force'],
       'explicit_cross_office_briefing_reference',
       'UNOCA briefer explicitly refers to the earlier UNOWAS briefing on the Niger withdrawal announcement.',
       'Demonstrates an attributed cross-office reference; not a single shared drafting or financial cost object.'),
      ('V7-X02','S/PV.10165',4,'S/2026/431',['Border closures','Secretary-General'],
       'briefer_explicit_substantive_report_reference',
       'Briefer attributes border-closure impacts to the paired Secretary-General report.',
       'This passage establishes source referral, not identity of the complete report and briefing.'),
      ('V7-X03','S/PV.10223',2,'S/PV.10165',['most recent briefing'],
       'explicit_previous_briefing_reference',
       'September briefer explicitly links the assessment to the preceding June briefing.',
       'Separate reporting periods and subsequent developments require time-stamped updates.'),
      ('V7-X04','S/PV.10223',2,'S/2026/724',['Badakhshan','armed clashes'],
       'briefer_explicit_substantive_report_reference',
       'Briefer directs readers to the paired report for detail on Badakhshan armed clashes.',
       'Detailed report and oral assessment remain distinct mandated products.')]
    for ident,sym,page,target,terms,relation,observation,limitation in extra:
        text=normalized(texts[sym][page-1])
        ensure(symbol_present(text,target) and all(term in text for term in terms),'Reviewed reference assertion changed: '+ident)
        checks.append(dict(check_id=ident,source_symbol=sym,printed_page=page,referenced_symbol=target,
            relation=relation,observation=observation,limitation=limitation,
            source_sha256=lookup[sym]['sha256'],result='pass'))
    classes=Counter(r['current_classification'] for r in current)
    ensure(len(current)==14 and classes=={'explicit_agenda_or_presentation_report_reference':13,
        'explicit_Council_discussion_report_reference':1},'Unapproved association classification change')
    rm10=next(r for r in current if r['record_id']=='RM010')
    ensure(rm10['briefer_to_report_dependency']=='not_established','Discussion reference promoted to briefer dependency')
    watch=json.loads((DATA/'course_watch_contract.json').read_text())
    ensure(len(watch['watch_population'])==8 and watch['scheduler_creation_verified'],'Watch contract incomplete')
    ensure(watch['checks_executed_at_creation']==0,'Setup misrepresented as completed weekly check')
    ensure(watch['first_weekly_check_date']=='2026-10-16','First weekly date changed')
    summary=dict(asof='2026-10-15',recovered_transcripts=len(receipt),recovered_pages=sum(int(r['pages']) for r in receipt),
        remaining_transcript_retrieval_gaps=0,effective_report_briefing_links=len(current),
        effective_link_classes=dict(classes),specified_reference_checks=len(checks),
        explicit_new_opening_presentations=3,independent_parser='PyMuPDF '+fitz.VersionBind,
        original_and_derived_bytes='verified',weekly_watch='created; Friday mornings America/New_York',
        first_weekly_check_date=watch['first_weekly_check_date'],watched_course_cohorts=8,
        new_course_completion_claims=0,frozen_prior_tables='unchanged',
        exhaustive_substantive_comparison='not_performed',mandated_deliverables='unchanged',
        parent_and_mission_rankings='unchanged',retrospective_2027_support='20/32 unchanged',
        financial_duplication='not_established',incremental_net_savings='not_estimated')
    return current,checks,independent,summary

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');args=p.parse_args()
    current,checks,independent,summary=derive()
    if args.write:
        for filename,rows in zip(OUTPUTS,[current,checks,independent]):write(DATA/filename,rows)
        (DATA/'final_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
        lines=['# Seven transcript gaps recovered; weekly course checks established','',
          '**15 October 2026 | Original UN records | Prior census snapshots unchanged**','',
          '## Completed','',
          '**All seven missing original English Council records are recovered and authenticated: 187 pages.** The effective 14-link register now contains 13 explicit formal-agenda/presentation associations and one retained Council-discussion-only association. This closes document retrieval, not every possible substantive comparison.','',
          '| Original record | Meeting date | Paired SG report | Pages |','|---|---|---|---:|']
        for r in read(DATA/'transcript_recovery.csv'):
            lines.append(f"| [{r['meeting_record']}]({r['source_url']}) | {r['meeting_date']} | {r['report_symbol']} | {r['pages']} |")
        lines+=['','[Original PDFs](../data/census_v7/originals) · [Recovery manifest](../data/census_v7/transcript_recovery.csv) · [Effective report–briefing links](../data/census_v7/report_briefing_links_effective.csv)','',
          '## What the recovered references establish','',
          '**Direct presentation:** S/PV.9931, S/PV.10060 and S/PV.10195 explicitly present their paired reports on printed page 2. The other four records explicitly identify their reports in the formal agenda/presidential introduction. These are document-specific links, not topic/date matches.','',
          '**Cross-office attribution:** On page 3 of S/PV.9931, the UNOCA briefer refers expressly to the earlier UNOWAS briefing, S/PV.9890, on the Niger withdrawal announcement. This strengthens the case for a shared, attributed regional evidence register while retaining separate regional analysis and Council outputs.','',
          '**Versioned updates:** S/PV.10223 page 2 refers both to the earlier briefing S/PV.10165 and to S/2026/724 for Badakhshan detail. S/PV.10165 page 4 also attributes border-closure impacts to S/2026/431. These referrals support shared factual inputs and controlled updates, not merger of the final products.','',
          'The earlier S/PV.10116–S/2026/99 relationship remains Council-discussion-only; it is not promoted to proven briefer dependence. [Eleven specified reference checks](../data/census_v7/recovery_content_checks.csv).','',
          '## Weekly official-source course watch','',
          '**The scheduled task is active for Friday mornings around 08:00 America/New_York, beginning 16 October 2026.** It monitors all eight unresolved cohorts in the frozen V6 register, using official UN and verified official host sources. No future check or new course completion is claimed at setup.','',
          'Notifications are conditional on material new completion, commencement, cancellation or rescheduling evidence, a resolved cohort-identity conflict, or a new material access blocker. Unchanged evidence remains silent. Advertised, opened, completed and certified stages remain separate. Korea’s conflicting programme dates must be reconciled; missing completion evidence is not evidence of cancellation.','',
          'Material findings are to be appended as dated, source-linked updates, with verified commits when repository writes are available. Frozen V5/V6 tables are not rewritten. [Watch contract and eight-cohort population](../data/census_v7/course_watch_contract.json).','',
          '## Recovery and validation','',
          'The prior recovery frontier admitted unrelated sidebar PDFs before reaching the symbol-specific viewer links. The revised collector uses exact-symbol official document-viewer links. The first V7 attempt accepted four records and withheld three on cover-text checks; its failure receipts remain under history. Removing extraction whitespace for identifier/date comparisons resolved those three without modifying PDF bytes or accepting wrong symbols.','',
          'pypdf verifies every original file, derived page-text hash and full text re-extraction in the recovery check. A second parser, PyMuPDF, independently verifies all seven cover symbols, dates, page counts and extractability across 187 pages. All covers and selected reference pages were visually inspected; not every page received visual or substantive review. [Independent checks](../data/census_v7/independent_pdf_checks.csv) · [Original failed attempt](../data/census_v7/history/first_summary.json).','',
          'Recovery is reproducible offline with `python3 scripts/recover_census_v7_layout.py`. Build the effective views with `python3 scripts/finalize_census_v7.py --write`; validate retained views with `python3 scripts/finalize_census_v7.py`.','',
          '**Unchanged:** mandated reports and briefings, parent/mission rankings, and 20/32 prior retrospective output-category support. No duplicate paid service or incremental net saving is established. Course completion remains an ongoing official-source verification task.','']
        report=ROOT/'docs/census_2025_2026_v7_recovery.md';report.write_text('\n'.join(lines),encoding='utf-8')
        tracked=[DATA/x for x in OUTPUTS]+[DATA/'final_summary.json',report,DATA/'course_watch_contract.json']
        (DATA/'final_output_manifest.json').write_text(json.dumps({str(f.relative_to(ROOT)):digest(f) for f in tracked},indent=2,sort_keys=True)+'\n')
    for filename,rows in zip(OUTPUTS,[current,checks,independent]):
        ensure(read(DATA/filename)==[{k:str(v) for k,v in r.items()} for r in rows],'Derived view differs: '+filename)
    ensure(json.loads((DATA/'final_summary.json').read_text())==summary,'Final summary differs')
    for name,hash_value in json.loads((DATA/'final_output_manifest.json').read_text()).items():
        ensure(digest(ROOT/name)==hash_value,'Final output hash changed: '+name)
    print(json.dumps(dict(status='PASS',**summary),indent=2,sort_keys=True))

if __name__=='__main__':main()
