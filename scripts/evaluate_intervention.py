#!/usr/bin/env python3
"""Evaluate declared scenarios for research; never approve or recognize savings."""
import argparse
import copy
import datetime as dt
import json
import re
from decimal import Decimal, localcontext
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CRITERIA = ("evidence_readiness", "operational_importance", "reform_relevance", "feasibility", "measurement_value")
GUARDS = ("mandate", "safety", "readiness", "quality", "timeliness", "transition", "work_transfer", "evidence_authority")
FRAME = ("period_start", "period_end", "currency", "unit", "financial_status", "price_basis", "cost_view", "service_definition", "required_output")
ADJUSTMENTS = ("demand", "security_conditions", "geographic_coverage", "language_coverage", "quality", "surge_reserve", "mandate_change", "vacancies", "inflation", "exchange_rates")
ROLES = ("RETAINED_SOURCE", "RECEIVING_PROVIDER", "TRANSITION_IMPLEMENTATION", "ONGOING_COMPLIANCE", "RESIDUAL_LIABILITY", "OTHER_EXTERNAL")
BENEFITS = ("CAPACITY_GAIN", "RECOVERY", "COST_AVOIDANCE", "CONTROL_IMPROVEMENT")


def present(value):
    return isinstance(value, str) and bool(value.strip())


def number(value):
    # Reject floats, booleans, NaN, exponents and unbounded precision explicitly.
    if not isinstance(value, str) or not re.fullmatch(r"-?\d+(?:\.\d+)?", value) or len(value.replace("-", "").replace(".", "")) > 100:
        raise ValueError("amount must be a finite decimal string of at most 100 digits")
    return Decimal(value)


def decimal_text(value):
    return format(value, "f")


def valid_date(value):
    try:
        return dt.date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def scenario_cost(scenario, name):
    errors, pairs, external = [], {}, Decimal("0")
    if not isinstance(scenario, dict):
        return None, [], [name + ": scenario missing"]
    for field in FRAME:
        if not present(scenario.get(field)):
            errors.append(name + ": missing frame " + field)
    start, end = valid_date(scenario.get("period_start")), valid_date(scenario.get("period_end"))
    if start is None or end is None or start > end:
        errors.append(name + ": invalid period")
    if not isinstance(scenario.get("currency"), str) or not re.fullmatch(r"[A-Z]{3}", scenario["currency"]):
        errors.append(name + ": invalid currency")
    if scenario.get("unit") != "currency_units":
        errors.append(name + ": convert to currency_units with an upstream receipt")
    if scenario.get("cost_view") not in ("CASH", "RESOURCE_ACCRUAL"):
        errors.append(name + ": unsupported cost_view")
    entities = scenario.get("entity_scope")
    if not isinstance(entities, list) or not entities or not all(present(x) for x in entities) or len(entities) != len(set(x for x in entities if isinstance(x, str))):
        errors.append(name + ": invalid entity_scope")
        entities = []
    adjustments = scenario.get("adjustment_receipts")
    if not isinstance(adjustments, dict) or any(not present(adjustments.get(x)) for x in ADJUSTMENTS):
        errors.append(name + ": missing comparability adjustment review")
    coverage = scenario.get("coverage")
    if not isinstance(coverage, dict) or coverage.get("all_affected_entities") is not True or coverage.get("all_cost_components") is not True or not present(coverage.get("receipt")) or coverage.get("omitted_components") != []:
        errors.append(name + ": incomplete full-system cost coverage")
    rows = scenario.get("costs")
    if not isinstance(rows, list) or not rows or len(rows) > 10000:
        return None, [], errors + [name + ": costs require 1 through 10000 explicit rows"]
    seen_ids, seen_components, external_entities = set(), set(), set()
    for i, row in enumerate(rows):
        prefix = f"{name}.costs[{i}]"
        if not isinstance(row, dict):
            errors.append(prefix + ": row must be an object")
            continue
        for field in ("record_id", "cost_object_id", "component_id", "entity_id", "source_receipt"):
            if not present(row.get(field)):
                errors.append(prefix + ": missing " + field)
        ident = row.get("record_id")
        if present(ident):
            if ident in seen_ids:
                errors.append(prefix + ": duplicate record_id")
            seen_ids.add(ident)
        component = (row.get("cost_object_id"), row.get("component_id"))
        if all(present(x) for x in component):
            if component in seen_components:
                errors.append(prefix + ": duplicate economic component")
            seen_components.add(component)
        if row.get("entity_id") not in entities:
            errors.append(prefix + ": entity outside declared full-system scope")
        if row.get("role") not in ROLES:
            errors.append(prefix + ": invalid cost role")
        try:
            amount = number(row.get("amount"))
        except ValueError:
            errors.append(prefix + ": missing or invalid amount; unknown cannot become zero")
            continue
        boundary = row.get("economic_boundary")
        if boundary == "EXTERNAL_COST":
            if row.get("internal_pair_id") is not None:
                errors.append(prefix + ": external cost cannot also be an internal transfer")
            external += amount
            if present(row.get("entity_id")):
                external_entities.add(row["entity_id"])
        elif boundary in ("INTERNAL_CHARGE", "INTERNAL_RECOVERY"):
            pair = row.get("internal_pair_id")
            if not present(pair) or not present(row.get("transfer_id")):
                errors.append(prefix + ": transfer needs pair and shared transfer identity")
            else:
                pairs.setdefault(pair, []).append((boundary, amount, row.get("entity_id"), row["transfer_id"]))
            if boundary == "INTERNAL_CHARGE" and amount < 0 or boundary == "INTERNAL_RECOVERY" and amount > 0:
                errors.append(prefix + ": internal transfer sign mismatch")
        else:
            errors.append(prefix + ": unsupported economic boundary")
    if set(entities) - external_entities:
        errors.append(name + ": affected entity lacks external cost or evidenced zero row")
    for row in rows:
        if isinstance(row, dict) and row.get("included_in") is not None:
            if not present(row["included_in"]):
                errors.append(name + ": invalid parent reference")
            elif row["included_in"] in seen_ids:
                errors.append(name + ": parent and included child both counted")
    eliminated = []
    for pair, members in sorted(pairs.items()):
        if len(members) != 2 or {x[0] for x in members} != {"INTERNAL_CHARGE", "INTERNAL_RECOVERY"} or sum((x[1] for x in members), Decimal("0")) != 0 or members[0][2] == members[1][2] or members[0][3] != members[1][3]:
            errors.append(name + ": unmatched internal transfer " + pair)
        else:
            eliminated.append(pair)
    return (None if errors else external), eliminated, errors


