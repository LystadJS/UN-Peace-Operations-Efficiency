#!/usr/bin/env python3
"""Validate the source-linked peace operations baseline using Python's standard library."""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
from collections import Counter
from pathlib import Path

DATASETS = {
    "source_manifest": "source_id",
    "functional_inventory": "function_id",
    "mandate_inventory": "mandate_id",
    "deliverable_inventory": "deliverable_id",
    "financial_guardrails": "record_id",
    "crosswalk": "crosswalk_id",
    "un80_register": "reform_id",
    "candidate_validation": "candidate_id",
    "non_overlap_controls": "control_id",
    "quality_issues": "issue_id",
    "evidence_links": "evidence_id",
}
CLASSES = {
    "documented_shared_structure", "documented_joint_process",
    "planned_coordination", "candidate_overlap",
    "complementary_different_roles", "distinct_mandates",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_dataset(root: Path, filename: str, id_field: str) -> list[dict[str, str]]:
    path = root / "data" / f"{filename}.csv"
    require(path.is_file(), f"Required dataset missing: {path}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        require(reader.fieldnames is not None and id_field in reader.fieldnames,
                f"{filename} missing primary key {id_field}")
        require(len(reader.fieldnames) == len(set(reader.fieldnames)),
                f"{filename} has duplicate column names")
        rows = list(reader)
    require(bool(rows), f"{filename} has no data rows")
    ids = [row.get(id_field, "") for row in rows]
    require(len(ids) == len(set(ids)), f"{filename} duplicate primary keys")
    for ix, row in enumerate(rows, 2):
        require(None not in row and all(value is not None and value.strip() for value in row.values()),
                f"{filename} contains empty/unexpected field on CSV row {ix}")
    return rows


def verify(root: Path, source_dir: Path | None = None) -> dict[str, int]:
    data = {name: read_dataset(root, name, key) for name, key in DATASETS.items()}
    source = {r["source_id"]: r for r in data["source_manifest"]}
    funcs = {r["function_id"]: r for r in data["functional_inventory"]}
    delivs = {r["deliverable_id"]: r for r in data["deliverable_inventory"]}
    crosswalks = {r["crosswalk_id"]: r for r in data["crosswalk"]}
    reforms = {r["reform_id"]: r for r in data["un80_register"]}

    require(set(source) == {"S03", "S05"}, "Source set must be S03 and S05")
    for sid, r in source.items():
        require(int(r["pages"]) > 0, f"Invalid PDF page count: {sid}")
        require(bool(re.fullmatch(r"[0-9a-f]{64}", r["sha256"])),
                f"Invalid source hash: {sid}")
        require(r["official_record_url"].startswith("https://"), f"No official link: {sid}")
        if source_dir:
            file = source_dir / r["file_name"]
            require(file.is_file(), f"Missing local source file: {file}")
            digest = hashlib.sha256(file.read_bytes()).hexdigest()
            require(digest == r["sha256"], f"Hash mismatch for {sid}: {file}")

    for fid, f in funcs.items():
        expected = "F" if f["department"] == "DPPA" else "G"
        require(fid.startswith(expected), f"Wrong function prefix for {fid}")
        require(f["source_id"] == ("S03" if expected == "F" else "S05"),
                f"Wrong function source for {fid}")
        require(1 <= int(f["pdf_page"]) <= int(source[f["source_id"]]["pages"]),
                f"Out-of-range function source page: {fid}")

    for r in data["deliverable_inventory"]:
        did = r["deliverable_id"]
        require(did.startswith("D" if r["department"] == "DPPA" else "P"),
                f"Wrong deliverable ID prefix: {did}")
        sid = "S03" if r["department"] == "DPPA" else "S05"
        require(1 <= int(r["pdf_page"]) <= int(source[sid]["pages"]),
                f"Invalid deliverable page: {did}")
        require(int(r["actual_2025"]) >= 0 and int(r["planned_2027"]) >= 0,
                f"Invalid measured outputs: {did}")
        require(r["unit_of_measure"] in {"documents", "three-hour meetings", "days", "missions", "materials", "projects"},
                f"Unrecognized output type: {did}")

    for cid, r in crosswalks.items():
        require(r["classification"] in CLASSES, f"Bad overlap class: {cid}")
        for side, prefix in [("dppa_function_id", "F"), ("dpo_function_id", "G")]:
            fid = r[side]
            require(fid in funcs and fid.startswith(prefix), f"Unknown crosswalk function: {cid} {fid}")
        if r["reform_id"] != "-":
            require(r["reform_id"] in reforms, f"Unknown reform ID: {cid}")
        for side, sid in [("dppa_pdf_page", "S03"), ("dpo_pdf_page", "S05")]:
            require(1 <= int(r[side]) <= int(source[sid]["pages"]),
                    f"Invalid crosswalk page: {cid} {side}")
        for did in ([] if r["deliverable_ids"] == "-" else r["deliverable_ids"].split(";")):
            require(did in delivs, f"Unknown linked deliverable {did} for {cid}")
        require(r["evidence_type"] in {"direct_documentation", "source_grounded_inference"},
                f"Bad evidence class: {cid}")

    for r in data["candidate_validation"]:
        for cid in r["crosswalk_ids"].split(";"):
            require(cid in crosswalks, f"Unknown candidate crosswalk {cid}")
        require(r["priority"] in {"high", "medium", "low"}, "Invalid candidate priority")
        require(r["savings_status"] in {"not_estimated", "not_applicable"},
                "Numerical savings not permitted in screening baseline")
        require(r["assessment_state"] in {"screening", "control"},
                "Invalid candidate state")

    for r in data["non_overlap_controls"]:
        require(r["crosswalk_id"] in crosswalks, "Non-overlap control has missing crosswalk")

    for r in data["mandate_inventory"]:
        require(r["relationship"] in {"shared_in_sources", "dppa_recorded", "dpo_recorded"},
                f"Invalid mandate relationship {r['mandate_id']}")
        require(r["dppa_anchor"] != "none" or r["dpo_anchor"] != "none",
                f"No documentary mandate anchor: {r['mandate_id']}")

    for r in data["un80_register"]:
        require(r["implementation_verification"] in {"not_independently_verified", "proposed_not_independently_verified"},
                f"Unwarranted implementation claim: {r['reform_id']}")
        if r["reform_category"] == "other_2027_reorganization_not_un80":
            require(r["reform_id"] == "U11", "Unexpected UNOAU status")

    link_counts = Counter()
    for r in data["evidence_links"]:
        objtype, oid, side, sid = (r[x] for x in ("object_type", "object_id", "side", "source_id"))
        expect = {"function": "functional_inventory", "deliverable": "deliverable_inventory",
                  "mandate": "mandate_inventory", "crosswalk": "crosswalk"}[objtype]
        objkey = DATASETS[expect]
        require(oid in {x[objkey] for x in data[expect]}, f"Orphan evidence: {oid}")
        require(1 <= int(r["pdf_page"]) <= int(source[sid]["pages"]),
                f"Evidence page invalid: {r['evidence_id']}")
        require(r["official_url"].startswith("https://"), f"Invalid evidence URL: {oid}")
        link_counts[(objtype, oid, side)] += 1
    for cid in crosswalks:
        require(link_counts[("crosswalk", cid, "DPPA")] == 1, f"Missing DPPA anchor: {cid}")
        require(link_counts[("crosswalk", cid, "DPO")] == 1, f"Missing DPO anchor: {cid}")
    require(len(data["quality_issues"]) > 0, "Source discrepancies must be visible")
    return {k: len(v) for k, v in data.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--source-dir", type=Path, help="Optional source-PDF directory for SHA-256 verification")
    args = parser.parse_args()
    try:
        stats = verify(args.root.resolve(), args.source_dir)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"VALIDATION FAILED: {exc}", file=sys.stderr)
        return 1
    print("VALIDATION PASSED")
    print(", ".join(f"{name}={n}" for name, n in stats.items()))
    print("Scope: referential and structural integrity only; not a savings or mandate audit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
