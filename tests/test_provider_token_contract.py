"""Captured payloads only; no credentials or live model evaluation."""
import socket

import pytest

from benchmark.adapters.providers import AnthropicAdapter, OpenAIAdapter
from benchmark.errors import AdapterConfigurationError
from benchmark.types import GenerationRequest, ModelSpec


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("real transport must not run")
    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket, "create_connection", blocked)


@pytest.mark.parametrize("adapter_type,wire_name", [
    (OpenAIAdapter, "max_output_tokens"), (AnthropicAdapter, "max_tokens"),
])
@pytest.mark.parametrize("input_name", ["max_output_tokens", "max_tokens"])
def test_token_alias_is_translated_without_mutating_request(monkeypatch, adapter_type, wire_name, input_name):
    captured = []
    monkeypatch.setenv("OPENAI_API_KEY", "unit-placeholder")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "unit-placeholder")
    def transport(url, headers, payload, timeout):
        captured.append(payload)
        return {"output_text": "Hello."}
    request = GenerationRequest(
        "abstract", ({"role": "user", "content": "Say hello."},),
        ModelSpec("test", "placeholder-model", "not-a-live-version"),
        generation_parameters={input_name: 256, "temperature": 0.0},
    )
    adapter_type(transport=transport).generate(request)
    assert captured[0][wire_name] == 256
    assert ({"max_tokens", "max_output_tokens"} - {wire_name}).isdisjoint(captured[0])
    assert dict(request.generation_parameters) == {input_name: 256, "temperature": 0.0}


@pytest.mark.parametrize("adapter_type", [OpenAIAdapter, AnthropicAdapter])
@pytest.mark.parametrize("parameters", [
    {"max_tokens": 10, "max_output_tokens": 20},
    {"max_output_tokens": True}, {"max_output_tokens": 1.5},
    {"max_output_tokens": 0}, {"max_output_tokens": -1},
    {"max_output_tokens": None}, {"max_tokens": "256"},
])
def test_invalid_or_ambiguous_limit_fails_before_dispatch(monkeypatch, adapter_type, parameters):
    monkeypatch.setenv("OPENAI_API_KEY", "unit-placeholder")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "unit-placeholder")
    def transport(*args):
        pytest.fail("invalid token limit must not dispatch")
    request = GenerationRequest("abstract", (), ModelSpec("test", "test", "test"),
                                generation_parameters=parameters)
    with pytest.raises(AdapterConfigurationError):
        adapter_type(transport=transport).generate(request)


def test_anthropic_strict_mode_still_requires_canonical_parameter(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "unit-placeholder")
    adapter = AnthropicAdapter(transport=lambda *args: pytest.fail("must not dispatch"))
    adapter.require_explicit_max_tokens = True
    request = GenerationRequest("abstract", (), ModelSpec("test", "test", "test"),
                                generation_parameters={"max_tokens": 256})
    with pytest.raises(AdapterConfigurationError, match="max_output_tokens missing"):
        adapter.generate(request)


@pytest.mark.parametrize("limit", [True, 1.5, float("inf"), float("nan")])
def test_strict_preflight_requires_an_integer_token_budget(limit):
    from benchmark.metadata import ExperimentMetadata
    from benchmark.preflight import PreflightError, assert_run_config_frozen
    metadata = ExperimentMetadata(
        run_id="abstract", experiment_id="test", dataset_id="abstract", dataset_version="1",
        model=ModelSpec("mock", "placeholder", "1"), configuration="test",
        context_mode="current_prompt_only", timeout_s=10,
        generation_parameters={"temperature": 0.0, "top_p": 1.0, "max_output_tokens": limit},
        retry_policy={"max_attempts": 1},
    )
    with pytest.raises(PreflightError, match="max_output_tokens"):
        assert_run_config_frozen(metadata)
