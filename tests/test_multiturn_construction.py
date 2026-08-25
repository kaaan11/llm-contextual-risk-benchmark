import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dataset.validate import validate_dataset  # noqa: E402
from scripts.build_multiturn_dataset import (  # noqa: E402
    DEFAULT_CONFIG,
    build_dataset,
    load_json,
    validate_built_dataset,
    validate_construction_spec,
)


class MultiTurnConstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = load_json(DEFAULT_CONFIG)
        validate_construction_spec(cls.spec)
        cls.dataset = build_dataset(cls.spec)

    def test_plan_has_requested_category_distribution(self):
        counts = {}
        for candidate in self.spec["candidate_plan"]:
            category = candidate["target_category"]
            counts[category] = counts.get(category, 0) + 1
        self.assertEqual(counts, self.spec["target_categories"])

    def test_plan_has_requested_length_distribution(self):
        counts = {}
        for candidate in self.spec["candidate_plan"]:
            length = str(len(candidate["prior_turns"]) + 1)
            counts[length] = counts.get(length, 0) + 1
        self.assertEqual(counts, self.spec["target_turn_counts"])

    def test_built_dataset_is_valid(self):
        self.assertEqual(validate_dataset(self.dataset), [])
        report = validate_built_dataset(self.dataset)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(len(self.dataset["records"]), 50)

    def test_each_record_preserves_canonical_prompt_identity(self):
        for record in self.dataset["records"]:
            canonical = record["canonical_final_prompt"]
            self.assertEqual(record["evaluation_conditions"]["final_prompt_only"]["prompt"], canonical)
            self.assertEqual(record["turns"][-1]["content"]["text"], canonical)
            self.assertEqual(record["evaluation_conditions"]["full_context"]["final_prompt_turn_id"], record["turns"][-1]["turn_id"])
            self.assertIsNone(record["model_observed_effect"])

    def test_construction_does_not_claim_review_or_evaluation(self):
        for record in self.dataset["records"]:
            self.assertEqual(record["source"], "original")
            self.assertIsNone(record["source_seed"])
            self.assertEqual(record["authoring_method"], "llm_assisted_draft")
            self.assertEqual(record["generation_assistance"], "drafting_only")
            self.assertFalse(record["researcher_qc"])
            self.assertEqual(record["external_validation_status"], "not_reviewed")
            self.assertEqual(record["evaluations"], [])

    def test_existing_output_reports_match_constructed_dataset(self):
        dataset_path = ROOT / "dataset" / "pilot" / "multiturn" / "multiturn_dataset.json"
        validation_path = ROOT / "results" / "dataset_audit" / "multiturn_validation.json"
        statistics_path = ROOT / "results" / "dataset_audit" / "multiturn_statistics.json"
        if not (dataset_path.exists() and validation_path.exists() and statistics_path.exists()):
            self.skipTest("Construction pipeline çıktıları henüz oluşturulmadı")
        written = json.loads(dataset_path.read_text(encoding="utf-8"))
        validation = json.loads(validation_path.read_text(encoding="utf-8"))
        statistics = json.loads(statistics_path.read_text(encoding="utf-8"))
        self.assertEqual(len(written["records"]), 50)
        self.assertEqual(validation["status"], "valid")
        self.assertEqual(statistics["total_conversations"], 50)
        self.assertEqual(statistics["total_turns"], 178)


if __name__ == "__main__":
    unittest.main()