def guard_status(rows):
    issues, status = [], "DECLARED_PASS_NOT_AUTHENTICATED"
    if not isinstance(rows, list):
        return "UNKNOWN", ["guard records missing"]
    index = {}
    for row in rows:
        if not isinstance(row, dict) or row.get("dimension") not in GUARDS:
            issues.append("invalid guard record")
            continue
        dimension = row["dimension"]
        if dimension in index:
            issues.append("duplicate guard " + dimension)
        index[dimension] = row
    failed = []
    for dimension in GUARDS:
        row = index.get(dimension, {})
        state = row.get("status")
        if state == "FAIL":
            failed.append(dimension)
        elif state == "PASS":
            if any(not present(row.get(x)) for x in ("receipt", "threshold_receipt", "owner_approval_receipt")):
                issues.append(dimension + ": PASS lacks evidence, prospective threshold or owner receipt")
        elif state == "NOT_APPLICABLE_WITH_JUSTIFICATION":
            if not present(row.get("justification")) or not present(row.get("owner_approval_receipt")):
                issues.append(dimension + ": applicability lacks justification or accepted review")
        else:
            issues.append(dimension + ": guard unknown")
    if failed:
        status = "BLOCKED"
        issues += [x + ": failed critical guard" for x in failed]
    elif issues:
        status = "UNKNOWN"
    return status, issues


def prioritize(inputs, guards):
    if guards != "DECLARED_PASS_NOT_AUTHENTICATED":
        return {"status": "BLOCKED" if guards == "BLOCKED" else "UNSCORABLE", "score": None, "issues": ["All critical safeguards require declared support before scoring."]}
    errors, values, weights = [], {}, {}
    if not isinstance(inputs, dict):
        inputs = {}
    if not present(inputs.get("weight_receipt")):
        errors.append("No reviewed weighting receipt")
    raw_weights, criteria = inputs.get("weights"), inputs.get("criteria")
    if not isinstance(raw_weights, dict) or set(raw_weights) != set(CRITERIA):
        errors.append("Weight vector missing or incomplete")
        raw_weights = {}
    if not isinstance(criteria, dict) or set(criteria) != set(CRITERIA):
        errors.append("Criterion vector missing or incomplete")
        criteria = {}
    for criterion in CRITERIA:
        row = criteria.get(criterion)
        try:
            if not isinstance(row, dict) or not present(row.get("receipt")):
                raise ValueError()
            value = number(row.get("value"))
            weight = number(raw_weights.get(criterion))
            if not 0 <= value <= 1 or not 0 <= weight <= 1:
                raise ValueError()
            values[criterion], weights[criterion] = value, weight
        except ValueError:
            errors.append(criterion + ": missing or invalid score, rubric receipt or weight")
    if len(weights) == len(CRITERIA) and sum(weights.values(), Decimal("0")) != 1:
        errors.append("Weights must sum exactly to one")
    if errors:
        return {"status": "UNSCORABLE", "score": None, "issues": errors}
    score = sum((values[x] * weights[x] for x in CRITERIA), Decimal("0"))
    return {"status": "SCORED_FOR_TRIAGE_ONLY", "score": decimal_text(score), "issues": [], "weight_receipt": inputs["weight_receipt"]}


