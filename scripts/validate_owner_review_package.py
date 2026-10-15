#!/usr/bin/env python3
"""Validate a consolidated public owner-review package; never activate a trial.

Default is read-only. --export adds a readable register and validation receipt.
Uses Python's standard library; no network, source re-extraction or rescoring.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/owner_review'
EXPECTED_REFERENCE = '4059dfffbb370c131a27db760487eb425ae302d530c3509eaf3814e70bce2b65'

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))

def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export', action='store_true')
    args = parser.parse_args()
    checks = []
    def check(condition, name):
        if not condition:
            raise AssertionError(name)
        checks.append(name)
    c = read_json(DATA / 'package_contract.json')
    for rel, sha in c['pinned_inputs'].items():
        check(digest(ROOT / rel) == sha, 'pinned input unchanged: ' + rel)
    pointer = read_json(ROOT / 'data/current_research_reference.json')
    adoption = read_json(ROOT / pointer['adoption_record_path'])
    ref = read_json(ROOT / pointer['reference_path'])
    check(pointer['reference_version'] == adoption['version'] == c['reference_version'] == '13.0', 'adopted version')
    check(digest(ROOT / pointer['reference_path']) == pointer['reference_sha256'] == EXPECTED_REFERENCE, 'adopted payload hash')
    check(adoption['status'] == 'adopted_for_research_only' and not adoption['authority']['live_use_authorized'], 'research-only authority')
    refmap = {r['observation_id']: r for r in ref}
    check(len(refmap) == len(ref) == 61, 'unchanged 61-row reference inventory')
    check(collections.Counter(r['case_id'] for r in ref) == {'SP08P1':20, 'SP09P1':41}, 'case denominators')
    for amendment in adoption['amendment_dispositions']:
        check(refmap[amendment['observation_id']]['source_assertion'] == amendment['adopted_assertion'], 'adopted assertion retained: ' + amendment['amendment_id'])
    first = read_csv(ROOT / pointer['historical_first_pass_path'])
    check(sum(r['first_pass_disposition'] == 'supported' for r in first) == 59, 'historical 59 supported unchanged')
    check(sum(bool(r['amendment_id']) for r in first) == 2 and len(first) == 61, 'historical two amendment records retained')
    rechecks = read_csv(ROOT / 'data/census_v13/affected_recheck.csv')
    check(len(rechecks) == 2, 'separate two-row post-amendment recheck')
    gates = read_json(ROOT / 'data/census_v10/activation_status.json')
    for case in ('SP08P1','SP09P1'):
        check(gates[case]['status'] == pointer['live_use_gates'][case] == c['live_use_gates'][case] == 'BLOCKED_FOR_LIVE_USE', 'closed gate: ' + case)
        check(not gates[case]['institutional_authority_verified'] and not gates[case]['live_execution_authorized'], 'no authority: ' + case)
    templates = sorted((ROOT / 'data/census_v10/templates').glob('*.csv'))
    check(len(templates) == 9 and all(not read_csv(p) for p in templates), 'nine live instruments empty')
    rows = read_csv(DATA / 'evidence_gap_register.csv')
    expected = {'GW01'} | {f'G08-0{i}' for i in range(1,5)} | {f'G09-0{i}' for i in range(1,6)} | {f'GA0{i}' for i in range(1,5)} | {'GF01','GF02'}
    check(len(rows) == len(expected) == 16 and {r['gap_id'] for r in rows} == expected, 'unique scoped gap IDs')
    check(collections.Counter(r['decision_stage'] for r in rows) == {'OWNER_REVIEW':10,'BEFORE_ANY_LIVE_SHADOW':4,'AFTER_SHADOW_SEPARATE_AUTHORIZATION':1,'AFTER_SUBSTITUTION_SEPARATE_AUTHORIZATION':1}, 'review phases not a ranking')
    for r in rows:
        gid = r['gap_id']
        check(r['request_status'] == 'NOT_SENT' and r['owner_response'] == 'NOT_OBTAINED', 'uncontacted status: '+gid)
        check(set(r['case_ids'].split(';')) <= set(gates), 'valid case scope: '+gid)
        check(all(r[k].strip() for k in ('confirmed_basis','proposed_additional_control','unresolved_question','minimum_evidence','closure_rule','consequence_while_open')), 'decision-complete row: '+gid)
        for oid in filter(None,r['observation_ids'].split(';')):
            check(oid in refmap and refmap[oid]['case_id'] in r['case_ids'].split(';'), 'reference bridge: '+gid+'/'+oid)
        check(all(p in c['pinned_inputs'] for p in r['source_paths'].split(';')), 'pinned evidence paths: '+gid)
    ranks = {r['candidate_id']:r['revised_public_rank'] for r in read_csv(ROOT / 'data/acabq_2027_ranked_consolidation.csv')}
    check(len(ranks) == 14 and {k:ranks[k] for k in ('C16','C09','C02','C05')} == {'C16':'1','C09':'5','C02':'6','C05':'7'}, 'frozen 14-parent ranking retained')
    check(c['owner_reviews'] == c['owner_approvals'] == c['live_trials'] == c['live_staff_records'] == 0, 'no fabricated execution')
    check(c['new_full_corpus_score'] == 'not_run' and c['staff_time_saved'] == c['cash_savings'] == 'not_estimated', 'no rescore or savings estimate')
    memo = (ROOT / 'docs/consolidated_owner_review_decision_memo.md').read_text(encoding='utf-8')
    check(all(s in memo for s in ('13.0','V10','not transmitted','59 supported unchanged','BLOCKED_FOR_LIVE_USE','16 proven defects')), 'memo decision/status boundaries')
    check('three custody exchanges' not in memo and all('three custody exchanges' not in row['confirmed_basis'] for row in rows), 'custody count remains people not exchange events')
    check('GF01' in memo and 'GF02' in memo and 'later gates' in memo, 'cost requests deferred')
    # Resolve pinned source links and newly authored relative links locally.
    for target in re.findall(r'\]\(([^)]+)\)',memo):
        if target.startswith('https://github.com/'):
            base=f"https://github.com/LystadJS/UN-Peace-Operations-Efficiency/blob/{c['baseline_commit']}/"
            check(target.startswith(base) and (ROOT/target[len(base):]).exists(), 'pinned memo link: '+target.rsplit('/',1)[-1])
        elif target != 'consolidated_owner_review_gaps.md':
            check((ROOT/'docs'/target).resolve().exists(), 'relative memo link: '+target)
    if args.export:
        base=f"https://github.com/LystadJS/UN-Peace-Operations-Efficiency/blob/{c['baseline_commit']}/"
        out=['# Consolidated owner-review evidence-gap register','',
             '**15 October 2026 | Research reference 13.0 | Existing V10 protocol**','',
             '**16 review questions, not 16 proven workflow defects.** Confirmed basis is retained research; proposed controls and closure rules are recommendations. All requests are NOT_SENT; all owner responses are NOT_OBTAINED. Roles are potential evidence holders, not appointments. Both live-use gates remain closed.','',
             'Start with GW01, then the relevant case rows. GA01–GA04 apply before a separately authorized live shadow. GF01–GF02 are later substitution/financial gates. A source-detail resolution does not prove an internal workflow gap.','']
        for r in rows:
            out += [f"## {r['gap_id']} | {r['topic']}",'',f"**Case:** {r['case_ids']} | **Stage:** {r['decision_stage']} | **Status:** {r['status']}",'']
            for key,label in [('confirmed_basis','Confirmed basis'),('proposed_additional_control','Proposed control'),('unresolved_question','Unresolved question'),('minimum_evidence','Minimum evidence'),('evidence_holder_role_not_assignment','Potential evidence holder'),('closure_rule','Closure rule'),('consequence_while_open','While open')]:
                out += [f"**{label}:** {r[key]}",'']
            out += [f"**Reference observations:** {r['observation_ids'] or 'Protocol/authorization question; no claim-level inference.'}",'',
                    '**Sources:** '+'; '.join(f'[{p}]({base}{p})' for p in r['source_paths'].split(';')),'']
        (ROOT/'docs/consolidated_owner_review_gaps.md').write_text('\n'.join(out),encoding='utf-8')
    report_path=ROOT/'docs/consolidated_owner_review_gaps.md'
    check(report_path.exists() and all(('## '+r['gap_id']+' |') in report_path.read_text(encoding='utf-8') for r in rows), 'readable register completeness')
    result={'package_id':c['package_id'],'status':'PASS_package_integrity_not_owner_review_or_live_authorization',
            'checks_passed':len(checks),'pinned_inputs_verified':len(c['pinned_inputs']),'gap_questions':16,
            'stage_counts':dict(collections.Counter(r['decision_stage'] for r in rows)),
            'reference_version':'13.0','reference_sha256':EXPECTED_REFERENCE,'historical_first_pass':{'supported':59,'amendment_holds':2},
            'new_scoring':'not_run','new_owner_evidence':'none','requests_sent':0,'live_gate_changes':0,'course_checks_run':0,
            'limitations':'Checks validate source identity, linkage and preservation. They do not independently verify substantive source claims, owner authority, an internal workflow gap, operational benefit or savings.',
            'output_hashes':{str(p.relative_to(ROOT)):digest(p) for p in [ROOT/'docs/consolidated_owner_review_decision_memo.md',report_path,DATA/'evidence_gap_register.csv',DATA/'package_contract.json']}}
    if args.export:
        (DATA/'validation_receipt.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__ == '__main__':
    main()
