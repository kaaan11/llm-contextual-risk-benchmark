"""Tests for smoke test live preflight validation and error handling (Issue #12)."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from benchmark.adapters.base import ModelAdapter
from benchmark.metadata import ExperimentMetadata
from benchmark.preflight import PreflightError, assert_run_config_frozen
from benchmark.smoke_test import load_smoke_config, run_smoke
from benchmark.types import AdapterResponse, GenerationRequest

ROOT = Path(__file__).resolve().parent.parent
REPO_CONFIG = ROOT / "configs" / "phase6a_smoke.json"


class StubAdapter(ModelAdapter):
    def __init__(self, provider: str = "openai") -> None:
        self.provider = provider
        self.generate_calls = 0

    def generate(self, request: GenerationRequest) -> AdapterResponse:
        self.generate_calls += 1
        return AdapterResponse(
            text="Stub response text",
            model=request.model,
            provider=self.provider,
            request_id=request.request_id or "stub-req-id",
            usage={"total_tokens": 15},
            metadata={},
        )


def _build_test_config(
    tmp_path: Path,
    *,
    extra_config: dict | None = None,
    include_top_p: bool | None = None,
) -> Path:
    config_dict, _ = load_smoke_config(REPO_CONFIG)
    config_dict["output_root"] = str(tmp_path / "results_out")
    config_dict["dataset_path"] = str(ROOT / "dataset" / "pilot" / "pilot_dataset.json")
    config_dict["manifest_path"] = str(ROOT / "tests" / "fixtures" / "phase6a_smoke_manifest.json")
    config_dict["max_samples"] = 20
    if include_top_p is False:
        config_dict.pop("top_p", None)
    elif include_top_p is True:
        config_dict["top_p"] = 1.0

    if extra_config:
        config_dict.update(extra_config)

    cfg_path = tmp_path / "src" / "configs" / "smoke_test_config.json"
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    cfg_path.write_text(json.dumps(config_dict, indent=2), encoding="utf-8")
    return cfg_path


MOCK_ENV = {
    "OPENAI_API_KEY": "mock-openai-key",
    "PHASE6A_OPENAI_MODEL": "gpt-4o",
    "PHASE6A_OPENAI_MODEL_VERSION": "2024-08-06",
    "ANTHROPIC_API_KEY": "mock-anthropic-key",
    "PHASE6A_ANTHROPIC_MODEL": "claude-3-5-sonnet",
    "PHASE6A_ANTHROPIC_MODEL_VERSION": "20241022",
}


def test_missing_top_p_causes_preflight_error_and_no_adapter_generate_called(tmp_path: Path):
    cfg_path = _build_test_config(
        tmp_path,
        include_top_p=False,
        extra_config={
            "providers": {
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
        },
    )

    stub = StubAdapter(provider="openai")
    with patch.dict("os.environ", MOCK_ENV, clear=True), \
         patch("benchmark.smoke_test._make_adapter", return_value=stub):
        summary = run_smoke(cfg_path, live=True)

    openai_result = next(p for p in summary["providers"] if p["provider"] == "openai")
    assert openai_result["status"] == "error"
    reason = openai_result.get("reason") or openai_result.get("error") or ""
    assert "top_p" in reason
    assert stub.generate_calls == 0


def test_repo_config_passes_preflight_and_stub_is_called(tmp_path: Path):
    # Tests that the repo config phase6a_smoke.json itself has top_p: 1.0 and passes live preflight
    cfg_path = _build_test_config(
        tmp_path,
        # Do not override top_p; take whatever REPO_CONFIG defines
        extra_config={
            "providers": {
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
        },
    )

    stub = StubAdapter(provider="openai")
    with patch.dict("os.environ", MOCK_ENV, clear=True), \
         patch("benchmark.smoke_test._make_adapter", return_value=stub):
        summary = run_smoke(cfg_path, live=True)

    openai_result = next(p for p in summary["providers"] if p["provider"] == "openai")
    assert openai_result["status"] == "completed"
    assert stub.generate_calls == 20


def test_two_providers_enabled_one_failing_preflight_other_completes(tmp_path: Path):
    cfg_path = _build_test_config(
        tmp_path,
        include_top_p=True,
        extra_config={
            "providers": {
                "openai": {
                    "enabled": True,
                    "credential_env": "OPENAI_API_KEY",
                    "model_env": "PHASE6A_OPENAI_MODEL",
                    "model_version_env": "PHASE6A_OPENAI_MODEL_VERSION",
                    "base_url_env": "OPENAI_BASE_URL",
                },
                "anthropic": {
                    "enabled": True,
                    "credential_env": "ANTHROPIC_API_KEY",
                    "model_env": "PHASE6A_ANTHROPIC_MODEL",
                    "model_version_env": "PHASE6A_ANTHROPIC_MODEL_VERSION",
                    "base_url_env": "ANTHROPIC_BASE_URL",
                },
                "open_weight": {"enabled": False},
            }
        },
    )

    openai_stub = StubAdapter(provider="openai")
    anthropic_stub = StubAdapter(provider="anthropic")

    def make_adapter_mock(name, provider_config, timeout_s):
        if name == "openai":
            return openai_stub
        if name == "anthropic":
            return anthropic_stub
        raise ValueError(f"Unknown provider: {name}")

    real_preflight = assert_run_config_frozen

    def failing_preflight_for_openai(metadata: ExperimentMetadata) -> str:
        if metadata.model.provider == "openai":
            raise PreflightError(
                "frozen run configuration incomplete — refusing to start evaluation:\n  - generation_parameters.top_p is required and must be frozen before evaluation"
            )
        return real_preflight(metadata)

    with patch.dict("os.environ", MOCK_ENV, clear=True), \
         patch("benchmark.smoke_test._make_adapter", side_effect=make_adapter_mock), \
         patch("benchmark.smoke_test.assert_run_config_frozen", side_effect=failing_preflight_for_openai, create=True), \
         patch("benchmark.runner.assert_run_config_frozen", side_effect=failing_preflight_for_openai):
        summary = run_smoke(cfg_path, live=True)

    openai_result = next(p for p in summary["providers"] if p["provider"] == "openai")
    anthropic_result = next(p for p in summary["providers"] if p["provider"] == "anthropic")

    assert openai_result["status"] == "error"
    reason = openai_result.get("reason") or openai_result.get("error") or ""
    assert "top_p" in reason
    assert openai_stub.generate_calls == 0

    assert anthropic_result["status"] == "completed"
    assert anthropic_stub.generate_calls == 20
