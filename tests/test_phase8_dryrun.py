import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from scripts.run_phase8_mock_dryrun import (
    build_cases_from_stimuli,
    build_synthetic_responses,
    run_phase8_dryrun,
)


class Phase8DryRunTests(unittest.TestCase):
    def test_build_cases_matches_171_conditions(self):
        cases = build_cases_from_stimuli()
        self.assertEqual(len(cases), 171)
        rids = {c.task_metadata["research_item_id"] for c in cases}
        self.assertEqual(len(rids), 50)

    def test_synthetic_responses_cover_all_cases(self):
        cases = build_cases_from_stimuli()
        responses = build_synthetic_responses(cases)
        self.assertEqual(len(responses), 171)
        for c in cases:
            self.assertIn(c.sample_id, responses)

    def test_dry_run_executes_and_writes_metrics(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "test-dryrun"
            metrics = run_phase8_dryrun(output_dir=out, limit=5)
            self.assertEqual(metrics["total_requests"], 5)
            self.assertEqual(metrics["completed_requests"], 5)
            self.assertIn("stratified_by_assistant_stance", metrics)
            self.assertIn("pure_inference_latency_ms", metrics)
            self.assertTrue((out / "responses.jsonl").exists())
            self.assertTrue((out / "metrics.json").exists())


if __name__ == "__main__":
    unittest.main()
