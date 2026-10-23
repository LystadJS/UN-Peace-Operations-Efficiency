#!/usr/bin/env python3
"""Structural evidence gates; receipts require substantive human/source review."""
from __future__ import annotations

import argparse
from datetime import date, datetime
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DICTIONARY = ROOT / "data/standards/candidate_states.json"
EXPECTED = {
    "SCREENING_CANDIDATE", "VALIDATION_READY", "OPERATIONALLY_VALIDATED",
    "FINANCIALLY_VALIDATED", "IMPLEMENTATION_READY", "REALIZATION_IN_PROGRESS",
    "REALIZED", "RETAIN_CURRENT_PROCESS", "CLOSED_INSUFFICIENT_EVIDENCE",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value):
    return isinstance(value, str) and bool(value.strip()) and value.strip().lower() not in {
        "unknown", "null", "none", "not_available", "not_obtained", "pending", "n/a"
    }


def read(path):
    # Duplicate JSON keys otherwise silently overwrite evidence/status fields.
    def unique(pairs):
        obj = {}
        for key, value in pairs:
            require(key not in obj, f"duplicate JSON key: {key}")
            obj[key] = value
        return obj
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique)


def validate_dictionary(d):
    require(isinstance(d, dict), "dictionary must be an object")
    require(type(d.get("schema_version")) is int and d["schema_version"] == 1,
            "dictionary schema_version must be integer 1")
    require(isinstance(d.get("states"), dict), "dictionary states must be an object")
    require(set(d["states"]) == EXPECTED, "dictionary must contain exactly the nine agreed states")
    for state, rule in d["states"].items():
        require(isinstance(rule, dict), f"{state}: rule must be an object")
        require(isinstance(rule.get("requires"), list) and rule["requires"], f"{state}: missing gate checks")
        require(all(text(x) for x in rule["requires"]), f"{state}: invalid check")
        require(len(rule["requires"]) == len(set(rule["requires"])), f"{state}: duplicate check")
        require(isinstance(rule.get("next"), list) and all(isinstance(x, str) for x in rule["next"])
                and set(rule["next"]) <= EXPECTED,
                f"{state}: unknown successor")
        require(state not in rule["next"], f"{state}: self transition prohibited")
    for state in ("REALIZED", "RETAIN_CURRENT_PROCESS", "CLOSED_INSUFFICIENT_EVIDENCE"):
        require(not d["states"][state]["next"], f"{state}: must be terminal")
    require(isinstance(d.get("claim_classes"), list) and all(text(x) for x in d["claim_classes"]),
            "claim_classes must be a list of strings")
    require(isinstance(d.get("savings_claim_classes"), list)
            and all(text(x) for x in d["savings_claim_classes"])
            and set(d["savings_claim_classes"]) == {"CASHABLE_SAVING", "REALIZED_SAVING"},
            "savings classes must remain explicit")
    require(set(d["savings_claim_classes"]) <= set(d.get("claim_classes", [])), "missing savings class")
    require(text(d.get("validator_version")), "missing validator version")
    for field in ("record_fields", "event_fields"):
        require(isinstance(d.get(field), list) and d[field] and all(text(x) for x in d[field]),
                f"invalid {field}")


