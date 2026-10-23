#!/usr/bin/env python3
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("workflow_execution",ROOT/"scripts/build_workflow_execution.py")
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class WorkflowExecutionTests(unittest.TestCase):
    def test_exact_population(self):
        value=module.build()
        self.assertEqual(value["counts"]["total_entries"],122)
        self.assertEqual(value["counts"]["fixed_tasks"],114)
        self.assertEqual(len([t for t in value["tasks"] if t["task_id"].startswith("X")]),21)

    def test_missing_or_duplicate_task_rejected(self):
        value=module.build()
        value["tasks"][-1]=copy.deepcopy(value["tasks"][0])
        with self.assertRaises(ValueError):
            module.validate(value)

    def test_fake_execution_or_closed_state_rejected(self):
        for mutation in ("closed","executed"):
            value=module.build()
            row=next(t for t in value["tasks"] if t["task_id"]=="X01")
            if mutation=="closed":
                row["artifact_delivery_status"]="CLOSED_COMPLETE"
            else:
                row["completion_evidence"]["substantive_audit_completed"]=True
            with self.assertRaises(ValueError):
                module.validate(value)

    def test_conditional_steps_are_templates(self):
        value=module.build()
        self.assertEqual([g["status"] for g in value["completion_gates"]],["PARTIAL","PARTIAL","BLOCKED","BLOCKED"])
        self.assertTrue(all(t["work_product_mode"]=="TEMPLATE_NOT_EXECUTED" for t in value["tasks"] if t["task_id"].startswith("W9")))

    def test_blocked_task_cannot_be_relabelled_as_research_delivery(self):
        value=module.build()
        next(t for t in value["tasks"] if t["task_id"]=="I02")["work_product_mode"]="PUBLIC_RESEARCH_OUTPUT"
        with self.assertRaises(ValueError):
            module.validate(value)

    def test_outputs_deterministic(self):
        self.assertEqual(module.outputs(),module.outputs())
        for path, content in module.outputs().items():
            self.assertEqual((ROOT/path).read_text(encoding="utf-8"),content)


if __name__=="__main__":
    unittest.main()
