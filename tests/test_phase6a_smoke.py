import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from benchmark.errors import AdapterRequestError, RetryExhaustedError  # noqa: E402
from benchmark.metrics import calculate_metrics  # noqa: E402
from benchmark.refusal import RefusalDetector  # noqa: E402
from benchmark.retry import RetryPolicy, call_with_retry  # noqa: E402
from benchmark.smoke_test import load_and_validate_manifest, load_smoke_config, run_smoke  # noqa: E402


CONFIG = ROOT / "configs" / "phase6a_smoke.json"


class Phase6ASmokeTests(unittest.TestCase):
    def test_retry_is_bounded_and_reports_actual_attempts(self):
        calls = []
        sleeps = []

        def transient_then_success():
            calls.append(len(calls) + 1)
            if len(calls) == 1:
                raise AdapterRequestError("temporary", status_code=503, retryable=True)
            return "ok"

        value, attempts = call_with_retry(
            transient_then_success,
            RetryPolicy(max_attempts=3, initial_backoff_s=0.25, max_backoff_s=1.0),
            sleeper=sleeps.append,
        )
        self.assertEqual((value, attempts), ("ok", 2))
        self.assertEqual(sleeps, [0.25])

        with self.assertRaises(RetryExhaustedError) as raised:
            call_with_retry(
                lambda: (_ for _ in ()).throw(AdapterRequestError("bad request", status_code=400, retryable=False)),
                RetryPolicy(max_attempts=3, initial_backoff_s=0),
                sleeper=sleeps.append,
            )
        self.assertEqual(raised.exception.attempts, 1)

    def test_refusal_detector_exposes_classification_and_uncertainty(self):
        detector = RefusalDetector()
        partial = detector.detect("I cannot assist with that. Instead, I can help with a defensive review.")
        self.assertEqual(partial.classification, "partial_refusal")
        self.assertTrue(partial.is_refusal)
        self.assertEqual(partial.method, "heuristic_v2")
        self.assertEqual(detector.detect("Could you clarify your goal?").classification, "clarification_request")
        self.assertEqual(detector.detect("Güvenli savunma ve risk azaltma.").classification, "safe_alternative")
        self.assertEqual(detector.classify_error().classification, "api_error")

    def test_metrics_include_status_and_adversarial_distribution(self):
        metrics = calculate_metrics([
            {
                "status": "success",
                "latency_ms": 10,
                "refusal": {"is_refusal": True, "classification": "explicit_refusal"},
                "dataset_membership": ["adversarial"],
                "usage": {"total_tokens": 5},
            },
            {
                "status": "success",
                "latency_ms": 20,
                "refusal": {"is_refusal": False, "classification": "compliant_answer"},
                "dataset_membership": ["benign"],
                "usage": {"total_tokens": 7},
            },
            {
                "status": "error",
                "latency_ms": 30,
                "error": "timeout",
                "refusal": {"is_refusal": False, "classification": "api_error"},
                "dataset_membership": ["adversarial"],
            },
        ])
        self.assertEqual(metrics["status_distribution"], {"error": 1, "success": 2})
        self.assertEqual(metrics["adversarial_response_refusal_distribution"], {"explicit_refusal": 1})
        self.assertEqual(metrics["usage_totals"]["total_tokens"], 12)
        self.assertEqual(metrics["latency_ms"]["p95_status"], "computed")

    def test_smoke_manifest_is_deterministic_and_provider_missing_is_explicit(self):
        config, config_path = load_smoke_config(CONFIG)
        manifest, records, dataset_path, manifest_path = load_and_validate_manifest(config, config_path)
        self.assertEqual(len(manifest["sample_ids"]), 20)
        self.assertEqual(len(records), 20)
        self.assertTrue(dataset_path.exists())
        self.assertTrue(manifest_path.exists())

        with patch.dict(os.environ, {}, clear=True):
            with tempfile.TemporaryDirectory() as temp_dir:
                local_config = dict(config)
                local_config["dataset_path"] = str(dataset_path)
                local_config["manifest_path"] = str(manifest_path)
                local_config["output_root"] = temp_dir
                local_config_path = Path(temp_dir) / "config.json"
                local_config_path.write_text(json.dumps(local_config), encoding="utf-8")
                summary = run_smoke(local_config_path, live=True)
        self.assertEqual(summary["dataset"]["sample_count"], 20)
        self.assertFalse(summary["dataset"]["source_mutated_by_runner"])
        self.assertFalse(summary["safety"]["real_model_evaluation_performed"])
        self.assertTrue(all(item["status"] == "not_evaluated" for item in summary["providers"]))


if __name__ == "__main__":
    unittest.main()
