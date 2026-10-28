"""Tests for run-config digest written to experiment_metadata.json (Issue #13)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from benchmark.adapters.base import ModelAdapter
from benchmark.logging import InMemoryResponseLogger
from benchmark.metadata import ExperimentMetadata
from benchmark.preflight import assert_run_config_frozen
from benchmark.runner import EvaluationRunner
from benchmark.types import AdapterResponse, GenerationRequest, ModelSpec


class StubAdapter(ModelAdapter):
    provider = "openai"

    def generate(self, request: GenerationRequest) -> AdapterResponse:
        return AdapterResponse(
            text="Stub response",
            model=request.model,
            provider=self.provider,
            request_id=request.request_id or "stub-id",
            usage={"total_tokens": 5},
            metadata={},
        )


def _make_metadata(**kwargs) -> ExperimentMetadata:
    base = {
        "run_id": "test-run-001",
        "experiment_id": "test-exp",
        "dataset_id": "test-dataset",
        "dataset_version": "0.1.0",
        "model": ModelSpec(provider="openai", name="gpt-4o", version="2024-08-06"),
        "configuration": "phase6a_baseline",
        "context_mode": "conversation_context",
        "generation_parameters": {
            "temperature": 0.0,
            "top_p": 1.0,
            "max_output_tokens": 256,
        },
        "timeout_s": 30.0,
        "retry_policy": {"max_attempts": 2, "initial_backoff_s": 0.5, "max_backoff_s": 4.0},
    }
    base.update(kwargs)
    return ExperimentMetadata(**base)


def test_strict_run_includes_digest_and_status(tmp_path: Path):
    metadata = _make_metadata()
    expected_digest = assert_run_config_frozen(metadata)

    adapter = StubAdapter()
    logger = InMemoryResponseLogger()
    runner = EvaluationRunner(adapter, metadata, logger, enforce_frozen_config=True)

    artifacts = runner.write_artifacts(tmp_path, [])
    assert "metadata" in artifacts

    written = json.loads(artifacts["metadata"].read_text(encoding="utf-8"))
    assert written["run_config_digest"] == expected_digest
    assert written["run_config_digest_status"] == "strict_preflight"


def test_changing_temperature_changes_digest(tmp_path: Path):
    md1 = _make_metadata(
        generation_parameters={"temperature": 0.0, "top_p": 1.0, "max_output_tokens": 256}
    )
    md2 = _make_metadata(
        generation_parameters={"temperature": 0.7, "top_p": 1.0, "max_output_tokens": 256}
    )

    d1 = assert_run_config_frozen(md1)
    d2 = assert_run_config_frozen(md2)
    assert d1 != d2

    adapter = StubAdapter()
    logger = InMemoryResponseLogger()

    out1 = tmp_path / "run1"
    runner1 = EvaluationRunner(adapter, md1, logger, enforce_frozen_config=True)
    runner1.write_artifacts(out1, [])
    written1 = json.loads((out1 / "experiment_metadata.json").read_text(encoding="utf-8"))

    out2 = tmp_path / "run2"
    runner2 = EvaluationRunner(adapter, md2, logger, enforce_frozen_config=True)
    runner2.write_artifacts(out2, [])
    written2 = json.loads((out2 / "experiment_metadata.json").read_text(encoding="utf-8"))

    assert written1["run_config_digest"] == d1
    assert written2["run_config_digest"] == d2
    assert written1["run_config_digest"] != written2["run_config_digest"]


def test_non_strict_run_gives_null_digest_and_non_strict_status(tmp_path: Path):
    metadata = _make_metadata()
    adapter = StubAdapter()
    logger = InMemoryResponseLogger()
    runner = EvaluationRunner(adapter, metadata, logger, enforce_frozen_config=False)

    artifacts = runner.write_artifacts(tmp_path, [])
    written = json.loads(artifacts["metadata"].read_text(encoding="utf-8"))

    assert "run_config_digest" in written
    assert written["run_config_digest"] is None
    assert written["run_config_digest_status"] == "not_computed_non_strict"
