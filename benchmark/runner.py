"""Model-agnostic evaluation runner."""

from __future__ import annotations

import hashlib
import json
from time import perf_counter, sleep
from pathlib import Path
from typing import Iterable

from .adapters.base import ModelAdapter
from .errors import DatasetLoadError, RetryExhaustedError, sanitize_error_message
from .preflight import assert_run_config_frozen
from .logging import ResponseLogger
from .metadata import ExperimentMetadata, utc_now, write_metadata
from .metrics import calculate_metrics
from .refusal import RefusalDetector
from .retry import RetryPolicy, call_with_retry
from .types import EvaluationCase, EvaluationResult, GenerationRequest


class EvaluationRunner:
    def __init__(
        self,
        adapter: ModelAdapter,
        metadata: ExperimentMetadata,
        logger: ResponseLogger,
        *,
        refusal_detector: RefusalDetector | None = None,
        retry_policy: RetryPolicy | None = None,
        enforce_frozen_config: bool = False,
    ) -> None:
        if metadata.context_mode not in {"current_prompt_only", "conversation_context"}:
            raise ValueError("context_mode geçersiz")
        self.adapter = adapter
        self.metadata = metadata
        self.logger = logger
        # F-10: canonical runs must not silently rely on undocumented provider
        # defaults for contract-frozen parameters. Strict mode validates the full
        # freeze list up front and records a stable run-config digest.
        self.run_config_digest: str | None = None
        if enforce_frozen_config:
            self.run_config_digest = assert_run_config_frozen(metadata)
            require_explicit = getattr(adapter, "require_explicit_max_tokens", None)
            if require_explicit is not None:
                adapter.require_explicit_max_tokens = True
        self.refusal_detector = refusal_detector or RefusalDetector()
        self.retry_policy = retry_policy or (
            RetryPolicy(**dict(metadata.retry_policy)) if metadata.retry_policy else RetryPolicy()
        )

    @staticmethod
    def _content_text(turn: dict) -> str:
        content = turn.get("content", {})
        if isinstance(content, dict) and isinstance(content.get("text"), str):
            return content["text"]
        raise DatasetLoadError(
            f"{turn.get('turn_id', '<unknown>')}: model input için text yok; content_ref çözümleme bu runner’da yok"
        )

    def _messages_for_case(self, case: EvaluationCase) -> tuple[dict[str, str], ...]:
        all_messages = tuple(
            {"role": str(turn["role"]), "content": self._content_text(dict(turn))}
            for turn in case.turns
        )
        if self.metadata.context_mode == "conversation_context":
            return all_messages
        # Current-prompt-only koşulunda system/developer talimatları korunur,
        # önceki konuşma turları çıkarılır.
        preserved = tuple(message for message in all_messages if message["role"] in {"system", "developer"})
        user_messages = tuple(message for message in all_messages if message["role"] == "user")
        if user_messages:
            return preserved + (user_messages[-1],)
        return preserved + (all_messages[-1],)

    @staticmethod
    def _digest(messages: tuple[dict[str, str], ...]) -> str:
        encoded = json.dumps(messages, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def run(self, cases: Iterable[EvaluationCase], *, fail_fast: bool = False) -> list[EvaluationResult]:
        results: list[EvaluationResult] = []
        max_samples = self.metadata.max_samples
        selected = list(cases)
        if max_samples is not None:
            selected = selected[:max_samples]

        for index, case in enumerate(selected, start=1):
            evaluation_id = f"{self.metadata.run_id}-evaluation-{index:04d}"
            request_id = f"{self.metadata.run_id}-{index:04d}"
            request_started_at = utc_now()
            started = perf_counter()
            attempts = 0
            request_digest = None
            messages: tuple[dict[str, str], ...] = ()
            provider_call_started = None
            provider_call_latency_ms = None
            pure_inference_latency_ms = None
            retry_overhead_ms = None
            retry_sleep_total = 0.0
            def tracking_sleeper(delay: float) -> None:
                nonlocal retry_sleep_total
                retry_sleep_total += delay
                sleep(delay)

            try:
                messages = self._messages_for_case(case)
                request_digest = self._digest(messages)
                request = GenerationRequest(
                    sample_id=case.sample_id,
                    messages=messages,
                    model=self.metadata.model,
                    system_instruction=None,
                    request_id=request_id,
                    generation_parameters=self.metadata.generation_parameters,
                )
                provider_call_started = perf_counter()
                response, attempts = call_with_retry(
                    lambda: self.adapter.generate(request),
                    self.retry_policy,
                    sleeper=tracking_sleeper,
                )
                provider_call_latency_ms = (perf_counter() - provider_call_started) * 1000.0
                retry_overhead_ms = retry_sleep_total * 1000.0
                pure_inference_latency_ms = max(0.0, provider_call_latency_ms - retry_overhead_ms)
                latency_ms = (perf_counter() - started) * 1000.0
                refusal = self.refusal_detector.detect(response.text)
                result = EvaluationResult(
                    evaluation_id=evaluation_id,
                    run_id=self.metadata.run_id,
                    sample_id=case.sample_id,
                    model=response.model,
                    configuration=self.metadata.configuration,
                    context_mode=self.metadata.context_mode,
                    response_text=response.text,
                    request_id=response.request_id,
                    latency_ms=latency_ms,
                    provider_call_latency_ms=provider_call_latency_ms,
                    pure_inference_latency_ms=pure_inference_latency_ms,
                    retry_overhead_ms=retry_overhead_ms,
                    refusal=refusal,
                    usage=response.usage,
                    input_turn_count=len(messages),
                    request_digest=request_digest,
                    dataset_membership=case.dataset_membership,
                    request_started_at=request_started_at,
                    request_completed_at=utc_now(),
                    attempts=attempts,
                    status="success",
                )
            except Exception as exc:  # runner sonuçlarında hata da kayıt altına alınır
                latency_ms = (perf_counter() - started) * 1000.0
                if provider_call_started is not None:
                    provider_call_latency_ms = (perf_counter() - provider_call_started) * 1000.0
                    retry_overhead_ms = retry_sleep_total * 1000.0
                    pure_inference_latency_ms = max(0.0, provider_call_latency_ms - retry_overhead_ms)
                if isinstance(exc, RetryExhaustedError):
                    attempts = exc.attempts
                refusal = self.refusal_detector.classify_error()
                result = EvaluationResult(
                    evaluation_id=evaluation_id,
                    run_id=self.metadata.run_id,
                    sample_id=case.sample_id,
                    model=self.metadata.model,
                    configuration=self.metadata.configuration,
                    context_mode=self.metadata.context_mode,
                    response_text=None,
                    request_id=request_id,
                    refusal=refusal,
                    latency_ms=latency_ms,
                    provider_call_latency_ms=provider_call_latency_ms,
                    pure_inference_latency_ms=pure_inference_latency_ms,
                    retry_overhead_ms=retry_overhead_ms,
                    error=sanitize_error_message(f"{type(exc).__name__}: {exc}"),
                    input_turn_count=len(messages),
                    request_digest=request_digest,
                    dataset_membership=case.dataset_membership,
                    request_started_at=request_started_at,
                    request_completed_at=utc_now(),
                    attempts=attempts,
                    status="error",
                )
                if fail_fast:
                    self.logger.log(result)
                    raise
            self.logger.log(result)
            results.append(result)
        return results

    def write_artifacts(self, output_dir: str | Path, results: Iterable[EvaluationResult]) -> dict[str, Path]:
        directory = Path(output_dir)
        directory.mkdir(parents=True, exist_ok=True)
        metadata_path = directory / "experiment_metadata.json"
        metrics_path = directory / "metrics.json"
        write_metadata(self.metadata, metadata_path)
        metrics_path.write_text(json.dumps(calculate_metrics(results), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return {"metadata": metadata_path, "metrics": metrics_path}
