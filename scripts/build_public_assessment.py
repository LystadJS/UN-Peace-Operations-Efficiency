#!/usr/bin/env python3
"""Reproduce the bounded public assessment; never promote operational gates."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'data/public_assessment/'
CASES = ('C01', 'C02', 'C03')
DISPOSITIONS = ('SUPPORTED_CONCERN', 'CONDITIONAL_OPPORTUNITY',
                'UNRESOLVED_QUESTION', 'RETAIN_CURRENT_PROCESS')
MONEY = {'PUBLISHED_BUDGET', 'PROPOSAL_ESTIMATE', 'CONDITIONAL_SCENARIO'}
OUT = PREFIX + 'portfolio.json'
DOC = 'docs/public_assessment_brief.md'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local(root, name):
    require(isinstance(name, str) and bool(name) and '\\' not in name,
            'Invalid source path')
    p = PurePosixPath(name)
    require(not p.is_absolute() and all(v not in ('', '.', '..') for v in name.split('/')),
            'Unsafe source path: ' + name)
    require(not any(v.lower() in {'private', 'restricted', 'internal', '.git', '.aws', '.codex', '.agents'}
                    for v in p.parts), 'Restricted source path: ' + name)
    target = root / name
    require(target.is_file() and not target.is_symlink() and
            target.resolve().is_relative_to(root.resolve()), 'Missing/unsafe source: ' + name)
    return target


def read(root, path):
    return json.loads(local(root, path).read_text())


def text(value, label):
    require(isinstance(value, str) and bool(value.strip()), 'Missing ' + label)


def texts(value, label):
    require(isinstance(value, list) and bool(value), 'Missing ' + label)
    for item in value:
        text(item, label)


def build(root=ROOT):
    root = Path(root)
    scope_path = PREFIX + 'scope.json'
    scope = read(root, scope_path)
    require(type(scope.get('schema_version')) is int and scope['schema_version'] == 1,
            'Invalid scope schema')
    require(scope.get('priority_case_ids') == list(CASES) and scope.get('parent_portfolio_count') == 14,
            'Exact three-case scope and fourteen-case parent denominator required')
    require(scope.get('disposition_vocabulary') == list(DISPOSITIONS), 'Wrong public disposition vocabulary')
    require(scope.get('operational_validation_optional') is True and
            scope.get('savings_before_financial_validation_forbidden') is True,
            'Public/operational boundary changed')
    for key in ('assessment_id', 'as_of', 'primary_end_state'):
        text(scope.get(key), key)
    criteria = scope.get('completion_criteria')
    require(isinstance(criteria, list) and criteria, 'Completion rubric required')
    ids = [row.get('id') for row in criteria]
    require(len(ids) == len(set(ids)) and set(ids) == {f'PA{i:02}' for i in range(1, 10)},
            'Nine explicit completion criteria required')
    for row in criteria:
        text(row.get('criterion'), 'criterion')
    exclusions = scope.get('scope_exclusions')
    require(isinstance(exclusions, list) and {x.get('case_id') for x in exclusions} ==
            {f'C{i:02}' for i in range(4, 15)} and len(exclusions) == 11,
            'Eleven excluded parent cases must remain visible')
    for row in exclusions:
        for key in ('rationale', 'reopening_trigger'):
            text(row.get(key), 'exclusion ' + key)
    required_paths = [scope_path] + [PREFIX + case + '.json' for case in CASES]
    source_hashes = {path: sha(local(root, path)) for path in required_paths}
    observed = set()
    question_texts = set()
    summaries = []
    overall = Counter({key: 0 for key in DISPOSITIONS})
    for case in CASES:
        path = PREFIX + case + '.json'
        value = read(root, path)
        require(type(value.get('schema_version')) is int and value['schema_version'] == 1 and
                value.get('case_id') == case and value.get('as_of') == scope['as_of'],
                'Case identity/schema/cutoff mismatch: ' + case)
        require(value.get('assessment_status') == 'PUBLIC_REVIEW_COMPLETE_WITH_LIMITATIONS' and
                value.get('operational_validation') == 'NOT_PERFORMED' and
                'recognized_benefit' in value and value['recognized_benefit'] is None,
                'Public review cannot claim operational validation or recognized benefits: ' + case)
        text(value.get('scope'), 'case scope')
        synthesis = value.get('case_synthesis')
        require(isinstance(synthesis, dict) and synthesis.get('mixed_question_dispositions_preserved') is True
                and synthesis.get('not_an_f03_advancement') is True, 'Qualified case synthesis required')
        for key in ('overall_judgment', 'recommended_decision'):
            text(synthesis.get(key), 'case synthesis ' + key)
        roles = value.get('proposed_responsible_roles')
        require(isinstance(roles, list) and roles, 'Proposed responsible roles required')
        for role in roles:
            text(role.get('role'), 'proposed role')
            text(role.get('purpose'), 'role purpose')
            require(role.get('acceptance_status') == 'NOT_CONFIRMED', 'Proposed role is not accepted ownership')
        questions = value.get('questions')
        require(isinstance(questions, list) and questions, 'Missing questions: ' + case)
        counts = Counter({key: 0 for key in DISPOSITIONS})
        for q in questions:
            ident = q.get('question_id')
            text(ident, 'question ID')
            require(ident.startswith(case + '-') and ident not in observed, 'Duplicate/wrong question ID')
            observed.add(ident)
            for key in ('question', 'answer', 'interpretation', 'next_action', 'reopen_trigger'):
                text(q.get(key), key)
            normalized = ' '.join(q['question'].lower().split())
            require(normalized not in question_texts, 'Duplicate question text')
            question_texts.add(normalized)
            for key in ('alternative_explanations', 'limits'):
                texts(q.get(key), key)
            require(q.get('disposition') in DISPOSITIONS, 'Wrong public disposition; F03 is separate')
            counts[q['disposition']] += 1
            receipts = q.get('evidence')
            require(isinstance(receipts, list) and receipts, 'Evidence receipts required')
            for receipt in receipts:
                target = local(root, receipt.get('path'))
                text(receipt.get('locator'), 'evidence locator')
                require(receipt.get('sha256') == sha(target), 'Stale evidence hash: ' + receipt['path'])
                source_hashes[receipt['path']] = sha(target)
        financial = value.get('financial_observations')
        require(isinstance(financial, list), 'Financial observations must be explicitly enumerated')
        for observation in financial:
            amount = observation.get('amount')
            require(type(amount) in (int, float) and math.isfinite(amount), 'Nonfinite/invalid monetary amount')
            require(observation.get('classification') in MONEY, 'Unclassified money or unsupported savings')
            for key in ('currency', 'period', 'source_locator', 'interpretation'):
                text(observation.get(key), 'financial ' + key)
            target = local(root, observation.get('source_path'))
            source_hashes[observation['source_path']] = sha(target)
        parent_path = f'data/cases/{case}.json'
        parent = read(root, parent_path)
        require(parent.get('candidate_state') == 'SCREENING_CANDIDATE' and
                parent.get('financial_validation') == 'NOT_PERFORMED', 'Historical F03 boundary changed')
        source_hashes[parent_path] = sha(local(root, parent_path))
        overall.update(counts)
        summaries.append({'case_id': case, 'source_path': path, 'scope': value['scope'],
                          'assessment_status': value['assessment_status'],
                          'question_count': len(questions), 'disposition_counts': dict(counts),
                          'questions': questions, 'financial_observations': financial,
                          'case_synthesis': synthesis, 'proposed_responsible_roles': roles,
                          'historical_parent_f03_state': parent['candidate_state']})
    ledger_path = 'data/portfolio/verified_benefit_ledger.json'
    ledger = read(root, ledger_path)
    rec = ledger.get('reconciliation', {})
    require(ledger.get('entries') == [] and rec.get('recognized_records') == 0 and
            rec.get('headline_realized_savings_usd') is None and rec.get('cross_class_total') is None and
            rec.get('class_totals_usd') and all(v is None for v in rec['class_totals_usd'].values()),
            'Unknown benefit ledger must remain unestimated')
    source_hashes[ledger_path] = sha(local(root, ledger_path))
    gates_path = 'data/adjudications/execution_gates.json'
    gates = read(root, gates_path)
    require(gates.get('actual_operational_audits_completed') == 0 and
            all(row.get('substantive_audit_completed') is False and
                row.get('execution_status') == 'BLOCKED_NOT_EXECUTED'
                for row in gates.get('records', [])) and bool(gates.get('records')),
            'Operational facts changed; public assessment cannot reset them to zero')
    source_hashes[gates_path] = sha(local(root, gates_path))
    review_path = PREFIX + 'peer_review.json'
    review_present = (root / review_path).exists()
    review_pass = False
    review_status = 'NOT_OBTAINED'
    rubric = {ident: 'NOT_INDEPENDENTLY_REVIEWED' for ident in ids}
    if review_present:
        review = read(root, review_path)
        require(review.get('schema_version') == 1 and review.get('reviewer_agent') == 'priority_access' and
                review.get('review_type') == 'AGENT_REVIEW_NOT_INSTITUTIONAL', 'Independent review identity required')
        require(review.get('reviewed_sources') == {p: source_hashes[p] for p in required_paths},
                'Independent review source mismatch')
        require(review.get('status') in ('PASS', 'CHANGES_REQUIRED'), 'Invalid review status')
        review_status = review['status']
        checks = review.get('checks')
        require(isinstance(checks, list) and len({x.get('id') for x in checks}) == len(checks),
                'Invalid/duplicate peer checks')
        by_id = {x['id']: x for x in checks}
        require(set(ids).issubset(by_id), 'Review must cover every explicit completion criterion')
        for check in checks:
            require(check.get('status') in ('PASS', 'FAIL', 'CHANGES_REQUIRED'), 'Invalid criterion status')
            text(check.get('rationale'), 'review rationale')
        texts(review.get('limitations'), 'review limitations')
        rubric = {ident: by_id[ident]['status'] for ident in ids}
        review_pass = review['status'] == 'PASS' and all(x['status'] == 'PASS' for x in checks)
        require(review['status'] != 'PASS' or review_pass, 'Review PASS contradicts failed checks')
        source_hashes[review_path] = sha(local(root, review_path))
    return {'schema_version': 1, 'assessment_id': scope['assessment_id'], 'as_of': scope['as_of'],
            'primary_end_state': scope['primary_end_state'], 'detailed_case_count': 3,
            'parent_portfolio_count': 14, 'scope_exclusions': exclusions,
            'public_question_count': len(observed), 'disposition_counts': dict(overall),
            'disposition_namespace': 'PUBLIC_ASSESSMENT_QUESTION; RETAIN_CURRENT_PROCESS does not change F03 state',
            'cases': summaries, 'completion_rubric': rubric,
            'public_assessment_complete': review_pass,
            'public_assessment_status': 'COMPLETE_WITH_LIMITATIONS' if review_pass else 'AWAITING_INDEPENDENT_ACCEPTANCE',
            'primary_public_assessment_status': 'COMPLETE_WITH_LIMITATIONS' if review_pass else 'AWAITING_INDEPENDENT_ACCEPTANCE',
            'peer_review_status': review_status,
            'independent_review_present': review_present,
            'completion_basis': 'Validated bounded inputs plus independent PA01–PA09 review; agent review is not UN institutional approval.',
            'operational_validation_optional': True, 'operational_validations_completed': 0,
            'recognized_benefit': None, 'monetary_headline': None,
            'monetary_aggregation': 'PROHIBITED; observations retain separate periods, scopes and classifications',
            'source_sha256': dict(sorted(source_hashes.items()))}


def render(value):
    lines = ['# Public efficiency assessment', '',
             f"**{value['public_assessment_status']}** — three detailed public assessments within fourteen retained screening cases, as of {value['as_of']}.", '',
             value['primary_end_state'], '',
             'Public question dispositions are separate from F03 candidate states. Operational validations remain zero; financial benefits remain unestimated. Monetary observations are source budgets, proposals or conditional scenarios and have no aggregate headline.', '',
             '| Case | Public judgment | Questions: concern / opportunity / unresolved / retain |',
             '| --- | --- | --- |']
    for case in value['cases']:
        counts = case['disposition_counts']
        lines.append(f"| [{case['case_id']}](../{case['source_path']}) | {case['case_synthesis']['overall_judgment']} | " +
                     ' / '.join(str(counts[x]) for x in DISPOSITIONS) + ' |')
    lines.extend(['', f"The {value['public_question_count']} question dispositions total " +
                  ', '.join(f"{value['disposition_counts'][key]} {key.lower().replace('_', ' ')}" for key in DISPOSITIONS) + '.', '',
                  'Completion requires explicit PA01–PA09 rubric acceptance and a hash-bound independent agent review. This is acceptance of a bounded public research product, including unresolved answers with stated limits. It does not require optional operational access or imply institutional approval, universal reform compliance or that every source was fully authenticated.', ''])
    for case in value['cases']:
        q = case['questions'][0]
        decisive = list(dict.fromkeys(item['limits'][0] for item in case['questions']))[:2]
        roles = '; '.join(role['role'] for role in case['proposed_responsible_roles'])
        lines.extend([f"## {case['case_id']}", '', 'Evidence basis: ' + q['interpretation'], '',
                      'Decisive gaps: ' + ' '.join(decisive), '',
                      'Next decision: ' + case['case_synthesis']['recommended_decision'], '',
                      'Proposed responsible roles: ' + roles + '. Acceptance is not confirmed; no dispatch or collection is implied.', '',
                      f"[Full question findings, source facts, mechanisms and reopening triggers](public_assessment/{case['case_id']}.md) · [Versioned evidence receipts](../{case['source_path']}).", ''])
    lines.extend(['Published monetary amounts retain their individual fund/client perimeter, period and adoption/proposal/scenario classification in the case records. Embedded proposal changes and their components are nonadditive; no default sum or monetary opportunity headline is produced. Nothing in this brief recognizes financial benefits or advances the historical F03 parents from screening.', '',
                  'The other eleven cases retain screening coverage only. Their individual proposed responsible roles, next decisions, exclusion rationales and reopening triggers are recorded in the [scope and triage register](../data/public_assessment/scope.json). No finding of resolution, current waste or absence of waste follows from exclusion.', '',
                  'See the [independent review](../data/public_assessment/peer_review.json) and [machine-readable assessment with every question and source hash](../data/public_assessment/portfolio.json).', ''])
    return '\n'.join(lines)


def outputs(root=ROOT):
    value = build(root)
    return {OUT: json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n', DOC: render(value)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--write', action='store_true')
    mode.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for path, content in outputs().items():
        if args.write:
            (ROOT / path).parent.mkdir(parents=True, exist_ok=True)
            (ROOT / path).write_text(content)
        else:
            require((ROOT / path).is_file() and (ROOT / path).read_text() == content, 'Stale output: ' + path)
    print('PASS: bounded public assessment; F03 and unestimated benefit boundary preserved')


if __name__ == '__main__':
    main()
