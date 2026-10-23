#!/usr/bin/env python3
"""Check public request declarations and known restricted path patterns; not a security certification."""
import argparse
import fnmatch
import json
import subprocess
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
REQUESTS = {"E01":"E01_rsce.json", "E02":"E02_assets.json", "E03":"E03_haiti.json",
            "E04":"E04_ga_directed.json", "E05":"E05_training.json", "E06":"E06_reporting_owners.json"}
FORBIDDEN_PREFIXES = ("data/private/", "data/restricted/", "private/", "output/internal/", "outputs/internal/")
FORBIDDEN_SUFFIXES = ("*.umojaxlsx", "*.internal.csv", "*.restricted.csv")
TOP_FIELDS = {"schema_version","artifact_type","request_status","authority_status","owner_acceptance","burden_estimate","period_parameters","handling","completeness_request","approval_gate","financial_limit","request_id","case_ids","purpose","proposed_custodian_roles","tables","case_specific_limits"}
SENSITIVE_FIELDS = {"person_name","staff_name","email","bank_account","passport_number","diagnosis","medical_diagnosis","raw_records","records","data","rows","samples","values"}


def validate_contract(value, expected_id):
    errors = []
    if not isinstance(value, dict):
        return ["contract must be an object"]
    if set(value) != TOP_FIELDS:
        errors.append("unexpected or missing top-level contract fields")
    expected = {"schema_version":1,"artifact_type":"EVIDENCE_REQUEST_CONTRACT","request_id":expected_id,
                "request_status":"DRAFT_NOT_SENT","authority_status":"NOT_AUTHORIZED_TO_COLLECT",
                "owner_acceptance":"NOT_OBTAINED","burden_estimate":"UNKNOWN"}
    for key, target in expected.items():
        if value.get(key) != target:
            errors.append("request declaration differs from approved public draft boundary: " + key)
    period = value.get("period_parameters", {})
    for key in ("baseline_start","baseline_end","intervention_start","intervention_end"):
        if key not in period or period[key] is not None:
            errors.append("period must remain explicitly unset pending approval: " + key)
    handling = value.get("handling", {})
    if handling.get("storage") != "APPROVED_RESTRICTED_SYSTEM_OUTSIDE_THIS_REPOSITORY_ONLY":
        errors.append("restricted storage declaration absent")
    for key in ("pseudonymization","access","retention","public_derivative","unnecessary_fields"):
        if not isinstance(handling.get(key), str) or not handling[key].strip():
            errors.append("handling rule missing: " + key)
    tables = value.get("tables", [])
    if not isinstance(tables, list) or not tables:
        return errors + ["tables must be nonempty declarations"]
    ids = set()
    for table in tables:
        if not isinstance(table, dict) or set(table) != {"table_id","grain","keys","fields"}:
            errors.append("table must contain declarations only, no actual records")
            continue
        if table["table_id"] in ids:
            errors.append("duplicate table identifier")
        ids.add(table["table_id"])
        fields = table["fields"]
        if not isinstance(fields, list) or not fields or not table["grain"] or not table["keys"]:
            errors.append("grain, key or field declarations missing")
            continue
        names = []
        for field in fields:
            if not isinstance(field, dict) or set(field) != {"name","type","purpose","required"}:
                errors.append("field must be a purpose-bound declaration without example values")
                continue
            names.append(field["name"])
            if field["name"].lower() in SENSITIVE_FIELDS:
                errors.append("unnecessary identifying/content field requested")
            if not field["purpose"] or field["required"] is not True or field["type"] not in {"string","date","decimal","integer"}:
                errors.append("field purpose, type or required flag invalid")
        if len(names) != len(set(names)) or not set(table["keys"]) <= set(names):
            errors.append("field names duplicate or key absent")
    return errors


def forbidden_paths(paths):
    return sorted(path for path in paths if path.startswith(FORBIDDEN_PREFIXES)
                  or any(fnmatch.fnmatch(PurePosixPath(path).name, pattern) for pattern in FORBIDDEN_SUFFIXES))


def validate(root=ROOT):
    errors = []
    for request_id, filename in REQUESTS.items():
        path = root / "data/evidence_requests" / filename
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            errors.append(request_id + ": missing or invalid contract JSON")
            continue
        errors.extend(request_id + ": " + error for error in validate_contract(value, request_id))
    result = subprocess.run(["git","ls-files","-z"], cwd=root, check=True, capture_output=True)
    tracked = result.stdout.decode("utf-8").strip("\0").split("\0")
    if forbidden_paths(tracked):
        errors.append("tracked files match restricted intake path patterns")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors = validate(args.root)
    if errors:
        raise SystemExit("\n".join(errors))
    print("Public request declarations and known restricted-path boundary passed; actual content disclosure review remains required.")


if __name__ == "__main__":
    main()
