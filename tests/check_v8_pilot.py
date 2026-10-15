#!/usr/bin/env python3
"""Independent V8 assertions and deliberately corrupted development fixtures.

These are software/representation tests, not operational error rates or human
adjudication. No live UN drafts, staff-time records or restricted data are used.
"""
from __future__ import annotations
import argparse
import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pilot', ROOT/'scripts/build_v8_pilot.py')
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)
DATA = ROOT/'data/census_v8'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--sources', action='store_true', help='Also check sources with an independent PDF parser')
    args = ap.parse_args()
    d = json.loads((DATA/'pilot_design.json').read_text())
    views = {v['product_id']: v for v in json.loads((DATA/'packet_views.json').read_text())}
    outcomes = []
    def check(name, truth):
        if not truth:
            raise AssertionError(name)
        outcomes.append({'test':name, 'result':'PASS', 'type':'independent_invariant'})
    check('four retained office-specific products', set(views)=={'R1','B1','R2','B2'})
    check('source-qualified conflicting visit dates retained', all(views[k]['date_options']==['2025-01-27','2025-01-28'] and views[k]['date_conflict'] for k in ['R1','B1','R2']))
    check('June briefing not force-filled with three core event blocks', {o['component_id'] for o in views['B2']['observations']}=={'P05','P10'})
    check('April briefing has no later-report observation or April 8 planning event', all(o['source_id'] not in {'R2','B2'} and o['component_id']!='P07' for o in views['B1']['observations']))
    check('no report backfill of April withdrawal announcement', all(o['component_id']!='P05' for o in views['R1']['observations']))
    check('workshop publication retains existing distinct canonical identity', next(c for c in d['components'] if c['component_id']=='P04')['canonical_evidence_id']=='EV004')
    check('three core inputs have nine output appearances not twelve', sum(o['component_id'] in {'P01','P02','P03'} and o['source_id'] in views for o in d['observations'])==9)
    check('announcement remains an announcement in both briefings', all(o['values']['status']=='announced' for o in d['observations'] if o['component_id']=='P05'))
    check('two page-linked notice corroborations are not editorial-dependency claims', [e['kind'] for e in d['edges'] if e['from_source'].startswith('N')]==['same_event_corroboration_editorial_direction_unproven']*2)
    check('separate Forum duration and representative-attendance point retained', next(o for o in d['observations'] if o['source_id']=='N01' and o['component_id']=='P02')['values']['event_end']=='2025-01-31' and next(o for o in d['observations'] if o['source_id']=='R2' and o['component_id']=='P02')['values']['event_end']=='2025-01-29')
    check('prior-year context not redated from document year', all(o['values']['event_year']==2024 for o in d['observations'] if o['component_id']=='P08'))
    for k,v in views.items():
        pilot.validate_packet(d,v)
        outcomes.append({'test':k+' complete packet contract', 'result':'PASS', 'type':'positive_fixture'})
    def row(view, source, component):
        return next(o for o in view['observations'] if o['source_id']==source and o['component_id']==component)
    def reject(name, product, change):
        v = copy.deepcopy(views[product]); change(v)
        try:
            pilot.validate_packet(d,v)
        except (ValueError,KeyError):
            outcomes.append({'test':name, 'result':'REJECTED_AS_EXPECTED', 'type':'synthetic_corruption_fixture'})
        else:
            raise AssertionError('Unsafe mutation accepted: '+name)
    reject('silently normalize visit start date','R1',lambda v:row(v,'R1','P01')['values'].__setitem__('event_start','2025-01-27'))
    reject('hide known date discrepancy','R2',lambda v:v.__setitem__('date_conflict',False))
    reject('convert greater-than attendance to exact count','R1',lambda v:row(v,'R1','P03')['values'].__setitem__('attendance_comparator','='))
    reject('convert adopted workplan to implemented','R1',lambda v:row(v,'R1','P03')['values'].__setitem__('workplan_stage','implemented'))
    reject('convert withdrawal announcement to completed withdrawal','B2',lambda v:row(v,'B2','P05')['values'].__setitem__('status','completed'))
    reject('backfill later report into earlier briefing','B1',lambda v:v['observations'].append(copy.deepcopy(next(o for o in d['observations'] if o['source_id']=='R2' and o['component_id']=='P07'))))
    reject('turn publication into another course','R2',lambda v:row(v,'R2','P04')['values'].__setitem__('product_type','course'))
    reject('substitute Forum duration for representative attendance','R2',lambda v:row(v,'R2','P02')['values'].__setitem__('event_end','2025-01-31'))
    reject('transfer final product ownership','R2',lambda v:v.__setitem__('owner','UNOWAS'))
    reject('silently remove office-specific analysis','B2',lambda v:v.__setitem__('observations',[o for o in v['observations'] if o['component_id']!='P10']))
    reject('insert unsupported core event into June briefing','B2',lambda v:v['observations'].append(copy.deepcopy(next(o for o in d['observations'] if o['source_id']=='R2' and o['component_id']=='P01'))))
    reject('invent monetary saving','R1',lambda v:v.__setitem__('incremental_net_savings',100))
    reject('invent saved staff hours','R1',lambda v:v.__setitem__('staff_hours_saved',6))
    reject('promote Forum participant to sole organizer','R1',lambda v:row(v,'R1','P02')['values'].__setitem__('role','sole_organizer'))
    reject('redate prior-period activity','R2',lambda v:row(v,'R2','P08')['values'].__setitem__('event_start','2025-12-17'))
    reject('erase attributed earlier briefing reference','B2',lambda v:row(v,'B2','P05')['values'].__setitem__('explicit_reference',None))
    reject('assign CNMC function to generic regional role','R1',lambda v:row(v,'R1','P06')['values'].__setitem__('role','generic_regional_officer'))
    reject('fabricate joint final clearance','B1',lambda v:v.__setitem__('approval','joint_final_clearance_completed'))
    independent_sources = []
    if args.sources:
        import fitz
        for s in d['sources']:
            if not s['file'].endswith('.pdf'):
                continue
            path = DATA/s['file']
            with fitz.open(path) as doc:
                check(s['source_id']+' independent PDF count and symbol', len(doc)==s['pages'] and pilot.norm(s['title']) in pilot.norm(doc[0].get_text()))
                for o in d['observations']:
                    if o['source_id'] != s['source_id']:
                        continue
                    text=pilot.norm(' '.join(doc[p-1].get_text() for p in o['pages']))
                    check(o['observation_id']+' independent parser anchors', all(pilot.norm(a) in text for a in o['anchors']))
                independent_sources.append({'source_id':s['source_id'],'pages':len(doc),'sha256':pilot.sha(path)})
    result={'status':'PASS','positive_fixture_count':4,
            'synthetic_corruption_fixtures_rejected':18,
            'independent_assertions':sum(o['type']=='independent_invariant' for o in outcomes),
            'total_checks':len(outcomes),'independent_pdf_sources':independent_sources,
            'interpretation':'Constructed source/representation checks; no operational error rate, time saving, live clearance or net saving established.',
            'results':outcomes}
    if args.write:
        (DATA/'acceptance_receipt.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='results'},indent=2))


if __name__=='__main__':
    main()
