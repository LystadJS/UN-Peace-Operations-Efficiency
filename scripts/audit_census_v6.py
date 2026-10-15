#!/usr/bin/env python3
"""Build and validate the bounded V6 identity, delivery and source-reuse audit.

--write requires the frozen public source artifact's PDF/HTML bytes under
v6_raw_sources. Default/--check validates versioned outputs offline. A successful
check does not certify the universe of UN activities, unique people or savings.
"""
from __future__ import annotations
import argparse, csv, hashlib, itertools, json, re, unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/census_v6'
ASOF='2026-10-15'
CAPTURE_RUN=38742342482
CAPTURE_ZIP_SHA='0ab2787b82213cb8302898f0254927f2413f2b66041142e12c48bb50e577a600'

def ensure(ok,message):
    if not ok: raise AssertionError(message)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):
    with (ROOT/path).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def js(path):return json.loads(path.read_text(encoding='utf-8'))
def write_json(path,data):path.write_text(json.dumps(data,indent=2,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf-8')
def write_csv(path,rows,fields=None):
    fields=fields or list(dict.fromkeys(k for r in rows for k in r))
    ensure(bool(fields),'Missing CSV schema')
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in rows:w.writerow({k:json.dumps(v,ensure_ascii=False,sort_keys=True) if isinstance(v,(list,dict)) else v for k,v in r.items()})
def clean(text):return re.sub(r'\s+',' ',text).strip()

def observations():
    raw=[]
    sources={r['source_id']:r for r in read('data/retrospective_2025_2026_sources.csv')}
    def source_urls(ids):return sorted({sources[s]['official_url'] for s in re.findall(r'SRC\d+',ids) if s in sources})
    def add(path,n,key,title,kind,start='',end='',actors='',urls=None,precision='',status='',role='primary'):
        raw.append(dict(observation_id=f'{path}:{n}',source_file=path,logical_record_number=n,local_id=key,title=title,kind=kind,start=start,end=end,actors=actors,urls=urls or [],date_precision=precision,status=status,register_role=role))
    p='data/retrospective_2025_2026_activities.csv'
    for n,r in enumerate(read(p),2):add(p,n,r['activity_id'],r['verified_activity_or_product'],r['activity_type'],r['actual_start_date_or_month_start'],r['actual_end_date_or_month_end'],r['documented_entity_roles'],source_urls(r['primary_source_id']+';'+r['corroborating_source_ids']),status=r['analysis_period_status'])
    p='data/systematic_field_training_canonical_2025_2026.csv'
    for n,r in enumerate(read(p),2):add(p,n,r['canonical_id'],r['activity_or_output'],r['kind'],r['reported_start'],r['reported_end'],r['entities_and_roles'],[r['official_source_url']],r['date_precision'],r['event_year_eligibility'],'consolidated_view')
    p='data/systematic_field_training_activity_2025_2026.csv'
    for n,r in enumerate(read(p),2):add(p,n,r['activity_id'],r['title'],r['category'],r['start_date'],r['end_date'],r['entity_roles'],source_urls(r['source_ref']+';'+r['other_sources']),status=r['exclusion_reason'],role='filtered_view')
    p='data/census_2025_2026_public_activities.csv'
    for n,r in enumerate(read(p),2):add(p,n,r['item_id'],r['title'],r['kind'],r['start'],r['end'],r['entities_and_roles'],source_urls(r['source_locator']) or [r['official_url']],status=r['identity_level'])
    p='data/systematic_verified_field_training_additions.csv'
    for n,r in enumerate(read(p),2):add(p,n,r['event_id'],r['canonical_event_or_publication'],r['deliverable_type'],r['event_start_date'],r['event_end_date'],r['named_entities'],[r['official_url']],r['event_date_precision'],r['source_stage'])
    p='data/census_v2/verified_joint_additions.csv'
    for n,r in enumerate(read(p),2):add(p,n,r['case_id'],r['event'],r['output_type'],r['activity_start_or_lower_bound'],r['activity_end_or_upper_bound'],r['actors'],[r['official_source_url']],r['date_precision'],r['evidence_class'])
    p='data/census_v3/extended_canonical_activities.csv'
    for n,r in enumerate(read(p),2):
        ds=r['source_event_date_or_range'].split('/')
        add(p,n,r['canonical_id'],r['title'],r['kind'],ds[0],ds[-1],r['entities'],[r['official_source_url']],r['date_precision'],r['delivery_status'])
    p='data/census_v4/attendance_evidence.csv'
    for n,r in enumerate(read(p),2):add(p,n,r['canonical_event_id'],r['event_title_and_place'],r['delivery_evidence'],r['event_date_or_start'],r['event_end_or_bound'],r['entities_and_roles'],[r['official_source_url']],status=r['reconciliation'],role='attendance_observation')
    v5=js(ROOT/'data/census_v5/reviewed_evidence.json');v5sources={r['source_id']:r for r in v5['sources']}
    for p in ('data/census_v5/adjudicated_activities.csv','data/census_v5/effective_activity_register.csv'):
        for n,r in enumerate(read(p),2):add(p,n,r['event_id'],r['title'],r['kind'],r['event_start'],r['event_end'],r['providers'],[v5sources[s]['url'] for s in json.loads(r['source_ids'])],r['date_precision'],r['delivery_status'],'effective' if 'effective' in p else 'superseded_seed')
    p='data/census_v3/verified_shared_knowledge_products.csv'
    for n,r in enumerate(read(p),2):add(p,n,r['product_id'],r['title'],r['product_type'],r['date_or_year'],r['date_or_year'],r['publisher_and_coauthors'],[r['official_url']],status=r['identity_control'],role='knowledge_product')
    for p,key in [('data/systematic_census_inventory_2025_2026.csv','canonical_activity_id'),('data/systematic_master_record_views_2025_2026.csv','canonical_event_id')]:
        known={r['local_id']:r for r in raw}
        for n,r in enumerate(read(p),2):
            if r[key] in known:
                a=known[r[key]];add(p,n,r[key],a['title'],a['kind'],a['start'],a['end'],a['actors'],a['urls'],a['date_precision'],a['status'],'mixed_inventory_view')
    return raw,v5

def build():
    from pypdf import PdfReader
    d=js(OUT/'review_decisions.json');ensure(d['asof']==ASOF,'Cutoff changed')
    rows,v5=observations();groups=defaultdict(list)
    for r in rows:groups[r['local_id']].append(r)
    ensure(len(rows)==371 and len(groups)==130,'Input corpus changed; review before publication')
    amap={key:cluster['canonical_id'] for cluster in d['alias_clusters'] for key in cluster['members']}
    ensure(len(amap)==12 and set(amap)<=set(groups),'Alias membership changed')
    preferred={k:next((r for r in v if r['register_role']=='effective'),v[0]) for k,v in groups.items()}
    aliases=[dict(local_id=k,canonical_id=amap.get(k,k),observation_count=len(groups[k]),decision='same_identity_alias' if k in amap and amap[k]!=k else 'canonical_identity_retained') for k in sorted(groups)]
    negatives={frozenset((x['left'],x['right'])):x['basis'] for x in d['negative_controls']}
    stop=set('the and in on of for to a at with un united nations course workshop training meeting joint mission 2025 2026'.split())
    def tokens(t):return set(re.findall('[a-z0-9]+',unicodedata.normalize('NFKD',t.lower())))-stop
    pairs=[];all_urls={k:{u for r in vv for u in r['urls']} for k,vv in groups.items()}
    for a,b in itertools.combinations(sorted(groups),2):
        x,y=preferred[a],preferred[b];ta,tb=tokens(x['title']),tokens(y['title'])
        j=len(ta&tb)/len(ta|tb) if ta|tb else 0
        s=SequenceMatcher(None,x['title'].lower(),y['title'].lower()).ratio()
        shared=sorted(all_urls[a]&all_urls[b]);candidate=bool(shared) or j>=.24 or s>=.60
        same=amap.get(a,a)==amap.get(b,b)
        ensure(not same or candidate,'Known positive omitted by candidate screen')
        reason=next((c['basis'] for c in d['alias_clusters'] if a in c['members'] and b in c['members']),None) if same else negatives.get(frozenset((a,b)))
        if not reason:
            reason=('Different date/cohort/location/function or event-versus-product grain after cross-version review; shared source or title alone is insufficient.' if candidate else 'No shared source URL or qualifying title similarity; retained after record-level corpus review.')
        pairs.append(dict(left_id=a,right_id=b,jaccard=round(j,6),sequence_similarity=round(s,6),shared_urls=shared,candidate=candidate,verdict='same_identity' if same else 'distinct_identity_retained',reason=reason))
    ensure(len(pairs)==8385 and sum(p['candidate'] for p in pairs)==189,'Pair-screen denominator changed')
    ensure(sum(p['verdict']=='same_identity' for p in pairs)==9,'Positive pair decisions changed')
    identities=defaultdict(list)
    for k in groups:identities[amap.get(k,k)].append(k)
    registry=[]
    for cid,members in sorted(identities.items()):
        primary=preferred[cid];obs=[r for m in members for r in groups[m]]
        grain=('report_or_other_non_event_product' if cid in d['non_event_ids'] else 'programme_or_multiple_course_group' if cid in d['programme_group_ids'] else 'formal_Council_briefing' if primary['kind']=='security_council_briefing' else 'activity_or_service_period_not_necessarily_single_session')
        eligibility='excluded_before_window' if cid in d['out_of_window_ids'] else 'delivery_not_verified' if cid in d['unverified_delivery_ids'] else 'retain_source_qualified_status'
        date_note='Retain original date precision: publication/quarter bounds are not exact occurrence dates.'
        if cid=='EV001':date_note='V6Q01: S/2025/187 para49 prints 28-31 January; S/2025/342 para61 prints 27-31 January. One visit identity; disputed start remains source-qualified.'
        registry.append(dict(canonical_id=cid,local_aliases=sorted(members),title=primary['title'],preferred_kind=primary['kind'],grain=grain,eligibility=eligibility,preferred_source_start=primary['start'],preferred_source_end=primary['end'],date_precision=primary['date_precision'],date_qualification=date_note,source_status=primary['status'],observation_count=len(obs),source_urls=sorted({u for r in obs for u in r['urls']}),global_population_complete=False,unique_people='not_estimated',incremental_net_savings='not_estimated'))
    ensure(len(registry)==123,'Canonical evidence count changed')
    for row in rows:row['canonical_id']=amap.get(row['local_id'],row['local_id'])
    write_csv(OUT/'observation_lineage.csv',rows);write_csv(OUT/'canonical_identity_map.csv',aliases)
    write_csv(OUT/'canonical_evidence_register.csv',registry)
    write_csv(OUT/'all_pair_screen.csv',pairs);write_csv(OUT/'candidate_adjudications.csv',[p for p in pairs if p['candidate']])
    write_csv(OUT/'alias_clusters.csv',d['alias_clusters']);write_csv(OUT/'negative_controls.csv',d['negative_controls'])
    write_json(OUT/'nonadditive_programme_and_baseline_controls.json',dict(programme_groups=v5['programme_groups'],existing_mechanisms=v5['existing_mechanisms'],interpretation='Outside the 130-ID CSV corpus. Programme group is not an additional single event; mechanisms are existing baselines.'))
    schedule={r['listing_id']:r for r in read('data/census_v5/advertised_training_controls.csv')}
    courses=[dict(**schedule[c['listing_id']],**{k:v for k,v in c.items() if k!='listing_id'},verification_asof=ASOF) for c in d['course_decisions']]
    ensure(len(courses)==8 and all(c['completed_participants'] is None for c in courses),'Unsupported course completion')
    write_csv(OUT/'course_delivery_verification.csv',courses)
    # Authenticate exact source bytes and re-extract rather than trusting cached text.
    access=js(OUT/'source_capture/document_access.json');texts={};docs=[]
    for item in access['records']:
        if item['status']!='downloaded_symbol_checked':
            docs.append(dict(requested_symbol=item['symbol'],status='unavailable',original_url='',sha256='',actual_cover_symbol='',pages=0,low_text_pages=[],page_text_sha256=''));continue
        path=ROOT/'v6_raw_sources'/(item['sha256']+'.pdf')
        ensure(path.exists() and sha(path)==item['sha256'],'Missing or altered original PDF: '+item['symbol'])
        pages=[p.extract_text() or '' for p in PdfReader(path).pages]
        cover=re.sub(r'\s+','',pages[0]);target=item['symbol']
        ensure(target in cover,'Requested symbol absent from cover')
        actual=target+'/Rev.1' if target+'/Rev.1' in cover else target
        texts[target]=pages
        text_sha=hashlib.sha256(json.dumps(pages,ensure_ascii=False).encode()).hexdigest()
        docs.append(dict(requested_symbol=target,status='verified_bytes_and_cover',original_url=item['url'],sha256=item['sha256'],actual_cover_symbol=actual,pages=len(pages),low_text_pages=[i+1 for i,p in enumerate(pages) if len(clean(p))<130],page_text_sha256=text_sha))
    ensure(sum(not k.startswith('S/PV.') for k in texts)==33,'Report capture unexpectedly incomplete')
    ensure(sum(k.startswith('S/PV.') for k in texts)==7,'Transcript capture changed; reassess new material')
    write_csv(OUT/'document_authentication.csv',docs)
    rr=[];ref_locations=[]
    for r in read('data/census_2025_2026_report_pair_tests.csv'):
        a,b=r['first_symbol'],r['second_symbol'];hits=[]
        for source,target in ((a,b),(b,a)):
            for pn,t in enumerate(texts[source],1):
                for m in re.finditer(re.escape(target)+r'(?!\d)',t):
                    hits.append(dict(pair_id=r['pair_id'],source_symbol=source,target_symbol=target,page=pn,text_character_offset=m.start(),evidence='explicit document-symbol reference; consult original source page'))
        verdict=('previous_reporting_period_reference' if r['pair_id'] in ('PAIR13','PAIR14') and hits else 'explicit_cross_mandate_reference' if hits else 'no_explicit_pair_reference_in_extracted_text')
        rr.append(dict(pair_id=r['pair_id'],first_symbol=a,second_symbol=b,classification=verdict,reference_occurrences=len(hits),source_pages=sorted({f"{h['source_symbol']} p{h['page']}" for h in hits}),interpretation=d['report_pair_interpretations'].get(r['pair_id'],'No explicit cross-reference to the paired document found in extracted text. Similar subject matter alone does not certify production reuse; image-only material and unpublished drafting provenance remain outside this test.'),revision_qualification='good-offices source is S/2025/7/Rev.1' if r['pair_id']=='PAIR04' else '',mandated_products_remain_separate=True,financial_duplication='not_established'))
        ref_locations.extend(hits)
    write_csv(OUT/'report_pair_reuse_tests.csv',rr);write_csv(OUT/'explicit_reference_locations.csv',ref_locations)
    rm=[]
    for r in read('data/systematic_report_meeting_links_2025_2026.csv'):
        report,pv=r['report_symbol'],r['meeting_record'];pages=texts.get(pv)
        refs=[i+1 for i,p in enumerate(pages or []) if report in p]
        if pages:
            ensure(refs,'Available transcript does not cite expected report')
            verdict='explicit_Council_discussion_report_reference' if r['record_id']=='RM010' else 'explicit_agenda_or_presentation_report_reference'
        else:verdict='transcript_not_retrieved_prior_link_retained_not_promoted'
        rm.append(dict(record_id=r['record_id'],report_symbol=report,meeting_record=pv,meeting_date=r['meeting_date'],prior_evidence_status=r['evidence_status'],current_classification=verdict,report_reference_pages=refs,full_transcript_checked=bool(pages),briefer_to_report_dependency='not_established' if r['record_id']=='RM010' or not pages else 'explicit_presentation_or_formal_agenda_association; see separate content tests',financial_duplication='not_established'))
    write_csv(OUT/'report_briefing_reuse_tests.csv',rm)
    for test in d['substantive_reuse_tests']:
        for side in ('source','target'):
            text=clean(' '.join(texts[test[side]][i-1] for i in test[side+'_pages']))
            for anchor in test[side+'_anchors']:ensure(anchor in text,f"Reviewed source anchor missing {test['test_id']} {side}: {anchor}")
    write_csv(OUT/'substantive_reuse_tests.csv',d['substantive_reuse_tests'])
    # HTTP success is not article success: preserve challenge pages as access limits.
    notice_checks=[]
    for n in js(OUT/'source_capture/notice_access.json'):
        textpath=ROOT/'v6_raw_sources'/n.get('text_file','missing')
        text=textpath.read_text() if textpath.is_file() else ''
        status='challenge_not_article_body' if 'Client Challenge' in text else 'retrieved_source_text' if len(text)>500 else 'insufficient_source_text'
        notice_checks.append(dict(source_id=n['source_id'],url=n['url'],transport_status=n['status'],content_status=status,source_sha256=n.get('sha256',''),characters=len(text)))
    write_csv(OUT/'notice_content_checks.csv',notice_checks)
    write_csv(OUT/'quality_exceptions.csv',d['quality_exceptions'])
    source_files=sorted({r['source_file'] for r in rows}|{'data/retrospective_2025_2026_sources.csv','data/census_v5/reviewed_evidence.json','data/census_v5/advertised_training_controls.csv','data/census_2025_2026_report_pair_tests.csv','data/systematic_report_meeting_links_2025_2026.csv'})
    manifest=[dict(path=p,sha256=sha(ROOT/p),interpretation='unchanged frozen pre-V6 input') for p in source_files]
    write_csv(OUT/'frozen_input_manifest.csv',manifest)
    summary=dict(asof=ASOF,baseline_commit=d['baseline_commit'],capture_run=CAPTURE_RUN,capture_zip_sha256=CAPTURE_ZIP_SHA,
      curated_registers=len({r['source_file'] for r in rows}),observation_rows=len(rows),local_identities=len(groups),pair_screen_population=len(pairs),candidate_pairs=sum(p['candidate'] for p in pairs),same_identity_pairs=9,alias_clusters=5,absorbed_alias_ids=7,canonical_evidence_identities=len(registry),
      v5_records=16,v5_prior_aliases=1,v5_distinct_additions_within_declared_corpus=15,
      course_dispositions=dict(Counter(c['verification_status'] for c in courses)),completed_scheduled_courses_verified=0,
      authenticated_pdfs=len(texts),authenticated_reports=33,authenticated_transcripts=7,unretrieved_transcripts=7,
      report_pair_tests=len(rr),report_pair_classes=dict(Counter(r['classification'] for r in rr)),report_briefing_tests=len(rm),report_briefing_classes=dict(Counter(r['current_classification'] for r in rm)),
      substantive_reuse_tests=len(d['substantive_reuse_tests']),notice_content_classes=dict(Counter(r['content_status'] for r in notice_checks)),quality_exceptions=len(d['quality_exceptions']),safeguards=d['safeguards'],completion='bounded cross-version identity review complete; scheduled-course completion and seven transcript bodies remain unverified')
    write_json(OUT/'audit_summary.json',summary)
    report=['# Cross-version census audit: identities, course delivery and source reuse','',f'**As of {ASOF} | Public evidence | Frozen financial and mandate controls unchanged**','',
      '## Decision','',
      '**The bounded cross-version identity audit is complete.** The 13 curated CSV registers/views contain 371 observations, 130 local IDs and **123 canonical evidence identities**, after reconciling five alias clusters. These mixed-grain identities are not 123 delivered events. All 8,385 ID pairs were screened; 189 candidate pairs were reviewed, with nine positive pair links absorbing seven aliases. The source-URL frame and the unobserved operational population are not being declared complete.','',
      'The eight course listings were checked, but **no exact-cohort completion is newly certified**: two scheduled periods have elapsed, one spans the cutoff and five begin in the future. This is neither a cancellation finding nor an assertion that the elapsed courses did not occur.','',
      'The source audit authenticated **40 PDFs: 33 requested report files and seven transcripts**. One report file is an identified revision. Seven other transcripts remain unavailable. The report comparisons establish six cross-mandate referral pairs and two references to previous reporting periods; six other pairs have no explicit paired-document reference in the extracted text.','',
      '## Canonical identity corrections','','| Canonical ID | Aliases absorbed | Verified identity |','|---|---|---|']
    for c in d['alias_clusters']:report.append(f"| {c['canonical_id']} | {', '.join(x for x in c['members'] if x!=c['canonical_id'])} | {c['basis']} |")
    report += ['', 'The other 15 V5 identities are distinct within this declared earlier curated corpus. Announcements, attendance enrichments, language mirrors and source publications do not create additional events. The record map is reversible; no historical source row or frozen identifier was deleted.','',
      'The evidence register keeps 17 non-event report/product identities, three programme or multiple-course groups, a 2024 exclusion and an unverified delivery record separate. Formal Council briefings, composite service periods, underway courses and exact sessions retain their own grain. Programme V5G001 and existing mechanisms V5B01/02 are separate nonadditive controls, not additional single events.','',
      '[Canonical evidence register](../data/census_v6/canonical_evidence_register.csv) · [Reversible ID map](../data/census_v6/canonical_identity_map.csv) · [Observation lineage](../data/census_v6/observation_lineage.csv) · [Candidate adjudications](../data/census_v6/candidate_adjudications.csv)','',
      '## Eight advertised courses','','| Listing | Course / host | Planned dates | Verification result |','|---|---|---|---|']
    for c in courses:
        dates=(c.get('planned_start','')+' to '+c.get('planned_end','')).strip() if c.get('planned_start') else c.get('planned_month','')
        report.append(f"| {c['listing_id']} | {c['course']} / {c['host']} | {dates} | {c['verification_status'].replace('_',' ')} |")
    report += ['', '**Korea:** A related host announcement and contemporaneous reporting were located, but programme dates do not exactly match the ITS listing. A reported opening and a planned four-week programme do not establish completion of the specific three-week scheduled cohort; no attendee total is imported. **Egypt:** No exact-cohort delivery or graduation record was found in the reviewed official sources. **Denmark:** The planned course end is after the cutoff; even commencement remains unverified. The five later courses are not yet due.','',
      'Source: [DPO ITS planned-training calendar](https://peacekeepingresourcehub.un.org/en/news). [Full course verification, source scope and unresolved identity evidence](../data/census_v6/course_delivery_verification.csv). Official host search results are discovery evidence unless a course-specific body or completion record supports a stronger claim.','',
      '## Explicit reuse across distinct products','','| Test | Source evidence | Interpretation |','|---|---|---|']
    for t in d['substantive_reuse_tests']:
        report.append(f"| {t['test_id']} | {t['source']} pp. {','.join(map(str,t['source_pages']))} → {t['target']} pp. {','.join(map(str,t['target_pages']))} | {t['interpretation']} |")
    report += ['', '**Additional cross-mandate referrals:** UNFICYP and good-offices reports in January/July 2025 and January/July 2026 deliberately refer readers across their reporting streams. In July 2026 the referrals run both ways. The resolution 1559 report S/2025/254 also directs readers to resolution 1701 report S/2025/153 for detailed developments. These are already observed reuse, not newly discovered paid duplication. The January 2025 good-offices PDF is S/2025/7/Rev.1 and is labelled accordingly.','',
      '**Report versus meeting:** Six recovered transcripts explicitly associate the named report with the formal agenda or presentation. The seventh, S/PV.10116, explicitly references S/2026/99 in Council discussion, upgrading the earlier topic/date-only association. However, matching humanitarian-appeal figures alone do not prove that the briefer took them from that report rather than the shared upstream appeal. Seven unavailable transcript bodies remain open, not silently treated as reviewed.','',
      '[14 report-pair tests](../data/census_v6/report_pair_reuse_tests.csv) · [14 report/briefing tests](../data/census_v6/report_briefing_reuse_tests.csv) · [Exact reference locations](../data/census_v6/explicit_reference_locations.csv) · [Original document authentication](../data/census_v6/document_authentication.csv)','',
      '## Shared-production recommendations','',
      '1. **Joint regional evidence packet:** Use canonical IDs for the Nigeria visit, Governors Forum and Dakar workshop, with source-specific dates, roles and approved facts. Retain distinct UNOWAS and UNOCA analysis and Council products. This builds on explicit source referral and briefing reuse already observed.','2. **Cyprus and Lebanon reference controls:** Maintain a common source catalogue and cross-reference/version checks rather than merging good-offices, peacekeeping or resolution-specific reports. Test whether existing referrals avoid duplicate evidence requests; actual drafting effort is not measured here.','3. **Time-stamped report-to-briefing updates:** Keep shared factual inputs, their original cutoff and subsequent amendments distinct. Afghanistan returnee totals changed between reporting dates; a later briefing must not inherit a stale total merely for consistency.','4. **Course administration, not inferred delivery:** Link stable course/cohort IDs to existing ITS/LCM systems, with advertised, opened, completed and certified statuses separated. Related topics, shared articles and equal headcounts are not grounds for merging specialist instruction.','',
      '## Quality controls and limits','',
      '**Nigeria date discrepancy:** S/2025/187 paragraph 49 records 28-31 January; S/2025/342 paragraph 61 records 27-31 January. Both ranges remain attached to one identity. The reason for the different start dates is not established.','',
      '**Source access:** Two press-site responses were client challenges despite successful HTTP retrieval; they are not article bodies. Original transcripts take precedence over inconsistent press metadata. Low-text/scanned annexes are listed and not certified by text extraction. Original PDF bytes were SHA-256 checked and re-extracted; structured offline checks alone do not repeat this authentication.','',
      '**Preserved:** All frozen pre-V6 source tables, mandated products, parent/mission rankings and 20/32 previous retrospective output-category support. **Not established:** a complete operational activity denominator, cross-course unique people, duplicate paid services or incremental net savings.','',
      'Reproduce from the retained source artifact: `python3 scripts/audit_census_v6.py --write`. Validate committed relationships and hashes offline: `python3 scripts/audit_census_v6.py --check`. The full repository Python/R acceptance suite remains applicable. [Summary](../data/census_v6/audit_summary.json) · [Quality exceptions](../data/census_v6/quality_exceptions.csv) · [Frozen inputs](../data/census_v6/frozen_input_manifest.csv)','']
    (ROOT/'docs/census_2025_2026_v6_audit.md').write_text('\n'.join(report),encoding='utf-8')
    # Hash only release outputs; raw sources have their own authenticated manifest.
    generated=sorted(p for p in OUT.glob('*.csv'))+[OUT/'audit_summary.json',OUT/'nonadditive_programme_and_baseline_controls.json',ROOT/'docs/census_2025_2026_v6_audit.md']
    write_json(OUT/'release_manifest.json',dict(review_decisions_sha256=sha(OUT/'review_decisions.json'),files={str(p.relative_to(ROOT)):sha(p) for p in generated},raw_source_authentication='performed during --write; offline checks verify versioned receipts not remote originals'))

def check():
    d=js(OUT/'review_decisions.json');m=js(OUT/'release_manifest.json');s=js(OUT/'audit_summary.json')
    ensure(sha(OUT/'review_decisions.json')==m['review_decisions_sha256'],'Review decisions changed without rebuilding')
    for path,digest in m['files'].items():ensure(sha(ROOT/path)==digest,'Release output changed: '+path)
    for r in read('data/census_v6/frozen_input_manifest.csv'):ensure(sha(ROOT/r['path'])==r['sha256'],'Frozen input changed: '+r['path'])
    ids=read('data/census_v6/canonical_identity_map.csv');obs=read('data/census_v6/observation_lineage.csv');reg=read('data/census_v6/canonical_evidence_register.csv')
    ensure(len(ids)==len({x['local_id'] for x in ids})==130,'Local ID loss or collision')
    ensure(len(reg)==len({r['canonical_id'] for r in reg})==123,'Canonical ID collision')
    ensure(len(obs)==len({r['observation_id'] for r in obs})==371,'Observation loss or duplication')
    imap={r['local_id']:r['canonical_id'] for r in ids}
    ensure(all(imap[r['local_id']]==r['canonical_id'] for r in obs),'Broken observation-to-canonical bridge')
    for c in d['negative_controls']:ensure(imap[c['left']]!=imap[c['right']],'Protected distinct identities merged')
    courses=read('data/census_v6/course_delivery_verification.csv')
    ensure(len(courses)==8 and all(not c['completed_participants'] for c in courses),'Invented scheduled-course completion')
    ensure(sum(c['verification_status']=='future_schedule_not_yet_due' for c in courses)==5,'Future-course control failed')
    ensure(s['report_pair_classes']=={'explicit_cross_mandate_reference':6,'previous_reporting_period_reference':2,'no_explicit_pair_reference_in_extracted_text':6},'Report reference verdicts changed')
    ensure(s['authenticated_pdfs']==40 and s['unretrieved_transcripts']==7,'Document coverage changed')
    ensure(s['safeguards']==d['safeguards'] and d['safeguards']['incremental_net_savings']=='not_estimated','Financial safeguards changed')
    print(json.dumps(dict(status='V6 bounded identity delivery and reuse gates passed',**s),indent=2,sort_keys=True))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true');parser.add_argument('--check',action='store_true');args=parser.parse_args()
    if args.write:build()
    check()
