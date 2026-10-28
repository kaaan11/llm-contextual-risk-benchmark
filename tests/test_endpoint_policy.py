"""Tests for endpoint trust policy and redirect blocking (#18).

Enforces:
1. https:// allowed for any host.
2. http:// allowed only for loopback (localhost, 127.0.0.0/8, ::1)
   with allow_plaintext_loopback: true.
3. Other schemes refused.
4. Userinfo in URL refused.
5. No opt-in for non-loopback http.
6. Refusal raises AdapterConfigurationError before credentials are read or transport is called.
7. Default json transport blocks HTTP redirects and leaks no credentials.
8. _make_adapter passes allow_plaintext_loopback from provider config.
"""

from __future__ import annotations

import http.server
import json
import os
import threading
from typing import Any
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request

import pytest

from benchmark.adapters.base import DisallowRedirectHandler, default_json_transport
from benchmark.adapters.endpoint_policy import check_endpoint, is_loopback_host
from benchmark.adapters.providers import AnthropicAdapter, OpenAIAdapter, OpenWeightAdapter
from benchmark.errors import AdapterConfigurationError, AdapterRequestError
from benchmark.smoke_test import _make_adapter
from benchmark.types import GenerationRequest, ModelSpec


def _make_request(provider: str) -> GenerationRequest:
    return GenerationRequest(
        sample_id="test-1",
        messages=({"role": "user", "content": "hello"},),
        model=ModelSpec(provider=provider, name="test-model", version="1.0"),
    )


class StubTransport:
    def __init__(self, response: dict[str, Any] | None = None) -> None:
        self.calls: list[tuple[str, dict[str, str], dict[str, Any], float]] = []
        self.response = response or {"choices": [{"message": {"content": "ok"}}], "content": [{"type": "text", "text": "ok"}]}

    def __call__(self, url: str, headers: Any, payload: Any, timeout_s: float) -> dict[str, Any]:
        self.calls.append((url, dict(headers), dict(payload), timeout_s))
        return self.response


# --- Unit tests: is_loopback_host and check_endpoint ---

@pytest.mark.parametrize(
    ("host", "expected"),
    [
        ("localhost", True),
        ("LOCALHOST", True),
        ("127.0.0.1", True),
        ("127.0.0.2", True),
        ("127.255.255.255", True),
        ("::1", True),
        ("[::1]", True),
        ("localhost.evil.com", False),
        ("127.0.0.1.nip.io", False),
        ("10.0.0.5", False),
        ("192.168.1.1", False),
        ("0.0.0.0", False),
        ("api.example.com", False),
        ("", False),
        (None, False),
    ],
)
def test_is_loopback_host(host: str | None, expected: bool):
    assert is_loopback_host(host) is expected


def test_check_endpoint_https_allowed():
    check_endpoint("https://api.example.com/v1")
    check_endpoint("https://localhost:8000/v1")
    check_endpoint("https://10.0.0.5:8000/v1")


def test_check_endpoint_http_non_loopback_refused():
    for url in ["http://api.example.com/v1", "http://localhost.evil.com/", "http://127.0.0.1.nip.io/", "http://10.0.0.5/"]:
        with pytest.raises(AdapterConfigurationError) as exc_info:
            check_endpoint(url, allow_plaintext_loopback=True)
        msg = str(exc_info.value).lower()
        assert "http" in msg
        assert "loopback" in msg
        assert "rule" in msg


def test_check_endpoint_http_loopback():
    loopback_urls = [
        "http://localhost:8000/v1",
        "http://127.0.0.1:8000/v1",
        "http://127.0.0.2:8000",
        "http://[::1]:8000",
    ]
    for url in loopback_urls:
        # Refused without opt-in
        with pytest.raises(AdapterConfigurationError) as exc_info:
            check_endpoint(url, allow_plaintext_loopback=False)
        msg = str(exc_info.value).lower()
        assert "allow_plaintext_loopback" in msg or "opt-in" in msg
        assert "rule" in msg

        # Allowed with opt-in
        check_endpoint(url, allow_plaintext_loopback=True)


def test_check_endpoint_other_schemes_refused():
    for url in ["ftp://x/", "file:///etc/passwd", "data:text/plain,hello", "localhost:8000"]:
        with pytest.raises(AdapterConfigurationError) as exc_info:
            check_endpoint(url, allow_plaintext_loopback=True)
        msg = str(exc_info.value).lower()
        assert "rule" in msg


def test_check_endpoint_userinfo_refused():
    for url in [
        "https://user:pw@host/",
        "http://user:pw@localhost:8000/",
        "https://user@host/path",
        "https://:pw@host/path",
    ]:
        with pytest.raises(AdapterConfigurationError) as exc_info:
            check_endpoint(url, allow_plaintext_loopback=True)
        msg = str(exc_info.value).lower()
        assert "userinfo" in msg
        assert "rule" in msg


