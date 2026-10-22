#!/usr/bin/env python3
"""One harmless in-memory mock request; no research data, API or empirical result."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from benchmark.adapters.mock import MockAdapter
from benchmark.logging import InMemoryResponseLogger
from benchmark.metadata import ExperimentMetadata
from benchmark.metrics import calculate_metrics
from benchmark.runner import EvaluationRunner
from benchmark.types import EvaluationCase, ModelSpec


def preview() -> dict:
    case = EvaluationCase(
        sample_id="offline-example", record_type="single_turn", dataset_membership=(),
        turns=({"role": "user", "content": {"text": "Say hello."}},),
    )
    metadata = ExperimentMetadata(
        run_id="offline-preview", experiment_id="tooling-example", dataset_id="abstract-example",
        dataset_version="1", model=ModelSpec("mock", "fixed-response", "1"),
        configuration="offline-example", context_mode="current_prompt_only",
    )
    results = EvaluationRunner(
        MockAdapter(default_response="Hello."), metadata, InMemoryResponseLogger(),
    ).run([case])
    if results[0].status != "success":
        raise RuntimeError("offline mock request failed")
    metrics = calculate_metrics(results)
    return {"attack_success_rate": metrics["attack_success_rate"],
            "completed_requests": metrics["completed_requests"], "empirical_result": False,
            "provider": "mock", "total_requests": metrics["total_requests"]}


if __name__ == "__main__":
    print(json.dumps(preview(), sort_keys=True))
