import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from benchmark.adapters import AnthropicAdapter, MockAdapter, OpenAIAdapter, OpenWeightAdapter  # noqa: E402
from benchmark.dry_run import run_dry_run  # noqa: E402
from benchmark.errors import AdapterConfigurationError
from benchmark.loader import DatasetLoader
from benchmark.logging import InMemoryResponseLogger, JsonlResponseLogger
from benchmark.metadata import ExperimentMetadata
from benchmark.metrics import calculate_metrics, percentile
from benchmark.refusal import RefusalDetector
from benchmark.runner import EvaluationRunner
from benchmark.types import AdapterResponse, EvaluationCase, EvaluationResult, ModelSpec  # noqa: E402


DATASET = ROOT / "dataset" / "pilot" / "pilot_dataset.json"


def metadata(context_mode="conversation_context", max_samples=3):
    return ExperimentMetadata(
        run_id="unit-run-001",
        experiment_id="unit-experiment",
        dataset_id="unit-dataset",
        dataset_version="0.1.0",
        model=ModelSpec(provider="mock", name="mock-model", version="0.1.0"),
        configuration="baseline",
        context_mode=context_mode,
        max_samples=max_samples,
    )


class BenchmarkFrameworkTests(unittest.TestCase):
    def test_loader_reads_and_filters_pilot_dataset(self):
        bundle = DatasetLoader().load(DATASET, limit=3, memberships=["benign"])
        self.assertEqual(len(bundle.records), 3)
        self.assertTrue(all("benign" in record["dataset_membership"] for record in bundle.records))
        self.assertEqual(bundle.dataset_version, "0.1.0")

    def test_mock_adapter_is_deterministic_without_network(self):
        adapter = MockAdapter({"sample-1": "mock response"})
        request = self._request("sample-1")
        response = adapter.generate(request)
        self.assertEqual(response.text, "mock response")
        self.assertEqual(len(adapter.calls), 1)

    def test_provider_adapters_use_injected_transport(self):
        captured = []

        def transport(url, headers, payload, timeout):
            captured.append((url, dict(headers), dict(payload), timeout))
            return {"id": "provider-response", "output_text": "safe response", "usage": {"total_tokens": 3}}

        request = self._request("sample-2", provider="openai")
        with patch.dict(os.environ, {"OPENAI_API_KEY": "unit-test-placeholder"}, clear=False):
            response = OpenAIAdapter(transport=transport).generate(request)
        self.assertEqual(response.text, "safe response")
        self.assertIn("Authorization", captured[0][1])
        self.assertNotIn("unit-test-placeholder", json.dumps(response.metadata))

    def test_anthropic_and_open_weight_normalize_common_text(self):
        anthropic = AnthropicAdapter(transport=lambda *args: {"content": [{"type": "text", "text": "anthropic"}]})
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "unit-test-placeholder"}, clear=False):
            response = anthropic.generate(self._request("sample-3", provider="anthropic"))
        self.assertEqual(response.text, "anthropic")

        open_weight = OpenWeightAdapter(
            endpoint="http://localhost:8000/mock",
            transport=lambda *args: {"choices": [{"message": {"content": "open-weight"}}]},
        )
        self.assertEqual(open_weight.generate(self._request("sample-4", provider="open_weight")).text, "open-weight")

    def test_provider_without_credentials_fails_before_network(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(AdapterConfigurationError):
                OpenAIAdapter(transport=lambda *args: self.fail("network transport çağrılmamalı")).generate(
                    self._request("sample-5", provider="openai")
                )

    def test_runner_selects_current_prompt_only_without_prior_user_turns(self):
        case = EvaluationCase(
            sample_id="context-1",
            record_type="multi_turn",
            dataset_membership=("multi_turn",),
            turns=(
                {"role": "system", "content": {"text": "system"}},
                {"role": "user", "content": {"text": "old user"}},
                {"role": "assistant", "content": {"text": "old assistant"}},
                {"role": "user", "content": {"text": "current user"}},
            ),
        )
        adapter = MockAdapter({"context-1": "I cannot assist with that."})
        logger = InMemoryResponseLogger()
        runner = EvaluationRunner(adapter, metadata("current_prompt_only", max_samples=1), logger)
        results = runner.run([case])
        self.assertEqual([message["content"] for message in adapter.calls[0].messages], ["system", "current user"])
        self.assertTrue(results[0].refusal.is_refusal)
        self.assertEqual(results[0].input_turn_count, 2)

    def test_runner_logs_errors_without_exposing_credentials(self):
        class FailingAdapter:
            provider = "mock"

            def generate(self, request):
                raise RuntimeError("provider unavailable")

        case = EvaluationCase("error-1", "single_turn", ("benign",), ({"role": "user", "content": {"text": "hello"}},))
        logger = InMemoryResponseLogger()
        result = EvaluationRunner(FailingAdapter(), metadata(max_samples=1), logger).run([case])[0]
        self.assertIsNotNone(result.error)
        self.assertIsNone(result.response_text)

    def test_response_logger_and_artifacts_are_jsonl_and_metadata_only(self):
        case = EvaluationCase("log-1", "single_turn", ("benign",), ({"role": "user", "content": {"text": "hello"}},))
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "responses.jsonl"
            logger = JsonlResponseLogger(path)
            results = EvaluationRunner(MockAdapter(default_response="safe"), metadata(max_samples=1), logger).run([case])
            logger.close()
            line = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(line["sample_id"], "log-1")
            self.assertIn("request_digest", line)
            self.assertEqual(results[0].error, None)

    def test_metrics_do_not_invent_asr_without_explicit_outcomes(self):
        result = EvaluationResult(
            evaluation_id="e1",
            run_id="r1",
            sample_id="s1",
            model=ModelSpec("mock", "m", "v"),
            configuration="baseline",
            context_mode="current_prompt_only",
            response_text="safe",
            request_id="q1",
            latency_ms=10.0,
            refusal=None,
            dataset_membership=("benign",),
        )
        metrics = calculate_metrics([result])
        self.assertIsNone(metrics["attack_success_rate"])
        self.assertEqual(metrics["attack_success_rate_status"], "not_computable_without_ground_truth")

    def test_metrics_compute_explicit_outcomes_and_latency(self):
        rows = [
            {"latency_ms": 10, "refusal": {"is_refusal": True}, "dataset_membership": ["adversarial"], "attack_success": False},
            {"latency_ms": 20, "refusal": {"is_refusal": False}, "dataset_membership": ["benign"], "attack_success": True},
            {"latency_ms": 30, "refusal": {"is_refusal": True}, "dataset_membership": ["adversarial"], "attack_success": True},
        ]
        metrics = calculate_metrics(rows)
        self.assertAlmostEqual(metrics["attack_success_rate"], 2 / 3)
        self.assertEqual(metrics["latency_ms"]["p95"], 29.0)
        self.assertAlmostEqual(metrics["refusal_rate_by_membership"]["adversarial"]["refusal_rate"], 1.0)

    def test_refusal_detector_is_transparent(self):
        detector = RefusalDetector()
        refusal = detector.detect("Bu isteğe yardımcı olamam; güvenli bir alternatif sunabilirim.")
        self.assertTrue(refusal.is_refusal)
        self.assertEqual(refusal.method, "heuristic_v2")
        self.assertFalse(detector.detect("Güvenli bir tasarım önerebilirim.").is_refusal)

    def test_mock_dry_run_writes_three_safe_artifacts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "dry-run"
            results = run_dry_run(DATASET, output_dir, limit=3)
            self.assertEqual(len(results), 3)
            self.assertTrue((output_dir / "responses.jsonl").exists())
            metrics = json.loads((output_dir / "metrics.json").read_text(encoding="utf-8"))
            self.assertEqual(metrics["total_requests"], 3)
            self.assertEqual(metrics["attack_success_rate_status"], "not_computable_without_ground_truth")
            self.assertGreaterEqual(metrics["refusal_count"], 1)

    def test_percentile_empty_and_invalid_quantile(self):
        self.assertIsNone(percentile([], 0.95))
        with self.assertRaises(ValueError):
            percentile([1, 2], 1.1)

    def test_client_round_trip_and_retry_overhead_isolated(self):
        from benchmark.errors import AdapterRequestError
        from benchmark.retry import RetryPolicy

        calls = 0

        def flaking_generator(request):
            nonlocal calls
            calls += 1
            if calls == 1:
                raise AdapterRequestError("transient rate limit", status_code=429, retryable=True)
            return AdapterResponse(text="recovered", model=ModelSpec("mock", "model", "0.1.0"), provider="mock")

        adapter = MockAdapter()
        adapter.generate = flaking_generator
        logger = InMemoryResponseLogger()
        runner = EvaluationRunner(
            adapter,
            metadata(),
            logger,
            retry_policy=RetryPolicy(max_attempts=2, initial_backoff_s=0.05),
        )
        case = EvaluationCase(
            "sample-1",
            "single_turn",
            ("benign",),
            ({"role": "user", "content": {"text": "hello"}},),
        )
        results = runner.run([case])
        self.assertEqual(len(results), 1)
        res = results[0]
        self.assertEqual(res.status, "success")
        self.assertEqual(res.attempts, 2)
        self.assertIsNotNone(res.retry_overhead_ms)
        self.assertGreaterEqual(res.retry_overhead_ms, 30.0)
        self.assertIsNone(res.pure_inference_latency_ms)
        self.assertEqual(res.pure_inference_latency_status, "unavailable_no_server_timing")
        self.assertIsNotNone(res.provider_round_trip_latency_ms)
        self.assertLess(res.provider_round_trip_latency_ms, res.provider_call_latency_ms)
        metrics = calculate_metrics(results)
        self.assertIn("pure_inference_latency_ms", metrics)
        self.assertIn("retry_overhead_ms", metrics)
        self.assertEqual(metrics["retry_overhead_ms"]["n"], 1)
        self.assertGreaterEqual(metrics["retry_overhead_ms"]["total_ms"], 30.0)

    def test_stratified_by_assistant_stance(self):
        from benchmark.metrics import classify_assistant_stance_stratum

        self.assertEqual(classify_assistant_stance_stratum("RI-AM-001_A"), "assistant_turn_shared")
        self.assertEqual(classify_assistant_stance_stratum("RI-DU-005_B"), "assistant_turn_differing")
        self.assertEqual(classify_assistant_stance_stratum("RI-NH-002_C"), "assistant_turn_differing")
        self.assertEqual(classify_assistant_stance_stratum("unknown_id"), "unspecified")

        rows = [
            {"sample_id": "RI-AM-001_B", "status": "success", "refusal": {"is_refusal": False}, "latency_ms": 10.0},
            {"sample_id": "RI-AM-002_C", "status": "success", "refusal": {"is_refusal": True}, "latency_ms": 10.0},
            {"sample_id": "RI-DU-001_B", "status": "success", "refusal": {"is_refusal": False}, "latency_ms": 10.0},
            {"sample_id": "RI-DU-001_C", "status": "success", "refusal": {"is_refusal": True}, "latency_ms": 10.0},
        ]
        metrics = calculate_metrics(rows)
        strata = metrics["stratified_by_assistant_stance"]
        self.assertIn("assistant_turn_shared", strata)
        self.assertIn("assistant_turn_differing", strata)
        self.assertEqual(strata["assistant_turn_shared"]["n"], 2)
        self.assertEqual(strata["assistant_turn_shared"]["refusals"], 1)
        self.assertEqual(strata["assistant_turn_shared"]["refusal_rate"], 0.5)
        self.assertEqual(strata["assistant_turn_differing"]["n"], 2)
        self.assertEqual(strata["assistant_turn_differing"]["refusals"], 1)

    @staticmethod
    def _request(sample_id, provider="mock"):
        from benchmark.types import GenerationRequest

        return GenerationRequest(
            sample_id=sample_id,
            messages=({"role": "user", "content": "hello"},),
            model=ModelSpec(provider, "model", "0.1.0"),
            request_id=f"request-{sample_id}",
        )


if __name__ == "__main__":
    unittest.main()
