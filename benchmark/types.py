"""Benchmark framework veri tipleri."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class ModelSpec:
    provider: str
    name: str
    version: str

    def to_dict(self) -> dict[str, str]:
        return {"provider": self.provider, "name": self.name, "version": self.version}


@dataclass(frozen=True)
class GenerationRequest:
    sample_id: str
    messages: tuple[Mapping[str, str], ...]
    model: ModelSpec
    system_instruction: str | None = None
    request_id: str | None = None
    generation_parameters: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AdapterResponse:
    text: str
    model: ModelSpec
    provider: str
    request_id: str | None = None
    usage: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EvaluationCase:
    sample_id: str
    record_type: str
    dataset_membership: tuple[str, ...]
    turns: tuple[Mapping[str, Any], ...]
    task_metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RefusalDecision:
    is_refusal: bool
    classification: str
    confidence: str
    method: str
    matched_signals: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvaluationResult:
    evaluation_id: str
    run_id: str
    sample_id: str
    model: ModelSpec
    configuration: str
    context_mode: str
    response_text: str | None
    request_id: str | None
    latency_ms: float | None
    refusal: RefusalDecision | None
    provider_call_latency_ms: float | None = None
    pure_inference_latency_ms: float | None = None
    retry_overhead_ms: float | None = None
    usage: Mapping[str, Any] = field(default_factory=dict)
    error: str | None = None
    input_turn_count: int = 0
    request_digest: str | None = None
    dataset_membership: tuple[str, ...] = ()
    request_started_at: str | None = None
    request_completed_at: str | None = None
    attempts: int = 1
    status: str = "success"

    def to_log_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "evaluation_id": self.evaluation_id,
            "run_id": self.run_id,
            "sample_id": self.sample_id,
            "model": self.model.to_dict(),
            "configuration": self.configuration,
            "context_mode": self.context_mode,
            "response_text": self.response_text,
            "request_id": self.request_id,
            "latency_ms": self.latency_ms,
            "provider_call_latency_ms": self.provider_call_latency_ms,
            "pure_inference_latency_ms": self.pure_inference_latency_ms,
            "retry_overhead_ms": self.retry_overhead_ms,
            "usage": dict(self.usage),
            "error": self.error,
            "input_turn_count": self.input_turn_count,
            "request_digest": self.request_digest,
            "dataset_membership": list(self.dataset_membership),
            "request_started_at": self.request_started_at,
            "request_completed_at": self.request_completed_at,
            "attempts": self.attempts,
            "status": self.status,
        }
        if self.refusal is not None:
            result["refusal"] = {
                "is_refusal": self.refusal.is_refusal,
                "classification": self.refusal.classification,
                "confidence": self.refusal.confidence,
                "method": self.refusal.method,
                "matched_signals": list(self.refusal.matched_signals),
            }
        else:
            result["refusal"] = None
        return result
