import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.build_researcher_design import (  # noqa: E402
    DESIGN_FIELDS,
    build_design_spec,
    validate_design,
)


class MultiTurnResearcherDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = build_design_spec()
        cls.validation = validate_design(cls.spec)

    def test_design_has_exactly_50_rows_and_requested_distribution(self):
        self.assertEqual(self.validation["status"], "valid")
        self.assertEqual(self.validation["rows_checked"], 50)
        self.assertEqual(self.validation["category_distribution"], {
            "context_changes_interpretation": 20,
            "context_has_no_material_effect": 15,
            "legitimate_technical_context": 10,
            "ambiguous_or_borderline": 5,
        })

    def test_design_turn_targets_are_preserved(self):
        self.assertEqual(self.validation["turn_count_distribution"], {
            "2": 10,
            "3": 15,
            "4": 15,
            "5": 7,
            "6": 3,
        })

    def test_all_design_decisions_are_explicitly_ai_proposed(self):
        for row in self.spec["rows"]:
            self.assertEqual(row["researcher_approval"], "PENDING_RESEARCHER_INPUT")
            self.assertEqual(set(row["field_status"]), set(DESIGN_FIELDS))
            self.assertTrue(all(value == "AI_PROPOSED" for value in row["field_status"].values()))
            self.assertFalse(row["full_conversation_generated"])
        self.assertEqual(self.validation["researcher_input_rows"], 50)
        self.assertEqual(self.validation["researcher_input_fields"], 450)
        self.assertEqual(self.validation["researcher_approval_claims"], 0)

    def test_design_contains_no_full_conversation_fields(self):
        forbidden = {"turns", "messages", "canonical_final_prompt", "evaluations"}
        for row in self.spec["rows"]:
            self.assertTrue(forbidden.isdisjoint(row))
            self.assertIsNone(row["source_seed"])

    def test_written_design_and_preservation_label_exist(self):
        design_path = ROOT / "dataset" / "pilot" / "multiturn" / "design_specification.json"
        markdown_path = ROOT / "docs" / "multiturn_researcher_design.md"
        validation_path = ROOT / "results" / "dataset_audit" / "multiturn_design_validation.json"
        label_path = ROOT / "dataset" / "pilot" / "multiturn" / "EXPLORATORY_DRAFT_V0.1_TR.json"
        for path in (design_path, markdown_path, validation_path, label_path):
            self.assertTrue(path.exists(), path)
        written = json.loads(design_path.read_text(encoding="utf-8"))
        label = json.loads(label_path.read_text(encoding="utf-8"))
        self.assertEqual(len(written["rows"]), 50)
        self.assertEqual(label["profile_id"], "EXPLORATORY_DRAFT_V0.1_TR")
        self.assertTrue(label["original_files_preserved"])
        self.assertFalse(label["provenance_rewritten"])


if __name__ == "__main__":
    unittest.main()
