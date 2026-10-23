#!/usr/bin/env python3
"""Check bounded reform register declarations; never authenticate legal effect."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_reform_obligations import validate as validate_obligations

ROOT = Path(__file__).resolve().parents[1]


def validate_register(name, data):
    errors = []
    def check(condition, message):
        if not condition:
            errors.append(f"{name}: {message}")
    if not isinstance(data, dict):
        return [f"{name}: expected object"]
    if name.endswith("_actions.json"):
        errors.extend(f"{name}: {e}" for e in validate_obligations(data))
        if data.get("obligations") == []:
            check(bool(data.get("zero_count_meaning")), "empty extraction must explain evidence boundary")
        for row in data.get("obligations", []):
            if not isinstance(row, dict):
                continue
            compliance = row.get("compliance", {})
            provision = row.get("provision", {})
            if compliance.get("status") == "NOT_APPLICABLE":
                check(bool(compliance.get("assessment_receipt")), "not applicable requires applicability assessment")
            if compliance.get("status") == "NOT_YET_DUE":
                deadline, cutoff = provision.get("deadline"), row.get("evidence_cutoff")
                check(isinstance(deadline, str) and isinstance(cutoff, str) and deadline > cutoff, "not yet due requires future sourced deadline")
    elif name.endswith("_instruments.json"):
        check(isinstance(data.get("instruments"), list), "instruments list required")
        for row in data.get("instruments", []):
            if not isinstance(row, dict):
                errors.append(name + ": invalid instrument row")
                continue
            classification = row.get("authority_classification", row.get("authority_class", "AUTHORITY_UNRESOLVED"))
            if classification in ("GA_ADOPTED", "SC_MANDATE"):
                # Index adoption authenticates existence, not action-specific legal effect.
                if name == "unga80_instruments.json":
                    check(row.get("adoption_status") == "ADOPTED_VERIFIED" and bool(row.get("authentication")) and bool(row.get("review_scope")), "adopted instrument requires final-text authentication and review")
                    check(bool(row.get("adoption_record")) and bool(row.get("official_url")), "adopted instrument requires adoption record and official locator")
                else:
                    check(row.get("operative_text_status") in ("VERIFIED", "RETRIEVED_AND_REVIEWED"), "governing authority requires operative text review")
                    check(bool(row.get("competence_review_receipt")), "governing authority requires competence review receipt")
    elif name == "acabq_recommendations.json":
        check(isinstance(data.get("recommendations"), list), "recommendations list required")
        for row in data.get("recommendations", []):
            check(row.get("authority_classification") == "ACABQ_ADVICE", "ACABQ source cannot become governing adoption")
            effect = row.get("financial_effect")
            if effect is not None:
                check(effect.get("not_a_savings_finding") is True, "advisory adjustment is not savings")
            check(row.get("implementation_status") != "VERIFIED" or bool(row.get("implementation_evidence_receipts")), "verified implementation requires separate receipts")
    elif name == "sg_proposals.json":
        check(isinstance(data.get("records"), list), "records list required")
        for row in data.get("records", []):
            check(row.get("source_treatment") in ("SG_PROPOSAL", "JOINT_PLAN_REPORTED", "EXISTING_ARRANGEMENT_REPORTED"), "SG proposal/management reports cannot become governing authority")
            adoption = row.get("ga_adoption", {})
            if adoption.get("status") in ("VERIFIED", "ADOPTED_VERIFIED"):
                check(bool(adoption.get("instrument")) and bool(adoption.get("operative_paragraph")) and bool(adoption.get("review_receipt")), "adoption requires separate adopted instrument review")
            implementation = row.get("implementation", {})
            if implementation.get("status") == "VERIFIED":
                check(bool(implementation.get("evidence_receipts")), "implementation requires separate operational evidence")
            benefit = row.get("realized_benefit", {})
            if benefit.get("amount") is not None:
                check(row.get("financial_validation") == "FINANCIALLY_VALIDATED" and bool(row.get("financial_review_receipt")), "monetary finding requires financial review gate")
    elif name == "un80_arrangement_reconciliation.json":
        check(isinstance(data.get("records"), list), "records list required")
        for row in data.get("records", []):
            if row.get("institutional_implementation_status") == "VERIFIED":
                check(bool(row.get("supplemental_evidence_refs")), "implementation requires supplemental evidence")
            if row.get("realized_benefit_amount") is not None:
                check(row.get("financial_validation_status") == "FINANCIALLY_VALIDATED" and bool(row.get("financial_review_receipt")), "monetary finding requires financial review gate")
    return errors


def validate(root=ROOT):
    directory = root / "data/reforms"
    schema = json.loads((directory / "obligation_schema.json").read_text())
    statuses = json.loads((directory / "compliance_statuses.json").read_text())
    errors = []
    if set(schema["compliance_states"]) != set(statuses["compliance"]):
        errors.append("Compliance dictionary differs from obligation contract")
    if set(schema["implementation_states"]) != set(statuses["implementation"]):
        errors.append("Implementation dictionary differs from obligation contract")
    checked = []
    for name in ("unga80_actions.json", "unga81_actions.json", "unga80_instruments.json", "unga81_instruments.json", "acabq_recommendations.json", "sg_proposals.json", "un80_arrangement_reconciliation.json"):
        path = directory / name
        if not path.exists():
            errors.append(f"Missing required reform register: {name}")
            continue
        errors.extend(validate_register(name, json.loads(path.read_text())))
        checked.append(name)
    for session in (80, 81):
        actions_path = directory / f"unga{session}_actions.json"
        instruments_path = directory / f"unga{session}_instruments.json"
        if actions_path.exists() and instruments_path.exists():
            actions = json.loads(actions_path.read_text()).get("obligations", [])
            instruments = json.loads(instruments_path.read_text()).get("instruments", [])
            symbols = {r.get("document_symbol", r.get("symbol")): r for r in instruments if isinstance(r, dict)}
            for action in actions:
                if not isinstance(action, dict):
                    continue
                symbol = action.get("document_symbol")
                instrument = symbols.get(symbol)
                if not instrument:
                    errors.append(f"GA{session}: obligation references unregistered instrument {symbol}")
                elif action.get("authority_class") in ("GA_ADOPTED", "SC_MANDATE"):
                    classification = instrument.get("authority_class", instrument.get("authority_classification"))
                    if classification != action["authority_class"] or instrument.get("adoption_status") != "ADOPTED_VERIFIED":
                        errors.append(f"GA{session}: obligation adoption conflicts with instrument {symbol}")
    return {"status": "PASS" if not errors else "FAIL", "checked_registers": checked, "errors": errors, "limitation": "Declaration consistency only; no source authentication, legal or implementation adjudication."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    result = validate(args.root)
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result["errors"]))


if __name__ == "__main__":
    main()
