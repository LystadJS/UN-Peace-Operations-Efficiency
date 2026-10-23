#!/usr/bin/env python3
"""Execute public synthetic rehearsals without activating any operational pilot."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = "data/pilots/synthetic_scenarios.json"
RECEIPT = "data/pilots/rehearsal_receipt.json"
PILOTS = {"PILOT-RSCE": "C01", "PILOT-UNIFIL-ASSETS": "C02", "PILOT-HAITI": "C03"}
DIMENSIONS = {"mandate", "safety", "readiness", "quality", "timeliness", "transition", "work_transfer", "evidence_authority"}


def load(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_preparation(charters, thresholds):
    """Check the current blocked-design snapshot, never create activation authority."""
    require(charters.get("institutional_approval") is False and charters.get("live_trial_started") is False, "Synthetic preparation cannot assert approval or a live trial")
    rows = charters.get("charters")
    require(isinstance(rows, list) and len(rows) == 3, "Exactly three scoped pilot charters required")
    require({row.get("pilot_id"): row.get("case_id") for row in rows} == PILOTS, "Pilot/case mapping changed")
    for row in rows:
        require(row.get("activation_status") == "BLOCKED", "Actual pilots remain blocked")
        require(row.get("candidate_state") == "SCREENING_CANDIDATE", "A draft charter cannot advance a case")
        for key in ("accepted_accountable_owner", "owner_acceptance_receipt", "baseline_version", "baseline_period", "measurement_window", "independent_sample_size", "power_or_precision_plan", "fallback_owner", "stop_authority"):
            require(row.get(key) is None, "Current charter must preserve unknown " + key)
        for key in ("operational_authority_receipts", "evidence_access_approval_receipts", "threshold_approval_receipts"):
            require(row.get(key) == [], "Current charter cannot invent approval receipts")
        require(row.get("request_status") == "NOT_SENT" and row.get("records_status") == "NOT_OBTAINED", "Draft charter is not an evidence receipt")
        benefits = row.get("benefits", {})
        require(set(benefits) == {"capacity_gain", "recovery", "cost_avoidance", "cashable_saving", "realized_saving"} and all(value is None for value in benefits.values()), "Actual pilot benefits must remain explicitly unknown")
    require(thresholds.get("numeric_thresholds_approved") is False, "No numeric threshold has owner approval")
    limits = thresholds.get("thresholds")
    require(isinstance(limits, list) and len(limits) == 24, "Three pilots need all eight threshold dimensions")
    identities = [(row.get("pilot_id"), row.get("dimension")) for row in limits]
    require(len(set(identities)) == 24 and set(identities) == {(pilot, dimension) for pilot in PILOTS for dimension in DIMENSIONS}, "Missing or duplicate threshold dimension")
    for row in limits:
        require(row.get("status") == "TBD_BLOCKED", "Unknown baseline requires blocked thresholds")
        for key in ("numeric_threshold", "noninferiority_margin", "baseline_value", "baseline_period", "observation_window", "independent_sample_size", "accepted_owner", "approval_receipt", "approval_date", "prospective_freeze_receipt"):
            require(row.get(key) is None, "Threshold snapshot must preserve unknown " + key)
    return {"charters": 3, "threshold_dimensions": 24, "actual_pilots_authorized": 0, "actual_pilots_started": 0}


def validate_requests(data, root=ROOT):
    """Validate the unsent request snapshot against all six prepared contracts."""
    rows = data.get("requests")
    require(isinstance(rows, list) and len(rows) == 6, "Six request contracts required")
    require({row.get("request_id") for row in rows} == {f"E0{i}" for i in range(1, 7)}, "Exact E01–E06 request IDs required")
    tracks = set()
    for row in rows:
        path = root / row["contract_path"]
        contract = load(path)
        require(contract.get("request_id") == row["request_id"], "Request identity differs from contract")
        require(contract.get("case_ids") == row.get("case_ids"), "Request case coverage differs from contract")
        require([table["table_id"] for table in contract["tables"]] == row.get("table_ids"), "Request table coverage differs from contract")
        require(contract.get("request_status") == "DRAFT_NOT_SENT" and contract.get("authority_status") == "NOT_AUTHORIZED_TO_COLLECT" and contract.get("owner_acceptance") == "NOT_OBTAINED", "Request contract cannot imply authorization or dispatch")
        require(row.get("dispatch_status") == "NOT_SENT" and row.get("response_status") == "NOT_OBTAINED" and row.get("collection_status") == "NOT_AUTHORIZED", "Prepared request is not sent, received or authorized")
        for key in ("accepted_owner", "recipient_identity", "dispatch_receipt", "requested_at", "received_at", "burden_estimate", "followup_due"):
            require(row.get(key) is None, "Unsent request preserves unknown " + key)
        require(row.get("response_receipts") == [] and row.get("access_approval_receipts") == [], "Unobtained response or approval must not have receipts")
        tracks.update((row["request_id"], case) for case in row["case_ids"])
        if row["request_id"] == "E04":
            require(row["case_ids"] == ["C04", "C05", "C06", "C07"], "Four GA-directed case subgroups must remain distinct")
    declared = data.get("case_tracks")
    require(isinstance(declared, list) and len(declared) == 10, "Ten case-specific tracks required, not nine")
    require({(row.get("request_id"), row.get("case_id")) for row in declared} == tracks, "Case-track coverage differs from contracts")
    require(all(row.get("dispatch_status") == "NOT_SENT" and row.get("response_status") == "NOT_OBTAINED" and row.get("approved_collection") is False for row in declared), "Case tracks must preserve unsent/unobtained status")
    require(data.get("counts") == {"draft_contracts": 6, "case_tracks": 10, "requests_sent": 0, "responses_obtained": 0, "accepted_owners": 0, "approved_collections": 0}, "Request counts contradict current evidence")
    require(data.get("external_actions_performed") == [], "No external dispatch or collection occurred")
    return {"draft_contracts": 6, "case_tracks": 10, "requests_sent": 0, "responses_obtained": 0}


def rehearse(data, evaluator):
    require(data.get("classification") == "SYNTHETIC_ONLY", "Rehearsal requires synthetic classification")
    require(all(data.get(key) is False for key in ("actual_un_records", "actual_owner_approvals", "live_trial")), "Rehearsal cannot claim actual records, approvals or live operation")
    rows = data.get("scenarios")
    require(isinstance(rows, list) and rows, "Synthetic scenarios required")
    require(len({row.get("scenario_id") for row in rows}) == len(rows), "Scenario identifiers must be unique")
    results = []
    for row in rows:
        ident, source = row.get("scenario_id"), row.get("input")
        require(isinstance(ident, str) and ident.startswith("SYN-"), "Synthetic identity prefix required")
        require(isinstance(source, dict) and source.get("evidence_mode") == "SYNTHETIC" and source.get("case_id") == ident, "Synthetic input identity and mode required")
        result = evaluator(source)
        observed = {"cost_status": result["cost_comparison"]["status"], "net_cost_difference": result["cost_comparison"]["net_cost_difference"], "guard_status": result["guardrails"]["status"], "priority_status": result["prioritization"]["status"]}
        require(observed == row.get("expected"), "Synthetic expected behavior changed: " + ident)
        require(result.get("candidate_advanced") is False and result.get("savings_amount") is None, "Synthetic evaluation cannot promote or recognize savings")
        results.append({"scenario_id": ident, "result": "PASS", "observed": observed, "candidate_advanced": False, "savings_amount": None, "input_sha256": hashlib.sha256(json.dumps(source, sort_keys=True, separators=(",", ":")).encode()).hexdigest(), "result_sha256": hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()})
    return results


def build(root=ROOT):
    evaluator_path = root / "scripts/evaluate_intervention.py"
    spec = importlib.util.spec_from_file_location("portfolio_rehearsal_evaluator", evaluator_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    preparation = validate_preparation(load(root / "data/pilots/charters.json"), load(root / "data/pilots/thresholds.json"))
    results = rehearse(load(root / SCENARIOS), module.evaluate)
    sources = [SCENARIOS, "scripts/evaluate_intervention.py", "scripts/rehearse_portfolio.py", "data/pilots/charters.json", "data/pilots/thresholds.json"]
    return {"schema_version": 1, "design_task": "E14", "status": "SYNTHETIC_SOFTWARE_REHEARSAL_PASSED", "execution_kind": "ACTUAL_LOCAL_SOFTWARE_EXECUTION_ON_EXPLICIT_SYNTHETIC_INPUTS", "source_hashes": {path: digest(root / path) for path in sources}, "scenario_count": len(results), "scenarios_passed": len(results), "results": results, "actual_preparation_status": preparation, "actual_operational_trials": 0, "actual_owner_approvals": 0, "actual_financial_validations": 0, "actual_savings_amount": None, "runtime_ci_attestation": "NOT_SUPPLIED_BY_THIS_DETERMINISTIC_RECEIPT", "limitations": ["Only bounded software behavior was exercised; no UN transaction or operational finding follows.", "Toy monetary differences do not estimate an actual intervention, benefit or saving.", "Synthetic PASS and owner receipts are fictional; all actual pilot activation gates remain blocked.", "This deterministic receipt authenticates listed input bytes and reproducible outputs, not a hosted-CI run or live operation."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--check-requests", action="store_true", help="Also validate E15 request snapshot, which follows E14")
    args = parser.parse_args()
    result = build()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        (ROOT / RECEIPT).write_text(rendered)
    else:
        require((ROOT / RECEIPT).read_text() == rendered, "Rehearsal receipt is stale")
    if args.check_requests:
        validate_requests(load(ROOT / "data/pilots/request_status.json"))
    print(f"Synthetic software rehearsal passed {result['scenarios_passed']} scenarios; actual pilots remain blocked.")


if __name__ == "__main__":
    main()
