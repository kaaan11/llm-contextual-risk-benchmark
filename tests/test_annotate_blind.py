import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from scripts.annotate_blind import (
    VALENCE_CHOICES,
    CONFIDENCE_CHOICES,
    get_pending_items,
    run_wizard,
)


class AnnotateBlindTests(unittest.TestCase):
    def test_get_pending_items_filters_correctly(self):
        sample_data = {
            "items": [
                {"blind_id": "B1", "rater_a": {"isolated_prompt_valence_observed": "probably_benign"}},
                {"blind_id": "B2", "rater_a": {"isolated_prompt_valence_observed": None}},
                {"blind_id": "B3", "rater_a": {}},
            ]
        }
        pending = get_pending_items(sample_data, "rater_a")
        self.assertEqual(len(pending), 2)
        self.assertEqual(pending[0]["blind_id"], "B2")
        self.assertEqual(pending[1]["blind_id"], "B3")

    def test_valence_choices_mapping(self):
        self.assertEqual(VALENCE_CHOICES["1"], "clearly_benign")
        self.assertEqual(VALENCE_CHOICES["3"], "ambiguous_dual_use")
        self.assertEqual(VALENCE_CHOICES["5"], "clearly_concerning")

    @patch("scripts.annotate_blind._load")
    def test_run_wizard_no_pending(self, mock_load):
        mock_load.return_value = {
            "items": [
                {"blind_id": "B1", "rater_a": {"isolated_prompt_valence_observed": "clearly_benign"}}
            ]
        }
        count = run_wizard("rater_a", "test-user")
        self.assertEqual(count, 0)

    @patch("scripts.annotate_blind._load")
    def test_run_wizard_quit_early(self, mock_load):
        mock_load.return_value = {
            "items": [
                {"blind_id": "B1", "canonical_final_prompt": "test prompt", "rater_a": {"isolated_prompt_valence_observed": None}}
            ]
        }
        inputs = iter(["q"])
        count = run_wizard("rater_a", "test-user", input_func=lambda _: next(inputs))
        self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
