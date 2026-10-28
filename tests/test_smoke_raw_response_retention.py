"""Tests for smoke test raw response retention policy (Issue #16)."""
from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from benchmark.adapters.base import ModelAdapter
from benchmark.smoke_test import (
    SmokeConfigError,
    load_smoke_config,
    run_smoke,
)
from benchmark.types import AdapterResponse, GenerationRequest


ROOT = Path(__file__).resolve().parent.parent
REPO_CONFIG = ROOT / "configs" / "phase6a_smoke.json"
STUB_OUTPUT_TEXT = "STUB_UNIQUE_RESPONSE_PAYLOAD_TOKEN_SECRET_98765"


class StubAdapter(ModelAdapter):
    provider = "openai"

    def generate(self, request: GenerationRequest) -> AdapterResponse:
        return AdapterResponse(
            text=STUB_OUTPUT_TEXT,
            model=request.model,
            provider="openai",
            request_id=request.request_id or "stub-req-id",
            usage={"total_tokens": 15},
            metadata={},
        )


def _build_test_config(tmp_path: Path, *, extra_config: dict | None = None) -> Path:
    config_dict, _ = load_smoke_config(REPO_CONFIG)
    config_dict["output_root"] = str(tmp_path / "results_out")
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
    if extra_config:
        config_dict.update(extra_config)
    # Config lives at <tmp>/src/configs/, so the config's source root is <tmp>/src
    # and other tmp_path directories are outside it.
    cfg_path = tmp_path / "src" / "configs" / "smoke_test_config.json"
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    cfg_path.write_text(json.dumps(config_dict, indent=2), encoding="utf-8")
    return cfg_path


@pytest.fixture
def mock_env():
    env_vars = {
        "OPENAI_API_KEY": "test-key-mock",
        "PHASE6A_OPENAI_MODEL": "gpt-4o-smoke",
        "PHASE6A_OPENAI_MODEL_VERSION": "2024-08-06",
    }
    with patch.dict(os.environ, env_vars, clear=False):
        yield


def test_repo_config_has_include_response_text_false():
    config_data = json.loads(REPO_CONFIG.read_text(encoding="utf-8"))
    response_logging = config_data.get("response_logging", {})
    assert response_logging.get("include_response_text") is False, (
        "repo config phase6a_smoke.json must set include_response_text to false"
    )
    retention = response_logging.get("retention", "")
    assert isinstance(retention, str) and len(retention) > 0, "retention notice must be non-empty"


def test_config_with_include_response_text_true_raises_smoke_config_error(tmp_path):
    cfg_path = _build_test_config(
        tmp_path,
        extra_config={
            "response_logging": {
                "include_response_text": True,
                "retention": "local",
            }
        },
    )
    with pytest.raises(SmokeConfigError, match=r"--raw-response-dir"):
        load_smoke_config(cfg_path)

    # Also test top-level include_response_text
    cfg_path2 = _build_test_config(
        tmp_path,
        extra_config={"include_response_text": True, "response_logging": {}},
    )
    with pytest.raises(SmokeConfigError, match=r"--raw-response-dir"):
        load_smoke_config(cfg_path2)


def test_default_smoke_run_omits_raw_response_text(tmp_path, mock_env):
    cfg_path = _build_test_config(tmp_path)
    output_root = tmp_path / "results_out"

    with patch("benchmark.smoke_test._make_adapter", return_value=StubAdapter()):
        summary = run_smoke(cfg_path, live=True)

    # 1. Check summary truthful reporting
    safety = summary["safety"]
    assert safety["raw_response_text_retained"] is False
    assert safety["raw_response_dir"] is None
    assert safety["raw_responses_are_local_only"] is True

    # 2. Check responses.jsonl under output_root
    exp_dir = output_root / "phase6a-real-model-smoke"
    jsonl_files = list(exp_dir.rglob("responses.jsonl"))
    assert len(jsonl_files) > 0, "Expected at least one responses.jsonl"
    for jf in jsonl_files:
        for line in jf.read_text(encoding="utf-8").strip().splitlines():
            record = json.loads(line)
            assert record["response_text"] is None, "response_text must be null in default run"

    # 3. Check that stub response text appears in NO file under output_root
    for file_path in exp_dir.rglob("*"):
        if file_path.is_file():
            content = file_path.read_bytes()
            assert STUB_OUTPUT_TEXT.encode("utf-8") not in content, (
                f"Stub response text leaked into {file_path}"
            )

    # 4. Check no responses.raw.jsonl exists anywhere in tmp_path
    raw_files = list(tmp_path.rglob("responses.raw.jsonl"))
    assert len(raw_files) == 0, f"Found unexpected raw response files: {raw_files}"


