"""Model adapter interface ve ortak HTTP yardımcıları."""

from __future__ import annotations

import json
import socket
from abc import ABC, abstractmethod
from typing import Any, Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import (
    HTTPRedirectHandler,
    OpenerDirector,
    ProxyHandler,
    Request,
    build_opener,
    getproxies,
)

from ..errors import AdapterRequestError, sanitize_error_message
from ..types import AdapterResponse, GenerationRequest


JsonTransport = Callable[[str, Mapping[str, str], Mapping[str, Any], float], Mapping[str, Any]]


class ModelAdapter(ABC):
    """Tüm model sağlayıcılarının uygulaması gereken sözleşme."""

    provider: str

    @abstractmethod
    def generate(self, request: GenerationRequest) -> AdapterResponse:
        raise NotImplementedError


class DisallowRedirectHandler(HTTPRedirectHandler):
    """Yönlendirmeleri engelleyerek kimlik bilgisi ve gövde sızıntısını önler."""

    def redirect_request(
        self,
        req: Any,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        target = urlsplit(newurl)
        scheme = (target.scheme or "").lower()
        host = target.netloc.split("@")[-1]
        raise AdapterRequestError(f"redirect not followed: HTTP {code} -> {scheme}://{host}")


def _build_opener() -> OpenerDirector:
    """Yönlendirmeleri engelleyen ve yalnızca HTTPS proxy'lerine izin veren opener oluşturur."""
    filtered_proxies = {k: v for k, v in getproxies().items() if k.lower() == "https"}
    return build_opener(ProxyHandler(filtered_proxies), DisallowRedirectHandler)


def urlopen(request: Request, timeout: float = 60.0):
    opener = _build_opener()
    return opener.open(request, timeout=timeout)


def default_json_transport(
    url: str,
    headers: Mapping[str, str],
    payload: Mapping[str, Any],
    timeout_s: float,
) -> Mapping[str, Any]:
    """Standart kütüphane ile JSON POST; testlerde transport inject edilebilir."""

    body = json.dumps(payload).encode("utf-8")
    request = Request(url, data=body, headers=dict(headers), method="POST")
    try:
        with urlopen(request, timeout=timeout_s) as response:  # nosec B310: endpoint config ile belirlenir
            data = response.read().decode("utf-8")
    except AdapterRequestError:
        raise
    except HTTPError as exc:
        raw_detail = exc.read().decode("utf-8", errors="replace")
        retryable = exc.code in {408, 425, 429} or 500 <= exc.code <= 599
        raise AdapterRequestError(
            f"HTTP {exc.code} sağlayıcı hatası",
            status_code=exc.code,
            retryable=retryable,
            detail=sanitize_error_message(raw_detail),
        ) from exc
    except URLError as exc:
        raise AdapterRequestError(f"Sağlayıcı bağlantı hatası: {exc.reason}", retryable=True) from exc
    except (TimeoutError, socket.timeout) as exc:
        raise AdapterRequestError("Sağlayıcı zaman aşımına uğradı", retryable=True) from exc
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError as exc:
        raise AdapterRequestError("Sağlayıcı geçerli JSON döndürmedi") from exc
    if not isinstance(parsed, Mapping):
        raise AdapterRequestError("Sağlayıcı yanıtı JSON nesnesi değil")
    return parsed


def extract_text(payload: Mapping[str, Any]) -> str:
    """Farklı sağlayıcıların yaygın text response biçimlerini normalize eder."""

    if isinstance(payload.get("output_text"), str):
        return payload["output_text"]
    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, Mapping):
            message = first.get("message")
            if isinstance(message, Mapping) and isinstance(message.get("content"), str):
                return message["content"]
            if isinstance(first.get("text"), str):
                return first["text"]
    content = payload.get("content")
    if isinstance(content, list):
        text_parts = [item.get("text", "") for item in content if isinstance(item, Mapping)]
        return "".join(part for part in text_parts if isinstance(part, str))
    if isinstance(payload.get("text"), str):
        return payload["text"]
    raise AdapterRequestError("Sağlayıcı yanıtında normalize edilebilir metin bulunamadı")
