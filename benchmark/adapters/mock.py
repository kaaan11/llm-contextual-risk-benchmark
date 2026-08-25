"""Gerçek API çağrısı yapmayan mock adapter."""

from __future__ import annotations

import time
from typing import Mapping

from .base import ModelAdapter
from ..types import AdapterResponse, GenerationRequest


class MockAdapter(ModelAdapter):
    provider = "mock"

    def __init__(
        self,
        responses: Mapping[str, str] | None = None,
        *,
        default_response: str = "Bu mock yanıttır.",
        latency_s: float = 0.0,
    ) -> None:
        self.responses = dict(responses or {})
        self.default_response = default_response
        self.latency_s = latency_s
        self.calls: list[GenerationRequest] = []

    def generate(self, request: GenerationRequest) -> AdapterResponse:
        self.calls.append(request)
        if self.latency_s > 0:
            time.sleep(self.latency_s)
        text = self.responses.get(request.sample_id, self.default_response)
        return AdapterResponse(
            text=text,
            model=request.model,
            provider=self.provider,
            request_id=request.request_id or f"mock-{request.sample_id}",
            usage={"prompt_tokens": sum(len(message.get("content", "").split()) for message in request.messages), "completion_tokens": len(text.split())},
            metadata={"mock": True},
        )
