import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class Phase7SchemaAuditTests(unittest.TestCase):
    def test_phase7_schema_audit_remains_distinct_from_phase7b_construction(self):
        report_path = ROOT / "results" / "dataset_audit" / "phase7_schema_audit.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "schema_extension_implemented_no_samples")
        self.assertEqual(report["implemented_schema_version"], "0.2.0")
        self.assertTrue(report["schema_extension_implemented"])
        self.assertEqual(report["phase7b_status"], "constructed_pending_researcher_qc")
        self.assertEqual(report["phase7b_samples_created"], 50)
        self.assertEqual(report["samples_created"], 0)
        self.assertEqual(report["expert_annotations_created"], 0)
        self.assertEqual(report["model_evaluations_run"], 0)
        multiturn_dataset = ROOT / "dataset" / "pilot" / "multiturn" / "multiturn_dataset.json"
        self.assertTrue(multiturn_dataset.exists())

    def test_existing_schema_gaps_are_explicit(self):
        report = json.loads(
            (ROOT / "results" / "dataset_audit" / "phase7_schema_audit.json").read_text(encoding="utf-8")
        )
        support = report["existing_schema_support"]
        self.assertTrue(support["multi_turn_turns"])
        self.assertFalse(support["paired_evaluation_conditions"])
        self.assertFalse(support["expected_vs_observed_effect_separation"])
        self.assertFalse(support["authoring_provenance"])


if __name__ == "__main__":
    unittest.main()