# --- Adapter-level tests with stub transport ---

def test_adapter_https_called():
    stub = StubTransport()
    adapter = OpenAIAdapter(endpoint="https://api.example.com/v1", transport=stub)
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        adapter.generate(_make_request("openai"))
    assert len(stub.calls) == 1
    assert stub.calls[0][0] == "https://api.example.com/v1"


def test_adapter_http_non_loopback_refused_even_with_opt_in():
    stub = StubTransport()
    adapter = OpenAIAdapter(
        endpoint="http://api.example.com/v1",
        transport=stub,
        allow_plaintext_loopback=True,
    )
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        with pytest.raises(AdapterConfigurationError) as exc_info:
            adapter.generate(_make_request("openai"))
    assert len(stub.calls) == 0
    assert "loopback" in str(exc_info.value).lower()


def test_adapter_http_loopback_opt_in_matrix():
    # Without opt-in -> refused
    stub = StubTransport()
    adapter = OpenAIAdapter(endpoint="http://localhost:8000/v1", transport=stub, allow_plaintext_loopback=False)
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        with pytest.raises(AdapterConfigurationError):
            adapter.generate(_make_request("openai"))
    assert len(stub.calls) == 0

    # With opt-in -> called
    stub_ok = StubTransport()
    adapter_ok = OpenAIAdapter(endpoint="http://localhost:8000/v1", transport=stub_ok, allow_plaintext_loopback=True)
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        adapter_ok.generate(_make_request("openai"))
    assert len(stub_ok.calls) == 1


@pytest.mark.parametrize("endpoint", ["http://127.0.0.2:8000", "http://[::1]:8000"])
def test_adapter_http_numeric_loopback_with_opt_in(endpoint: str):
    stub = StubTransport()
    adapter = OpenAIAdapter(endpoint=endpoint, transport=stub, allow_plaintext_loopback=True)
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        adapter.generate(_make_request("openai"))
    assert len(stub.calls) == 1
    assert stub.calls[0][0] == endpoint


@pytest.mark.parametrize("endpoint", ["http://localhost.evil.com/", "http://127.0.0.1.nip.io/"])
def test_adapter_http_fake_loopback_domains_refused(endpoint: str):
    stub = StubTransport()
    adapter = OpenAIAdapter(endpoint=endpoint, transport=stub, allow_plaintext_loopback=True)
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        with pytest.raises(AdapterConfigurationError):
            adapter.generate(_make_request("openai"))
    assert len(stub.calls) == 0


@pytest.mark.parametrize("endpoint", ["ftp://x/", "https://user:pw@host/"])
def test_adapter_ftp_and_userinfo_refused(endpoint: str):
    stub = StubTransport()
    adapter = OpenAIAdapter(endpoint=endpoint, transport=stub, allow_plaintext_loopback=True)
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        with pytest.raises(AdapterConfigurationError):
            adapter.generate(_make_request("openai"))
    assert len(stub.calls) == 0


def test_open_weight_no_key_http_10_0_0_5_refused():
    stub = StubTransport()
    adapter = OpenWeightAdapter(
        endpoint="http://10.0.0.5/",
        transport=stub,
        allow_plaintext_loopback=True,
    )
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(AdapterConfigurationError) as exc_info:
            adapter.generate(_make_request("open_weight"))
    assert len(stub.calls) == 0
    assert "loopback" in str(exc_info.value).lower()


def test_refusal_message_does_not_contain_api_key():
    fake_key = "sk-RECOGNISED-SECRET-KEY-1234567890"
    stub = StubTransport()

    # OpenAI
    openai_adapter = OpenAIAdapter(
        endpoint="http://api.example.com/v1",
        transport=stub,
        allow_plaintext_loopback=True,
    )
    with patch.dict(os.environ, {"OPENAI_API_KEY": fake_key}):
        with pytest.raises(AdapterConfigurationError) as exc_info:
            openai_adapter.generate(_make_request("openai"))
        assert fake_key not in str(exc_info.value)
    assert len(stub.calls) == 0

    # Anthropic
    anthropic_adapter = AnthropicAdapter(
        endpoint="http://api.example.com/v1",
        transport=stub,
        allow_plaintext_loopback=True,
    )
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": fake_key}):
        with pytest.raises(AdapterConfigurationError) as exc_info:
            anthropic_adapter.generate(_make_request("anthropic"))
        assert fake_key not in str(exc_info.value)
    assert len(stub.calls) == 0

    # OpenWeight
    ow_adapter = OpenWeightAdapter(
        endpoint="http://api.example.com/v1",
        transport=stub,
        allow_plaintext_loopback=True,
    )
    with patch.dict(os.environ, {"OPENWEIGHT_API_KEY": fake_key}):
        with pytest.raises(AdapterConfigurationError) as exc_info:
            ow_adapter.generate(_make_request("open_weight"))
        assert fake_key not in str(exc_info.value)
    assert len(stub.calls) == 0


