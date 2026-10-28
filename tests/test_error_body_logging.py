"""Tests for HTTP error body handling and isolation (Issue #21).

Verifies that provider HTTP error bodies are captured as detail,
sanitized, and preserved only in opt-in raw response logs,
never reaching results-tree logs or exception messages.
"""
from __future__ import annotations

import io
import json
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

import pytest

from benchmark.adapters.base import ModelAdapter, default_json_transport
from benchmark.errors import AdapterRequestError
from benchmark.logging import JsonlResponseLogger
from benchmark.metadata import ExperimentMetadata
from benchmark.runner import EvaluationRunner
from benchmark.smoke_test import load_smoke_config, run_smoke
from benchmark.types import AdapterResponse, EvaluationCase, GenerationRequest, ModelSpec


ROOT = Path(__file__).resolve().parent.parent
REPO_CONFIG = ROOT / "configs" / "phase6a_smoke.json"


def _make_dummy_case(sample_id: str = "case-1") -> EvaluationCase:
    return EvaluationCase(
        sample_id=sample_id,
        record_type="single_turn",
        dataset_membership=("benign",),
        turns=({"role": "user", "content": {"text": "hello"}},),
    )


def _make_dummy_metadata() -> ExperimentMetadata:
    return ExperimentMetadata(
        run_id="run-err-test",
        experiment_id="exp-err-test",
        dataset_id="test-dataset",
        dataset_version="1.0.0",
        model=ModelSpec(provider="mock", name="test-model", version="1.0"),
        configuration="test-config",
        context_mode="conversation_context",
    )


def test_default_json_transport_moves_body_to_detail():
    marker = "BODY-MARKER-21-TRANSPORT"
    body_bytes = f'{{"error": "{marker}", "token": "sk-1234567890abcdef1234"}}'.encode("utf-8")
    http_error = HTTPError(
        url="https://test.local/v1/chat",
        code=500,
        msg="Internal Server Error",
        hdrs={},
        fp=io.BytesIO(body_bytes),
    )

    with patch("benchmark.adapters.base.urlopen", side_effect=http_error):
        with pytest.raises(AdapterRequestError) as exc_info:
            default_json_transport(
                url="https://test.local/v1/chat",
                headers={"Authorization": "Bearer token"},
                payload={"input": "test"},
                timeout_s=5.0,
            )

    exc = exc_info.value
    # Exception message does NOT contain the marker body
    assert marker not in str(exc)
    assert str(exc) == "HTTP 500 sağlayıcı hatası"
    # .detail contains the marker body, with credential sanitized
    assert exc.detail is not None
    assert marker in exc.detail
    assert "sk-1234567890abcdef1234" not in exc.detail
    assert "[REDACTED]" in exc.detail
    # status_code and retryable are as before
    assert exc.status_code == 500
    assert exc.retryable is True


def test_default_json_transport_non_retryable_code():
    marker = "BODY-MARKER-21-400"
    body_bytes = f'{{"error": "{marker}"}}'.encode("utf-8")
    http_error = HTTPError(
        url="https://test.local/v1/chat",
        code=400,
        msg="Bad Request",
        hdrs={},
        fp=io.BytesIO(body_bytes),
    )

    with patch("benchmark.adapters.base.urlopen", side_effect=http_error):
        with pytest.raises(AdapterRequestError) as exc_info:
            default_json_transport(
                url="https://test.local/v1/chat",
                headers={},
                payload={},
                timeout_s=5.0,
            )

    exc = exc_info.value
    assert marker not in str(exc)
    assert str(exc) == "HTTP 400 sağlayıcı hatası"
    assert exc.detail is not None
    assert marker in exc.detail
    assert exc.status_code == 400
    assert exc.retryable is False


class FailingAdapter(ModelAdapter):
    provider = "mock"

    def __init__(self, marker: str, status_code: int = 500) -> None:
        self.marker = marker
        self.status_code = status_code

    def generate(self, request: GenerationRequest) -> AdapterResponse:
        raise AdapterRequestError(
            f"HTTP {self.status_code} sağlayıcı hatası",
            status_code=self.status_code,
            retryable=False,
            detail=f'{{"detail": "{self.marker}"}}',
        )


def test_runner_results_tree_logger_excludes_marker(tmp_path: Path):
    marker = "BODY-MARKER-21-TREE-ISOLATED"
    output_dir = tmp_path / "results_tree"
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "responses.jsonl"

    case = _make_dummy_case()
    metadata = _make_dummy_metadata()
    adapter = FailingAdapter(marker=marker, status_code=503)

    with JsonlResponseLogger(log_path, include_response_text=False) as logger:
        runner = EvaluationRunner(adapter, metadata, logger)
        results = runner.run([case])
        runner.write_artifacts(output_dir, results)

    # In memory result check
    assert len(results) == 1
    res = results[0]
    assert res.status == "error"
    assert "sağlayıcı hatası" in str(res.error)  # error keeps class chain + HTTP code, not the body
    assert "503" in str(res.error)
    assert marker not in str(res.error)
    assert res.error_detail == f'{{"detail": "{marker}"}}'

    # Marker must appear in NO file under the output dir (scan bytes)
    for file_path in output_dir.rglob("*"):
        if file_path.is_file():
            content = file_path.read_bytes()
            assert marker.encode("utf-8") not in content, (
                f"Marker leaked into results tree file: {file_path}"
            )

    # In the serialized log file, error_detail and response_text are None
    lines = [json.loads(line) for line in log_path.read_text(encoding="utf-8").strip().splitlines()]
    assert len(lines) == 1
    record = lines[0]
    assert record["response_text"] is None
    assert record["error_detail"] is None
    assert "sağlayıcı hatası" in record["error"]  # error keeps class chain + HTTP code, not the body
    assert "503" in record["error"]
    assert marker not in json.dumps(record)


