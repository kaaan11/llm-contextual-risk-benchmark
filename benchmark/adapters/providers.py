"""OpenAI, Anthropic ve generic open-weight adapter’ları.

Varsayılan transport gerçek HTTP çağrısı yapar, ancak testlerde transport
fonksiyonu inject edilerek ağ ve credential ihtiyacı ortadan kaldırılır.
"""

from __future__ import annotations

import os
from typing import Any, Mapping

from .base import ModelAdapter, JsonTransport, default_json_transport, extract_text
from .endpoint_policy import check_endpoint
from ..errors import AdapterConfigurationError
from ..types import AdapterResponse, GenerationRequest


def _generation_parameters(request: GenerationRequest) -> dict[str, Any]:
    parameters = dict(request.generation_parameters)
    reserved = {"model", "input", "messages", "store", "system", "instructions"}
    conflicts = reserved.intersection(parameters)
    if conflicts:
        raise AdapterConfigurationError(
            "generation_parameters cannot override reserved request fields: " + ", ".join(sorted(conflicts))
        )
    return parameters


def _messages(request: GenerationRequest) -> list[dict[str, str]]:
    messages = [dict(message) for message in request.messages]
    if request.system_instruction:
        return [{"role": "system", "content": request.system_instruction}, *messages]
    return messages


def _token_parameters(
    request: GenerationRequest, wire_name: str, *, require_canonical: bool = False,
    default: int | None = None,
) -> dict[str, Any]:
    """Translate the canonical token limit without silently overriding an alias."""
    parameters = _generation_parameters(request)
    canonical = "max_output_tokens"
    legacy = "max_tokens"
    if canonical in parameters and legacy in parameters:
        raise AdapterConfigurationError("Use only max_output_tokens; max_tokens alias is also present")
    if require_canonical and canonical not in parameters:
        raise AdapterConfigurationError(
            "max_output_tokens missing from generation_parameters while frozen-config "
            "enforcement is active; refusing undocumented provider default (F-10)"
        )
    limit = parameters.pop(canonical, parameters.pop(legacy, default))
    if limit is not None:
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise AdapterConfigurationError("max_output_tokens must be a positive integer")
        parameters[wire_name] = limit
    elif canonical in request.generation_parameters or legacy in request.generation_parameters:
        raise AdapterConfigurationError("max_output_tokens must be a positive integer")
    return parameters


def _response(request: GenerationRequest, provider: str, payload: Mapping[str, Any]) -> AdapterResponse:
    return AdapterResponse(
        text=extract_text(payload),
        model=request.model,
        provider=provider,
        request_id=str(payload.get("id")) if payload.get("id") is not None else request.request_id,
        usage=payload.get("usage", {}) if isinstance(payload.get("usage", {}), Mapping) else {},
        metadata={"response_keys": sorted(str(key) for key in payload.keys())},
    )


class OpenAIAdapter(ModelAdapter):
    provider = "openai"

    def __init__(
        self,
        *,
        transport: JsonTransport | None = None,
        endpoint: str | None = None,
        api_key_env: str = "OPENAI_API_KEY",
        timeout_s: float = 60.0,
        allow_plaintext_loopback: bool = False,
    ) -> None:
        self.transport = transport or default_json_transport
        self.endpoint = endpoint or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1/responses")
        self.api_key_env = api_key_env
        self.timeout_s = timeout_s
        self.allow_plaintext_loopback = allow_plaintext_loopback

    def generate(self, request: GenerationRequest) -> AdapterResponse:
        check_endpoint(self.endpoint, allow_plaintext_loopback=self.allow_plaintext_loopback)
        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise AdapterConfigurationError(f"{self.api_key_env} ortam değişkeni tanımlı değil")
        payload: dict[str, Any] = {
            "model": request.model.name,
            "input": _messages(request),
            "store": False,
            **_token_parameters(request, "max_output_tokens"),
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        if request.request_id:
            headers["X-Client-Request-Id"] = request.request_id
        response = self.transport(self.endpoint, headers, payload, self.timeout_s)
        return _response(request, self.provider, response)


class AnthropicAdapter(ModelAdapter):
    provider = "anthropic"

    def __init__(
        self,
        *,
        transport: JsonTransport | None = None,
        endpoint: str | None = None,
        api_key_env: str = "ANTHROPIC_API_KEY",
        api_version_env: str = "ANTHROPIC_API_VERSION",
        timeout_s: float = 60.0,
        allow_plaintext_loopback: bool = False,
    ) -> None:
        self.transport = transport or default_json_transport
        self.endpoint = endpoint or os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1/messages")
        self.api_key_env = api_key_env
        self.api_version_env = api_version_env
        self.timeout_s = timeout_s
        self.allow_plaintext_loopback = allow_plaintext_loopback
        # F-10: when the runner enforces the frozen configuration, a missing
        # max_output_tokens must fail loudly instead of silently using this
        # adapter's historical 1024 default.
        self.require_explicit_max_tokens = False

    def generate(self, request: GenerationRequest) -> AdapterResponse:
        check_endpoint(self.endpoint, allow_plaintext_loopback=self.allow_plaintext_loopback)
        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise AdapterConfigurationError(f"{self.api_key_env} ortam değişkeni tanımlı değil")
        messages = [message for message in _messages(request) if message.get("role") != "system"]
        parameters = _token_parameters(
            request, "max_tokens", require_canonical=self.require_explicit_max_tokens, default=1024,
        )
        payload: dict[str, Any] = {
            "model": request.model.name,
            "messages": messages,
            **parameters,
        }
        system_messages = [message["content"] for message in _messages(request) if message.get("role") == "system"]
        if system_messages:
            payload["system"] = "\n\n".join(system_messages)
        headers = {
            "x-api-key": api_key,
            "anthropic-version": os.environ.get(self.api_version_env, "2023-06-01"),
            "Content-Type": "application/json",
        }
        response = self.transport(self.endpoint, headers, payload, self.timeout_s)
        return _response(request, self.provider, response)


class OpenWeightAdapter(ModelAdapter):
    """Yerel veya hosted open-weight endpoint’i için genel JSON adapter’ı."""

    provider = "open_weight"

    def __init__(
        self,
        *,
        transport: JsonTransport | None = None,
        endpoint: str | None = None,
        api_key_env: str = "OPENWEIGHT_API_KEY",
        timeout_s: float = 120.0,
        allow_plaintext_loopback: bool = False,
    ) -> None:
        self.transport = transport or default_json_transport
        self.endpoint = endpoint or os.environ.get("OPENWEIGHT_BASE_URL")
        self.api_key_env = api_key_env
        self.timeout_s = timeout_s
        self.allow_plaintext_loopback = allow_plaintext_loopback

    def generate(self, request: GenerationRequest) -> AdapterResponse:
        if not self.endpoint:
            raise AdapterConfigurationError("OPENWEIGHT_BASE_URL ortam değişkeni tanımlı değil")
        check_endpoint(self.endpoint, allow_plaintext_loopback=self.allow_plaintext_loopback)
        payload: dict[str, Any] = {
            "model": request.model.name,
            "messages": _messages(request),
            **_generation_parameters(request),
        }
        headers = {"Content-Type": "application/json"}
        api_key = os.environ.get(self.api_key_env)
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        response = self.transport(self.endpoint, headers, payload, self.timeout_s)
        return _response(request, self.provider, response)
