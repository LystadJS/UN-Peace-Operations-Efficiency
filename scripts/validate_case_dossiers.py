#!/usr/bin/env python3
"""Verify current screening-dossier snapshots; not underlying operational truth."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASE_IDS = tuple(f"C{i:02}" for i in range(1, 15))
BENEFITS = {"cashable_saving", "realized_saving", "capacity_gain", "recovery", "cost_avoidance"}


def validate(root=ROOT, case_ids=CASE_IDS, expected_snapshots=230):
    errors, snapshots, csv_snapshots, json_snapshots = [], 0, 0, 0
    root = Path(root).resolve()
    directory = root / "data/cases"
    observed_ids = {path.stem for path in directory.glob("C*.json")}
    if observed_ids != set(case_ids):
        errors.append("Case population differs from reviewed release")
    cache = {}
    for case_id in case_ids:
        path = directory / (case_id + ".json")
        try:
            dossier = json.loads(path.read_text())
        except (OSError, ValueError):
            errors.append(case_id + ": missing or invalid dossier")
            continue
        if not isinstance(dossier, dict):
            errors.append(case_id + ": dossier is not an object")
            continue
        if dossier.get("case_id") != case_id:
            errors.append(case_id + ": dossier identity mismatch")
        for key, value in {"candidate_state": "SCREENING_CANDIDATE", "disposition": "BLOCKED_PENDING_EVIDENCE", "owner_confirmation_status": "NOT_OBTAINED", "evidence_request_sent": False, "financial_validation": "NOT_PERFORMED"}.items():
            if dossier.get(key) != value or type(dossier.get(key)) is not type(value):
                errors.append(case_id + ": current evidence boundary changed: " + key)
        if dossier.get("accountable_owner") is not None or dossier.get("operational_baseline") is not None:
            errors.append(case_id + ": unknown owner/baseline must not be fabricated")
        benefits = dossier.get("benefits", {})
        if not isinstance(benefits, dict) or not BENEFITS <= set(benefits) or any(benefits.get(key) is not None for key in BENEFITS) or benefits.get("status") != "NOT_ESTIMATED":
            errors.append(case_id + ": benefit estimates changed without substantive review")
        evidence = dossier.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(case_id + ": source evidence snapshots missing")
            continue
        for i, row in enumerate(evidence):
            prefix = f"{case_id}.evidence[{i}]"
            snapshots += 1
            if not isinstance(row, dict) or not isinstance(row.get("path"), str):
                errors.append(prefix + ": invalid source reference")
                continue
            relative = Path(row["path"])
            source = (root / relative).resolve()
            if relative.is_absolute() or ".." in relative.parts or not source.is_relative_to(root) or not source.is_file():
                errors.append(prefix + ": missing or unsafe source path")
                continue
            try:
                if row["path"] not in cache:
                    raw = source.read_bytes()
                    cache[row["path"]] = (hashlib.sha256(raw).hexdigest(), raw.decode("utf-8"))
                sha, text = cache[row["path"]]
                if sha != row.get("sha256"):
                    errors.append(prefix + ": source-file hash differs")
                if "csv_line" in row and "json_pointer" not in row:
                    csv_snapshots += 1
                    line = row["csv_line"]
                    records = list(csv.DictReader(text.splitlines(keepends=True)))
                    if type(line) is not int or line < 2 or line - 2 >= len(records) or records[line - 2] != row.get("source_snapshot"):
                        errors.append(prefix + ": CSV locator or exact snapshot differs")
                elif "json_pointer" in row and "csv_line" not in row:
                    json_snapshots += 1
                    # The three existing JSON receipts explicitly retain selected root fields.
                    if row["json_pointer"] != "" or row.get("snapshot_scope") != "selected top-level fields, not full document":
                        errors.append(prefix + ": unsupported or unmarked JSON subset scope")
                        continue
                    original, snapshot = json.loads(text), row.get("source_snapshot")
                    if not isinstance(original, dict) or not isinstance(snapshot, dict) or not snapshot or any(key not in original or original[key] != value for key, value in snapshot.items()):
                        errors.append(prefix + ": selected JSON snapshot differs")
                else:
                    errors.append(prefix + ": one supported locator is required")
            except (OSError, UnicodeError, ValueError, TypeError, KeyError, csv.Error):
                errors.append(prefix + ": cannot resolve source snapshot")
    if snapshots != expected_snapshots:
        errors.append(f"Expected {expected_snapshots} reviewed evidence snapshots; found {snapshots}")
    return {"status": "PASS" if not errors else "FAIL", "case_count": len(case_ids), "evidence_snapshots": snapshots, "csv_snapshots": csv_snapshots, "selected_json_snapshots": json_snapshots, "unique_source_files": len(cache), "errors": errors, "limitation": "Source-byte and locator fidelity only; public reports do not establish complete transactions, authority, operational outcomes or savings."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    result = validate(args.root)
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result["errors"]))


if __name__ == "__main__":
    main()
