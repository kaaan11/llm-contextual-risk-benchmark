import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.build_multiturn_researcher_review import (  # noqa: E402
    DEFAULT_MARKDOWN,
    DEFAULT_REVIEW,
    build_review_spec,
    make_revision_entry,
    validate_review,
)
from scripts.build_researcher_design import build_design_spec  # noqa: E402


class MultiTurnResearcherReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review = build_review_spec(build_design_spec())

    def test_review_has_exactly_50_pending_entries(self):
        report = validate_review(self.review)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["entries_checked"], 50)
        self.assertEqual(report["pending_samples"], 50)
        self.assertEqual(report["approved_samples"], 0)
        self.assertTrue(all(entry["review_decision"] == "PENDING" for entry in self.review["entries"]))
        self.assertTrue(all(entry["researcher_approved"] is False for entry in self.review["entries"]))

    def test_category_and_effect_distributions_are_separate(self):
        report = validate_review(self.review)
        self.assertEqual(sum(report["category_distribution"].values()), 50)
        self.assertEqual(sum(report["context_effect_distribution"].values()), 50)
        self.assertNotEqual(report["category_distribution"], report["context_effect_distribution"])

    def test_review_entries_have_required_researcher_fields(self):
        required = {
            "sample_id",
            "review_decision",
            "researcher_approved",
            "researcher_notes",
            "current_design",
        }
        for entry in self.review["entries"]:
            self.assertTrue(required.issubset(entry))
            self.assertIsNone(entry["researcher_notes"])

    def test_rejected_sample_cannot_be_approved_without_new_review(self):
        review = copy.deepcopy(self.review)
        review["entries"][0]["review_decision"] = "REJECT"
        review["entries"][0]["researcher_approved"] = True
        report = validate_review(review)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("rejected sample" in error for error in report["errors"]))

    def test_revision_preserves_original_design_snapshot(self):
        entry = copy.deepcopy(self.review["entries"][0])
        original = copy.deepcopy(entry["original_design"])
        entry["review_decision"] = "REVISE"
        revised = make_revision_entry(
            entry,
            {"design_confidence": "medium"},
            "Researcher requests a more cautious confidence level.",
            "0.1.1",
        )
        self.assertEqual(revised["original_design"], original)
        self.assertEqual(revised["current_design"]["design_confidence"], "medium")
        self.assertEqual(revised["revised_version"], "0.1.1")
        self.assertEqual(revised["review_decision"], "PENDING")
        self.assertFalse(revised["researcher_approved"])

    def test_written_review_table_has_exactly_50_entries(self):
        self.assertTrue(DEFAULT_REVIEW.exists())
        self.assertTrue(DEFAULT_MARKDOWN.exists())
        review = json.loads(DEFAULT_REVIEW.read_text(encoding="utf-8"))
        markdown_lines = DEFAULT_MARKDOWN.read_text(encoding="utf-8").splitlines()
        entry_lines = [line for line in markdown_lines if line.startswith("| EN-")]
        self.assertEqual(len(review["entries"]), 50)
        self.assertEqual(len(entry_lines), 50)
        self.assertNotIn("canonical_final_prompt", DEFAULT_MARKDOWN.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
