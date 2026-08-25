"""Sınırlı ve gözlemlenebilir retry politikası."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, TypeVar

from .errors import AdapterRequestError, RetryExhaustedError


T = TypeVar("T")


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 2
    initial_backoff_s: float = 0.5
    max_backoff_s: float = 4.0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts en az 1 olmalı")
        if self.initial_backoff_s < 0 or self.max_backoff_s < 0:
            raise ValueError("backoff negatif olamaz")

    def to_dict(self) -> dict[str, float | int]:
        return {
            "max_attempts": self.max_attempts,
            "initial_backoff_s": self.initial_backoff_s,
            "max_backoff_s": self.max_backoff_s,
        }


def is_retryable(error: Exception) -> bool:
    if isinstance(error, AdapterRequestError):
        return error.retryable is True
    return isinstance(error, (TimeoutError, ConnectionError))


def call_with_retry(
    function: Callable[[], T],
    policy: RetryPolicy,
    *,
    sleeper: Callable[[float], None] = time.sleep,
) -> tuple[T, int]:
    last_error: Exception | None = None
    for attempt in range(1, policy.max_attempts + 1):
        try:
            return function(), attempt
        except Exception as error:  # retryability policy aşağıda uygulanır
            last_error = error
            if attempt >= policy.max_attempts or not is_retryable(error):
                break
            delay = min(policy.initial_backoff_s * (2 ** (attempt - 1)), policy.max_backoff_s)
            sleeper(delay)
    assert last_error is not None
    raise RetryExhaustedError(
        f"Çağrı {policy.max_attempts} deneme sonunda tamamlanamadı: {last_error}",
        attempts=attempt,
        last_error=last_error,
    ) from last_error
