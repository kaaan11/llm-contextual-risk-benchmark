import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from scripts.phase7g_status import get_status_report
from scripts.adjudicate_blind import get_disagreements, run_adjudication_wizard
from scripts.review_context import get_pending_context_items, run_context_wizard
from scripts.decide_phase7g import get_pending_decision_items, run_decide_wizard


class Phase7GToolingTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp_dir.name)
        p1 = patch("scripts.adjudicate_blind.BLIND", self.tmp_path / "phase7g_blind_review.json")
        p2 = patch("scripts.review_context.QC", self.tmp_path / "phase7g_human_qc.json")
        p3 = patch("scripts.decide_phase7g.QC", self.tmp_path / "phase7g_human_qc.json")
        p1.start()
        p2.start()
        p3.start()
        self.addCleanup(p1.stop)
        self.addCleanup(p2.stop)
        self.addCleanup(p3.stop)
        self.addCleanup(self.tmp_dir.cleanup)

    def test_status_report_structure(self):
        rep = get_status_report()
        self.assertEqual(rep["total"], 50)
        self.assertIn("rater_a_done", rep)
        self.assertIn("rater_b_done", rep)
        self.assertIn("blockers", rep)
        self.assertFalse(rep["ready_for_phase8"])

    def test_get_disagreements_filters_correctly(self):
        sample = {
            "items": [
                {"blind_id": "B1", "annotation_status": "DISAGREEMENT_PENDING_ADJUDICATION"},
                {"blind_id": "B2", "annotation_status": "ADJUDICATED"},
                {"blind_id": "B3", "annotation_status": "PENDING"},
            ]
        }
        res = get_disagreements(sample)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["blind_id"], "B1")

    @patch("scripts.adjudicate_blind._load")
    def test_run_adjudication_wizard_no_disagreements(self, mock_load):
        mock_load.return_value = {"items": []}
        count = run_adjudication_wizard("adjudicator_1")
        self.assertEqual(count, 0)

    @patch("scripts.review_context._load")
    def test_run_context_wizard_no_pending(self, mock_load):
        mock_load.return_value = {"items": []}
        count = run_context_wizard("researcher_1")
        self.assertEqual(count, 0)

    @patch("scripts.decide_phase7g._load")
    def test_run_decide_wizard_no_pending(self, mock_load):
        mock_load.return_value = {"items": []}
        count = run_decide_wizard("lead_1")
        self.assertEqual(count, 0)

    def test_compute_agreement_stats_full_matrix(self):
        from scripts.phase7g_agreement import compute_agreement_stats

        items = [
            {"blind_id": "B1", "rater_a": {"isolated_prompt_valence_observed": "clearly_benign"}, "rater_b": {"isolated_prompt_valence_observed": "clearly_benign"}},
            {"blind_id": "B2", "rater_a": {"isolated_prompt_valence_observed": "probably_benign"}, "rater_b": {"isolated_prompt_valence_observed": "probably_benign"}},
            {"blind_id": "B3", "rater_a": {"isolated_prompt_valence_observed": "ambiguous_dual_use"}, "rater_b": {"isolated_prompt_valence_observed": "probably_concerning"}},
            {"blind_id": "B4", "rater_a": {"isolated_prompt_valence_observed": "clearly_benign"}, "rater_b": {"isolated_prompt_valence_observed": "clearly_concerning"}}, # severe divergence
        ]
        stats = compute_agreement_stats(items)
        self.assertEqual(stats["n_paired"], 4)
        self.assertEqual(stats["percent_agreement"], 50.0) # 2/4 exact match
        self.assertIsNotNone(stats["unweighted_kappa"])
        self.assertIsNotNone(stats["linear_weighted_kappa"])
        self.assertIsNotNone(stats["quadratic_weighted_kappa"])
        self.assertEqual(len(stats["severe_divergences"]), 1)
        self.assertEqual(stats["severe_divergences"][0]["blind_id"], "B4")
        self.assertEqual(stats["severe_divergences"][0]["delta"], 4)


if __name__ == "__main__":
    unittest.main()