def test_opt_in_raw_response_dir_retains_raw_text(tmp_path, mock_env):
    cfg_path = _build_test_config(tmp_path)
    output_root = tmp_path / "results_out"
    raw_dir = tmp_path / "raw_dir_target"

    with patch("benchmark.smoke_test._make_adapter", return_value=StubAdapter()):
        summary = run_smoke(cfg_path, live=True, raw_response_dir=raw_dir)

    # 1. Check summary truthful reporting
    safety = summary["safety"]
    assert safety["raw_response_text_retained"] is True
    assert safety["raw_response_dir"] == str(raw_dir.resolve())
    assert safety["raw_responses_are_local_only"] is True

    # 2. Check raw file exists and contains stub text
    raw_file = raw_dir / "phase6a-real-model-smoke" / "openai" / "responses.raw.jsonl"
    assert raw_file.exists(), f"Expected raw response file at {raw_file}"
    raw_lines = [json.loads(line) for line in raw_file.read_text(encoding="utf-8").strip().splitlines()]
    assert len(raw_lines) > 0
    assert all(r["response_text"] == STUB_OUTPUT_TEXT for r in raw_lines)

    # 3. Check results-tree file still has none
    exp_dir = output_root / "phase6a-real-model-smoke"
    jsonl_files = list(exp_dir.rglob("responses.jsonl"))
    assert len(jsonl_files) > 0
    for jf in jsonl_files:
        for line in jf.read_text(encoding="utf-8").strip().splitlines():
            record = json.loads(line)
            assert record["response_text"] is None

    # 4. Check results tree does not contain stub text
    for file_path in exp_dir.rglob("*"):
        if file_path.is_file():
            content = file_path.read_bytes()
            assert STUB_OUTPUT_TEXT.encode("utf-8") not in content, (
                f"Stub response text leaked into results path: {file_path}"
            )


def test_raw_response_dir_inside_results_raises_smoke_config_error(tmp_path):
    cfg_path = _build_test_config(tmp_path)
    forbidden_dir = ROOT / "results" / "forbidden_smoke_raw_test"
    output_root = tmp_path / "results_out"

    with pytest.raises(SmokeConfigError, match=r"raw_response_dir"):
        run_smoke(cfg_path, live=True, raw_response_dir=forbidden_dir)

    # Confirm no file or directory was written
    assert not forbidden_dir.exists(), "Forbidden dir should not be created"
    assert not output_root.exists(), "Output root should not be created before validation failure"


def test_raw_responses_are_local_only_derivation_inside_source_root(tmp_path, mock_env):
    cfg_path = _build_test_config(tmp_path)
    local_raw_dir = tmp_path / "src" / "scratch_raw"  # inside the config's source root
    with patch("benchmark.smoke_test._make_adapter", return_value=StubAdapter()):
        summary = run_smoke(cfg_path, live=True, raw_response_dir=local_raw_dir)

    safety = summary["safety"]
    assert safety["raw_response_text_retained"] is True
    assert safety["raw_response_dir"] == str(local_raw_dir.resolve())
    # Inside the source tree, so it is not "local only".
    assert safety["raw_responses_are_local_only"] is False


def test_main_cli_parses_raw_response_dir(tmp_path, mock_env):
    import sys
    from benchmark.smoke_test import main

    cfg_path = _build_test_config(tmp_path)
    raw_dir = tmp_path / "cli_raw_target"

    test_args = [
        "smoke_test.py",
        "--config", str(cfg_path),
        "--live",
        "--raw-response-dir", str(raw_dir),
    ]
    with patch.object(sys, "argv", test_args):
        with patch("benchmark.smoke_test._make_adapter", return_value=StubAdapter()):
            ret_code = main()
            assert ret_code == 0

    assert (raw_dir / "phase6a-real-model-smoke" / "openai" / "responses.raw.jsonl").exists()
