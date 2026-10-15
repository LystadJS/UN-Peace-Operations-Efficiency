#!/usr/bin/env python3
"""Narrow adoption checks and deliberate corruption controls; no new source review."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import adopt_v13_reference as a

class AdoptionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = a.outputs(a.ROOT)
        cls.rows = json.loads(cls.files[a.OUT+'research_reference.json'])
        cls.old = a.patch.read_json(a.ROOT, a.patch.CANDIDATE)
        cls.views = {p:cls.files[a.OUT+'views/'+p.replace(':','_')+'.md'].decode() for p in a.PRODUCTS}

    def bad_row(self, oid, change):
        rows = copy.deepcopy(self.rows)
        change(next(r for r in rows if r['observation_id']==oid))
        with self.assertRaises(ValueError):
            a.check_affected(rows,self.views)

    def test_exact_payload_identity(self):
        body = self.files[a.OUT+'research_reference.json']
        self.assertEqual(body,(a.ROOT/'data/census_v12/reference_preview.json').read_bytes())
        self.assertEqual(a.sha(body),'4059dfffbb370c131a27db760487eb425ae302d530c3509eaf3814e70bce2b65')

    def test_two_row_locality(self):
        changed = [x['observation_id'] for x,y in zip(self.old,self.rows) if x!=y]
        self.assertEqual(changed,['V9:CY028','V9:CY041'])
        self.assertEqual(len(self.rows),61)
        for old,new in zip(self.old,self.rows):
            for key in set(old)-{'source_assertion','qualified_values'}:
                self.assertEqual(old[key],new[key])
            for key,value in json.loads(old['qualified_values']).items():
                self.assertEqual(json.loads(new['qualified_values'])[key],value)

    def test_first_pass_not_rescored(self):
        import csv,io
        rows=list(csv.DictReader(io.StringIO(self.files[a.OUT+'reference_lineage.csv'].decode())))
        self.assertEqual(sum(r['first_pass_disposition']=='supported' for r in rows),59)
        self.assertEqual(sum(r['first_pass_disposition']=='amendment_requested_scoring_withheld' for r in rows),2)
        self.assertEqual(sum(r['current_disposition']=='post_amendment_affected_recheck_passed' for r in rows),2)
        self.assertEqual(sum(r['current_disposition']=='carried_forward_unchanged_not_reassessed' for r in rows),59)

    def test_affected_views_only(self):
        self.assertEqual(set(self.views),{'V9:G2','V9:G3'})
        self.assertEqual(self.views['V9:G2'].count('\n## V9:'),6)
        self.assertEqual(self.views['V9:G3'].count('\n## V9:'),8)
        self.assertEqual(sum(v.count('carried_forward_unchanged_not_reassessed') for v in self.views.values()),12)
        self.assertEqual(len(a.check_affected(self.rows,self.views)),2)

    def test_collapsed_custody_action_rejected(self):
        self.bad_row('V9:CY028',lambda r:r.update(source_assertion='Information exchanged in 202 instances and three people.'))

    def test_exact_amount_rejected(self):
        self.bad_row('V9:CY041',lambda r:r.update(source_assertion=r['source_assertion'].replace('more than EUR1.7','EUR1.7')))

    def test_strict_bound_loss_rejected(self):
        def mutate(row):
            v=json.loads(row['qualified_values']);v['lifetime_utilized_eur_comparator']='>='
            row['qualified_values']=json.dumps(v)
        self.bad_row('V9:CY041',mutate)

    def test_source_locator_loss_rejected(self):
        v=copy.deepcopy(self.views)
        r=next(r for r in self.rows if r['observation_id']=='V9:CY028')
        v['V9:G2']=v['V9:G2'].replace(r['source_sha256'],'REMOVED')
        with self.assertRaises(ValueError):a.check_affected(self.rows,v)

    def test_unaffected_view_addition_rejected(self):
        v=dict(self.views);v['V8:R1']='not requested'
        with self.assertRaises(ValueError):a.check_affected(self.rows,v)

    def test_inverse_returns_historical_rows(self):
        ops=a.patch.read_json(a.ROOT,'data/census_v12/reference_inverse.jsonpatch')
        self.assertEqual(a.patch.replay(self.rows,ops),self.old)

    def test_authority_separation(self):
        record=json.loads(self.files[a.OUT+'adoption_record.json'])
        self.assertEqual(record['status'],'adopted_for_research_only')
        self.assertEqual(record['authority']['request_timestamp_utc'],'2026-10-15T20:58:38Z')
        self.assertFalse(record['authority']['institutional_approval'])
        self.assertFalse(record['authority']['live_use_authorized'])
        self.assertEqual(record['live_use'],'BLOCKED_FOR_LIVE_USE')
        self.assertEqual(len(record['amendment_dispositions']),2)

    def test_live_activation_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);shutil.copytree(a.ROOT/'data/census_v10',root/'data/census_v10')
            p=root/'data/census_v10/protocol.json';data=json.loads(p.read_text())
            data['case_activation']['SP09P1']['additional_person_minute_ceiling']=30
            p.write_text(json.dumps(data))
            with self.assertRaises(ValueError):a.patch.closed_gates(root)

    def test_preserved_inputs_and_outputs(self):
        self.assertEqual(self.files,a.outputs(a.ROOT))
        for name,body in self.files.items():self.assertEqual((a.ROOT/name).read_bytes(),body)
        gates=json.loads(self.files[a.OUT+'closed_gate_receipt.json'])
        self.assertTrue(gates['research_reference_adopted'])
        self.assertFalse(gates['live_execution'])
        self.assertTrue(all(g['status']=='BLOCKED_FOR_LIVE_USE' for g in gates['live_gates'].values()))

if __name__=='__main__':unittest.main(verbosity=2)