def benefit_effects(rows):
    errors, seen, objects = [], set(), set()
    if not isinstance(rows, list):
        return {"status": "INVALID", "effects": [], "issues": ["benefit_effects must be a list"]}
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"effect[{i}] is not an object")
            continue
        for key in ("effect_id", "cost_object_id", "component_id", "benefit_pool_id", "period", "unit", "source_receipt"):
            if not present(row.get(key)):
                errors.append(f"effect[{i}]: missing {key}")
        identity = row.get("effect_id")
        if present(identity):
            if identity in seen:
                errors.append(f"effect[{i}]: duplicate effect")
            seen.add(identity)
        obj = tuple(row.get(x) for x in ("cost_object_id", "component_id", "period"))
        if all(present(x) for x in obj):
            if obj in objects:
                errors.append(f"effect[{i}]: overlapping economic component across benefit classes")
            objects.add(obj)
        if row.get("benefit_class") not in BENEFITS:
            errors.append(f"effect[{i}]: unsupported benefit class; savings recognition is excluded")
        if row.get("amount") is None:
            if not present(row.get("missing_reason")):
                errors.append(f"effect[{i}]: unknown amount requires reason")
        else:
            try:
                number(row.get("amount"))
            except ValueError:
                errors.append(f"effect[{i}]: invalid amount")
    return {"status": "INVALID" if errors else "SEPARATE_EFFECTS_UNVALIDATED", "effects": rows, "issues": errors, "aggregation": "WITHHELD; benefit classes, units, pools and periods remain separate"}


def evaluate(data):
    if not isinstance(data, dict):
        raise ValueError("input must be an object")
    with localcontext() as ctx:
        ctx.prec = 512
        baseline, intervention = data.get("baseline"), data.get("intervention_scenario")
        btotal, bpairs, berrors = scenario_cost(baseline, "baseline")
        itotal, ipairs, ierrors = scenario_cost(intervention, "intervention_scenario")
        errors = berrors + ierrors
        if data.get("evidence_mode") not in ("SYNTHETIC", "PUBLIC_RESEARCH", "RESTRICTED_APPROVED"):
            errors.append("evidence_mode must explicitly identify source treatment")
        if isinstance(baseline, dict) and isinstance(intervention, dict):
            for field in FRAME:
                if baseline.get(field) != intervention.get(field):
                    errors.append("unaligned comparison frame: " + field)
            bentities, ientities = baseline.get("entity_scope"), intervention.get("entity_scope")
            if isinstance(bentities, list) and isinstance(ientities, list) and all(present(x) for x in bentities + ientities):
                if set(bentities) != set(ientities):
                    errors.append("unaligned entity scope")
        counterfactual = data.get("counterfactual")
        if not isinstance(counterfactual, dict) or any(counterfactual.get(x) is not True for x in ("frozen", "feasible", "prebooked_included")) or any(not present(counterfactual.get(x)) for x in ("baseline_version", "receipt", "confounder_review_receipt", "prebooked_receipt")):
            errors.append("counterfactual or prebooked baseline support missing")
        cost = {"status": "NOT_COMPUTABLE" if errors else "CALCULATED_UNVALIDATED", "baseline_external_cost": None, "intervention_external_cost": None, "net_cost_difference": None, "currency": baseline.get("currency") if isinstance(baseline, dict) else None, "eliminated_internal_pairs": {"baseline": bpairs, "intervention": ipairs}, "issues": errors, "interpretation": "HYPOTHETICAL_SCENARIO" if data.get("evidence_mode") == "SYNTHETIC" else "UNVALIDATED_DECLARED_COST_COMPARISON"}
        if not errors:
            cost.update(baseline_external_cost=decimal_text(btotal), intervention_external_cost=decimal_text(itotal), net_cost_difference=decimal_text(btotal - itotal))
        gstatus, gissues = guard_status(data.get("guards"))
        return {"schema_version": 1, "model_version": "P08-P14-1", "case_id": data.get("case_id"), "evidence_mode": data.get("evidence_mode"), "cost_comparison": cost, "guardrails": {"status": gstatus, "issues": gissues}, "prioritization": prioritize(data.get("priority_inputs"), gstatus), "benefits": benefit_effects(data.get("benefit_effects", [])), "candidate_advanced": False, "savings_amount": None, "limitations": ["References and coverage assertions are declarations, not authenticated evidence.", "No legal, operational, financial-validation or implementation authority is supplied.", "Cost comparison is not an attributed or realized benefit; review nonadditivity before portfolio aggregation."]}