def validate_records(payload, d, previous=None):
    validate_dictionary(d)
    require(isinstance(payload, dict) and type(payload.get("schema_version")) is int
            and payload["schema_version"] == 1,
            "records schema_version must be 1")
    records = payload.get("candidates")
    require(isinstance(records, list), "candidates must be a list")
    identities = set()
    by_id = {}
    for r in records:
        require(isinstance(r, dict), "candidate must be an object")
        require(set(d["record_fields"]) <= r.keys(), "missing candidate field")
        require(text(r["candidate_id"]) and text(r["version"]), "candidate ID/version required")
        key = (r["candidate_id"], r["version"])
        require(key not in identities, f"duplicate candidate/version: {key}")
        identities.add(key)
        by_id[key] = r
        state = r["current_state"]
        require(isinstance(state, str) and state in d["states"], f"{key}: unknown state")
        require(isinstance(r["claim_class"], str) and r["claim_class"] in d["claim_classes"],
                f"{key}: unknown claim class")
        history = r["history"]
        require(isinstance(history, list) and history, f"{key}: history required")
        prior_state = None
        prior_time = None
        visited = set()
        for e in history:
            require(isinstance(e, dict) and set(d["event_fields"]) <= e.keys(), f"{key}: missing event field")
            s = e["state"]
            require(isinstance(s, str) and s in d["states"], f"{key}: unknown event state")
            if prior_state is None:
                require(s == "SCREENING_CANDIDATE", f"{key}: history must start at screening")
            else:
                require(s in d["states"][prior_state]["next"], f"{key}: illegal transition {prior_state} -> {s}")
            require(all(text(e[x]) for x in ("actor", "rationale", "validator_version")),
                    f"{key}: event actor/rationale/version required")
            require(e["validator_version"] == d["validator_version"], f"{key}: unsupported validator version")
            try:
                timestamp = datetime.fromisoformat(e["recorded_at"].replace("Z", "+00:00"))
                cutoff = date.fromisoformat(e["evidence_cutoff"])
            except (ValueError, TypeError, AttributeError):
                raise ValueError(f"{key}: invalid event timestamp/cutoff") from None
            require(timestamp.tzinfo is not None, f"{key}: timestamp timezone required")
            require(cutoff <= timestamp.date(), f"{key}: evidence cutoff after event")
            require(prior_time is None or timestamp > prior_time, f"{key}: event timestamps must increase")
            checks, receipts = e["checks"], e["evidence_receipts"]
            require(isinstance(checks, dict) and isinstance(receipts, dict), f"{key}: checks/receipts must be objects")
            for check in d["states"][s]["requires"]:
                require(checks.get(check) is True, f"{key}: {s} unmet check: {check}")
                refs = receipts.get(check)
                require(isinstance(refs, list) and refs and all(text(x) for x in refs),
                        f"{key}: {s} missing evidence receipt: {check}")
            prior_state, prior_time = s, timestamp
            visited.add(s)
        require(state == prior_state, f"{key}: current state disagrees with history")
        amount = r["savings_amount"]
        is_savings = r["claim_class"] in d["savings_claim_classes"]
        if is_savings:
            require("FINANCIALLY_VALIDATED" in visited, f"{key}: savings require financial gate")
            require(state not in {"RETAIN_CURRENT_PROCESS", "CLOSED_INSUFFICIENT_EVIDENCE"},
                    f"{key}: closed case cannot carry an active savings claim")
            require(type(amount) in (int, float) and math.isfinite(amount) and amount > 0,
                    f"{key}: savings amount must be positive and finite")
            require(isinstance(r["currency"], str) and len(r["currency"]) == 3 and r["currency"].isalpha()
                    and r["currency"].isupper(), f"{key}: three-letter currency required")
            require(text(r["period"]), f"{key}: savings period required")
            if r["claim_class"] == "REALIZED_SAVING":
                require(state == "REALIZED", f"{key}: realized saving requires REALIZED state")
        else:
            require(amount is None and r["currency"] is None and r["period"] is None,
                    f"{key}: non-savings class must leave savings fields null")
    if previous is not None:
        validate_records(previous, d)
        for old in previous["candidates"]:
            key = (old["candidate_id"], old["version"])
            require(key in by_id, f"{key}: prior version deleted")
            new = by_id[key]
            require(new["history"][:len(old["history"])] == old["history"],
                    f"{key}: historical events changed or removed")
    return len(records)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dictionary", type=Path, default=DICTIONARY)
    parser.add_argument("--records", type=Path, help="JSON candidate envelope to validate")
    parser.add_argument("--previous", type=Path, help="prior records envelope for append-only verification")
    args = parser.parse_args()
    try:
        require(not args.previous or args.records, "--previous requires --records")
        d = read(args.dictionary)
        validate_dictionary(d)
        count = validate_records(read(args.records), d, read(args.previous) if args.previous else None) if args.records else 0
        print(f"PASS: nine-state dictionary; {count} supplied candidate records structurally valid")
        print("Evidence receipt contents, institutional authority, and financial conclusions are not authenticated by this validator.")
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
