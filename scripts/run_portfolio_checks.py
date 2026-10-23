#!/usr/bin/env python3
"""Run the explicit offline public-portfolio suite and emit an external receipt."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PLAN = "data/portfolio/validation_plan.json"
RUNNER = "scripts/run_portfolio_checks.py"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(root, *args):
    return subprocess.check_output(["git", *args], cwd=root)


def safe_relative(value):
    return isinstance(value, str) and bool(value) and not Path(value).is_absolute() and ".." not in Path(value).parts and not value.startswith("-")


def check_plan(plan, root=ROOT):
    require(isinstance(plan, dict) and plan.get("schema_version") == 1, "Invalid validation plan")
    require(plan.get("python_minimum") == "3.11" and plan.get("network_required") is False and plan.get("publishes") is False, "Plan must declare Python >=3.11, offline operation and no publishing")
    steps = plan.get("steps")
    require(isinstance(steps, list) and steps, "Explicit nonempty steps required")
    require(type(plan.get("timeout_seconds")) is int and 1 <= plan["timeout_seconds"] <= 600, "Bounded step timeout required")
    ids, tests, paths = set(), set(), set()
    for step in steps:
        require(isinstance(step, dict), "Step must be an object")
        ident = step.get("id")
        require(isinstance(ident, str) and re.fullmatch(r"[a-z0-9-]+", ident) is not None and ident not in ids, "Unique safe step ID required")
        ids.add(ident)
        require(isinstance(step.get("tasks"), list) and step["tasks"] and all(isinstance(x, str) and x for x in step["tasks"]), "Each check must declare task coverage")
        argv = step.get("argv")
        require(isinstance(argv, list) and len(argv) >= 3 and argv[:2] == ["python", "-B"], "Explicit Python argv required; no shell execution")
        target = argv[2]
        require(safe_relative(target) and target.endswith(".py") and target.startswith(("scripts/", "tests/")), "Unsafe validation script")
        require((root / target).is_file() and (root / target).resolve().is_relative_to(root.resolve()) and not (root / target).is_symlink(), "Required validation script missing or unsafe: " + target)
        paths.add(target)
        if target.startswith("tests/"):
            tests.add(target)
        for arg in argv[3:]:
            require(isinstance(arg, str), "Argument must be text")
            if arg in {"--check", "--check-requests", "--records"}:
                continue
            require(safe_relative(arg) and arg.endswith(".json") and (root / arg).is_file() and (root / arg).resolve().is_relative_to(root.resolve()) and not (root / arg).is_symlink(), "Unsupported argument or missing/unsafe JSON input: " + arg)
            paths.add(arg)
        require("--records" not in argv or argv.index("--records") + 1 < len(argv) and argv[argv.index("--records") + 1].endswith(".json"), "Records argument needs explicit JSON input")
    required_tests = plan.get("required_tests")
    require(isinstance(required_tests, list) and required_tests and len(required_tests) == len(set(required_tests)) and tests == set(required_tests), "Required tests differ from executed explicit test paths")
    required_ids = plan.get("required_step_ids")
    require(isinstance(required_ids, list) and len(required_ids) == len(set(required_ids)) and ids == set(required_ids), "Required checks differ from executed steps")
    required_paths = plan.get("required_paths")
    require(isinstance(required_paths, list) and required_paths, "Required artifact paths must be enumerated")
    for path in required_paths:
        require(safe_relative(path) and (root / path).is_file() and (root / path).resolve().is_relative_to(root.resolve()) and not (root / path).is_symlink(), "Required artifact missing or unsafe: " + str(path))
        paths.add(path)
    return {"steps": len(steps), "test_scripts": len(tests), "required_paths": len(paths)}, paths


def tracked_hashes(root):
    paths = [x for x in git(root, "ls-files", "-z").decode("utf-8").split("\0") if x]
    result = {}
    for name in paths:
        path = root / name
        if path.is_symlink():
            raw = ("symlink:" + os.readlink(path)).encode()
        elif path.is_file():
            raw = path.read_bytes()
        else:
            result[name] = None
            continue
        result[name] = hashlib.sha256(raw).hexdigest()
    return result


def status(root):
    return git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all")


def validate_receipt_path(path, root=ROOT, runner_temp=None):
    resolved = Path(path).resolve()
    require(not resolved.is_relative_to(root.resolve()), "Runtime receipt must stay outside the repository")
    allowed = [Path("/tmp").resolve()]
    if runner_temp:
        allowed.append(Path(runner_temp).resolve())
    require(any(resolved.is_relative_to(directory) and resolved != directory for directory in allowed), "Runtime receipt must be under /tmp or RUNNER_TEMP")
    return resolved


def execute(plan, root=ROOT, run=subprocess.run):
    root = Path(root).resolve()
    require(sys.version_info >= (3, 11), "Portfolio checks require Python >=3.11")
    summary, paths = check_plan(plan, root)
    require(not status(root), "Exact-commit runtime acceptance requires a clean worktree/index, including all nonignored untracked files")
    for path in sorted(paths | {PLAN, RUNNER}):
        require(bool(git(root, "ls-files", "--error-unmatch", "--", path).strip()), "Validation control/input is not tracked: " + path)
    raw_plan = (root / PLAN).read_bytes()
    require(json.loads(raw_plan) == plan, "Execution plan differs from committed plan bytes")
    before = tracked_hashes(root)
    head = git(root, "rev-parse", "HEAD").decode().strip()
    tree = git(root, "rev-parse", "HEAD^{tree}").decode().strip()
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    receipt = {"schema_version": 1, "suite": "public-portfolio", "status": "RUNNING", "tested_commit": head, "tested_tree": tree, "initial_tracked_clean": True, "initial_worktree_clean_including_untracked": True, "plan_sha256": hashlib.sha256(raw_plan).hexdigest(), "environment": {"python": sys.version.split()[0], "python_implementation": sys.implementation.name, "python_minimum": "3.11", "external_packages_required": [], "runtime_version_is_observed_not_pinned": True}, "started_at": started, "plan_summary": summary, "results": [], "passed_steps": 0, "changed_tracked_files": [], "candidate_advanced": False, "savings_amount": None, "limitations": "Offline software/declaration acceptance only; no UN evidence authentication, operational adjudication, institutional authority or benefit realization. Legacy A12 runtime groups remain separately required."}
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment.pop("PYTHONPATH", None)
    failed = False
    for step in plan["steps"]:
        print(f"[public-portfolio] {step['id']}", flush=True)
        argv = [sys.executable, *step["argv"][1:]]
        started_step = time.monotonic()
        try:
            result = run(argv, cwd=root, env=environment, check=False, capture_output=True, text=True, timeout=plan["timeout_seconds"])
            code, stdout, stderr = result.returncode, result.stdout or "", result.stderr or ""
        except subprocess.TimeoutExpired as error:
            code = 124
            stdout = error.stdout or ""
            stderr = error.stderr or ""
            if isinstance(stdout, bytes):
                stdout = stdout.decode("utf-8", errors="replace")
            if isinstance(stderr, bytes):
                stderr = stderr.decode("utf-8", errors="replace")
            stderr += "\nDeclared step timeout exceeded."
        for output in (stdout, stderr):
            if output:
                print(output, end="" if output.endswith("\n") else "\n", flush=True)
        passed = code == 0
        failed = failed or not passed
        receipt["passed_steps"] += int(passed)
        receipt["results"].append({"id": step["id"], "argv": step["argv"], "exit_code": code, "status": "PASS" if passed else "FAIL", "duration_seconds": round(time.monotonic() - started_step, 6), "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(), "stderr_sha256": hashlib.sha256(stderr.encode()).hexdigest()})
    after = tracked_hashes(root)
    receipt["changed_tracked_files"] = sorted(path for path in set(before) | set(after) if before.get(path) != after.get(path))
    receipt["final_worktree_clean_including_untracked"] = not bool(status(root))
    receipt["final_head_unchanged"] = git(root, "rev-parse", "HEAD").decode().strip() == head
    mutated = bool(receipt["changed_tracked_files"]) or not receipt["final_worktree_clean_including_untracked"] or not receipt["final_head_unchanged"]
    receipt["status"] = "FAIL_WORKTREE_MUTATION" if mutated else "FAIL" if failed else "PASS"
    receipt["finished_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-plan", action="store_true")
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    target = None
    try:
        if args.receipt:
            target = validate_receipt_path(args.receipt, ROOT, os.environ.get("RUNNER_TEMP"))
        plan = json.loads((ROOT / PLAN).read_text())
        if args.check_plan:
            summary, _ = check_plan(plan)
            print(json.dumps({"status": "PASS_PLAN_STRUCTURE_NOT_RUNTIME", **summary}))
            return 0
        require(target is not None, "--receipt under /tmp or RUNNER_TEMP is required for runtime execution")
        result = execute(plan)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps({"status": result["status"], "passed_steps": result["passed_steps"], "receipt": str(target)}))
        return 0 if result["status"] == "PASS" else 1
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        if target:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps({"schema_version": 1, "suite": "public-portfolio", "status": "PREFLIGHT_FAILED_NO_RUNTIME_ATTESTATION", "initial_tracked_clean": False, "error": str(error), "candidate_advanced": False, "savings_amount": None}, indent=2) + "\n")
        print("FAIL: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
