#!/usr/bin/env python3
"""Synthetic lineage controls; no repository operational script is executed."""
import csv
import io
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import build_repository_lineage as line


class LineageTests(unittest.TestCase):
    def test_documentation_is_not_production(self):
        edges,_=line.extract('docs/readme.md','[dataset](../data/a.csv)',{'data/a.csv'})
        self.assertIn('DOCUMENTS',{x[2] for x in edges})
        self.assertNotIn('WRITES',{x[2] for x in edges})

    def test_resolved_writer_and_reader(self):
        code="from pathlib import Path\nROOT=Path(__file__).resolve().parents[1]\n(ROOT/'data/a.csv').read_text()\n(ROOT/'data/b.csv').write_text('x')\n"
        edges,_=line.extract('scripts/sample.py',code,{'data/a.csv','data/b.csv'})
        self.assertIn(('data/a.csv','READS'),{(x[1],x[2]) for x in edges})
        self.assertIn(('data/b.csv','WRITES'),{(x[1],x[2]) for x in edges})

    def test_dynamic_writer_is_unresolved(self):
        edges,gaps=line.extract('scripts/a.py',"(root/name).write_text('x')",{'data/a.csv'})
        self.assertFalse(any(x[2]=='WRITES' for x in edges))
        self.assertTrue(gaps)

    def test_assertion_validation_distinct_from_read(self):
        code="from pathlib import Path\nROOT=Path(__file__).resolve().parents[1]\nassert (ROOT/'data/a.csv').read_text() == 'x'\n(ROOT/'data/b.csv').read_text()\n"
        edges,_=line.extract('scripts/a.py',code,{'data/a.csv','data/b.csv'})
        validated={x[1] for x in edges if x[2]=='VALIDATES'}
        self.assertEqual(validated,{'data/a.csv'})

    def test_hash_manifest_is_preservation_not_write(self):
        source=json.dumps({'data/a.csv':'a'*64})
        edges,_=line.extract('data/manifest.json',source,{'data/a.csv'})
        self.assertIn('PRESERVES',{x[2] for x in edges})
        self.assertNotIn('WRITES',{x[2] for x in edges})

    def test_workflow_invokes_exact_command(self):
        edges,_=line.extract('.github/workflows/a.yml','run: python scripts/a.py',{'scripts/a.py'})
        self.assertIn('INVOKES',{x[2] for x in edges})

    def test_workflow_cwd_override_not_assumed(self):
        edges,gaps=line.extract('.github/workflows/a.yml','working-directory: work\nrun: python scripts/a.py',{'scripts/a.py'})
        self.assertFalse(any(x[2]=='INVOKES' for x in edges))
        self.assertTrue(gaps)

    def test_local_import(self):
        edges,_=line.extract('scripts/a.py','import helper',{'scripts/helper.py'})
        self.assertEqual(edges[0][2],'IMPORTS')

    def test_graph_scope_and_evidence(self):
        output=line.build()
        nodes=list(csv.DictReader(io.StringIO(output[line.NODE_OUT].decode())))
        edges=list(csv.DictReader(io.StringIO(output[line.EDGE_OUT].decode())))
        scope=json.loads((line.ROOT/line.SCOPE).read_text())
        population={x['path'] for x in scope['files']}
        self.assertEqual(len(nodes),len(population))
        self.assertEqual({x['node_id'] for x in nodes},population)
        self.assertEqual(len({x['edge_id'] for x in edges}),len(edges))
        for e in edges:
            self.assertIn(e['source'],population)
            self.assertIn(e['target'],population)
            self.assertEqual(e['source'],e['evidence_file'])
            self.assertGreater(int(e['evidence_line']),0)


if __name__=='__main__': unittest.main()