def test_default_endpoints_pass_unchanged():
    stub = StubTransport()
    openai = OpenAIAdapter(transport=stub)
    anthropic = AnthropicAdapter(transport=stub)
    assert openai.endpoint == "https://api.openai.com/v1/responses"
    assert anthropic.endpoint == "https://api.anthropic.com/v1/messages"

    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        openai.generate(_make_request("openai"))
    assert len(stub.calls) == 1

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        anthropic.generate(_make_request("anthropic"))
    assert len(stub.calls) == 2


# --- Redirect blocking tests ---

def test_direct_call_disallow_redirect_handler():
    handler = DisallowRedirectHandler()
    req = Request("https://api.example.com/v1")
    with pytest.raises(AdapterRequestError) as exc_info:
        handler.redirect_request(req, None, 302, "Found", {}, "http://127.0.0.1:9000/leaked?token=secret")

    exc = exc_info.value
    assert str(exc) == "redirect not followed: HTTP 302 -> http://127.0.0.1:9000"
    # Ensure no query/token/path in message
    assert "token" not in str(exc)
    assert "secret" not in str(exc)
    assert "leaked" not in str(exc)


@pytest.mark.skipif(
    os.environ.get("BENCHMARK_TEST_OFFLINE") == "1",
    reason="needs loopback sockets; the offline profile blocks every connect. "
           "test_direct_call_disallow_redirect_handler covers the handler offline.",
)
def test_default_transport_blocks_redirect_and_protects_credentials():
    received_on_target: list[dict[str, Any]] = []

    class TargetHandler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            received_on_target.append({
                "path": self.path,
                "headers": dict(self.headers),
            })
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "intercepted"}')

        def log_message(self, format, *args):
            pass

    target_server = http.server.HTTPServer(("127.0.0.1", 0), TargetHandler)
    target_server.timeout = 5
    target_port = target_server.server_port
    target_thread = threading.Thread(target=target_server.handle_request)
    target_thread.start()

    class RedirectHandler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            self.send_response(302)
            self.send_header("Location", f"http://127.0.0.1:{target_port}/leak-path")
            self.end_headers()

        def log_message(self, format, *args):
            pass

    redirect_server = http.server.HTTPServer(("127.0.0.1", 0), RedirectHandler)
    redirect_server.timeout = 5
    redirect_port = redirect_server.server_port
    redirect_thread = threading.Thread(target=redirect_server.handle_request)
    redirect_thread.start()

    secret_auth = "Bearer sk-super-secret-authorization-token"
    secret_key = "anthropic-key-secret-999"

    try:
        with pytest.raises(AdapterRequestError) as exc_info:
            default_json_transport(
                url=f"http://127.0.0.1:{redirect_port}/v1/chat",
                headers={"Authorization": secret_auth, "x-api-key": secret_key},
                payload={"model": "test", "messages": []},
                timeout_s=5.0,
            )

        err_msg = str(exc_info.value)
        assert err_msg == f"redirect not followed: HTTP 302 -> http://127.0.0.1:{target_port}"
        assert secret_auth not in err_msg
        assert secret_key not in err_msg
        assert "leak-path" not in err_msg

        # Target server must have received NOTHING
        assert len(received_on_target) == 0

    finally:
        redirect_server.server_close()
        redirect_thread.join(timeout=10)
        # Ping target server if it is still waiting so handle_request returns
        try:
            import urllib.request
            urllib.request.urlopen(f"http://127.0.0.1:{target_port}/", timeout=0.5)  # nosec B310
        except Exception:
            pass
        target_server.server_close()
        target_thread.join(timeout=10)


# --- _make_adapter config pass-through tests ---

def test_make_adapter_passes_allow_plaintext_loopback():
    base_config = {
        "credential_env": "TEST_KEY",
        "model_env": "TEST_MODEL",
        "model_version_env": "TEST_VERSION",
    }

    # Default: absent -> False
    adapter_default = _make_adapter("openai", base_config, timeout_s=30.0)
    assert adapter_default.allow_plaintext_loopback is False

    # Explicit false -> False
    cfg_false = dict(base_config, allow_plaintext_loopback=False)
    adapter_false = _make_adapter("openai", cfg_false, timeout_s=30.0)
    assert adapter_false.allow_plaintext_loopback is False

    # Explicit true -> True for openai, anthropic, and open_weight
    cfg_true = dict(base_config, allow_plaintext_loopback=True)

    openai_adapter = _make_adapter("openai", cfg_true, timeout_s=30.0)
    assert openai_adapter.allow_plaintext_loopback is True

    anthropic_adapter = _make_adapter("anthropic", cfg_true, timeout_s=30.0)
    assert anthropic_adapter.allow_plaintext_loopback is True

    open_weight_adapter = _make_adapter("open_weight", cfg_true, timeout_s=30.0)
    assert open_weight_adapter.allow_plaintext_loopback is True
