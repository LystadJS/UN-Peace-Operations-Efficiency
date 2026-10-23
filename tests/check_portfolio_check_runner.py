#!/usr/bin/env python3
"""Exercise clean-commit receipts, failures, mutation detection and path controls."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("portfolio_runner", ROOT / "scripts/run_portfolio_checks.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for folder in ("scripts", "tests", "data/portfolio"):
            (self.root / folder).mkdir(parents=True)
        (self.root / runner.RUNNER).write_text("# SYNTHETIC runner control fixture\n")
        (self.root / "tests/check_fixture.py").write_text("print('SYNTHETIC PASS')\n")
        self.plan = {"schema_version": 1, "python_minimum": "3.11", "network_required": False, "publishes": False, "timeout_seconds": 10, "required_tests": ["tests/check_fixture.py"], "required_step_ids": ["fixture"], "required_paths": ["tests/check_fixture.py"], "steps": [{"id": "fixture", "argv": ["python", "-B", "tests/check_fixture.py"], "tasks": ["SYNTHETIC_TEST_ONLY"]}]}
        self.write_plan()
        self.git("init", "-q")
        self.commit()

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, stderr=subprocess.STDOUT)

    def write_plan(self):
        (self.root / runner.PLAN).write_text(json.dumps(self.plan))

    def commit(self):
        self.git("add", ".")
        self.git("-c", "user.name=SyntheticTest", "-c", "user.email=synthetic@example.invalid", "commit", "-qm", "Synthetic test fixture only")

    def test_clean_commit_receipt_has_exact_commit_tree_plan_and_exit(self):
        result = runner.execute(self.plan, self.root)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["tested_commit"], self.git("rev-parse", "HEAD").decode().strip())
        self.assertEqual(result["tested_tree"], self.git("rev-parse", "HEAD^{tree}").decode().strip())
        self.assertEqual(result["results"][0]["exit_code"], 0)
        self.assertEqual(result["changed_tracked_files"], [])
        self.assertTrue(result["initial_worktree_clean_including_untracked"])

    def test_nonignored_untracked_file_blocks_runtime(self):
        (self.root / "untracked.txt").write_text("SYNTHETIC")
        with self.assertRaises(ValueError):
            runner.execute(self.plan, self.root)

    def test_staged_change_blocks_runtime(self):
        (self.root / "tests/check_fixture.py").write_text("print('changed')\n")
        self.git("add", ".")
        with self.assertRaises(ValueError):
            runner.execute(self.plan, self.root)

    def test_tracked_mutation_is_a_failure(self):
        def mutate(argv, **kwargs):
            (self.root / "tests/check_fixture.py").write_text("# changed by synthetic test\n")
            return subprocess.CompletedProcess(argv, 0, "", "")
        result = runner.execute(self.plan, self.root, mutate)
        self.assertEqual(result["status"], "FAIL_WORKTREE_MUTATION")
        self.assertEqual(result["changed_tracked_files"], ["tests/check_fixture.py"])

    def test_new_untracked_output_is_a_failure(self):
        def mutate(argv, **kwargs):
            (self.root / "unexpected-output.json").write_text("{}")
            return subprocess.CompletedProcess(argv, 0, "", "")
        result = runner.execute(self.plan, self.root, mutate)
        self.assertEqual(result["status"], "FAIL_WORKTREE_MUTATION")
        self.assertFalse(result["final_worktree_clean_including_untracked"])

    def test_failure_records_exit_and_runs_remaining_declared_checks(self):
        (self.root / "tests/check_second.py").write_text("print('second')\n")
        self.plan["required_tests"].append("tests/check_second.py")
        self.plan["required_step_ids"].append("second")
        self.plan["steps"].append({"id": "second", "argv": ["python", "-B", "tests/check_second.py"], "tasks": ["SYNTHETIC"]})
        self.write_plan()
        self.commit()
        codes = iter([9, 0])
        result = runner.execute(self.plan, self.root, lambda argv, **kwargs: subprocess.CompletedProcess(argv, next(codes), "", ""))
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual([row["exit_code"] for row in result["results"]], [9, 0])

    def test_missing_test_is_not_silently_skipped(self):
        (self.root / "tests/check_fixture.py").unlink()
        with self.assertRaises(ValueError):
            runner.check_plan(self.plan, self.root)

    def test_write_or_shell_arguments_rejected(self):
        for argument in ("--write", "; git push", "https://example.invalid/input.json"):
            with self.subTest(argument=argument):
                changed = json.loads(json.dumps(self.plan))
                changed["steps"][0]["argv"].append(argument)
                with self.assertRaises(ValueError):
                    runner.check_plan(changed, self.root)

    def test_receipt_location_and_symlink_escape(self):
        accepted = runner.validate_receipt_path("/tmp/synthetic-portfolio-receipt.json", self.root)
        self.assertEqual(accepted, Path("/tmp/synthetic-portfolio-receipt.json"))
        with self.assertRaises(ValueError):
            runner.validate_receipt_path(self.root / "receipt.json", self.root)
        with self.assertRaises(ValueError):
            runner.validate_receipt_path("/workspace/receipt.json", self.root)
        with tempfile.TemporaryDirectory() as other:
            link = Path(other) / "repo-link"
            link.symlink_to(self.root, target_is_directory=True)
            with self.assertRaises(ValueError):
                runner.validate_receipt_path(link / "receipt.json", self.root)

    def test_plan_test_coverage_cannot_silently_drop_required_test(self):
        self.plan["required_tests"].append("tests/missing_required.py")
        with self.assertRaises(ValueError):
            runner.check_plan(self.plan, self.root)


if __name__ == "__main__":
    unittest.main()