def sensitivity(data):
    """Compare declared triage preferences; preserve blocked and unscorable cases."""
    if not isinstance(data, dict) or not isinstance(data.get("cases"), list) or not isinstance(data.get("vectors"), list) or not data["vectors"]:
        raise ValueError("sensitivity needs cases and nonempty vectors")
    cases, vectors = data["cases"], data["vectors"]
    case_ids = [row.get("case_id") for row in cases if isinstance(row, dict)]
    vector_ids = [row.get("id") for row in vectors if isinstance(row, dict)]
    if len(case_ids) != len(cases) or not all(present(x) for x in case_ids) or len(set(case_ids)) != len(case_ids):
        raise ValueError("unique case identifiers required")
    if len(vector_ids) != len(vectors) or not all(present(x) for x in vector_ids) or len(set(vector_ids)) != len(vector_ids):
        raise ValueError("unique vector identifiers required")
    illustrative = data.get("illustrative") is True
    results, observed_ranks = [], {ident: [] for ident in case_ids}
    for vector in vectors:
        if not illustrative and not present(vector.get("receipt")):
            raise ValueError("nonillustrative vector needs its review receipt")
        scores = []
        for case in cases:
            inputs = copy.deepcopy(case.get("priority_inputs"))
            if not isinstance(inputs, dict):
                inputs = {}
            inputs.update(weights=vector.get("weights"), weight_receipt="ILLUSTRATIVE_DESIGN_NOT_APPROVED" if illustrative else vector["receipt"])
            state, _ = guard_status(case.get("guards"))
            with localcontext() as ctx:
                ctx.prec = 512
                result = prioritize(inputs, state)
            scores.append({"case_id": case["case_id"], **result, "rank": None})
        eligible = [row for row in scores if row["score"] is not None]
        for row in eligible:
            # Competition ranking preserves ties without arbitrary case-ID preference.
            row["rank"] = 1 + sum(Decimal(other["score"]) > Decimal(row["score"]) for other in eligible)
            observed_ranks[row["case_id"]].append(row["rank"])
        results.append({"vector_id": vector["id"], "cases": scores})
    intervals = {ident: {"best": min(ranks) if ranks else None, "worst": max(ranks) if ranks else None, "scored_vectors": len(ranks)} for ident, ranks in observed_ranks.items()}
    reversals = []
    for i, a in enumerate(case_ids):
        for b in case_ids[i + 1:]:
            signs = set()
            for result in results:
                rows = {row["case_id"]: row for row in result["cases"]}
                if rows[a]["score"] is not None and rows[b]["score"] is not None:
                    avalue, bvalue = Decimal(rows[a]["score"]), Decimal(rows[b]["score"])
                    signs.add((avalue > bvalue) - (avalue < bvalue))
            if -1 in signs and 1 in signs:
                reversals.append([a, b])
    return {"schema_version": 1, "status": "ILLUSTRATIVE_PREFERENCE_STRESS_ONLY" if illustrative else "DECLARED_REVIEWED_WEIGHT_SENSITIVITY", "vectors": results, "rank_intervals": intervals, "pairwise_reversals": reversals, "candidate_advanced": False, "savings_amount": None, "limitations": ["Preference stability does not establish evidence truth or institutional authority.", "Unscorable and blocked cases retain null ranks; no score imputation."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--sensitivity", action="store_true")
    args = parser.parse_args()
    source = json.loads(args.input.read_text())
    result = sensitivity(source) if args.sensitivity else evaluate(source)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