def test_runner_raw_logger_retains_marker(tmp_path: Path):
    marker = "BODY-MARKER-21-RAW-RETAINED"
    raw_dir = tmp_path / "raw_out"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_log_path = raw_dir / "responses.raw.jsonl"

    case = _make_dummy_case()
    metadata = _make_dummy_metadata()
    adapter = FailingAdapter(marker=marker, status_code=500)

    with JsonlResponseLogger(raw_log_path, include_response_text=True) as logger:
        runner = EvaluationRunner(adapter, metadata, logger)
        results = runner.run([case])

    assert len(results) == 1
    lines = [json.loads(line) for line in raw_log_path.read_text(encoding="utf-8").strip().splitlines()]
    assert len(lines) == 1
    record = lines[0]
    assert record["error_detail"] == f'{{"detail": "{marker}"}}'
    assert "sağlayıcı hatası" in record["error"]  # error keeps class chain + HTTP code, not the body
    assert "500" in record["error"]


def test_smoke_level_error_body_isolated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    marker = "BODY-MARKER-21-SMOKE-TEST"
    output_root = tmp_path / "results_out"
    raw_dir = tmp_path / "raw_target"

    config_dict, _ = load_smoke_config(REPO_CONFIG)
    config_dict["output_root"] = str(output_root)
    config_dict["dataset_path"] = str(ROOT / "dataset" / "pilot" / "pilot_dataset.json")
    config_dict["manifest_path"] = str(ROOT / "tests" / "fixtures" / "phase6a_smoke_manifest.json")
    config_dict["max_samples"] = 20
    config_dict["top_p"] = 1.0
    config_dict["providers"] = {
        "openai": {
            "enabled": True,
            "credential_env": "OPENAI_API_KEY",
            "model_env": "PHASE6A_OPENAI_MODEL",
            "model_version_env": "PHASE6A_OPENAI_MODEL_VERSION",
            "base_url_env": "OPENAI_BASE_URL",
        },
        "anthropic": {"enabled": False},
        "open_weight": {"enabled": False},
    }

    cfg_path = tmp_path / "src" / "configs" / "smoke_test_config.json"
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    cfg_path.write_text(json.dumps(config_dict, indent=2), encoding="utf-8")

    monkeypatch.setenv("OPENAI_API_KEY", "mock-test-key")
    monkeypatch.setenv("PHASE6A_OPENAI_MODEL", "mock-model")
    monkeypatch.setenv("PHASE6A_OPENAI_MODEL_VERSION", "2026-01-01")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://mock-api.local")

    failing_adapter = FailingAdapter(marker=marker, status_code=502)

    with patch("benchmark.smoke_test._make_adapter", return_value=failing_adapter):
        summary = run_smoke(cfg_path, live=True, raw_response_dir=raw_dir)

    exp_dir = output_root / str(config_dict["experiment_id"])
    assert exp_dir.exists()

    # 1. No file under exp_dir contains the marker
    for file_path in exp_dir.rglob("*"):
        if file_path.is_file():
            content = file_path.read_bytes()
            assert marker.encode("utf-8") not in content, (
                f"Marker leaked into smoke results file: {file_path}"
            )

    # 2. Results-tree responses.jsonl has error_detail == None
    results_jsonl = exp_dir / "openai" / "responses.jsonl"
    assert results_jsonl.exists()
    results_records = [json.loads(line) for line in results_jsonl.read_text(encoding="utf-8").strip().splitlines()]
    assert len(results_records) > 0
    for record in results_records:
        assert record["response_text"] is None
        assert record["error_detail"] is None
        assert "sağlayıcı hatası" in record["error"]  # error keeps class chain + HTTP code, not the body
        assert "502" in record["error"]
        assert marker not in json.dumps(record)

    # 3. Raw dir responses.raw.jsonl has the marker in error_detail
    raw_jsonl = raw_dir / str(config_dict["experiment_id"]) / "openai" / "responses.raw.jsonl"
    assert raw_jsonl.exists()
    raw_records = [json.loads(line) for line in raw_jsonl.read_text(encoding="utf-8").strip().splitlines()]
    assert len(raw_records) > 0
    for record in raw_records:
        assert record["error_detail"] == f'{{"detail": "{marker}"}}'
        assert "sağlayıcı hatası" in record["error"]  # error keeps class chain + HTTP code, not the body
        assert "502" in record["error"]
