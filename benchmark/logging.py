"""Yanıt ve run artifact logger’ları."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from .errors import LoggingError
from .types import EvaluationResult


class ResponseLogger(Protocol):
    def log(self, result: EvaluationResult) -> None:
        ...

    def close(self) -> None:
        ...


class InMemoryResponseLogger:
    def __init__(self) -> None:
        self.results: list[EvaluationResult] = []

    def log(self, result: EvaluationResult) -> None:
        self.results.append(result)

    def close(self) -> None:
        return None


class JsonlResponseLogger:
    """Bir evaluation sonucunu satır bazında append eder.

    F-08/F-24 remediation: bir dosya zaten doluysa sessizce append etmek,
    yeniden çalıştırmalarda satır çift sayımına yol açar. Bu yüzden varsayılan
    davranış fail-closed'tur: mevcut, dolu bir dosyaya yazmak için
    ``append_ok=True`` açıkça verilmelidir. Smoke/dry-run yerel scratch
    akışları bu bayrağı bilinçli olarak geçer; kalıcı değerlendirme
    çıktılarında taze bir çıktı dizini kullanılmalıdır.
    """

    def __init__(self, path: str | Path, *, include_response_text: bool = True,
                 append_ok: bool = False) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.include_response_text = include_response_text
        if not append_ok and self.path.exists() and self.path.stat().st_size > 0:
            raise LoggingError(
                f"{self.path} already exists and is non-empty; refusing to append "
                f"(duplicate-row hazard). Use a fresh output directory or pass "
                f"append_ok=True explicitly.")
        self._handle = self.path.open("a", encoding="utf-8", newline="\n")

    def log(self, result: EvaluationResult) -> None:
        payload = result.to_log_dict()
        if not self.include_response_text:
            payload["response_text"] = None
            payload["error_detail"] = None
        self._handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
        self._handle.flush()

    def close(self) -> None:
        if not self._handle.closed:
            self._handle.close()

    def __enter__(self) -> "JsonlResponseLogger":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
