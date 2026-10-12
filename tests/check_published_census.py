#!/usr/bin/env python3
"""Offline HTML fixtures plus census release checks; no invented event totals."""
import csv
import importlib.util
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('census',ROOT/'scripts/expand_published_census.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Checks(unittest.TestCase):
 def html(self,meta='',text='UNOWAS and UNOCA jointly held a workshop on 26 February 2025 in Dakar.'):
  return ('<html><head>'+meta+'</head><main><h1>Test publication</h1><article><p>'+text+'</p></article></main></html>').encode()
 def test_publication_not_event(self):
  a,c=m.extract_article(self.html('<meta property="article:published_time" content="2025-04-02T12:00:00Z">','UNOCA held a training workshop on 17 October 2024; this later note summarizes it.'),'https://unoca.unmissions.org/en/news/a','UNOCA','2026-10-12')
  self.assertEqual(a['publication_date'],'2025-04-02');self.assertIn('17 October 2024',c[0]['explicit_event_date_mentions'])
  self.assertEqual(c[0]['event_id'],'not_assigned')
 def test_missing_date(self):
  a,c=m.extract_article(self.html(),'https://unoca.unmissions.org/en/news/a','UNOCA','2026-10-12')
  self.assertEqual(a['publication_date'],'');self.assertEqual(a['chronology_status'],'publication_date_unresolved')
 def test_future(self):
  a,c=m.extract_article(self.html('<meta name="date" content="2026-12-01">'),'https://unoca.unmissions.org/en/news/a','UNOCA','2026-10-12')
  self.assertEqual(a['chronology_status'],'after_cutoff');self.assertFalse(c)
 def test_conflict(self):
  a,c=m.extract_article(self.html('<meta name="date" content="2025-04-02"><time datetime="2025-04-03"></time>'),'https://unoca.unmissions.org/en/news/a','UNOCA','2026-10-12')
  self.assertEqual(a['publication_date_method'],'conflicting_publication_metadata')
 def test_participation_not_joint(self):
  a,c=m.extract_article(self.html('<meta name="date" content="2025-04-02">','UNRCCA hosted a meeting at which UNAMA participated in the discussion of regional peace.'),'https://unrcca.unmissions.org/en/news/a','UNRCCA','2026-10-12')
  self.assertEqual(c[0]['joint_language'],'false');self.assertEqual(c[0]['evidence_status'],'machine_located_paragraph_needs_event_identity_and_role_review')
 def test_scope(self):
  self.assertFalse(m.allowed('https://evil.test/en/news/a'));self.assertFalse(m.allowed('http://unoca.unmissions.org/en/news/a'))
  self.assertEqual(m.normal_url('https://unoca.unmissions.org/en/news/a/#x'),'https://unoca.unmissions.org/en/news/a')

def validate_outputs(folder):
 def read(name):
  p=folder/(name+'.csv')
  if not p.exists():return []
  with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
 s=json.loads((folder/'summary.json').read_text())
 frame=read('notice_frame');attempts=read('article_fetches');notices=read('notices');candidates=read('event_paragraph_candidates');coverage=read('coverage')
 assert s['asof']=='2026-10-12'
 assert len(frame)==s['frame_notices'] and len(attempts)==s['article_attempts']
 assert len(notices)==s['downloaded_notices'] and len(candidates)==s['candidate_paragraphs']
 assert len({r['notice_url'] for r in frame})==len(frame)
 assert len({r['url'] for r in attempts})==len(attempts)
 assert {r['url'] for r in attempts}=={r['notice_url'] for r in frame if r['selected_for_fetch']=='true'}
 assert {r['url'] for r in notices}=={r['url'] for r in attempts if r['status']=='downloaded'}
 ids={r['notice_id'] for r in notices}
 assert len(ids)==len(notices) and len({r['candidate_id'] for r in candidates})==len(candidates)
 assert all(r['notice_id'] in ids and r['event_id']=='not_assigned' and r['duplicate_payment']=='not_estimated' for r in candidates)
 assert all(r['event_census_status']=='notice_not_adjudicated_event' for r in notices)
 assert len(coverage)==6 and sum(int(r['frame_notices']) for r in coverage)==len(frame)
 assert sum(int(r['downloaded']) for r in coverage)==len(notices)
 assert all(r['event_population_denominator']=='unknown' and r['adjudicated_event_completeness']=='not_claimed' for r in coverage)
 assert s['duplicate_spending']=='not_estimated' and s['unknown_event_counts_not_zero'] is True
 reports=read('council_reports');meetings=read('council_meeting_variants');caps=read('council_fetches')
 assert len(reports)==s['council_reports'] and len(meetings)==s['council_meeting_variants']
 assert len({r['meeting_base_id'] for r in meetings})==s['distinct_council_meetings']
 assert len(caps)==4 and sum(r['status']=='fetched_index' for r in caps)==s['council_index_success']
 assert all(r['snapshot_asof']=='2026-10-12' for r in reports+meetings)
 assert all(r['date']<='2026-10-12' for r in meetings)
 assert all(r['indexed_date']<='2026-10-12' for r in reports)
 assert all((r['indexed_date'][:4]!=r['index_year'])==(r['date_year_mismatch']=='true') for r in reports)
 print('CENSUS V2 COUNTS AND NON-INFERENCE CONTROLS PASSED')
 print(json.dumps(s,indent=2))

if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='--outputs':validate_outputs(Path(sys.argv[2]))
 else:unittest.main()
