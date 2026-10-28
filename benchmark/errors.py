"""Benchmark-specific exceptions ve güvenli hata metni yardımcıları."""

from __future__ import annotations

import re


_SECRET_PATTERNS = (
    (re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s,;]+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(x-api-key\s*[:=]\s*)[^\s,;]+"), r"\1[REDACTED]"),
    (re.compile(r"\b(?:sk|key|token)-[A-Za-z0-9_-]{12,}\b"), "[REDACTED]"),
)


def sanitize_error_message(message: str, *, limit: int = 500) -> str:
    """Hata metnini loglamadan önce bilinen credential biçimlerini maskeler."""

    sanitized = str(message)
    for pattern, replacement in _SECRET_PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized[:limit]


class BenchmarkError(Exception):
    """Framework temel hatası."""


class DatasetLoadError(BenchmarkError):
    """Dataset yükleme veya kayıt biçimi hatası."""


class LoggingError(BenchmarkError):
    """Run artifact günlükleme hatası (ör. mevcut dolu dosyaya append reddi)."""


class AdapterConfigurationError(BenchmarkError):
    """Adapter yapılandırması veya credential eksikliği."""


class AdapterRequestError(BenchmarkError):
    """Sağlayıcı isteği hatası.

    ``retryable`` bilgisi, runner’ın 4xx kalıcı hataları ile geçici ağ/5xx
    hatalarını ayırmasını sağlar.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        retryable: bool | None = None,
        detail: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.retryable = retryable
        self.detail = detail


class RetryExhaustedError(BenchmarkError):
    """Sınırlı denemeler sonunda çözülemeyen çağrı."""

    def __init__(self, message: str, *, attempts: int, last_error: Exception) -> None:
        super().__init__(message)
        self.attempts = attempts
        self.last_error = last_error

    @property
    def detail(self) -> str | None:
        return getattr(self.last_error, "detail", None)
