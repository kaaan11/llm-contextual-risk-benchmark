"""Deterministic fake clock/adapter timings, without a network or model."""
from unittest.mock import patch

import pytest

from benchmark.logging import InMemoryResponseLogger
from benchmark.metadata import ExperimentMetadata
from benchmark.metrics import calculate_metrics
from benchmark.retry import RetryPolicy
from benchmark.runner import EvaluationRunner
from benchmark.types import AdapterResponse, EvaluationCase, ModelSpec


@pytest.mark.parametrize("failure", [False, True])
def test_client_attempt_timings_do_not_claim_server_inference(failure):
    now = [0.0]
    calls = [0]
    model = ModelSpec("mock", "clock-test", "1")

    class Adapter:
        def generate(self, request):
            calls[0] += 1
            now[0] += 0.020
            if calls[0] == 1 or failure:
                raise TimeoutError("fake timeout")
            return AdapterResponse("Hello.", model, "mock")

    def sleeper(delay):
        # Measured sleep differs from policy-requested delay, testing actual wall time.
        now[0] += delay + 0.010

    metadata = ExperimentMetadata(
        "clock-test", "abstract", "abstract", "1", model, "test", "current_prompt_only",
    )
    case = EvaluationCase("abstract", "single_turn", (),
                          ({"role": "user", "content": {"text": "Say hello."}},))
    logger = InMemoryResponseLogger()
    with patch("benchmark.runner.perf_counter", side_effect=lambda: now[0]), \
         patch("benchmark.runner.sleep", side_effect=sleeper):
        result = EvaluationRunner(
            Adapter(), metadata, logger,
            retry_policy=RetryPolicy(max_attempts=2, initial_backoff_s=0.1),
        ).run([case])[0]
    assert result.attempts == calls[0] == 2
    assert result.status == ("error" if failure else "success")
    assert result.provider_call_latency_ms == pytest.approx(150.0)
    assert result.provider_round_trip_latency_ms == pytest.approx(40.0)
    assert result.retry_overhead_ms == pytest.approx(110.0)
    assert result.pure_inference_latency_ms is None
    assert result.pure_inference_latency_status == "unavailable_no_server_timing"
    assert result.to_log_dict()["provider_round_trip_latency_ms"] == pytest.approx(40.0)
    metrics = calculate_metrics([result])
    assert metrics["pure_inference_latency_ms"]["n"] == 0
    assert metrics["pure_inference_latency_status_counts"] == {"unavailable_no_server_timing": 1}
    assert metrics["provider_round_trip_latency_ms"]["n"] == (0 if failure else 1)
    assert metrics["provider_round_trip_latency_ms"]["p95"] is None
